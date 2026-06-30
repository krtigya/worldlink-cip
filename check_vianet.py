import httpx
import asyncio
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


async def check():
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=30) as c:
        r = await c.get('https://www.vianet.com.np/vianetwifi6/')
        soup = BeautifulSoup(r.text, 'lxml')
        tables = soup.find_all("table")
        print(f"Found {len(tables)} tables")
        for i, t in enumerate(tables):
            rows = t.find_all("tr")
            print(f"\n=== TABLE {i} ({len(rows)} rows) ===")
            if rows:
                header_cells = rows[0].find_all(["th", "td"])
                headers_text = [c.get_text(strip=True) for c in header_cells]
                print("Header row:", headers_text)
                if len(rows) > 1:
                    second_cells = rows[1].find_all(["th", "td"])
                    print("Row 1:", [c.get_text(strip=True) for c in second_cells])


asyncio.run(check())