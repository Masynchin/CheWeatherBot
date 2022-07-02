"""Основной модуль, отвещающий за работу с telegram.

Работа с пользователем - позволяем получить прогноз погоды,
зарегистрироваться в рассылке, отписаться от рассылки
"""

import asyncio
import datetime as dt

from aiohttp.web import Application, run_app
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.dispatcher.filters import Text as TextFilter
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

from app import config
from app import db
from app import keyboards
from app import mailing
from app import stickers
from app import templates
from app import utils
from app import weather
from app.che import CheDatetime
from app.logger import logger
from app.times import MailingDatetimes, SleepBetween


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(MemoryStorage())


# START И ПОМОЩЬ


@dp.message(commands=["start"])
async def send_welcome(message):
    """Приветсвенное сообщение с клавиатурой и информацией о командах"""
    await message.answer(
        templates.WELCOME,
        parse_mode="MARKDOWN",
        reply_markup=keyboards.MainKeyboard(),
    )
    logger.info("Пользователь {} выполнил /start", message.from_user.id)


@dp.message(TextFilter(text=keyboards.HELP))
async def send_info(message):
    """Информационное сообщение со всеми основными командами"""
    await message.answer(templates.INFO, parse_mode="MARKDOWN")


# ПРОГНОЗ


@dp.message(TextFilter(text=keyboards.WEATHER))
async def send_weather(message):
    """Отправка текущей погоды"""
    forecast = await weather.get_current_weather()
    text = forecast.format()
    sticker = forecast.get_sticker()
    await message.answer_sticker(sticker)
    await message.answer(text)
    logger.info(
        "Пользователь {} получил текущую погоду", message.from_user.id
    )


@dp.message(TextFilter(text=keyboards.HOUR_FORECAST))
async def send_hour_forecast(message):
    """Отправка прогноза на следующий час"""
    timestamp = CheDatetime.current()
    forecast = await weather.get_hourly_forecast(timestamp)
    text = forecast.format()
    sticker = forecast.get_sticker()
    await message.answer_sticker(sticker)
    await message.answer(text)
    logger.info(
        "Пользователь {} получил прогноз погоды на час",
        message.from_user.id,
    )


class ChooseForecastHour(StatesGroup):
    """Состояние пользователя при выборе конкретного часа прогноза"""

    hour = State()


@dp.message(TextFilter(text=keyboards.EXACT_HOUR_FORECAST), state=None)
async def send_exact_hour_forecast(message, state):
    """
    Пользователь нажал на кнопку прогноза в конкретный час.
    Отправляем клавиатуру с двенадцатью ближайшими часами
    """
    await state.set_state(ChooseForecastHour.hour)
    await message.answer(
        "Выберите час прогноза:",
        reply_markup=keyboards.ForecastHourChoice.current(),
    )


@dp.callback_query(ChooseForecastHour.hour)
async def handle_hour_forecast_choice(call, state):
    """Отправка прогноза на час, выбранный пользователем"""
    await state.clear()

    hour = CheDatetime.from_timestamp(call.data)
    forecast = await weather.get_exact_hour_forecast(hour)
    text = forecast.format()
    sticker = forecast.get_sticker()

    hour = hour.strftime("%H:%M")
    await call.message.edit_text(f"Прогноз на {hour}")
    await call.message.answer_sticker(sticker)
    await call.message.answer(text)
    logger.info(
        "Пользователь {} получил прогноз погоды на {} часов",
        call.from_user.id,
        hour,
    )


@dp.message(TextFilter(text=keyboards.TOMORROW_FORECAST))
async def send_daily_forecast(message):
    """Отправка прогноза на день"""
    timestamp = CheDatetime.current()
    forecast = await weather.get_daily_forecast(timestamp)
    text = forecast.format()
    sticker = forecast.get_sticker()
    await message.answer_sticker(sticker)
    await message.answer(text)
    logger.info(
        "Пользователь {} получил прогноз погоды на день",
        message.from_user.id,
    )


class ChooseForecastDay(StatesGroup):
    """Состояние пользователя при выборе конкретного дня прогноза"""

    day = State()


@dp.message(TextFilter(text=keyboards.EXACT_DAY_FORECAST), state=None)
async def send_exact_day_forecast(message, state):
    """
    Пользователь нажал на кнопку прогноза в конкретный день.
    Отправляем клавиатуру со следующими семью днями
    """
    await state.set_state(ChooseForecastDay.day)
    await message.answer(
        "Выберите день прогноза:",
        reply_markup=keyboards.ForecastDayChoice.current(),
    )


@dp.callback_query(ChooseForecastDay.day)
async def handle_daily_forecast_choice(call, state):
    """Отправка прогноза на день, выбранный пользователем"""
    await state.clear()

    day = CheDatetime.from_timestamp(call.data)
    forecast = await weather.get_exact_day_forecast(day)
    text = forecast.format()
    sticker = forecast.get_sticker()

    day = utils.format_date_as_day(day)
    await call.message.edit_text(f"Прогноз на {day}")
    await call.message.answer_sticker(sticker)
    await call.message.answer(text)
    logger.info(
        "Пользователь {} получил прогноз погоды на {}",
        call.from_user.id,
        day,
    )


# О РАССЫЛКЕ


@dp.message(TextFilter(text=keyboards.MAILING))
async def send_mailing_info(message):
    """Отправка информации о подписке пользователя на рассылку.

    Отправляем время рассылки, если зарегистрирован, или шаблон с тем,
    что его нет в рассылке, если его нет в рассылке
    """
    user_id = message.from_user.id
    mailing_info = await mailing.get_user_mailing_info(user_id)
    await message.answer(mailing_info)


class NewSub(StatesGroup):
    """Состояния пользователя при выборе времени для регистрации в рассылке"""

    hour = State()
    minute = State()


@dp.message(commands=["subscribe_to_mailing"], state=None)
async def subscribe_to_mailing(message, state):
    """
    Пользователь решил зарегистрироваться в рассылке,
    отправляем клавиатуру с выбором часа рассылки
    """
    await state.set_state(NewSub.hour)
    await message.answer(
        "Выберите час:", reply_markup=keyboards.HourChoiceKeyboard()
    )


@dp.callback_query(NewSub.hour)
async def set_hour_callback(call, state):
    """
    После выбора часа рассылки отправляем
    клавиатуру с выбором минуты рассылки
    """
    await state.update_data(hour=int(call.data))
    await call.message.edit_text(
        "Выберите минуты:", reply_markup=keyboards.MinuteChoiceKeyboard()
    )
    await state.set_state(NewSub.minute)


@dp.callback_query(NewSub.minute)
async def set_minute_callback(call, state):
    """Пользователь выбрал час и минуту рассылки, регистрируем его в БД"""
    data = await state.get_data()
    user_id = call.from_user.id
    time = dt.time(hour=data["hour"], minute=int(call.data))
    await db.new_subscriber(user_id, time)

    await state.clear()
    await call.message.delete()  # удаляем клавитуру выбора минуты расылки
    await bot.send_message(
        text=templates.USER_SUBSCRIBED.format(time.hour, time.minute),
        chat_id=call.message.chat.id,
    )
    logger.info("Пользователь {} внесён в рассылку", user_id)


class ChangeTime(StatesGroup):
    """Состояния пользователя при изменении времени рассылки"""

    hour = State()
    minute = State()


@dp.message(commands=["change_time_mailing"], state=None)
async def change_time_mailing(message, state):
    """
    Пользователь решил поменять время рассылки,
    отправляем клавиатуру с выбором нового часа рассылки
    """
    await message.answer(
        "Выберите час:", reply_markup=keyboards.HourChoiceKeyboard()
    )
    await state.set_state(ChangeTime.hour)


@dp.callback_query(ChangeTime.hour)
async def change_hour_callback(call, state):
    """
    После выбора нового часа рассылки отправляем
    клавиатуру с выбором новой минуты рассылки
    """
    await state.update_data(hour=int(call.data))
    await state.set_state(ChangeTime.minute)
    await call.message.edit_text(
        "Выберите минуты:", reply_markup=keyboards.MinuteChoiceKeyboard()
    )


@dp.callback_query(ChangeTime.minute)
async def change_minute_callback(call, state):
    """Пользователь выбрал новые час и минуту рассылки, обновляем его в БД"""
    data = await state.get_data()
    user_id = call.from_user.id
    time = dt.time(hour=data["hour"], minute=int(call.data))
    await db.change_subscriber_mailing_time(user_id, time)

    await state.clear()
    await call.message.delete()
    await bot.send_message(
        text=templates.USER_CHANGED_MAILING_TIME.format(
            time.hour, time.minute
        ),
        chat_id=call.message.chat.id,
    )
    logger.info("Пользователь {} изменил время рассылки", user_id)


@dp.message(commands=["cancel_mailing"])
async def cancel_mailing(message):
    """Пользователь решил отписаться от рассылки, удаляем из БД"""
    user_id = message.from_user.id
    await db.delete_subscriber(user_id)
    await message.answer("Успешно удалено из подписки")
    logger.info("Пользователь {} удалён из подписки", user_id)


# ОБРАБОТКА ОШИБОК


@dp.errors()
async def handle_errors(update):
    """Обработка непредвиденных ошибок"""
    await update.message.answer_sticker(stickers.MAINTAINCE_STICKER)
    await update.message.answer(templates.MAINTAINCE_MESSAGE)
    logger.exception("Произошла непредвиденная ошибка!")
    return True


# MAIN


@logger.catch(level="CRITICAL")
def main():
    """Главная функция, отвечающая за запуск бота и рассылки"""
    logger.info("Запуск")
    if config.RUN_TYPE == "polling":
        polling(dp)
    elif config.RUN_TYPE == "webhook":
        webhook(dp)


async def on_polling_startup():
    """Функция перед запуском бота в режиме polling"""
    await db.create_db()
    add_mailing_task()


async def on_webhook_startup():
    """Функция перед запуском бота в режиме webhook"""
    await db.create_db()
    add_mailing_task()
    await bot.set_webhook(config.WEBHOOK_URL, drop_pending_updates=True)


def add_mailing_task():
    """Добавляем асинхронную рассылку в основной event loop"""
    start = utils.round_time_by_fifteen_minutes(CheDatetime.current())
    mailing_times = SleepBetween(
        MailingDatetimes(start, dt.timedelta(minutes=15))
    )
    asyncio.create_task(mailing.mailing(bot, mailing_times))


def polling(dp):
    """Запуск бота в режиме long-polling"""
    dp.startup.register(on_polling_startup)
    dp.run_polling(bot)


def webhook(dp):
    """Запуск бота в режиме webhook"""
    dp.startup.register(on_webhook_startup)
    app = Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(
        app, path=config.WEBHOOK_PATH
    )
    setup_application(app, dp)
    run_app(app, host=config.WEBAPP_HOST, port=config.WEBAPP_PORT)
