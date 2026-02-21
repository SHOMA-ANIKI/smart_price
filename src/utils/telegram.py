import httpx
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self):
        self.token = settings.TELEGRAM_TOKEN
        self.base_url = f"https://api.telegram.org{self.token}/sendMessage"
        self.timeout = 5.0

    async def send_message(self, chat_id: int, text: str) -> bool:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                return True
            except httpx.HTTPStatusError as e:
                logger.error(f"Telegram API error: {e.response.text}")
            except Exception as e:
                logger.error(f"Unexpected error sending telegram message: {e}")

            return False
