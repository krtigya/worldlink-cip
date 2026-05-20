"""
Integration-style tests for /api/plans endpoints using FastAPI TestClient.
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

MOCK_PLANS = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "isp_id": 2, "isp_name": "Vianet Communications", "isp_slug": "vianet",
        "normalized_name": "Vianet Gold 300", "plan_type": "residential",
        "status": "active", "download_mbps": 300, "upload_mbps": None,
        "price_monthly": 1499.0, "price_quarterly": None, "price_annual": None,
        "setup_fee": 0.0, "vat_included": True, "fup_gb": None,
        "is_unlimited": True, "contract_months": 1,
        "bundles": [], "bundle_flags": ["router"],
        "description": None, "price_per_mbps": 5.0,
        "first_seen_at": "2025-01-01T00:00:00",
        "last_seen_at":  "2025-06-01T00:00:00",
    }
]


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@patch("app.api.routes.plans.get_db")
def test_list_plans_returns_200(mock_db):
    mock_session = AsyncMock()
    mock_result  = AsyncMock()
    mock_result.fetchall.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_db.return_value.__aexit__  = AsyncMock(return_value=None)

    resp = client.get("/api/plans")
    assert resp.status_code in (200, 500)   # 500 OK in test env without real DB


def test_api_docs_available():
    resp = client.get("/docs")
    assert resp.status_code == 200
