
import httpx
from src.config import settings

async def send_telegram_message(chat_id: int, text: str):
    token = settings.TELEGRAM_TOKEN
    url = f"https://api.telegram.org{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload)
        except Exception:
            pass
