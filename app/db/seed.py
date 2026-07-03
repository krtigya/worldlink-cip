"""here i write the code to seed the initial ISP records and intelligence rules into the database.
Seed initial ISP records and intelligence rules."""

from sqlalchemy.orm import Session
from app.models import Isp, IntelRule
from app.logger import get_logger

logger = get_logger(__name__)

ISP_SEEDS = [
    {
        "slug": "worldlink", "name": "WorldLink Communications",
        "website_url": "https://worldlink.com.np", "is_competitor": False,
        "scraper_config": {
            "plan_list_url": "https://worldlink.com.np/packages",
            "selectors": {
                "plan_container": ".package-card", "name": ".package-name",
                "price": ".package-price", "speed": ".package-speed",
                "bundles": ".package-features li"
            }
        }
    },
    {
        "slug": "vianet", "name": "Vianet Communications",
        "website_url": "https://vianet.com.np", "is_competitor": True,
        "scraper_config": {
            "plan_list_url": "https://vianet.com.np/internet-packages",
            "selectors": {
                "plan_container": ".plan-card", "name": "h3.plan-name",
                "price": ".price-value", "speed": ".speed-label",
                "bundles": ".features li"
            }
        }
    },
    {
        "slug": "subisu", "name": "Subisu Cablenet",
        "website_url": "https://subisu.net.np", "is_competitor": True,
        "scraper_config": {
            "plan_list_url": "https://subisu.net.np/packages",
            "selectors": {
                "plan_container": ".package-box", "name": ".pack-title",
                "price": ".pack-rate", "speed": ".pack-speed",
                "bundles": ".pack-features li"
            }
        }
    },
    {
        "slug": "dishhome", "name": "DishHome Fibernet",
        "website_url": "https://dishhome.com.np", "is_competitor": True,
        "scraper_config": {
            "plan_list_url": "https://dishhome.com.np/fibernet",
            "selectors": {
                "plan_container": ".plan-wrapper", "name": ".plan-title",
                "price": ".monthly-price", "speed": ".speed-tag",
                "bundles": ".included-features li"
            }
        }
    },
    {
        "slug": "cgnet", "name": "CG Net",
        "website_url": "https://cgnet.com.np", "is_competitor": True,
        "scraper_config": {
            "plan_list_url": "https://cgnet.com.np/packages",
            "selectors": {
                "plan_container": ".pkg-card", "name": ".pkg-name",
                "price": ".pkg-price", "speed": ".pkg-speed",
                "bundles": ".pkg-benefits li"
            }
        }
    },
]

RULE_SEEDS = [
    {
        "rule_key": "price_undercut_20pct",
        "name": "Competitor Price Undercut >20%",
        "description": "Competitor plan is >20% cheaper than WorldLink at same speed tier",
        "condition": {"type": "price_diff", "operator": "lt", "threshold": -20, "field": "price_diff_pct"},
        "severity": "critical", "channels": ["slack", "email"],
    },
    {
        "rule_key": "new_bundle_detected",
        "name": "New OTT/IPTV Bundle Detected",
        "condition": {"type": "change_type", "value": "bundle_added"},
        "severity": "high", "channels": ["slack"],
    },
    {
        "rule_key": "new_plan_launched",
        "name": "New Competitor Plan Launched",
        "condition": {"type": "change_type", "value": "plan_added"},
        "severity": "high", "channels": ["slack"],
    },
    {
        "rule_key": "plan_discontinued",
        "name": "Competitor Plan Discontinued",
        "condition": {"type": "change_type", "value": "plan_removed"},
        "severity": "medium", "channels": ["slack"],
    },
    {
        "rule_key": "free_speed_upgrade",
        "name": "Competitor Free Speed Upgrade",
        "condition": {
            "type": "compound",
            "conditions": [
                {"type": "change_type", "value": "speed_change"},
                {"type": "price_diff", "operator": "lte", "threshold": 0}
            ]
        },
        "severity": "critical", "channels": ["slack", "email"],
    },
    {
        "rule_key": "new_campaign",
        "name": "New Promotional Campaign",
        "condition": {"type": "change_type", "value": "campaign_started"},
        "severity": "medium", "channels": ["slack"],
    },
]


def seed_database(session: Session) -> None:
    """Idempotent seed — safe to run multiple times."""
    for data in ISP_SEEDS:
        existing = session.query(Isp).filter_by(slug=data["slug"]).first()
        if not existing:
            session.add(Isp(**data))
            logger.info("seeded_isp", slug=data["slug"])

    for data in RULE_SEEDS:
        existing = session.query(IntelRule).filter_by(rule_key=data["rule_key"]).first()
        if not existing:
            session.add(IntelRule(**data))
            logger.info("seeded_rule", rule_key=data["rule_key"])

    session.commit()
    logger.info("seed_complete")
