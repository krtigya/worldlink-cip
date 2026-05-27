"""
app/ingestion/scrapers/dishhome_scraper.py
Playwright scraper for DishHome — React SPA.

"You need to enable JavaScript to run this app."
Intercepts their internal API calls for internet plan data.
"""
from playwright.async_api import Page, Response
from app.ingestion.scrapers.base_scraper import BaseScraper
from app.logger import get_logger

logger = get_logger(__name__)

PLAN_URLS = [
    "https://dishhome.com.np/internet/residential",
    "https://dishhome.com.np/internet",
]

# Known individual plan page IDs (fallback)
FALLBACK_PLAN_PAGES = [
    ("DishHome 100 Mbps", "https://dishhome.com.np/internet/6326bc516853716210f000ec"),
    ("DishHome 200 Mbps", "https://dishhome.com.np/internet/6326bce86853716210f0010e"),
    ("DishHome 300 Mbps", "https://dishhome.com.np/internet/6326bd566853716210f00130"),
]


class DishhomeScraper(BaseScraper):

    async def extract_plans(self, page: Page) -> list[dict]:
        config      = self.isp.scraper_config
        source_url  = config.get("plan_list_url", PLAN_URLS[0])
        intercepted = []
        seen_keys   = set()

        async def handle_response(response: Response):
            url = response.url
            # DishHome React app calls their backend API
            if any(kw in url for kw in [
                "/api/internet", "/api/package", "/api/plan",
                "/internet/list", "/packages", "/plans",
                "dishhome.com.np/api",
            ]):
                try:
                    data  = await response.json()
                    items = (
                        data.get("data")
                        or data.get("packages")
                        or data.get("plans")
                        or data.get("internetPlans")
                        or data.get("result")
                        or (data if isinstance(data, list) else [])
                    )
                    if not isinstance(items, list):
                        return
                    for item in items:
                        name  = str(item.get("name") or item.get("title") or item.get("planName", ""))
                        price = str(item.get("price") or item.get("monthly_price") or item.get("amount") or item.get("monthlyCharge", ""))
                        speed = str(item.get("speed") or item.get("bandwidth") or item.get("downloadSpeed") or item.get("download_speed", ""))
                        key   = f"{name}_{price}_{speed}"
                        if key in seen_keys or not name:
                            continue
                        seen_keys.add(key)
                        intercepted.append({
                            "isp_id":          self.isp.id,
                            "raw_name":        name,
                            "raw_price":       price,
                            "raw_speed":       speed,
                            "raw_bundles":     self._extract_features(item),
                            "raw_description": str(item.get("description", "")),
                            "source_url":      source_url,
                        })
                except Exception:
                    pass

        page.on("response", handle_response)

        # Try listing pages first
        for url in PLAN_URLS:
            try:
                await page.goto(url, wait_until="networkidle", timeout=60_000)
                await page.wait_for_timeout(3_000)
                if intercepted:
                    logger.info("dishhome_api_intercept_success", count=len(intercepted))
                    return intercepted
            except Exception as e:
                logger.warning("dishhome_page_load_failed", url=url, error=str(e))

        # Fallback: visit individual known plan pages
        logger.warning("dishhome_api_intercept_failed_trying_individual_pages", isp=self.isp.slug)
        fallback = config.get("fallback_urls", FALLBACK_PLAN_PAGES)
        for plan_name, url in fallback:
            try:
                await page.goto(url, wait_until="networkidle", timeout=60_000)
                await page.wait_for_timeout(2_000)
                if intercepted:
                    break
            except Exception as e:
                logger.warning("dishhome_individual_page_failed", plan=plan_name, error=str(e))

        if intercepted:
            logger.info("dishhome_api_intercept_success_fallback", count=len(intercepted))
            return intercepted

        logger.warning("dishhome_no_plans_found")
        return []

    def _extract_features(self, item: dict) -> list[str]:
        features = (
            item.get("features") or item.get("addons")
            or item.get("includes") or item.get("benefits") or []
        )
        if isinstance(features, list):
            return [
                f if isinstance(f, str) else str(f.get("name") or f.get("title", ""))
                for f in features
            ]
        return []
