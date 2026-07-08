

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)



class Severity(str, Enum):
    CRITICAL = "critical"   # price drop >10%, plan removed
    HIGH     = "high"       # bundle change, new plan, speed change
    MEDIUM   = "medium"     # price change 3-10%
    LOW      = "low"        # minor metadata change


class ChangeType(str, Enum):
    PRICE_DECREASE  = "price_decrease"
    PRICE_INCREASE  = "price_increase"
    SPEED_CHANGE    = "speed_change"
    BUNDLE_ADDED    = "bundle_added"
    BUNDLE_REMOVED  = "bundle_removed"
    PLAN_ADDED      = "plan_added"
    PLAN_REMOVED    = "plan_removed"
    STATUS_CHANGE   = "status_change"



@dataclass
class ScrapedPlan:
    """Normalized output from any ISP scraper."""
    isp_id:          int
    raw_name:        str
    normalized_name: str
    plan_type:       str
    download_mbps:   int
    speed_raw:       str
    price_monthly:   Decimal | None
    price_quarterly: Decimal | None
    price_annual:    Decimal | None
    price_raw:       str
    vat_included:    bool
    is_unlimited:    bool
    contract_months: int
    bundles:         list[dict]   
    bundle_flags:    set[str]     
    description:     str
    scrape_url:      str
    raw_data:        dict = field(default_factory=dict)


@dataclass
class ChangeEvent:
    """One detected change to be written to change_logs."""
    isp_id:      int
    plan_id:     int | None       
    change_type: ChangeType
    severity:    Severity
    field_name:  str | None
    old_value:   str | None
    new_value:   str | None
    diff_pct:    float | None
    summary:     str
    details:     dict




def _price_severity(diff_pct: float) -> Severity:
    """Map a price diff percentage to severity. diff_pct is signed (negative = cheaper)."""
    abs_pct = abs(diff_pct)
    if abs_pct >= 10:
        return Severity.CRITICAL
    if abs_pct >= 3:
        return Severity.MEDIUM
    return Severity.LOW


def _change_type_for_price(diff_pct: float) -> ChangeType:
    return ChangeType.PRICE_DECREASE if diff_pct < 0 else ChangeType.PRICE_INCREASE



def _diff_price(
    field_name: str,
    isp_id: int,
    plan_id: int,
    old_val: Decimal | None,
    new_val: Decimal | None,
    isp_name: str,
    plan_name: str,
) -> ChangeEvent | None:
    """Compare one price field; return a ChangeEvent if it changed."""
    if old_val is None and new_val is None:
        return None
    if old_val == new_val:
        return None
    # Treat None→value as not comparable (plan variant added, handled elsewhere)
    if old_val is None or new_val is None:
        return None

    diff_pct = float((new_val - old_val) / old_val * 100)
    if abs(diff_pct) < 0.5:          # ignore rounding noise
        return None

    change_type = _change_type_for_price(diff_pct)
    severity = _price_severity(diff_pct)
    direction = "dropped" if diff_pct < 0 else "increased"

    return ChangeEvent(
        isp_id=isp_id,
        plan_id=plan_id,
        change_type=change_type,
        severity=severity,
        field_name=field_name,
        old_value=str(old_val),
        new_value=str(new_val),
        diff_pct=round(diff_pct, 2),
        summary=(
            f"{isp_name} '{plan_name}' {field_name} {direction} "
            f"from Rs {old_val:,.0f} to Rs {new_val:,.0f} ({diff_pct:+.1f}%)"
        ),
        details={
            "field": field_name,
            "old": float(old_val),
            "new": float(new_val),
            "diff_pct": round(diff_pct, 2),
        },
    )


def _diff_speed(
    isp_id: int,
    plan_id: int,
    old_mbps: int,
    new_mbps: int,
    isp_name: str,
    plan_name: str,
) -> ChangeEvent | None:
    if old_mbps == new_mbps:
        return None
    diff_pct = (new_mbps - old_mbps) / old_mbps * 100
    direction = "increased" if new_mbps > old_mbps else "decreased"
    return ChangeEvent(
        isp_id=isp_id,
        plan_id=plan_id,
        change_type=ChangeType.SPEED_CHANGE,
        severity=Severity.HIGH,
        field_name="download_mbps",
        old_value=str(old_mbps),
        new_value=str(new_mbps),
        diff_pct=round(diff_pct, 2),
        summary=(
            f"{isp_name} '{plan_name}' speed {direction} "
            f"from {old_mbps} Mbps to {new_mbps} Mbps"
        ),
        details={"old_mbps": old_mbps, "new_mbps": new_mbps, "diff_pct": round(diff_pct, 2)},
    )


def _diff_bundles(
    isp_id: int,
    plan_id: int,
    old_flags: set[str],
    new_flags: set[str],
    isp_name: str,
    plan_name: str,
) -> list[ChangeEvent]:
    events = []
    added   = new_flags - old_flags
    removed = old_flags - new_flags

    if added:
        events.append(ChangeEvent(
            isp_id=isp_id,
            plan_id=plan_id,
            change_type=ChangeType.BUNDLE_ADDED,
            severity=Severity.HIGH,
            field_name="bundle_flags",
            old_value=json.dumps(sorted(old_flags)),
            new_value=json.dumps(sorted(new_flags)),
            diff_pct=None,
            summary=f"{isp_name} '{plan_name}' added bundles: {', '.join(sorted(added))}",
            details={"added": sorted(added), "removed": [], "old": sorted(old_flags), "new": sorted(new_flags)},
        ))

    if removed:
        events.append(ChangeEvent(
            isp_id=isp_id,
            plan_id=plan_id,
            change_type=ChangeType.BUNDLE_REMOVED,
            severity=Severity.HIGH,
            field_name="bundle_flags",
            old_value=json.dumps(sorted(old_flags)),
            new_value=json.dumps(sorted(new_flags)),
            diff_pct=None,
            summary=f"{isp_name} '{plan_name}' removed bundles: {', '.join(sorted(removed))}",
            details={"added": [], "removed": sorted(removed), "old": sorted(old_flags), "new": sorted(new_flags)},
        ))

    return events




def diff_plan(
    scraped:  ScrapedPlan,
    existing: dict[str, Any],   # one row from the plans table as a dict
    isp_name: str,
) -> list[ChangeEvent]:
    """
    Compare a single freshly scraped plan against its existing DB row.
    Returns a (possibly empty) list of ChangeEvents.
    """
    events: list[ChangeEvent] = []
    plan_id   = existing["id"]
    plan_name = scraped.normalized_name

    # ── Price fields ──────────────────────────────────────────
    for field_name in ("price_monthly", "price_quarterly", "price_annual"):
        ev = _diff_price(
            field_name=field_name,
            isp_id=scraped.isp_id,
            plan_id=plan_id,
            old_val=existing.get(field_name),
            new_val=getattr(scraped, field_name),
            isp_name=isp_name,
            plan_name=plan_name,
        )
        if ev:
            events.append(ev)

    # ── Speed ────────────────────────────────────────────────
    ev = _diff_speed(
        isp_id=scraped.isp_id,
        plan_id=plan_id,
        old_mbps=existing["download_mbps"],
        new_mbps=scraped.download_mbps,
        isp_name=isp_name,
        plan_name=plan_name,
    )
    if ev:
        events.append(ev)

    # ── Bundle flags ─────────────────────────────────────────
    old_flags = set(existing.get("bundle_flags") or [])
    new_flags = scraped.bundle_flags or set()
    events.extend(_diff_bundles(scraped.isp_id, plan_id, old_flags, new_flags, isp_name, plan_name))

    # ── Status change (active → inactive, etc.) ───────────────
    if existing.get("status") != scraped.plan_type:   # e.g. active → promotional
        pass  # add if your scrapers ever set status directly

    return events


def diff_plans(
    scraped_plans:    list[ScrapedPlan],
    existing_plans:   list[dict[str, Any]],   # rows from DB for this isp_id
    isp_name:         str,
) -> list[ChangeEvent]:
    """
    Full diff for one ISP's scrape run.

    Detects:
    - Changed prices / speed / bundles on existing plans
    - Newly added plans (plan_added)
    - Plans that have disappeared (plan_removed)
    """
    events: list[ChangeEvent] = []
    isp_id = scraped_plans[0].isp_id if scraped_plans else None

    # Index existing plans by normalized_name for O(1) lookup
    existing_by_name: dict[str, dict] = {p["normalized_name"]: p for p in existing_plans}
    scraped_by_name:  dict[str, ScrapedPlan] = {p.normalized_name: p for p in scraped_plans}

    # ── Check each scraped plan against DB ────────────────────
    for name, scraped in scraped_by_name.items():
        if name not in existing_by_name:
            # Brand new plan
            events.append(ChangeEvent(
                isp_id=scraped.isp_id,
                plan_id=None,
                change_type=ChangeType.PLAN_ADDED,
                severity=Severity.HIGH,
                field_name=None,
                old_value=None,
                new_value=None,
                diff_pct=None,
                summary=f"{isp_name} new plan detected: '{name}' at {scraped.price_raw}",
                details={
                    "normalized_name": name,
                    "download_mbps": scraped.download_mbps,
                    "price_monthly": float(scraped.price_monthly) if scraped.price_monthly else None,
                    "price_annual":  float(scraped.price_annual)  if scraped.price_annual  else None,
                    "bundle_flags":  sorted(scraped.bundle_flags or []),
                },
            ))
        else:
            
            events.extend(diff_plan(scraped, existing_by_name[name], isp_name))

    
    for name, existing in existing_by_name.items():
        if name not in scraped_by_name and existing.get("status") == "active":
            events.append(ChangeEvent(
                isp_id=existing["isp_id"],
                plan_id=existing["id"],
                change_type=ChangeType.PLAN_REMOVED,
                severity=Severity.CRITICAL,
                field_name="status",
                old_value="active",
                new_value="removed",
                diff_pct=None,
                summary=f"{isp_name} plan no longer listed: '{name}'",
                details={"normalized_name": name, "last_seen_price": str(existing.get("price_monthly"))},
            ))

    logger.info(
        "Diff complete for %s: %d scraped, %d existing, %d changes detected",
        isp_name, len(scraped_plans), len(existing_plans), len(events),
    )
    return events


# ── DB persistence ────────────────────────────────────────────────────────────

async def persist_changes(
    session:  AsyncSession,
    events:   list[ChangeEvent],
    scraped:  list[ScrapedPlan],
) -> int:
    """
    Writes ChangeEvents to change_logs and upserts updated plan rows.
    Returns the number of change_log rows inserted.
    """
    if not events and not scraped:
        return 0

    
    for plan in scraped:
        await session.execute(
            text("""
                INSERT INTO plans (
                    isp_id, raw_name, normalized_name, plan_type, status,
                    download_mbps, speed_raw,
                    price_monthly, price_quarterly, price_annual, price_raw,
                    vat_included, is_unlimited, contract_months,
                    bundles, bundle_flags, description, scrape_url, raw_data,
                    updated_at
                ) VALUES (
                    :isp_id, :raw_name, :normalized_name, :plan_type, 'active',
                    :download_mbps, :speed_raw,
                    :price_monthly, :price_quarterly, :price_annual, :price_raw,
                    :vat_included, :is_unlimited, :contract_months,
                    :bundles::jsonb, :bundle_flags, :description, :scrape_url, :raw_data::jsonb,
                    NOW()
                )
                ON CONFLICT (isp_id, normalized_name)
                DO UPDATE SET
                    price_monthly   = EXCLUDED.price_monthly,
                    price_quarterly = EXCLUDED.price_quarterly,
                    price_annual    = EXCLUDED.price_annual,
                    price_raw       = EXCLUDED.price_raw,
                    download_mbps   = EXCLUDED.download_mbps,
                    speed_raw       = EXCLUDED.speed_raw,
                    bundles         = EXCLUDED.bundles,
                    bundle_flags    = EXCLUDED.bundle_flags,
                    status          = 'active',
                    updated_at      = NOW()
            """),
            {
                "isp_id":          plan.isp_id,
                "raw_name":        plan.raw_name,
                "normalized_name": plan.normalized_name,
                "plan_type":       plan.plan_type,
                "download_mbps":   plan.download_mbps,
                "speed_raw":       plan.speed_raw,
                "price_monthly":   plan.price_monthly,
                "price_quarterly": plan.price_quarterly,
                "price_annual":    plan.price_annual,
                "price_raw":       plan.price_raw,
                "vat_included":    plan.vat_included,
                "is_unlimited":    plan.is_unlimited,
                "contract_months": plan.contract_months,
                "bundles":         json.dumps(plan.bundles),
                "bundle_flags":    list(plan.bundle_flags or []),
                "description":     plan.description,
                "scrape_url":      plan.scrape_url,
                "raw_data":        json.dumps(plan.raw_data),
            },
        )

    # 2. Mark plans that disappeared as inactive
    removed_names = [
        e.details["normalized_name"]
        for e in events
        if e.change_type == ChangeType.PLAN_REMOVED
    ]
    if removed_names:
        await session.execute(
            text("""
                UPDATE plans SET status = 'inactive', updated_at = NOW()
                WHERE isp_id = :isp_id AND normalized_name = ANY(:names)
            """),
            {"isp_id": events[0].isp_id, "names": removed_names},
        )

    # 3. Insert change_logs rows (skip plan_added until after upsert so plan_id exists)
    inserted = 0
    for ev in events:
        if ev.change_type == ChangeType.PLAN_ADDED:
            # Resolve the plan_id that was just upserted
            row = await session.execute(
                text("SELECT id FROM plans WHERE isp_id = :isp_id AND normalized_name = :name"),
                {"isp_id": ev.isp_id, "name": ev.details["normalized_name"]},
            )
            result = row.fetchone()
            ev.plan_id = result[0] if result else None

        await session.execute(
            text("""
                INSERT INTO change_logs (
                    isp_id, plan_id, change_type, severity,
                    field_name, old_value, new_value, diff_pct,
                    summary, details, detected_at
                ) VALUES (
                    :isp_id, :plan_id, :change_type, :severity,
                    :field_name, :old_value, :new_value, :diff_pct,
                    :summary, :details::jsonb, NOW()
                )
            """),
            {
                "isp_id":      ev.isp_id,
                "plan_id":     ev.plan_id,
                "change_type": ev.change_type.value,
                "severity":    ev.severity.value,
                "field_name":  ev.field_name,
                "old_value":   ev.old_value,
                "new_value":   ev.new_value,
                "diff_pct":    ev.diff_pct,
                "summary":     ev.summary,
                "details":     json.dumps(ev.details),
            },
        )
        inserted += 1

    await session.commit()
    return inserted


# ── DB fetch helper ───────────────────────────────────────────────────────────

async def fetch_existing_plans(session: AsyncSession, isp_id: int) -> list[dict]:
    """Fetch all active plans for an ISP from the DB."""
    result = await session.execute(
        text("""
            SELECT id, isp_id, normalized_name, download_mbps,
                   price_monthly, price_quarterly, price_annual,
                   bundle_flags, status
            FROM plans
            WHERE isp_id = :isp_id AND status != 'removed'
        """),
        {"isp_id": isp_id},
    )
    rows = result.mappings().all()
    return [dict(r) for r in rows]
