"""
Simple HTTP scraper for WorldLink — uses httpx + BeautifulSoup
instead of Playwright since WorldLink has standard HTML.
"""
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from app.logger import get_logger

logger = get_logger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class WorldLinkScraper:
    def __init__(self, isp):
        self.isp = isp

    async def scrape(self) -> list[dict]:
        config = self.isp.scraper_config
        url = config["plan_list_url"]
        selectors = config["selectors"]

        logger.info("worldlink_http_scrape_start", url=url)

        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text
        except Exception as e:
            logger.error("worldlink_fetch_failed", error=str(e))
            return []

        soup = BeautifulSoup(html, "lxml")
        containers = containers = soup.find_all("div", class_=lambda c: c and "plans-card" in c and "item" in c)

        if not containers:
            logger.warning("worldlink_no_plans_found", selector=selectors["plan_container"])
            return []

        plans = []
        for el in containers:
            name_el  = el.select_one(selectors.get("name", ""))
            price_el = el.select_one(selectors.get("price", ""))
            speed_el = el.select_one(selectors.get("speed", ""))

            raw_name  = name_el.get_text(strip=True)  if name_el  else ""
            raw_price = price_el.get_text(strip=True) if price_el else ""
            raw_speed = speed_el.get_text(strip=True) if speed_el else ""

            bundle_sel = selectors.get("bundles")
            raw_bundles = (
                [b.get_text(strip=True) for b in el.select(bundle_sel) if b.get_text(strip=True)]
                if bundle_sel else []
            )

            desc_el = el.select_one(".description, p")
            raw_description = desc_el.get_text(strip=True) if desc_el else ""

            if raw_name and raw_price:
                plans.append({
                    "isp_id":          self.isp.id,
                    "raw_name":        raw_name,
                    "raw_price":       raw_price,
                    "raw_speed":       raw_speed,
                    "raw_bundles":     raw_bundles,
                    "raw_description": raw_description,
                    "source_url":      url,
                    "scraped_at":      datetime.utcnow().isoformat(),
                })

        logger.info("worldlink_scrape_complete", plans=len(plans))
        return plans