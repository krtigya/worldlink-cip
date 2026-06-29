"""
Here i refactor code for Celery application factory with Redis broker + backend.
"""
from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "worldlink_cip",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.ingestion.tasks.scrape_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kathmandu",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.ingestion.tasks.scrape_tasks.*": {"queue": "scrape"},
        "app.reports.*": {"queue": "reports"},
    },
    beat_schedule={
        # ── Full sweep every 6 hours ──────────────────────────
        "scrape-all-isps": {
            "task": "app.ingestion.tasks.scrape_tasks.scrape_all_isps",
            "schedule": crontab(minute=0, hour="*/6"),
        },
        # ── Per-ISP named tasks (staggered by 5 min) ─────────
        "scrape-worldlink": {
            "task": "app.ingestion.tasks.scrape_tasks.scrape_worldlink_task",
            "schedule": crontab(minute=0, hour="*/12"),
        },
        "scrape-vianet": {
            "task": "app.ingestion.tasks.scrape_tasks.scrape_vianet_task",
            "schedule": crontab(minute=5, hour="*/12"),
        },
        "scrape-cgnet": {
            "task": "app.ingestion.tasks.scrape_tasks.scrape_cgnet_task",
            "schedule": crontab(minute=10, hour="*/12"),
        },
        "scrape-dishhome": {
            "task": "app.ingestion.tasks.scrape_tasks.scrape_dishhome_task",
            "schedule": crontab(minute=15, hour="*/12"),
        },
        # ── Weekly report every Monday 8am NPT (2:15 UTC) ────
        "weekly-report": {
            "task": "app.ingestion.tasks.scrape_tasks.generate_weekly_report",
            "schedule": crontab(minute=15, hour=2, day_of_week=1),
        },
    },
)