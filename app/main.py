"""Основной модуль, отвещающий за работу с telegram.

Работа с пользователем - позволяем получить прогноз погоды,
зарегистрироваться в рассылке, отписаться от рассылки
"""

import asyncio
import datetime as dt

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text as TextFilter
from aiogram.types.message import ParseMode

import config
import db
import keyboards
from logger import logger
import mailing
import templates
import stickers
import utils
import weather


bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# START И ПОМОЩЬ


@dp.message_handler(commands=["start"])
async def send_welcome(message):
    """Приветсвенное сообщение с клавиатурой и информацией о командах"""
    await message.answer(
        templates.WELCOME,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboards.main,
    )
    logger.info("Пользователь {} выполнил /start", message.from_user["id"])


@dp.message_handler(TextFilter(equals=keyboards.HELP))
async def send_info(message):
    """Информационное сообщение со всеми основными командами"""
    await message.answer(templates.INFO, parse_mode=ParseMode.MARKDOWN)


# ПРОГНОЗ


@dp.message_handler(TextFilter(equals=keyboards.WEATHER))
async def send_weather(message):
    """Отправка текущей погоды"""
    text, weather_type = await weather.get_current_weather()
    sticker = stickers.get_by_weather(weather_type)
    await message.answer_sticker(sticker)
    await message.answer(text)
    logger.info(
        "Пользователь {} получил текущую погоду", message.from_user["id"]
    )


@dp.message_handler(TextFilter(equals=keyboards.HOUR_FORECAST))
async def send_hour_forecast(message):
    """Отправка прогноза на следующий час"""
    text, weather_type = await weather.get_hourly_forecast()
    sticker = stickers.get_by_weather(weather_type)
    await message.answer_sticker(sticker)
    await message.answer(text)
    logger.info(
        "Пользователь {} получил прогноз погоды на час",
        message.from_user["id"],
    )


class ChooseForecastHour(StatesGroup):
    """Состояние пользователя при выборе конкретного часа прогноза"""

    hour = State()


@dp.message_handler(TextFilter(equals=keyboards.EXACT_HOUR_FORECAST))
async def send_exact_hour_forecast(message):
    """
    Пользователь нажал на кнопку прогноза в конкретный час.
    Отправляем клавиатуру с двенадцатью ближайшими часами
    """
    await ChooseForecastHour.hour.set()
    await message.answer(
        "Выберите час прогноза:",
        reply_markup=keyboards.forecast_hour_choice(),
    )


@dp.callback_query_handler(state=ChooseForecastHour.hour)
async def handle_hour_forecast_choice(call, state):
    """Отправка прогноза на час, выбранный пользователем"""
    await state.finish()

    hour = utils.convert_json_timestamp_to_datetime(call.data)
    text, weather_type = await weather.get_exact_hour_forecast(hour)
    sticker = stickers.get_by_weather(weather_type)

    hour = hour.strftime("%H:%M")
    await call.message.edit_text(f"Прогноз на {hour}")
    await call.message.answer_sticker(sticker)
    await call.message.answer(text)
    logger.info(
        "Пользователь {} получил прогноз погоды на {} часов",
        call.from_user["id"],
        hour,
    )


@dp.message_handler(TextFilter(equals=keyboards.TOMORROW_FORECAST))
async def send_daily_forecast(message):
    """Отправка прогноза на день"""
    text, weather_type = await weather.get_daily_forecast()
    sticker = stickers.get_by_weather(weather_type)
    await message.answer_sticker(sticker)
    await message.answer(text)
    logger.info(
        "Пользователь {} получил прогноз погоды на день",
        message.from_user["id"],
    )


class ChooseForecastDay(StatesGroup):
    """Состояние пользователя при выборе конкретного дня прогноза"""

    day = State()


@dp.message_handler(TextFilter(equals=keyboards.EXACT_DAY_FORECAST))
async def send_exact_day_forecast(message):
    """
    Пользователь нажал на кнопку прогноза в конкретный день.
    Отправляем клавиатуру со следующими семью днями
    """
    await ChooseForecastDay.day.set()
    await message.answer(
        "Выберите день прогноза:",
        reply_markup=keyboards.forecast_day_choice(),
    )


@dp.callback_query_handler(state=ChooseForecastDay.day)
async def handle_daily_forecast_choice(call, state):
    """Отправка прогноза на день, выбранный пользователем"""
    await state.finish()

    day = utils.convert_json_timestamp_to_datetime(call.data)
    text, weather_type = await weather.get_exact_day_forecast(day)
    sticker = stickers.get_by_weather(weather_type)

    day = utils.format_date_as_day(day)
    await call.message.edit_text(f"Прогноз на {day}")
    await call.message.answer_sticker(sticker)
    await call.message.answer(text)
    logger.info(
        "Пользователь {} получил прогноз погоды на {}",
        call.from_user["id"],
        day,
    )


# О РАССЫЛКЕ


@dp.message_handler(TextFilter(equals=keyboards.MAILING))
async def send_mailing_info(message):
    """Отправка информации о подписке пользователя на рассылку.

    Отправляем время рассылки, если зарегистрирован, или шаблон с тем,
    что его нет в рассылке, если его нет в рассылке
    """
    user_id = message.from_user["id"]
    mailing_info = await mailing.get_user_mailing_info(user_id)
    await message.answer(mailing_info)


class NewSub(StatesGroup):
    """Состояния пользователя при выборе времени для регистрации в рассылке"""

    hour = State()
    minute = State()


@dp.message_handler(commands=["subscribe_to_mailing"])
async def subscribe_to_mailing(message):
    """
    Пользователь решил зарегистрироваться в рассылке,
    отправляем клавиатуру с выбором часа рассылки
    """
    await NewSub.hour.set()
    await message.answer("Выберите час:", reply_markup=keyboards.hour_choice)


@dp.callback_query_handler(state=NewSub.hour)
async def set_hour_callback(call, state):
    """
    После выбора часа рассылки отправляем
    клавиатуру с выбором минуты рассылки
    """
    await state.update_data(hour=int(call.data))
    await call.message.edit_text(
        "Выберите минуты:", reply_markup=keyboards.minute_choice
    )
    await NewSub.next()


@dp.callback_query_handler(state=NewSub.minute)
async def set_minute_callback(call, state):
    """Пользователь выбрал час и минуту рассылки, регистрируем его в БД"""
    async with state.proxy() as data:
        user_id = call["from"]["id"]
        time = dt.time(hour=data["hour"], minute=int(call.data))
        await db.new_subscriber(user_id, time)

    await state.finish()
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


@dp.message_handler(commands=["change_time_mailing"])
async def change_time_mailing(message):
    """
    Пользователь решил поменять время рассылки,
    отправляем клавиатуру с выбором нового часа рассылки
    """
    await message.answer("Выберите час:", reply_markup=keyboards.hour_choice)
    await ChangeTime.hour.set()


@dp.callback_query_handler(state=ChangeTime.hour)
async def change_hour_callback(call, state):
    """
    После выбора нового часа рассылки отправляем
    клавиатуру с выбором новой минуты рассылки
    """
    await state.update_data(hour=int(call.data))
    await ChangeTime.next()
    await call.message.edit_text(
        "Выберите минуты:", reply_markup=keyboards.minute_choice
    )


@dp.callback_query_handler(state=ChangeTime.minute)
async def change_minute_callback(call, state):
    """Пользователь выбрал новые час и минуту рассылки, обновляем его в БД"""
    async with state.proxy() as data:
        user_id = call["from"]["id"]
        time = dt.time(hour=data["hour"], minute=int(call.data))
        await db.change_subscriber_mailing_time(user_id, time)

    await state.finish()
    await call.message.delete()
    await bot.send_message(
        text=templates.USER_CHANGED_MAILING_TIME.format(
            time.hour, time.minute
        ),
        chat_id=call.message.chat.id,
    )
    logger.info("Пользователь {} изменил время рассылки", user_id)


@dp.message_handler(commands=["cancel_mailing"])
async def cancel_mailing(message):
    """Пользователь решил отписаться от рассылки, удаляем из БД"""
    user_id = message.from_user["id"]
    await db.delete_subscriber(user_id)
    await message.answer("Успешно удалено из подписки")
    logger.info("Пользователь {} удалён из подписки", user_id)


# ОБРАБОТКА ОШИБОК


@dp.errors_handler()
async def handle_errors(update, error):
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
    loop = asyncio.get_event_loop()
    add_mailing_to_loop(loop)
    executor.start_polling(dp, loop=loop, skip_updates=True)


def add_mailing_to_loop(loop):
    """Добавляем асинхронную рассылку в основной event loop"""
    loop.create_task(mailing.mailing(bot))
