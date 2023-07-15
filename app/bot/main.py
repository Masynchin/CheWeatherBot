"""Инициализация и запуск бота"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp

from app import config
from app.bot.handlers import (
    CancelMailing,
    ChangeMailingHour,
    ChangeMailingMinute,
    ChangeMailingTime,
    CurrentWeather,
    DailyForecast,
    Errors,
    ExactDayForecast,
    ExactDayOptions,
    ExactHourForecast,
    ExactHourOptions,
    HourForecast,
    Info,
    MailingInfo,
    SetMailingHour,
    SetMailingMinute,
    SubscribeToMailing,
    Welcome,
)
from app.bot.polling import Polling
from app.bot.webhook import Webhook
from app.bot.task import MailingTask
from app.db import Subscribers, async_session
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

    async with async_session() as db_session, \
               aiohttp.ClientSession() as client_session:
        db = Subscribers(db_session)
        weather = OwmWeather.for_che(config.WEATHER_API_KEY, client_session)
        task = MailingTask.default(db, weather)
        routes = [
            Welcome(),
            Info(),
            CurrentWeather(weather),
            HourForecast(weather),
            ExactHourOptions(),
            ExactHourForecast(weather),
            DailyForecast(weather),
            ExactDayOptions(),
            ExactDayForecast(weather),
            MailingInfo(db),
            SubscribeToMailing(),
            SetMailingHour(),
            SetMailingMinute(db),
            ChangeMailingTime(),
            ChangeMailingHour(),
            ChangeMailingMinute(db),
            CancelMailing(db),
            Errors(),
        ]
        for route in routes:
            route.register(dp)

        if config.RUN_TYPE == "polling":
            await Polling(dp, tasks=[task]).run(bot)
        elif config.RUN_TYPE == "webhook":
            ...
