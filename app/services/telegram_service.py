import requests

from app.config import Settings


class TelegramService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.last_message: str | None = None

    def send_message(self, text: str) -> None:
        self.last_message = text
        if self.settings.use_mock_data:
            print(text)
            return
        response = requests.post(
            f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage",
            json={
                "chat_id": self.settings.telegram_chat_id,
                "text": text,
            },
            timeout=30,
        )
        response.raise_for_status()
