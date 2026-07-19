# CIP — Session Notes & Punch List

##  Fixed and verified tonight (2026-07-19)

### 1. WorldLink scraper only captured 3 plans instead of the real ~9-20
**Root cause:** `app/ingestion/scrapers/worldlink_scraper.py` pointed at a stale URL
(`worldlink.com.np/packages`, redirects to homepage) instead of the real listing
(`worldlink.com.np/internet-plans/residential-broadband/`), and had no pagination
(the real listing spans 4 pages).

**Fix applied:** Rewrote scraper to hit the correct base URL, walk all paginated
pages (auto-detects total page count from the pagination control), and include
badge/variant text in `raw_name` so bundle variants don't silently collapse.

**Result:** WorldLink went from 3 plans → 9 real plans (200/250/300 Mbps ×
1/3/12 month durations), all with correct prices confirmed via direct DB query
and live scrape logs.

**Residual gap (not fixed, low priority):** The 9 captured plans are the base
tiers only — NETTV/Nokia Beacon bundle variants at the same speed+duration still
collapse into one row. Real coverage on WorldLink's site is 20+ cards including
bundle permutations. Deeper HTML inspection needed to capture those distinctly
(likely need a stable identifier beyond visible text — maybe the "Buy Plan" link
href — since duplicate visible text appears across pages).

---

### 2. `/api/plans/compare` — same plan showing two different WorldLink prices
**Root cause:** `app/api/routes/plans.py`, `compare_vs_worldlink()` — the `wl` CTE
selected one row per WorldLink plan (`SELECT download_mbps, price_monthly`) instead
of one row per speed tier. Once WorldLink correctly had 3 active plans at 300 Mbps
(from fix #1 above), the `LEFT JOIN wl ON wl.download_mbps = p.download_mbps`
became a cartesian product — every competitor plan at 300 Mbps got joined against
all 3 WorldLink 300 Mbps rows, producing duplicate output rows with different
`worldlink_price` values for the same competitor plan.

**Fix applied:** Changed the `wl` CTE to `SELECT download_mbps, MIN(price_monthly)
... GROUP BY download_mbps` — same pattern already correctly used in
`/api/reports/positioning`. Now one canonical (cheapest) WL price per speed tier.

**Result:** Verified via dashboard screenshots — "Entrepreneur 300 Mbps 12 Months"
(DishHome) now appears once with a single consistent WL price (Rs 1,550), instead
of twice with conflicting Rs 4,050 / Rs 1,550.

---

## Top priority for next session

### 3. `price_monthly` is not actually monthly for multi-month plans
**Diagnosis (confirmed, not yet fixed):** In `app/normalization/normalizer.py`,
`normalize_plan()`:
- `contract_months=1` is **hardcoded** — never reflects the plan's real duration
  (1/3/12 months), regardless of what the scraper found.
- `price_monthly = normalize_price(raw.get("raw_price", "0"))` takes the raw
  scraped number as-is — for a "3 Months, Rs. 4,050" plan, `price_monthly` gets
  set to **4050** (the full period total), not **1350** (the true monthly rate).
- `price_quarterly` / `price_annual` are declared in `NormalizedPlan` but **never
  populated** — always `None`, for every plan, every ISP.

**Why this matters:** Every query using `MIN(price_monthly)` (both `/compare` and
`/positioning`, i.e. the two endpoints we just fixed tonight) is biased toward
whichever plan has the *shortest* contract, not the *cheapest actual monthly
cost*. E.g. WorldLink's 300 Mbps 12-month plan is actually Rs 1,300/mo (15,600÷12)
— cheaper than the 1-month plan at Rs 1,550/mo — but the dashboard currently shows
Rs 1,550 as "the WorldLink price" because it's the smallest raw number, not the
smallest true monthly rate.

**This is a systemic bug affecting all 5 ISPs**, not just WorldLink — any scraper
whose `raw_price` reflects a multi-month total is affected. Needs careful handling
because different ISPs may already report true monthly rates (e.g. need to check
before assuming duration division is universally correct).

**Suggested approach for next session:**
1. Audit each ISP's actual `raw_price` / `raw_name` format — does it embed
   duration ("for 3 Months") the way WorldLink's does? Check Vianet, Subisu,
   DishHome, CG Net individually before changing shared normalizer logic.
2. Add a `raw_duration` field scrapers can populate explicitly (parsed from
   name/duration text), rather than inferring from raw_name in the normalizer.
3. Compute a true `price_monthly = raw_total_price / duration_months` when a
   plan has a multi-month period text, and correctly populate `price_quarterly`
   / `price_annual` from the original totals.
4. Re-verify all 5 ISPs' data after the change — this touches the shared
   normalizer, so a scraper that was already correct could break if handled
   naively.
5. Re-check `/compare` and `/positioning` dashboards after fixing — WorldLink's
   "cheapest" plan at each speed tier will likely change (12-month plans will
   now correctly win over 1-month plans).

---

## Remaining from earlier punch list (not started)

### 4. Consolidate seed data into a single Python-based seeder
Currently mixing raw SQL seed files (multiple inconsistent versions seen across
this project) with the working `app/db/seed.py` (ISPs + rules only, correctly
idempotent). Plan data itself now comes from real scrapes, which is good — but
worth a single clear story for what seeds what, especially so a mentor/PM
reviewing the repo isn't confused by stale SQL files.

### 5. Basic pytest coverage
Highest-value targets, in order:
- `ChangeDetector` (`app/detection/change_detector.py`) — feed two plan
  snapshots, assert correct `ChangeEvent`s are emitted (price change, new plan,
  discontinued, bundle added/removed, FUP change)
- `RulesEngine` (`app/intelligence/rules_engine.py`) — assert a given
  `ChangeEvent` matches/doesn't match the right `IntelRule`s
- `AlertDispatcher` (`app/alerts/alert_dispatcher.py`) — assert email fires only
  for critical/high severity, Slack fires for all (mock the HTTP/SMTP calls,
  don't hit real endpoints in tests)
- Once fix #3 above is done, add normalizer tests specifically covering
  multi-month price division

### 6. README pass
Architecture overview (scrape → normalize → detect → rules → dispatch pipeline),
setup instructions, dashboard screenshot. This is what a mentor/PM reads first.

### 7. (Minor, optional) Toast severity filtering
Dashboard toast popups currently fire for every severity; email only fires for
critical/high. Decide if that's intentional (toast = lower-friction channel) or
should be made consistent.

---

## Environment notes (useful context for next session)

- **Bind mounts are now correctly configured** in `docker-compose.yml` for
  `app`, `worker`, `beat` (`./app:/app/app`) — Python code edits take effect on
  `docker compose restart <service>`, no rebuild needed. This was a major
  source of confusion earlier in the project (edits appeared to "not save" when
  actually the running container was reading a stale image).
- Removed obsolete `version: "3.9"` from `docker-compose.yml`.
- Windows `cmd`/PowerShell doesn't support `cat`, multi-line piped commands, or
  Unix redirects the same way Bash does — use `docker compose exec <service>
  <command>` directly rather than piping through `cat`/`grep` on the Windows
  host; pipe *inside* the container instead
  (`docker compose exec app bash -c "cmd1 | cmd2"`).
- Email alerting fully verified working (Gmail SMTP via App Password — regular
  Gmail passwords are rejected by Google for SMTP).
- Slack webhook was rotated after an earlier accidental commit exposure —
  confirm the current one in `.env` is the rotated version, not the original
  leaked one, if debugging Slack issues.