"""Конфиг со всеми важными переменными.

Все данные экспортируются из переменных окружения.
Содержит токен telegram-бота, ключ API погодного сервера и путь к базе данных
"""

import os
from urllib.parse import urlencode


BOT_TOKEN = os.getenv("BOT_TOKEN")

WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/onecall?" + urlencode({
    "lat": 59.09,
    "lon": 37.91,
    "appid": os.getenv("WEATHER_API_KEY"),
    "units": "metric",
    "exclude": "minutely",
    "lang": "ru",
})

RUN_TYPE = os.getenv("RUN_TYPE", "polling")

DATABASE_URL = (
    os.getenv("DATABASE_URL", "sqlite+aiosqlite:///subscribers.db")
    .replace("postgres", "postgresql+asyncpg")
)

HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME", "")

WEBHOOK_HOST = f"https://{HEROKU_APP_NAME}.herokuapp.com"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8080))
