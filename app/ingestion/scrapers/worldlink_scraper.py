
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
BASE_URL = "https://worldlink.com.np/internet-plans/residential-broadband/"
MAX_PAGES_SAFETY_CAP = 10  # hard ceiling so a scraper bug can't loop forever


class WorldLinkScraper:
    def __init__(self, isp):
        self.isp = isp

    async def scrape(self) -> list[dict]:
        config    = self.isp.scraper_config
        selectors = config.get("selectors", {})

        all_plans: list[dict] = []
        seen_raw_names: set[str] = set()

        async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
            page_num = 1
            total_pages = None

            while page_num <= MAX_PAGES_SAFETY_CAP:
                url = f"{BASE_URL}page/{page_num}/"
                logger.info("worldlink_http_scrape_start", url=url, page=page_num)

                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    html = response.text
                except Exception as e:
                    logger.error("worldlink_fetch_failed", url=url, error=str(e))
                    break

                soup = BeautifulSoup(html, "lxml")

                if total_pages is None:
                    total_pages = self._detect_total_pages(soup)
                    logger.info("worldlink_pagination_detected", total_pages=total_pages)

                containers = soup.find_all("div", class_=lambda c: c and "plans-card" in c and "item" in c)
                if not containers:
                    logger.warning("worldlink_no_plans_found", page=page_num,
                                    selector=selectors.get("plan_container"))
                    break

                page_plans = self._parse_containers(containers, url)

                for p in page_plans:
                    
                    if p["raw_name"] not in seen_raw_names:
                        seen_raw_names.add(p["raw_name"])
                        all_plans.append(p)

                logger.info("worldlink_page_scraped", page=page_num, plans_found=len(page_plans))

                if total_pages and page_num >= total_pages:
                    break
                page_num += 1

        logger.info("worldlink_scrape_complete", plans=len(all_plans), pages_scraped=page_num)
        return all_plans

    def _detect_total_pages(self, soup: BeautifulSoup) -> int | None:
        """
        Read the pagination control (numbered page links) to find the
        highest page number, so we don't hardcode a page count that
        breaks the moment WorldLink adds or removes a page.
        """
        page_links = soup.select("a[href*='/page/']")
        page_numbers = []
        for a in page_links:
            text = a.get_text(strip=True)
            if text.isdigit():
                page_numbers.append(int(text))
        return max(page_numbers) if page_numbers else None

    def _parse_containers(self, containers, source_url: str) -> list[dict]:
        plans = []
        for el in containers:
            speed_el    = el.select_one(".plans__speed")
            amount_el   = el.select_one(".plans__title .amount")
            duration_el = el.select_one(".plans__duration")
            features_el = el.select_one(".plans__features")
            badge_el    = el.select_one(".plans__badge, .plan-badge, [class*='badge']")

            raw_speed    = speed_el.get_text(strip=True) if speed_el else ""
            raw_price    = f"Rs. {amount_el.get_text(strip=True)}" if amount_el else ""
            raw_duration = duration_el.get_text(strip=True) if duration_el else ""
            raw_badge    = badge_el.get_text(strip=True) if badge_el else ""

          
            name_parts = [p for p in ["WorldLink", raw_speed, raw_duration, raw_badge] if p]
            raw_name = " ".join(name_parts).strip()

            raw_bundles = []
            if features_el:
                raw_bundles = [
                    t for t in features_el.stripped_strings
                    if t and len(t) > 1
                ]
            if raw_badge:
                raw_bundles.append(raw_badge)

            if raw_name and raw_price:
                plans.append({
                    "isp_id":          self.isp.id,
                    "raw_name":        raw_name,
                    "raw_price":       raw_price,
                    "raw_speed":       raw_speed,
                    "raw_bundles":     raw_bundles,
                    "raw_description": f"WorldLink {raw_speed} plan, {raw_duration}. No FUP, unlimited data.".strip(),
                    "source_url":      source_url,
                    "scraped_at":      datetime.utcnow().isoformat(),
                })
        return plans