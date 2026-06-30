import httpx
import asyncio
from bs4 import BeautifulSoup


async def check():
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as c:
        r = await c.get('https://worldlink.com.np/')
        soup = BeautifulSoup(r.text, 'lxml')
        cards = soup.find_all("div", class_=lambda cl: cl and "plans-card" in cl and "item" in cl)
        print(f"Found {len(cards)} cards\n")
        if cards:
            print("=== FIRST CARD FULL HTML ===")
            print(cards[0].prettify()[:3000])


asyncio.run(check())