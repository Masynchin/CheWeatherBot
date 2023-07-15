"""Основной модуль, отвещающий за работу с telegram.

Работа с пользователем - позволяем получить прогноз погоды,
зарегистрироваться в рассылке, отписаться от рассылки
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

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
from app.db import Subscribers
from app.logger import logger
from app.weather import OwmWeather


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@logger.catch(level="CRITICAL")
def main():
    """Главная функция, отвечающая за запуск бота и рассылки"""
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    logger.info("Запуск")

    db = Subscribers()
    weather = OwmWeather.for_che(config.WEATHER_API_KEY)
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
        Polling(dp, tasks=[task]).run(bot)
    elif config.RUN_TYPE == "webhook":
        ...
