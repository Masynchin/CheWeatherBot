"""Конфиг со всеми важными переменными.

Все данные экспортируются из переменных окружения
"""

import os


BOT_TOKEN = os.getenv("BOT_TOKEN")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

RUN_TYPE = os.getenv("RUN_TYPE", "polling")

DATABASE_URL = os.getenv("DATABASE_URL", "subscribers.db")
