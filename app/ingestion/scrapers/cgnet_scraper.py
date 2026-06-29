import re
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

        speed_headings = soup.find_all("h3", string=re.compile(r"\d+\s*Mbps", re.I))

        for h3 in speed_headings:
            speed_text = h3.get_text(strip=True)
            price_text = ""
            price_raw  = ""

            for tag in h3.find_next_siblings():
                t = tag.get_text(strip=True)
                m = re.search(r"Rs\.\s*([\d,]+)\s*/\s*year", t, re.I)
                if m:
                    price_raw  = t
                    price_text = m.group(1).replace(",", "")
                    break
                if tag.name in ("h2", "h3"):
                    break

            features = []
            for tag in h3.find_next_siblings():
                if tag.name in ("ul", "ol"):
                    features = [li.get_text(strip=True) for li in tag.find_all("li")]
                    break
                if tag.name in ("h2", "h3"):
                    break

            if speed_text and price_text:
                plans.append({
                    "isp_id":          self.isp.id,
                    "raw_name":        f"CGNet WiFi6 {speed_text} 12M",
                    "raw_price":       price_raw,
                    "raw_speed":       speed_text,
                    "raw_bundles":     features,
                    "raw_description": f"CGNet Wi-Fi 6 {speed_text} annual plan. No FUP. VAT included.",
                    "source_url":      url,
                    "scraped_at":      datetime.utcnow().isoformat(),
                })

        return plans