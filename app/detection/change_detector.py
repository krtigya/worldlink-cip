"""app/detection/change_detector.py
Compares freshly-scraped normalized plans against DB state.
Emits structured ChangeEvent objects and persists everything in one transaction.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Plan, PricingHistory, ChangeLog, ChangeType, SeverityLevel
from app.normalization.normalizer import NormalizedPlan
from app.logger import get_logger

logger = get_logger(__name__)

PRICE_DELTA_THRESHOLD_PCT = 0.5
SPEED_DELTA_THRESHOLD_MBPS = 5


@dataclass
class ChangeEvent:
    isp_id: int
    change_type: ChangeType
    severity: SeverityLevel
    summary: str
    details: dict
    scrape_run_id: str
    plan_id: Optional[str] = None
    field_name: Optional[str] = None
    old_value: Optional[object] = None
    new_value: Optional[object] = None
    diff_pct: Optional[float] = None


def _price_severity(diff_pct: float) -> SeverityLevel:
    abs_diff = abs(diff_pct)
    if abs_diff >= 30: return SeverityLevel.critical
    if abs_diff >= 20: return SeverityLevel.high
    if abs_diff >= 10: return SeverityLevel.medium
    return SeverityLevel.low


def _plan_key(isp_id: int, normalized_name: str, download_mbps: int) -> str:
    return f"{isp_id}:{normalized_name.lower()}:{download_mbps}"


class ChangeDetector:

    def detect_and_persist(
        self,
        scraped_plans: list[NormalizedPlan],
        scrape_run_id: str,
        session: Session,
    ) -> list[ChangeEvent]:
        if not scraped_plans:
            return []

        isp_id = scraped_plans[0].isp_id
        events: list[ChangeEvent] = []

        existing_plans: list[Plan] = (
            session.query(Plan)
            .filter(Plan.isp_id == isp_id, Plan.status.in_(["active", "promotional"]))
            .all()
        )
        existing_map = {
            _plan_key(p.isp_id, p.normalized_name, p.download_mbps): p
            for p in existing_plans
        }
        scraped_keys = {
            _plan_key(p.isp_id, p.normalized_name, p.download_mbps)
            for p in scraped_plans
        }

        for scraped in scraped_plans:
            key      = _plan_key(scraped.isp_id, scraped.normalized_name, scraped.download_mbps)
            existing = existing_map.get(key)

            if not existing:
                new_plan = None
                try:
                    new_plan = self._insert_plan(session, scraped)
                    session.flush()
                except Exception:
                    session.rollback()
                    new_plan = session.query(Plan).filter(
                        Plan.isp_id == scraped.isp_id,
                        Plan.normalized_name == scraped.normalized_name,
                        Plan.download_mbps == scraped.download_mbps,
                    ).first()

                if not new_plan:
                    continue

                events.append(ChangeEvent(
                    isp_id=isp_id,
                    change_type=ChangeType.plan_added,
                    severity=SeverityLevel.high,
                    summary=(f"New plan detected: {scraped.normalized_name} — "
                             f"NPR {scraped.price_monthly}/mo at {scraped.download_mbps} Mbps"),
                    details={"plan_name": scraped.normalized_name,
                             "download_mbps": scraped.download_mbps,
                             "price_monthly": scraped.price_monthly,
                             "bundle_flags": scraped.bundle_flags},
                    scrape_run_id=scrape_run_id,
                    plan_id=str(new_plan.id),
                ))
            else:
                plan_events = self._diff_plan(session, existing, scraped, scrape_run_id)
                events.extend(plan_events)

        for key, existing in existing_map.items():
            if key not in scraped_keys:
                existing.status = "discontinued"
                events.append(ChangeEvent(
                    isp_id=isp_id,
                    change_type=ChangeType.plan_removed,
                    severity=SeverityLevel.medium,
                    summary=(f"Plan discontinued: {existing.normalized_name} "
                             f"({existing.download_mbps} Mbps @ NPR {existing.price_monthly})"),
                    details={"plan_name": existing.normalized_name},
                    scrape_run_id=scrape_run_id,
                    plan_id=str(existing.id),
                ))

        # Flush all plans before adding change logs
        try:
            session.flush()
        except Exception:
            session.rollback()
            return []

        # Get valid plan IDs to avoid FK violations
        valid_plan_ids = {
            str(p.id) for p in session.query(Plan).filter(Plan.isp_id == isp_id).all()
        }

        for ev in events:
            if ev.plan_id and ev.plan_id not in valid_plan_ids:
                continue
            session.add(ChangeLog(
                isp_id=ev.isp_id,
                plan_id=ev.plan_id,
                change_type=ev.change_type,
                severity=ev.severity,
                field_name=ev.field_name,
                old_value=ev.old_value,
                new_value=ev.new_value,
                diff_pct=ev.diff_pct,
                summary=ev.summary,
                details=ev.details,
                scrape_run_id=ev.scrape_run_id,
            ))

        session.commit()
        logger.info("detection_complete", isp_id=isp_id,
                    events=len(events), run=scrape_run_id)
        return events

    def _diff_plan(
        self,
        session: Session,
        existing: Plan,
        scraped: NormalizedPlan,
        scrape_run_id: str,
    ) -> list[ChangeEvent]:
        events: list[ChangeEvent] = []
        plan_id = str(existing.id)
        changed = False

        price_diff_pct = ((scraped.price_monthly - float(existing.price_monthly))
                          / float(existing.price_monthly)) * 100
        if abs(price_diff_pct) > PRICE_DELTA_THRESHOLD_PCT:
            change_type = (ChangeType.price_decrease if price_diff_pct < 0
                           else ChangeType.price_increase)
            events.append(ChangeEvent(
                isp_id=existing.isp_id,
                change_type=change_type,
                severity=_price_severity(price_diff_pct),
                field_name="price_monthly",
                old_value=float(existing.price_monthly),
                new_value=scraped.price_monthly,
                diff_pct=round(price_diff_pct, 1),
                summary=(f"{existing.normalized_name}: price "
                         f"{'dropped' if price_diff_pct < 0 else 'increased'} "
                         f"NPR {existing.price_monthly} -> {scraped.price_monthly} "
                         f"({price_diff_pct:+.1f}%)"),
                details={"plan_name": existing.normalized_name,
                         "download_mbps": existing.download_mbps,
                         "old_price": float(existing.price_monthly),
                         "new_price": scraped.price_monthly},
                scrape_run_id=scrape_run_id,
                plan_id=plan_id,
            ))
            changed = True

        speed_diff = scraped.download_mbps - existing.download_mbps
        if abs(speed_diff) > SPEED_DELTA_THRESHOLD_MBPS:
            events.append(ChangeEvent(
                isp_id=existing.isp_id,
                change_type=ChangeType.speed_change,
                severity=SeverityLevel.high if speed_diff > 0 else SeverityLevel.medium,
                field_name="download_mbps",
                old_value=existing.download_mbps,
                new_value=scraped.download_mbps,
                diff_pct=round((speed_diff / existing.download_mbps) * 100, 1),
                summary=(f"{existing.normalized_name}: speed changed "
                         f"{existing.download_mbps} -> {scraped.download_mbps} Mbps"),
                details={"plan_name": existing.normalized_name,
                         "old_speed": existing.download_mbps,
                         "new_speed": scraped.download_mbps,
                         "price_unchanged": abs(price_diff_pct) <= PRICE_DELTA_THRESHOLD_PCT},
                scrape_run_id=scrape_run_id,
                plan_id=plan_id,
            ))
            changed = True

        old_flags = set(existing.bundle_flags or [])
        new_flags = set(scraped.bundle_flags)
        added   = new_flags - old_flags
        removed = old_flags - new_flags

        if added:
            events.append(ChangeEvent(
                isp_id=existing.isp_id, change_type=ChangeType.bundle_added,
                severity=SeverityLevel.high,
                field_name="bundle_flags", old_value=list(old_flags), new_value=list(new_flags),
                summary=f"{existing.normalized_name}: new bundles — {', '.join(added)}",
                details={"added": list(added), "plan_name": existing.normalized_name},
                scrape_run_id=scrape_run_id, plan_id=plan_id,
            ))
            changed = True

        if removed:
            events.append(ChangeEvent(
                isp_id=existing.isp_id, change_type=ChangeType.bundle_removed,
                severity=SeverityLevel.medium,
                field_name="bundle_flags", old_value=list(old_flags), new_value=list(new_flags),
                summary=f"{existing.normalized_name}: bundles removed — {', '.join(removed)}",
                details={"removed": list(removed), "plan_name": existing.normalized_name},
                scrape_run_id=scrape_run_id, plan_id=plan_id,
            ))
            changed = True

        fup_changed = (existing.fup_gb != scraped.fup_gb or
                       existing.is_unlimited != scraped.is_unlimited)
        if fup_changed:
            events.append(ChangeEvent(
                isp_id=existing.isp_id, change_type=ChangeType.fup_change,
                severity=SeverityLevel.medium,
                field_name="fup_gb",
                old_value={"fup_gb": existing.fup_gb, "is_unlimited": existing.is_unlimited},
                new_value={"fup_gb": scraped.fup_gb, "is_unlimited": scraped.is_unlimited},
                summary=(f"{existing.normalized_name}: data policy changed — "
                         f"{'Unlimited' if existing.is_unlimited else f'{existing.fup_gb}GB'} -> "
                         f"{'Unlimited' if scraped.is_unlimited else f'{scraped.fup_gb}GB'}"),
                details={"plan_name": existing.normalized_name},
                scrape_run_id=scrape_run_id, plan_id=plan_id,
            ))
            changed = True

        if changed:
            self._update_plan(existing, scraped)
            session.add(PricingHistory(
                plan_id=existing.id, isp_id=existing.isp_id,
                price_monthly=scraped.price_monthly,
                download_mbps=scraped.download_mbps, upload_mbps=scraped.upload_mbps,
                fup_gb=scraped.fup_gb, bundle_flags=scraped.bundle_flags,
                status="active", scrape_run_id=scrape_run_id,
            ))
        else:
            existing.last_seen_at = datetime.now(timezone.utc)

        return events

    def _insert_plan(self, session: Session, p: NormalizedPlan) -> Plan:
        plan = Plan(
            isp_id=p.isp_id, raw_name=p.raw_name, normalized_name=p.normalized_name,
            plan_type=p.plan_type, status="active",
            download_mbps=p.download_mbps, upload_mbps=p.upload_mbps, speed_raw=p.speed_raw,
            price_monthly=p.price_monthly, price_quarterly=p.price_quarterly,
            price_annual=p.price_annual, price_raw=p.price_raw,
            setup_fee=p.setup_fee, vat_included=p.vat_included,
            fup_gb=p.fup_gb, is_unlimited=p.is_unlimited, contract_months=p.contract_months,
            bundles=p.bundles, bundle_flags=p.bundle_flags,
            description=p.description, scrape_url=p.scrape_url, raw_data=p.raw_data,
        )
        session.add(plan)
        return plan

    def _update_plan(self, plan: Plan, p: NormalizedPlan) -> None:
        plan.price_monthly = p.price_monthly
        plan.download_mbps = p.download_mbps
        plan.upload_mbps   = p.upload_mbps
        plan.fup_gb        = p.fup_gb
        plan.is_unlimited  = p.is_unlimited
        plan.bundles       = p.bundles
        plan.bundle_flags  = p.bundle_flags
        plan.raw_data      = p.raw_data
        plan.last_seen_at  = datetime.now(timezone.utc)