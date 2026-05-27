"""
app/ingestion/scrapers/cgnet_scraper.py
HTTP scraper for CGNet — server-rendered HTML, no JS needed.

Page structure (from live site):
  Each plan block contains:
    h2: price  e.g. "Rs 3,345/-"
    h2: speed  e.g. "350 Mbps"
    h2: plan name (Rockstar / Popular / Sprinter)
    p:  "For X months"
    li: feature items
"""
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

PLAN_URL   = "https://cgnet.com.np/residential/internet"
PLAN_NAMES = {"Rockstar", "Popular", "Sprinter"}


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
        all_h2 = soup.find_all("h2")
        plans  = []

        i = 0
        while i < len(all_h2):
            h2_text = all_h2[i].get_text(strip=True)

            # Each plan block starts with price h2: "Rs 3,345/-"
            if re.match(r"^Rs\s[\d,]+/-$", h2_text):
                price_text = h2_text
                speed_text = ""
                plan_name  = ""
                features   = []
                duration   = ""

                # Next h2s: speed then plan name
                for j in range(i + 1, min(i + 6, len(all_h2))):
                    t = all_h2[j].get_text(strip=True)
                    if re.match(r"^\d+\s*Mbps$", t, re.I) and not speed_text:
                        speed_text = t
                    elif t in PLAN_NAMES and not plan_name:
                        plan_name = t
                    if speed_text and plan_name:
                        break

                # Find duration "For X months" in nearby <p> tags before this h2
                for tag in all_h2[i].find_all_previous("p", limit=5):
                    pt = tag.get_text(strip=True)
                    if re.match(r"For \d+\s*months?", pt, re.I):
                        duration = pt
                        break

                # Find features in nearby <li> tags after this h2
                for tag in all_h2[i].find_next_siblings():
                    if tag.name in ("ul", "ol"):
                        features = [li.get_text(strip=True) for li in tag.find_all("li") if li.get_text(strip=True)]
                        break
                    if tag.name == "h2" and tag.get_text(strip=True) in PLAN_NAMES:
                        break

                if speed_text and plan_name and price_text:
                    dur_match  = re.search(r"(\d+)\s*months?", duration, re.I)
                    dur_str    = f"{dur_match.group(1)} Month" if dur_match else ""
                    raw_name   = f"{plan_name} {speed_text} {dur_str}".strip()

                    plans.append({
                        "isp_id":          self.isp.id,
                        "raw_name":        raw_name,
                        "raw_price":       price_text,
                        "raw_speed":       speed_text,
                        "raw_bundles":     features,
                        "raw_description": f"{plan_name} {speed_text} internet plan. {duration}".strip(),
                        "source_url":      url,
                        "scraped_at":      datetime.utcnow().isoformat(),
                    })

            i += 1

        return plans
