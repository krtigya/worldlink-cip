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
        config    = self.isp.scraper_config
        url       = config["plan_list_url"]
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
        containers = soup.find_all("div", class_=lambda c: c and "plans-card" in c and "item" in c)

        if not containers:
            logger.warning("worldlink_no_plans_found", selector=selectors.get("plan_container"))
            return []

        plans = []
        for el in containers:
            speed_el    = el.select_one(".plans__speed")
            amount_el   = el.select_one(".plans__title .amount")
            duration_el = el.select_one(".plans__duration")
            features_el = el.select_one(".plans__features")

            raw_speed    = speed_el.get_text(strip=True) if speed_el else ""
            raw_price    = f"Rs. {amount_el.get_text(strip=True)}" if amount_el else ""
            raw_duration = duration_el.get_text(strip=True) if duration_el else ""
            raw_name     = f"WorldLink {raw_speed} {raw_duration}".strip()

            raw_bundles = []
            if features_el:
                raw_bundles = [
                    t for t in features_el.stripped_strings
                    if t and len(t) > 1
                ]

            if raw_name and raw_price:
                plans.append({
                    "isp_id":          self.isp.id,
                    "raw_name":        raw_name,
                    "raw_price":       raw_price,
                    "raw_speed":       raw_speed,
                    "raw_bundles":     raw_bundles,
                    "raw_description": f"WorldLink {raw_speed} plan, {raw_duration}. No FUP, unlimited data.".strip(),
                    "source_url":      url,
                    "scraped_at":      datetime.utcnow().isoformat(),
                })

        logger.info("worldlink_scrape_complete", plans=len(plans))
        return plans