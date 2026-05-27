"""
Playwright scraper for Subisu — Vue.js SPA.

The page uses {{ }} Vue templates — data is loaded via API calls.
We intercept the API responses to get plan data.
Known API pattern: GET /api/package/{type}/{duration}/{router}
                   GET /api/packages or /residential/package-data
"""
from playwright.async_api import Page, Response
from app.ingestion.scrapers.base_scraper import BaseScraper
from app.logger import get_logger

logger = get_logger(__name__)

# Known package URLs to visit to trigger API calls
PACKAGE_URLS = [
    "https://subisu.net.np/residential/package/ftth/12-month/5-ghz",
    "https://subisu.net.np/residential/package/ftth/3-month/5-ghz",
    "https://subisu.net.np/residential/package/ftth/1-month/5-ghz",
    "https://subisu.net.np/residential/package/renew/12-month",
    "https://subisu.net.np/residential/package/renew/3-month",
    "https://subisu.net.np/residential/package/renew/1-month",
]


class SubisuScraper(BaseScraper):

    async def extract_plans(self, page: Page) -> list[dict]:
        config     = self.isp.scraper_config
        source_url = config.get("plan_list_url", PACKAGE_URLS[0])
        intercepted = []
        seen_keys   = set()

        async def handle_response(response: Response):
            url = response.url
            # Subisu API pattern: /api/package or /package-data or /residential/package
            if any(kw in url for kw in ["/api/package", "/package-data", "/api/residential", "/api/plan"]):
                try:
                    data = await response.json()
                    # Subisu returns nested structure: data.packages or data.plans or flat list
                    items = (
                        data.get("packages")
                        or data.get("plans")
                        or data.get("data")
                        or (data if isinstance(data, list) else [])
                    )
                    for item in items:
                        name  = str(item.get("title") or item.get("name") or item.get("package_title", ""))
                        price = str(item.get("value") or item.get("price") or item.get("amount") or item.get("monthly_fee", ""))
                        speed = str(item.get("speed") or item.get("bandwidth") or item.get("download_speed", ""))
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

        # Visit each package URL to trigger the API calls
        for pkg_url in PACKAGE_URLS:
            try:
                await page.goto(pkg_url, wait_until="networkidle", timeout=60_000)
                await page.wait_for_timeout(2_000)
                if intercepted:
                    break  # got data, no need to visit more pages
            except Exception as e:
                logger.warning("subisu_page_load_failed", url=pkg_url, error=str(e))
                continue

        if intercepted:
            logger.info("subisu_api_intercept_success", count=len(intercepted))
            return intercepted

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