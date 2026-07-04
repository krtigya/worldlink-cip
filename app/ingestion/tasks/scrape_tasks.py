import sys
import asyncio

import traceback
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.ingestion.tasks.celery_app import celery_app
from app.ingestion.scrapers.scraper_factory import ScraperFactory
from app.normalization.normalizer import normalize_plan
from app.detection.change_detector import ChangeDetector
from app.intelligence.rules_engine import RulesEngine
from app.alerts.alert_dispatcher import AlertDispatcher
from app.rag.rag_service import RagService
from app.reports.report_generator import ReportGenerator
from app.models import Isp, Plan, ScrapeRun
from app.logger import get_logger
from app.db.session import get_sync_db    

logger = get_logger(__name__)


def _run_async(coro):
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        try:
            if hasattr(loop, "shutdown_asyncgens"):
                loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()
        asyncio.set_event_loop(None)


def _get_session() -> Session:
    """Return a synchronous DB session from the sync session factory."""
    return next(get_sync_db())


@celery_app.task(
    bind=True,
    name="app.ingestion.tasks.scrape_tasks.scrape_isp",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def scrape_isp(self, isp_id: int) -> dict:
    
    session    = _get_session()
    run_id     = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)

    isp = session.query(Isp).filter_by(id=isp_id).first()
    if not isp:
        raise ValueError(f"ISP {isp_id} not found")

    run = ScrapeRun(id=run_id, isp_id=isp_id, status="running", started_at=start_time)
    session.add(run)
    session.commit()

    logger.info("scrape_started", isp=isp.slug, run_id=run_id)

    try:
        scraper   = ScraperFactory.create(isp)
        raw_plans = _run_async(scraper.scrape())
        logger.info("scrape_raw_complete", isp=isp.slug, count=len(raw_plans))

        normalized_plans = []
        for raw in raw_plans:
            try:
                normalized_plans.append(normalize_plan(raw, isp.slug))
            except ValueError as e:
                logger.warning("normalization_failed", isp=isp.slug, name=raw.get("raw_name"), error=str(e))

        detector = ChangeDetector()
        events   = detector.detect_and_persist(normalized_plans, run_id, session)

        if events:
            plan_ids = [e.plan_id for e in events if e.plan_id]
            plans_by_id = {
                str(p.id): p
                for p in session.query(Plan).filter(Plan.id.in_(plan_ids)).all()
            } if plan_ids else {}

            isp_names  = {isp_id: isp.name}
            rules_eng  = RulesEngine(session)
            alerts     = rules_eng.evaluate(events, plans_by_id, isp_names)

            if alerts:
                dispatcher = AlertDispatcher()
                _run_async(dispatcher.dispatch(alerts))
                logger.info("alerts_dispatched", isp=isp.slug, count=len(alerts))

        try:
            rag = RagService()
            rag.index_all_plans(session)
        except Exception as e:
            logger.warning("rag_reindex_failed", error=str(e))

        duration_ms   = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        plans_new     = sum(1 for e in events if e.change_type.value == "plan_added")
        plans_removed = sum(1 for e in events if e.change_type.value == "plan_removed")
        plans_updated = len(events) - plans_new - plans_removed

        run.status           = "success"
        run.plans_found      = len(raw_plans)
        run.plans_new        = plans_new
        run.plans_updated    = plans_updated
        run.plans_removed    = plans_removed
        run.changes_detected = len(events)
        run.duration_ms      = duration_ms
        run.completed_at     = datetime.now(timezone.utc)
        session.commit()

        logger.info("scrape_complete", isp=isp.slug, run_id=run_id,
                    events=len(events), duration_ms=duration_ms)
        return {"isp": isp.slug, "plans": len(raw_plans), "changes": len(events), "run_id": run_id}

    except Exception as exc:
        run.status        = "failed"
        run.error_message = str(exc)
        run.error_stack   = traceback.format_exc()
        run.completed_at  = datetime.now(timezone.utc)
        session.commit()
        logger.error("scrape_failed", isp=isp.slug, error=str(exc))
        raise


@celery_app.task(name="app.ingestion.tasks.scrape_tasks.scrape_all_isps")
def scrape_all_isps() -> dict:
    """
    Queue individual scrape tasks for every active ISP.

    Staggers each task by 120 seconds (countdown=i*120) so all four
    scrapers don't hammer the DB and target sites simultaneously.

    Returns:
        Dict with keys: queued (count), jobs (list of {isp, job_id}).
    """
    session = _get_session()
    isps    = session.query(Isp).filter_by(status="active").all()

    job_ids = []
    for i, isp in enumerate(isps):
        result = scrape_isp.apply_async(args=[isp.id], countdown=i * 120)
        job_ids.append({"isp": isp.slug, "job_id": result.id})
        logger.info("scrape_queued", isp=isp.slug, job_id=result.id)

    logger.info("all_isps_queued", count=len(isps))
    return {"queued": len(isps), "jobs": job_ids}


@celery_app.task(name="app.ingestion.tasks.scrape_tasks.generate_weekly_report")
def generate_weekly_report() -> dict:
    """
    Generate and persist the weekly competitive intelligence report.

    Computes the Monday of the current week as the report period start,
    then delegates to ReportGenerator which queries change_logs for that week.

    Returns:
        Dict with keys: week (ISO date string), summary (first 100 chars).
    """
    from datetime import date, timedelta
    session    = _get_session()
    today      = date.today()
    week_start = today - timedelta(days=today.weekday())

    logger.info("report_generation_started", week=str(week_start))
    generator = ReportGenerator(session)
    report    = _run_async(generator.generate(week_start))
    logger.info("report_generation_complete", week=str(week_start))
    return {"week": str(week_start), "summary": report.get("summary", "")[:100]}


def _isp_id_by_slug(slug: str) -> int:
    """
    Resolve an ISP's primary key from its slug.

    Used by named shortcut tasks so isp_ids never need to be hardcoded
    as constants — slugs are stable across environments, integer ids are not.

    Args:
        slug: ISP slug string e.g. 'worldlink', 'vianet', 'cgnet', 'dishhome'.

    Raises:
        ValueError: If no active ISP row exists with the given slug.
    """
    session = _get_session()
    isp = session.query(Isp).filter_by(slug=slug).first()
    if not isp:
        raise ValueError(f"No ISP found with slug '{slug}'")
    return isp.id


@celery_app.task(
    bind=True,
    name="app.ingestion.tasks.scrape_tasks.scrape_worldlink_task",
    max_retries=2,
    default_retry_delay=300,
)
def scrape_worldlink_task(self):
    """
    Named shortcut task for scraping WorldLink.

    Resolves WorldLink's isp_id by slug and enqueues scrape_isp as a
    new Celery task via .apply_async(), keeping execution fully async
    and isolated from this task's worker process.
    """
    try:
        return scrape_isp.apply_async(args=[_isp_id_by_slug("worldlink")])
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="app.ingestion.tasks.scrape_tasks.scrape_vianet_task",
    max_retries=2,
    default_retry_delay=300,
)
def scrape_vianet_task(self):
    """
    Named shortcut task for scraping Vianet.

    Resolves Vianet's isp_id by slug and enqueues scrape_isp as a
    new Celery task via .apply_async().
    """
    try:
        return scrape_isp.apply_async(args=[_isp_id_by_slug("vianet")])
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="app.ingestion.tasks.scrape_tasks.scrape_cgnet_task",
    max_retries=2,
    default_retry_delay=300,
)
def scrape_cgnet_task(self):
    """
    Named shortcut task for scraping CGNet.

    Resolves CGNet's isp_id by slug and enqueues scrape_isp as a
    new Celery task via .apply_async().
    """
    try:
        return scrape_isp.apply_async(args=[_isp_id_by_slug("cgnet")])
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="app.ingestion.tasks.scrape_tasks.scrape_dishhome_task",
    max_retries=2,
    default_retry_delay=300,
)
def scrape_dishhome_task(self):
    """
    Named shortcut task for scraping DishHome.

    Resolves DishHome's isp_id by slug and enqueues scrape_isp as a
    new Celery task via .apply_async(). DishHome uses Playwright so
    may take longer — default_retry_delay is 300s accordingly.
    """
    try:
        return scrape_isp.apply_async(args=[_isp_id_by_slug("dishhome")])
    except Exception as exc:
        raise self.retry(exc=exc)