import httpx
import re
from typing import Optional


class WBParser:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*"
        }
        self.timeout = 10.0

    def _extract_article(self, url: str) -> Optional[str]:
        match = re.search(r"catalog/(\d+)/detail", url)
        return match.group(1) if match else None

    async def get_price(self, url: str) -> Optional[float]:
        article = self._extract_article(url)
        if not article:
            return None

        art_int = int(article)
        vol = art_int // 100000
        part = art_int // 1000

        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            for i in range(1, 21):
                basket_num = f"{i:02}"
                api_url = f"https://basket-{basket_num}.wb.ru/vol{vol}/part{part}/{article}/info/ru/card.json"

                try:
                    response = await client.get(api_url)
                    if response.status_code == 200:
                        data = response.json()
                        sizes = data.get("sizes", [])
                        if not sizes:
                            continue

                        raw_price = sizes[0].get("price", {}).get("total", 0)
                        return float(raw_price) / 100
                except (httpx.RequestError, ValueError):
                    continue
        return None
