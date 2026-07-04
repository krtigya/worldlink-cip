"""
Playwright scraper for DishHome — React SPA.
Intercepts dmnwebapi.dishhome.com.np internal API for plan data.
"""
from playwright.async_api import Page, Response
from app.ingestion.scrapers.base_scraper import BaseScraper
from app.logger import get_logger

logger = get_logger(__name__)

PLAN_URLS = [
    "https://dishhome.com.np/internet/plans",
    "https://dishhome.com.np/internet/residential",
]

API_KEYWORD = "dmnwebapi.dishhome.com.np/v1/internet/get-internet-packages"


class DishhomeScraper(BaseScraper):

    async def extract_plans(self, page: Page) -> list[dict]:
        config      = self.isp.scraper_config
        source_url  = config.get("plan_list_url", PLAN_URLS[0])
        intercepted = []
        seen_keys   = set()

        async def handle_response(response: Response):
            url = response.url
            if API_KEYWORD not in url:
                return
            try:
                data     = await response.json()
                packages = data.get("data", [])
                if not isinstance(packages, list):
                    return

                for pkg in packages:
                    title      = pkg.get("title", "")
                    speed      = pkg.get("speed", "")
                    combo_type = pkg.get("combo_type", "Internet")
                    description = pkg.get("description", "")
                    prices     = pkg.get("prices", [])

                    for price_entry in prices:
                        duration = price_entry.get("type", "")
                        internet_price = price_entry.get("internet_price", 0)
                        installation   = price_entry.get("installation_charge", 0)
                        drop_wire      = price_entry.get("drop_wire", 0)
                        router_charge  = price_entry.get("router", 0)
                        itv_stb        = price_entry.get("itv_stb_charge", 0)
                        no_of_itv      = price_entry.get("no_of_itv", 0)

                        total_price = (
                            internet_price + installation + drop_wire
                            + router_charge + itv_stb
                        )

                        key = f"{title}_{duration}"
                        if key in seen_keys:
                            continue
                        seen_keys.add(key)

                        bundles = []
                        if no_of_itv:
                            bundles.append(f"{no_of_itv} TV(s) included")
                        if router_charge == 0:
                            bundles.append("Free router")
                        if "iTV" in combo_type:
                            bundles.append("iTV IPTV")
                        if "DTH" in combo_type:
                            bundles.append("DTH satellite TV")

                        intercepted.append({
                            "isp_id":          self.isp.id,
                            "raw_name":        f"{title} {duration}",
                            "raw_price":       f"Rs. {total_price:,}",
                            "raw_speed":       speed,
                            "raw_bundles":     bundles,
                            "raw_description": description,
                            "source_url":      source_url,
                        })
            except Exception as e:
                logger.warning("dishhome_parse_error", error=str(e))

        page.on("response", handle_response)

        for url in PLAN_URLS:
            try:
                await page.goto(url, wait_until="networkidle", timeout=60_000)
                await page.wait_for_timeout(3_000)
                if intercepted:
                    logger.info("dishhome_api_intercept_success", count=len(intercepted))
                    return intercepted
            except Exception as e:
                logger.warning("dishhome_page_load_failed", url=url, error=str(e))

        if intercepted:
            logger.info("dishhome_api_intercept_success", count=len(intercepted))
            return intercepted

        logger.warning("dishhome_no_plans_found")
        return []