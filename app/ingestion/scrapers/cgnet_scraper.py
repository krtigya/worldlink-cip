"""
HTTP scraper for CGNet — the site was redesigned (Wi-Fi 6 packages page).
Good news: it's server-rendered — every plan card (all speed/duration/service
combinations) is present in the initial HTML, just toggled `hidden` client-side
by the interactive filter UI. So a plain httpx+BeautifulSoup fetch captures
everything without needing Playwright/JS execution.

Selectors are attribute-based (data-service, data-duration, data-plan-id) rather
than CSS classes, since those are stable identifiers the site's own filter JS
relies on — much less likely to break on a future style-only redesign than
class names would be.
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

PLAN_URL = "https://cgnet.com.np/wifi-six"


class CgnetScraper:
    def __init__(self, isp):
        self.isp = isp

    async def scrape(self) -> list[dict]:
        config = self.isp.scraper_config
        url    = config.get("plan_list_url", PLAN_URL)

        logger.info("cgnet_http_scrape_start", url=url)

        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text
        except Exception as e:
            logger.error("cgnet_fetch_failed", error=str(e))
            return []

        soup  = BeautifulSoup(html, "lxml")
        plans = self._parse_plans(soup, url)

        if not plans:
            logger.warning("cgnet_no_plans_found", url=url)
        else:
            logger.info("cgnet_scrape_complete", plans=len(plans))

        return plans

    def _parse_plans(self, soup: BeautifulSoup, url: str) -> list[dict]:
        plans = []

        # Cards are <article data-wifi-six-plan-card data-service="..." data-duration="...">
        # Every combination is present in the DOM regardless of the `hidden`
        # attribute (that's just the client-side filter's current display state).
        cards = soup.find_all("article", attrs={"data-wifi-six-plan-card": True})

        for card in cards:
            service  = card.get("data-service", "internet")
            duration = card.get("data-duration", "")

            speed_el = card.find("h3")
            price_el = card.find("strong")
            if not speed_el or not price_el:
                continue

            raw_speed = speed_el.get_text(strip=True)
            raw_price = price_el.get_text(strip=True)

            is_iptv = service == "iptv"
            service_label = "Internet + IPTV" if is_iptv else "Internet Only"
            raw_name = f"CGNet {raw_speed} {service_label} {duration} Months"

            # Feature bullet points (router included, latency, etc.)
            raw_bundles = [
                li.get_text(strip=True)
                for li in card.select("ul li")
                if li.get_text(strip=True)
            ]
            if is_iptv:
                raw_bundles.append("IPTV service included")

            highest_speed = bool(card.find(string=lambda t: t and "Highest speed" in t))
            if highest_speed:
                raw_bundles.append("Highest speed tier")

            button = card.find("button", class_="js-open-plan")
            plan_id = button.get("data-plan-id") if button else None

            plans.append({
                "isp_id":          self.isp.id,
                "raw_name":        raw_name,
                "raw_price":       raw_price,
                "raw_speed":       raw_speed,
                "raw_bundles":     raw_bundles,
                "raw_description": (
                    f"CGNet Wi-Fi 6 {raw_speed}, {service_label}, {duration}-month term. "
                    f"No FUP applied. Prices include VAT."
                ),
                "source_url":      url,
                "scraped_at":      datetime.utcnow().isoformat(),
                "raw_data": {"plan_id": plan_id, "service": service, "duration": duration},
            })

        return plans