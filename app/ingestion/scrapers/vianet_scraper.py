"""
HTTP scraper for Vianet — static HTML table, no JS needed.

Page structure (from live site):
  Plans are in two <table> blocks:
    1. "Renewal Rate" table  — rows: 1 Month / 3 Months / 12 Months
    2. "New Connection" table — rows: 3 Months / 12 Months
  Columns: Plus (100 Mbps) | Pro (200 Mbps) | Ultra (300 Mbps)
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

PLAN_URL = "https://www.vianet.com.np/superhitinternetpack/"

# Column → (plan name, speed)
COLUMNS = {
    "Plus":  ("Vianet Plus",  "100 Mbps"),
    "Pro":   ("Vianet Pro",   "200 Mbps"),
    "Ultra": ("Vianet Ultra", "300 Mbps"),
}


class VianetScraper:
    def __init__(self, isp):
        self.isp = isp

    async def scrape(self) -> list[dict]:
        config = self.isp.scraper_config
        url    = config.get("plan_list_url", PLAN_URL)

        logger.info("worldlink_http_scrape_start", url=url)

        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text
        except Exception as e:
            logger.error("vianet_fetch_failed", error=str(e))
            return []

        soup  = BeautifulSoup(html, "lxml")
        plans = self._parse_plans(soup, url)

        if not plans:
            logger.warning("worldlink_no_plans_found", selector="table")
        else:
            logger.info("worldlink_scrape_complete", plans=len(plans))

        return plans

    def _parse_plans(self, soup: BeautifulSoup, url: str) -> list[dict]:
        plans = []
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 3:
                continue

            # Detect header row — find column names (Plus / Pro / Ultra)
            header_row = rows[0]
            headers    = [td.get_text(strip=True) for td in header_row.find_all(["th", "td"])]

            # Find which columns map to plan names
            col_map = {}  # col_index → (plan_name, speed)
            for idx, h in enumerate(headers):
                for key, (name, speed) in COLUMNS.items():
                    if key in h:
                        col_map[idx] = (name, speed)

            if not col_map:
                continue

            # Detect table type from heading text above or caption
            table_type = "renewal"
            prev = table.find_previous(["h2", "h3", "h4", "p", "strong"])
            if prev and "new connection" in prev.get_text(strip=True).lower():
                table_type = "new_connection"

            # Parse data rows (skip header rows that contain speed info)
            for row in rows[1:]:
                cells = row.find_all(["th", "td"])
                if not cells:
                    continue

                row_label = cells[0].get_text(strip=True)  # e.g. "1 Month", "3 Months"
                if not re.match(r"\d+\s*Month", row_label, re.I):
                    continue  # skip speed rows, button rows, etc.

                for col_idx, (plan_name, speed) in col_map.items():
                    if col_idx >= len(cells):
                        continue

                    price_text = cells[col_idx].get_text(strip=True)
                    # Skip empty or non-price cells
                    if not re.search(r"Rs[\s.,\d]+", price_text):
                        continue

                    raw_name = f"{plan_name} {row_label} ({table_type.replace('_', ' ').title()})"
                    plans.append({
                        "isp_id":          self.isp.id,
                        "raw_name":        raw_name,
                        "raw_price":       price_text,
                        "raw_speed":       speed,
                        "raw_bundles":     [],
                        "raw_description": f"Vianet {plan_name} {speed} - {row_label} {table_type}",
                        "source_url":      url,
                        "scraped_at":      datetime.utcnow().isoformat(),
                    })

        return plans