"""Основной модуль, отвещающий за работу с telegram.

Работа с пользователем - позволяем получить прогноз погоды,
зарегистрироваться в рассылке, отписаться от рассылки
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app import config
from app.bot.handlers import (
    CancelMailing,
    ChangeHourMailing,
    ChangeMinuteMailing,
    ChangeTimeMailing,
    DailyForecast,
    Errors,
    ExactHourForecast,
    HandleExactDayForecast,
    HandleExactHourForecast,
    HourForecast,
    Info,
    MailingInfo,
    SendExactDayForecast,
    SetMailingHour,
    SetMinuteMailing,
    SubscribeToMailing,
    Weather,
    Welcome,
)
from app.bot.polling import Polling
from app.bot.webhook import Webhook
from app.bot.task import MailingTask
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

    weather = OwmWeather()
    task = MailingTask.default(weather)
    routes = [
        Welcome(),
        Info(),
        Weather(weather),
        HourForecast(weather),
        ExactHourForecast(),
        HandleExactHourForecast(weather),
        DailyForecast(weather),
        SendExactDayForecast(),
        HandleExactDayForecast(weather),
        MailingInfo(),
        SubscribeToMailing(),
        SetMailingHour(),
        SetMinuteMailing(),
        ChangeTimeMailing(),
        ChangeHourMailing(),
        ChangeMinuteMailing(),
        CancelMailing(),
        Errors(),
    ]
    for route in routes:
        route.register(dp)

    if config.RUN_TYPE == "polling":
        Polling(dp, tasks=[task]).run(bot)
    elif config.RUN_TYPE == "webhook":
        ...
