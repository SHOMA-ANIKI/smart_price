import httpx
import re

async def get_wb_price(url: str) -> float | None:
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
    match = re.search(r"catalog/(\d+)/detail", url)
    if not match: return None
    art = match.group(1)
    vol, part = int(art) // 100000, int(art) // 1000
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        for i in range(1, 21):
            api_url = f"https://basket-{i:02}.wb.ru/vol{vol}/part{part}/{art}/info/ru/card.json"
            try:
                res = await client.get(api_url)
                if res.status_code == 200:
                    data = res.json()
                    return float(data.get("sizes", [{}])[0].get("price", {}).get("total", 0)) / 100
            except: continue
    return None
