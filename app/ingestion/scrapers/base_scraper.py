
import sys
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Response
from app.config import get_settings
from app.logger import get_logger

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

settings = get_settings()
logger   = get_logger(__name__)

BLOCKED_RESOURCES = {"image", "media", "font", "stylesheet"}
STEALTH_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

class BaseScraper(ABC):
    """
    Abstract base for all ISP scrapers.
    Subclasses implement extract_plans(); everything else is handled here.
    """

    def __init__(self, isp: object):
        self.isp     = isp
        self.browser: Optional[Browser]        = None
        self.context: Optional[BrowserContext] = None

    

    @abstractmethod
    async def extract_plans(self, page: Page) -> list[dict]:
        """Parse the loaded page and return list of raw plan dicts."""
        ...

   

    async def scrape(self) -> list[dict]:
        """Main entry point — handles retry and browser lifecycle."""
        @retry(
            stop=stop_after_attempt(settings.scraper_retry_attempts),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )
        async def _run():
            try:
                return await self._execute_scrape()
            finally:
                await self._close_browser()

        result = await _run()
        logger.info("scrape_complete", isp=self.isp.slug, plans=len(result))
        return result

   

    async def _launch_browser(self) -> None:
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=settings.scraper_headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

    async def _create_context(self) -> BrowserContext:
        extra_headers = self.isp.scraper_config.get("headers", {})
        self.context = await self.browser.new_context(
            user_agent=STEALTH_UA,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            timezone_id="Asia/Kathmandu",
            extra_http_headers=extra_headers,
        )
        await self.context.route(
            "**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,mp4,mp3,webp}",
            lambda route: route.abort()
        )
        return self.context

    async def _get_page(self) -> Page:
        await self._launch_browser()
        await self._create_context()
        page = await self.context.new_page()
        page.set_default_timeout(settings.scraper_timeout_ms)
        return page

    async def _close_browser(self):
        try:
            if self.context: await self.context.close()
            if self.browser: await self.browser.close()
        except Exception:
            pass
        finally:
            self.browser = self.context = None

    

    async def _navigate(self, page: Page, url: str) -> None:
        await page.goto(url, wait_until="networkidle", timeout=settings.scraper_timeout_ms)
        wait_sel = self.isp.scraper_config.get("wait_for_selector")
        if wait_sel:
            await page.wait_for_selector(wait_sel, timeout=settings.scraper_timeout_ms)

    async def _scroll_to_load(self, page: Page) -> None:
        await page.evaluate("""async () => {
            await new Promise(resolve => {
                let total = 0;
                const timer = setInterval(() => {
                    window.scrollBy(0, 400);
                    total += 400;
                    if (total >= document.body.scrollHeight) { clearInterval(timer); resolve(); }
                }, 100);
            });
        }""")
        await page.wait_for_timeout(500)

 

    async def _execute_scrape(self) -> list[dict]:
        config = self.isp.scraper_config
        url    = config["plan_list_url"]

        page = await self._get_page()
        await self._navigate(page, url)

        if config.get("pagination_type") == "scroll":
            await self._scroll_to_load(page)

        plans = await self.extract_plans(page)

      
        if config.get("pagination_type") == "click":
            all_plans, page_num = list(plans), 1
            while page_num < 20:
                next_btn = await page.query_selector(config.get("pagination_selector", ".next-page"))
                if not next_btn: break
                if await next_btn.get_attribute("disabled") is not None: break
                await next_btn.click()
                await page.wait_for_load_state("networkidle")
                all_plans.extend(await self.extract_plans(page))
                page_num += 1
            return all_plans

        return plans


class ConfigDrivenScraper(BaseScraper):
    """
    Uses CSS selectors stored in isp.scraper_config to extract plans.
    Works for most ISPs with standard HTML structure.
    """

    async def extract_plans(self, page: Page) -> list[dict]:
        selectors  = self.isp.scraper_config["selectors"]
        source_url = page.url
        isp_id     = self.isp.id

        return await page.evaluate(
            """([sel, isp_id, source_url]) => {
                const containers = document.querySelectorAll(sel.plan_container);
                return Array.from(containers).map(el => ({
                    isp_id,
                    raw_name:        el.querySelector(sel.name)?.textContent?.trim()    ?? "",
                    raw_price:       el.querySelector(sel.price)?.textContent?.trim()   ?? "",
                    raw_speed:       el.querySelector(sel.speed)?.textContent?.trim()   ?? "",
                    raw_bundles:     sel.bundles
                        ? Array.from(el.querySelectorAll(sel.bundles))
                              .map(b => b.textContent?.trim()).filter(Boolean)
                        : [],
                    raw_description: el.querySelector(".description, p")?.textContent?.trim() ?? "",
                    source_url,
                    scraped_at:      new Date().toISOString(),
                })).filter(p => p.raw_name && p.raw_price);
            }""",
            [selectors, isp_id, source_url]
        )