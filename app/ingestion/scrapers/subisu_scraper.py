"""
app/ingestion/scrapers/subisu_scraper.py
Playwright scraper for Subisu — JavaScript-rendered SPA.
Intercepts API calls first; falls back to DOM scraping.
"""
from playwright.async_api import Page, Response
from app.ingestion.scrapers.base_scraper import BaseScraper
from app.logger import get_logger

logger = get_logger(__name__)

PLAN_URL = "https://subisu.net.np/residential"


class SubisuScraper(BaseScraper):

    async def extract_plans(self, page: Page) -> list[dict]:
        config     = self.isp.scraper_config
        source_url = config.get("plan_list_url", PLAN_URL)
        intercepted = []

        # Strategy 1: Intercept XHR/fetch API responses
        async def handle_response(response: Response):
            url = response.url
            if any(kw in url for kw in ["/api/package", "/api/plan", "/packages", "/plans"]):
                try:
                    data  = await response.json()
                    items = (
                        data.get("data")
                        or data.get("packages")
                        or data.get("plans")
                        or (data if isinstance(data, list) else [])
                    )
                    for item in items:
                        intercepted.append({
                            "isp_id":          self.isp.id,
                            "raw_name":        str(item.get("name") or item.get("title", "")),
                            "raw_price":       str(item.get("price") or item.get("monthly_price") or item.get("amount", "")),
                            "raw_speed":       str(item.get("speed") or item.get("bandwidth") or item.get("download_speed", "")),
                            "raw_bundles":     self._extract_features(item),
                            "raw_description": str(item.get("description", "")),
                            "source_url":      source_url,
                        })
                except Exception:
                    pass

        page.on("response", handle_response)
        await page.goto(source_url, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(3_000)

        if intercepted:
            logger.info("subisu_api_intercept_success", count=len(intercepted))
            return intercepted

        # Strategy 2: DOM fallback — try common selectors used by Nepali ISP sites
        logger.warning("subisu_api_intercept_failed_trying_dom", isp=self.isp.slug)

        selector_sets = [
            {"container": ".package-box",   "name": "h3,h2,.package-name", "price": ".price,.package-price", "speed": ".speed,.bandwidth"},
            {"container": ".plan-card",      "name": "h3,h2",               "price": ".price",                "speed": ".speed"},
            {"container": ".pricing-card",   "name": "h3,h2,.plan-name",    "price": ".price,.amount",        "speed": ".speed,.mbps"},
            {"container": ".internet-plan",  "name": "h3,h2",               "price": ".price",                "speed": ".speed"},
            {"container": "[class*='plan']", "name": "h3,h2",               "price": "[class*='price']",      "speed": "[class*='speed']"},
        ]

        for sel in selector_sets:
            try:
                await page.wait_for_selector(sel["container"], timeout=5_000)
            except Exception:
                continue

            plans = await page.evaluate(
                """([sel, isp_id, source_url]) => {
                    return Array.from(document.querySelectorAll(sel.container)).map(el => ({
                        isp_id,
                        raw_name:    el.querySelector(sel.name)?.textContent?.trim()  ?? "",
                        raw_price:   el.querySelector(sel.price)?.textContent?.trim() ?? "",
                        raw_speed:   el.querySelector(sel.speed)?.textContent?.trim() ?? "",
                        raw_bundles: Array.from(el.querySelectorAll("li, .feature, .addon"))
                                        .map(b => b.textContent?.trim()).filter(Boolean),
                        source_url,
                    })).filter(p => p.raw_name && p.raw_price);
                }""",
                [sel, self.isp.id, source_url]
            )
            if plans:
                logger.info("subisu_dom_scrape_success", selector=sel["container"], count=len(plans))
                return plans

        logger.warning("subisu_no_plans_found", url=source_url)
        return []

    def _extract_features(self, item: dict) -> list[str]:
        features = item.get("features") or item.get("addons") or item.get("includes") or []
        if isinstance(features, list):
            return [
                f if isinstance(f, str) else str(f.get("name") or f.get("title", ""))
                for f in features
            ]
        return []
