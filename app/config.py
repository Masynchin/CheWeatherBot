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

DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite+aiosqlite:///subscribers.db"
)
