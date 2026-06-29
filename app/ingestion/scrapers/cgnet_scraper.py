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

HEADERS = { ... }

PLAN_URL   = "https://cgnet.com.np/wifi-six"  

PLAN_NAMES = {"250 Mbps", "350 Mbps", "400 Mbps"}  # speeds are the h3 headings

def _parse_plans(self, soup: BeautifulSoup, url: str) -> list[dict]:
    plans = []

    # Plans are under the #packages section
    # Each plan card has: h3 (speed), p (price like "Rs. 13,499 / year"), ul (features)
    packages_section = soup.find(id="packages") or soup.find("section", string=re.compile("packages", re.I))

    # Fallback: find all h3 tags that look like speeds
    speed_headings = soup.find_all("h3", string=re.compile(r"\d+\s*Mbps", re.I))

    for h3 in speed_headings:
        speed_text = h3.get_text(strip=True)

        # Find price — look for "Rs. X,XXX / year" in nearby siblings/parent
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

        # Find features
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