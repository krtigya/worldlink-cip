"""
Unit tests for the normalization layer.
Run with: pytest tests/test_normalizer.py -v
"""
import pytest
from app.normalization.normalizer import (
    normalize_speed, normalize_price, normalize_bundles,
    detect_fup, detect_plan_type, normalize_plan,
)


class TestNormalizeSpeed:

    def test_mbps(self):
        assert normalize_speed("100 Mbps") == (100, None)

    def test_gbps(self):
        assert normalize_speed("1 Gbps") == (1000, None)

    def test_mbps_no_space(self):
        assert normalize_speed("300Mbps") == (300, None)

    def test_up_down_notation(self):
        assert normalize_speed("300/50 Mbps") == (300, 50)

    def test_upto_format(self):
        assert normalize_speed("Upto 500 Mbps") == (500, None)

    def test_short_g(self):
        assert normalize_speed("1G") == (1000, None)

    def test_short_m(self):
        assert normalize_speed("200M") == (200, None)


class TestNormalizePrice:

    def test_plain_number(self):
        assert normalize_price("1999") == 1999.0

    def test_rs_prefix(self):
        assert normalize_price("Rs. 1,499") == 1499.0

    def test_npr_prefix(self):
        assert normalize_price("NPR 2,099") == 2099.0

    def test_per_month(self):
        assert normalize_price("799/mo") == 799.0

    def test_with_commas(self):
        assert normalize_price("2,500") == 2500.0


class TestNormalizeBundles:

    def test_iptv_detected(self):
        _, flags = normalize_bundles(["Free IPTV included", "HD channels"])
        assert "iptv" in flags

    def test_ott_detected(self):
        _, flags = normalize_bundles(["Netflix subscription", "Unlimited streaming"])
        assert "ott" in flags

    def test_router_detected(self):
        _, flags = normalize_bundles(["Free Wi-Fi Router included"])
        assert "router" in flags

    def test_no_bundles(self):
        bundles, flags = normalize_bundles(["Standard plan"])
        assert flags == []

    def test_multiple_bundles(self):
        _, flags = normalize_bundles(["Free Router", "IPTV", "Netflix"])
        assert "router" in flags
        assert "iptv" in flags
        assert "ott" in flags


class TestDetectFup:

    def test_unlimited(self):
        fup, unlimited = detect_fup(["Unlimited data", "No FUP"])
        assert unlimited is True
        assert fup is None

    def test_fup_gb(self):
        fup, unlimited = detect_fup(["500 GB FUP limit"])
        assert fup == 500
        assert unlimited is False

    def test_no_info(self):
        fup, unlimited = detect_fup(["Fast internet"])
        assert fup is None
        assert unlimited is False


class TestDetectPlanType:

    def test_residential(self):
        assert detect_plan_type("Home Fiber 100M") == "residential"

    def test_business(self):
        assert detect_plan_type("Business Office Pack 200M") == "business"

    def test_enterprise(self):
        assert detect_plan_type("Enterprise Corporate 1Gbps") == "enterprise"

    def test_fiber(self):
        assert detect_plan_type("FTTH Fiber Plus 300M") == "fiber"


class TestNormalizePlan:

    def test_full_normalization(self):
        raw = {
            "isp_id":          1,
            "raw_name":        "Vianet Gold 300",
            "raw_price":       "Rs. 1,499",
            "raw_speed":       "300 Mbps",
            "raw_bundles":     ["Free Router", "Netflix Included"],
            "raw_description": "Best value plan",
            "source_url":      "https://vianet.com.np/packages",
        }
        plan = normalize_plan(raw, "vianet")

        assert plan.download_mbps   == 300
        assert plan.price_monthly   == 1499.0
        assert plan.isp_id          == 1
        assert "router" in plan.bundle_flags
        assert "ott"    in plan.bundle_flags
        assert plan.normalized_name != ""

    def test_invalid_speed_raises(self):
        raw = {
            "isp_id": 1, "raw_name": "Plan X", "raw_price": "999",
            "raw_speed": "N/A", "raw_bundles": [], "source_url": "",
        }
        with pytest.raises(ValueError):
            normalize_plan(raw, "test")
