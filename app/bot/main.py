"""Инициализация и запуск бота"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp

from app import config
from app.bot.handlers import Logic
from app.bot.polling import Polling
from app.bot.task import MailingTask
from app.db import AiosqliteConnection, Subscribers, create_db
from app.logger import logger
from app.weather import OwmWeather


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@logger.catch(level="CRITICAL")
async def main():
    """Главная функция, отвечающая за запуск бота и рассылки"""
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    logger.info("Запуск")

    async with AiosqliteConnection(config.DATABASE_URL) as db_session, \
               aiohttp.ClientSession() as client_session:
        await create_db(db_session)
        db = Subscribers(db_session)
        weather = OwmWeather.for_che(config.WEATHER_API_KEY, client_session)
        task = MailingTask.default(db, weather)
        logic = Logic(db, weather)
        logic.register(dp)

        if config.RUN_TYPE == "polling":
            await Polling(dp, tasks=[task]).run(bot)
        elif config.RUN_TYPE == "webhook":
            ...
