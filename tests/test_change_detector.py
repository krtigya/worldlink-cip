"""
Unit tests for the change detection engine.
"""
import uuid
import pytest
from unittest.mock import MagicMock, patch
from app.detection.change_detector import (
    ChangeDetector, ChangeEvent, _plan_key, _price_severity
)
from app.models.change_log import ChangeType, SeverityLevel
from app.normalization.normalizer import NormalizedPlan


def make_normalized_plan(**kwargs) -> NormalizedPlan:
    defaults = dict(
        isp_id=2, raw_name="Vianet Gold 300", normalized_name="Vianet Gold 300",
        plan_type="residential", download_mbps=300, upload_mbps=None,
        speed_raw="300 Mbps", price_monthly=1499.0, price_raw="Rs 1499",
        vat_included=True, fup_gb=None, is_unlimited=True,
        contract_months=1, bundles=[], bundle_flags=[],
        description=None, scrape_url="https://vianet.com.np", raw_data={},
    )
    defaults.update(kwargs)
    return NormalizedPlan(**defaults)


def make_db_plan(**kwargs):
    plan = MagicMock()
    plan.id            = uuid.uuid4()
    plan.isp_id        = 2
    plan.normalized_name = "Vianet Gold 300"
    plan.download_mbps = 300
    plan.price_monthly = 1999.0
    plan.bundle_flags  = []
    plan.fup_gb        = None
    plan.is_unlimited  = True
    plan.status        = "active"
    for k, v in kwargs.items():
        setattr(plan, k, v)
    return plan


class TestPriceSeverity:

    def test_critical_price_drop(self):
        assert _price_severity(-35.0) == SeverityLevel.critical

    def test_high_price_drop(self):
        assert _price_severity(-22.0) == SeverityLevel.high

    def test_medium_price_drop(self):
        assert _price_severity(-12.0) == SeverityLevel.medium

    def test_low_price_drop(self):
        assert _price_severity(-5.0) == SeverityLevel.low


class TestPlanKey:

    def test_key_format(self):
        key = _plan_key(1, "WorldLink 100", 100)
        assert key == "1:worldlink 100:100"

    def test_key_case_insensitive(self):
        assert _plan_key(1, "PLAN", 100) == _plan_key(1, "plan", 100)


class TestChangeDetector:

    def _make_session(self, existing_plans):
        session = MagicMock()
        session.query.return_value.filter.return_value.all.return_value = existing_plans
        session.query.return_value.filter.return_value.filter.return_value.all.return_value = existing_plans
        return session

    def test_detects_new_plan(self):
        detector = ChangeDetector()
        session  = self._make_session([])  # no existing plans
        scraped  = [make_normalized_plan()]

        with patch.object(detector, "_insert_plan", return_value=MagicMock(id=uuid.uuid4())):
            session.flush = MagicMock()
            events = detector.detect_and_persist(scraped, "run-1", session)

        assert any(e.change_type == ChangeType.plan_added for e in events)

    def test_detects_price_decrease(self):
        detector = ChangeDetector()
        existing = make_db_plan(price_monthly=1999.0)
        session  = self._make_session([existing])
        scraped  = [make_normalized_plan(price_monthly=1499.0)]

        with patch.object(session, "add"), patch.object(session, "commit"):
            events = detector.detect_and_persist(scraped, "run-1", session)

        price_events = [e for e in events if e.change_type == ChangeType.price_decrease]
        assert len(price_events) == 1
        assert price_events[0].diff_pct < 0

    def test_detects_bundle_added(self):
        detector = ChangeDetector()
        existing = make_db_plan(bundle_flags=[])
        session  = self._make_session([existing])
        scraped  = [make_normalized_plan(bundle_flags=["ott", "router"])]

        with patch.object(session, "add"), patch.object(session, "commit"):
            events = detector.detect_and_persist(scraped, "run-1", session)

        bundle_events = [e for e in events if e.change_type == ChangeType.bundle_added]
        assert len(bundle_events) == 1

    def test_detects_plan_removed(self):
        detector = ChangeDetector()
        existing = [make_db_plan(normalized_name="Old Plan 100", download_mbps=100)]
        session  = self._make_session(existing)
        # Scraped a completely different plan — Old Plan 100 disappears
        scraped  = [make_normalized_plan(normalized_name="New Plan 200", download_mbps=200)]

        with patch.object(detector, "_insert_plan", return_value=MagicMock(id=uuid.uuid4())):
            session.flush = MagicMock()
            with patch.object(session, "add"), patch.object(session, "commit"):
                events = detector.detect_and_persist(scraped, "run-1", session)

        removed = [e for e in events if e.change_type == ChangeType.plan_removed]
        assert len(removed) == 1

    def test_no_changes_when_identical(self):
        detector = ChangeDetector()
        existing = make_db_plan()
        session  = self._make_session([existing])
        # Same plan, same price, same bundles
        scraped  = [make_normalized_plan(price_monthly=1999.0, bundle_flags=[])]

        with patch.object(session, "add"), patch.object(session, "commit"):
            events = detector.detect_and_persist(scraped, "run-1", session)

        significant = [e for e in events if e.change_type not in
                       (ChangeType.plan_added, ChangeType.plan_removed)]
        assert len(significant) == 0
