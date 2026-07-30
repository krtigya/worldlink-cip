"""
One-time backfill: recompute contract_months, price_quarterly, price_annual
for every existing plan, using the same duration-detection logic now in
normalize_plan(). This is needed because ChangeDetector only calls
_update_plan() when price/speed/bundles/fup actually differ — plans whose
price already matches the corrected value (from a prior scrape) never get
touched again, leaving contract_months/price_quarterly/price_annual stuck
at their pre-fix values (contract_months=1, quarterly/annual=None) forever.

Run once with: docker compose exec worker python /app/backfill_contract_months.py
"""
from app.db.session import get_sync_db
from app.models import Plan
from app.normalization.normalizer import detect_contract_months

session = next(get_sync_db())

plans = session.query(Plan).all()
updated = 0

for plan in plans:
    duration_text = f"{plan.raw_name or ''} {plan.description or ''}"
    contract_months = detect_contract_months(duration_text)

    if contract_months == plan.contract_months:
        continue  # already correct, skip

    # price_monthly on this row is assumed to ALREADY be the true monthly
    # rate (either it was always contract_months=1, or a prior scrape after
    # the normalizer fix already divided it correctly). Reconstruct the
    # original period total from that for price_quarterly/price_annual.
    total_for_period = float(plan.price_monthly) * contract_months

    plan.contract_months = contract_months
    if contract_months == 3:
        plan.price_quarterly = total_for_period
        plan.price_annual = None
    elif contract_months == 12:
        plan.price_annual = total_for_period
        plan.price_quarterly = None
    else:
        plan.price_quarterly = None
        plan.price_annual = None

    updated += 1
    print(f"  {plan.raw_name}: contract_months {contract_months}, "
          f"price_monthly={plan.price_monthly}, "
          f"quarterly={plan.price_quarterly}, annual={plan.price_annual}")

session.commit()
print(f"\nBackfill complete. Updated {updated} of {len(plans)} plans.")