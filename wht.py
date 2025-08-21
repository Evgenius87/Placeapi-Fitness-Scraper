import requests

from src.conf.config import settings

TG_API = settings.telegram_bot_token


whook = 'ce8a7767e46b.ngrok-free.app'

r = requests.get(f"https://api.telegram.org/bot{TG_API}/setWebhook?url=https://{whook}/webhook")
# r1 = requests.get(f"https://api.telegram.org/bot{TG_API}/getWebhookInfo")
print(r.json())
# print(r1.json())

