import asyncio
from playwright.async_api import async_playwright


async def check():
    urls_seen = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        async def handle_response(response):
            url = response.url
            if "dishhome" in url and ("api" in url.lower() or response.request.resource_type == "xhr" or response.request.resource_type == "fetch"):
                urls_seen.append((response.request.resource_type, url, response.status))

        page.on("response", handle_response)

        await page.goto("https://dishhome.com.np/internet/plans", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)

        print(f"=== {len(urls_seen)} XHR/fetch calls captured ===")
        for rtype, url, status in urls_seen:
            print(f"[{status}] {rtype}: {url}")

        print("\n=== Page title ===")
        print(await page.title())

        print("\n=== Visible text snippet (first 2000 chars) ===")
        body_text = await page.inner_text("body")
        print(body_text[:2000])

        await browser.close()


asyncio.run(check())