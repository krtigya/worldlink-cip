"""
app/ingestion/scrapers/dishhome_scraper.py
Playwright scraper for DishHome — React SPA that requires JS.
Intercepts their internal REST API calls for plan data.
Falls back to navigating individual plan pages if API not found.
"""
from playwright.async_api import Page, Response
from app.ingestion.scrapers.base_scraper import BaseScraper
from app.logger import get_logger

logger = get_logger(__name__)

PLAN_URL      = "https://dishhome.com.np/internet/residential"
FALLBACK_URLS = [
    # Known individual plan pages
    ("100 Mbps", "https://dishhome.com.np/internet/6326bc516853716210f000ec"),
    ("200 Mbps", "https://dishhome.com.np/internet/6326bce86853716210f0010e"),
    ("300 Mbps", "https://dishhome.com.np/internet/6326bd566853716210f00130"),
]


class DishhomeScraper(BaseScraper):

    async def extract_plans(self, page: Page) -> list[dict]:
        config     = self.isp.scraper_config
        source_url = config.get("plan_list_url", PLAN_URL)
        intercepted = []

        # Strategy 1: Intercept REST API calls
        async def handle_response(response: Response):
            url = response.url
            if any(kw in url for kw in ["/api/internet", "/api/package", "/api/plan", "/packages", "/plans"]):
                try:
                    data  = await response.json()
                    items = (
                        data.get("data")
                        or data.get("packages")
                        or data.get("plans")
                        or data.get("internetPlans")
                        or (data if isinstance(data, list) else [])
                    )
                    for item in items:
                        intercepted.append({
                            "isp_id":          self.isp.id,
                            "raw_name":        str(item.get("name") or item.get("title") or item.get("planName", "")),
                            "raw_price":       str(item.get("price") or item.get("monthly_price") or item.get("amount") or item.get("monthlyCharge", "")),
                            "raw_speed":       str(item.get("speed") or item.get("bandwidth") or item.get("downloadSpeed", "")),
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
            logger.info("dishhome_api_intercept_success", count=len(intercepted))
            return intercepted

        # Strategy 2: DOM scraping on listing page
        logger.warning("dishhome_api_intercept_failed_trying_dom", isp=self.isp.slug)

        selector_sets = [
            {"container": ".plan-card",       "name": "h2,h3,.plan-name",     "price": ".price,.plan-price",   "speed": ".speed,.bandwidth"},
            {"container": ".internet-plan",   "name": "h2,h3",                "price": ".price",               "speed": ".speed"},
            {"container": "[class*='plan']",  "name": "h2,h3",                "price": "[class*='price']",     "speed": "[class*='speed']"},
            {"container": ".package",         "name": "h2,h3,.package-title", "price": ".price,.package-price","speed": ".speed"},
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
                        raw_bundles: Array.from(el.querySelectorAll("li, .feature, .addon, .benefit"))
                                        .map(b => b.textContent?.trim()).filter(Boolean),
                        source_url,
                    })).filter(p => p.raw_name && p.raw_price);
                }""",
                [sel, self.isp.id, source_url]
            )
            if plans:
                logger.info("dishhome_dom_scrape_success", selector=sel["container"], count=len(plans))
                return plans

        # Strategy 3: Scrape individual known plan pages
        logger.warning("dishhome_falling_back_to_individual_pages", isp=self.isp.slug)
        return await self._scrape_individual_pages(page)

    async def _scrape_individual_pages(self, page: Page) -> list[dict]:
        """Navigate each known plan page and extract price/speed from the DOM."""
        plans = []
        config     = self.isp.scraper_config
        fallback   = config.get("fallback_urls", FALLBACK_URLS)

        for plan_name, url in fallback:
            try:
                await page.goto(url, wait_until="networkidle", timeout=60_000)
                await page.wait_for_timeout(2_000)

                # Extract all visible text containing Rs and Mbps
                data = await page.evaluate("""() => {
                    const getText = sel => document.querySelector(sel)?.textContent?.trim() ?? "";
                    const getAll  = sel => Array.from(document.querySelectorAll(sel))
                                            .map(e => e.textContent?.trim()).filter(Boolean);

                    // Try to find price — look for elements containing "Rs"
                    const priceEl = Array.from(document.querySelectorAll("h1,h2,h3,span,p,div"))
                        .find(el => /Rs\.?\s*[\d,]+/.test(el.textContent) && el.children.length === 0);

                    // Try to find speed — look for elements containing "Mbps"
                    const speedEl = Array.from(document.querySelectorAll("h1,h2,h3,span,p,div"))
                        .find(el => /\d+\s*Mbps/i.test(el.textContent) && el.children.length === 0);

                    return {
                        price:    priceEl?.textContent?.trim() ?? "",
                        speed:    speedEl?.textContent?.trim() ?? "",
                        features: getAll("li, .feature, .benefit, .addon"),
                        title:    getText("h1,h2"),
                    };
                }""")

                if data.get("price") or data.get("speed"):
                    plans.append({
                        "isp_id":          self.isp.id,
                        "raw_name":        data.get("title") or plan_name,
                        "raw_price":       data.get("price", ""),
                        "raw_speed":       data.get("speed", plan_name),
                        "raw_bundles":     data.get("features", []),
                        "raw_description": f"DishHome {plan_name} internet plan",
                        "source_url":      url,
                    })
                    logger.info("dishhome_individual_page_scraped", plan=plan_name)

            except Exception as e:
                logger.warning("dishhome_individual_page_failed", plan=plan_name, error=str(e))
                continue

        if not plans:
            logger.warning("dishhome_no_plans_found")

        return plans

    def _extract_features(self, item: dict) -> list[str]:
        features = item.get("features") or item.get("addons") or item.get("includes") or item.get("benefits") or []
        if isinstance(features, list):
            return [
                f if isinstance(f, str) else str(f.get("name") or f.get("title", ""))
                for f in features
            ]
        return []
