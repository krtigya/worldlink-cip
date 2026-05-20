"""
VianetScraper — intercepts Vianet's internal XHR API for plan data.
More reliable than DOM scraping for JavaScript-heavy SPAs.
"""
import asyncio
import json
from playwright.async_api import Page, Response
from app.ingestion.scrapers.base_scraper import BaseScraper
from app.logger import get_logger

logger = get_logger(__name__)


class VianetScraper(BaseScraper):

    async def extract_plans(self, page: Page) -> list[dict]:
        source_url     = self.isp.scraper_config["plan_list_url"]
        intercepted    = []

        # Strategy 1: Intercept API response
        async def handle_response(response: Response):
            url = response.url
            if "/api/packages" in url or "/api/plans" in url:
                try:
                    data  = await response.json()
                    items = data.get("data") or data.get("packages") or (data if isinstance(data, list) else [])
                    for item in items:
                        intercepted.append({
                            "isp_id":          self.isp.id,
                            "raw_name":        str(item.get("name") or item.get("title", "")),
                            "raw_price":       str(item.get("price") or item.get("monthly_price") or item.get("amount", "")),
                            "raw_speed":       str(item.get("speed") or item.get("bandwidth") or item.get("download_speed", "")),
                            "raw_bundles":     self._extract_bundles_from_api(item),
                            "raw_description": str(item.get("description", "")),
                            "source_url":      source_url,
                        })
                except Exception:
                    pass

        page.on("response", handle_response)
        await page.goto(source_url, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(2_000)

        if intercepted:
            return intercepted

        # Strategy 2: Fallback DOM scraping
        logger.warning("vianet_api_intercept_failed_falling_back_to_dom", isp=self.isp.slug)
        return await self._dom_fallback(page, source_url)

    async def _dom_fallback(self, page: Page, source_url: str) -> list[dict]:
        selector_sets = [
            {"container": ".plan-card",    "name": "h3",            "price": ".price",        "speed": ".speed"},
            {"container": ".package-card", "name": ".package-name", "price": ".package-price", "speed": ".speed-tag"},
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
                        raw_bundles: Array.from(el.querySelectorAll("li,.feature"))
                                        .map(b => b.textContent?.trim()).filter(Boolean),
                        source_url,
                    })).filter(p => p.raw_name);
                }""",
                [sel, self.isp.id, source_url]
            )
            if plans:
                return plans

        return []

    def _extract_bundles_from_api(self, item: dict) -> list[str]:
        features = item.get("features") or item.get("addons") or item.get("includes") or []
        if isinstance(features, list):
            return [
                f if isinstance(f, str) else str(f.get("name") or f.get("title", ""))
                for f in features
            ]
        return []
