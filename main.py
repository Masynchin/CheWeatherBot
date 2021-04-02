import asyncio
import datetime as dt
import os

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
import weather


bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# START И ПОМОЩЬ


@dp.message_handler(commands=["start"])
async def send_welcome(message):
    await message.answer(templates.WELCOME,
        parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.main)
    logger.info(f"Пользователь {message.from_user['id']} выполнил /start")


@dp.message_handler(TextFilter(equals=keyboards.HELP))
async def send_info(message):
    await message.answer(templates.INFO, parse_mode=ParseMode.MARKDOWN)


# ПРОГНОЗ


@dp.message_handler(TextFilter(equals=keyboards.WEATHER))
async def send_weather(message):
    text, wtype = await weather.current_weather()
    sticker = stickers.get_by_weather(wtype)
    await message.answer_sticker(sticker)
    await message.answer(text)
    logger.info(
        f"Пользователь {message.from_user['id']} получил текущую погоду")


@dp.message_handler(TextFilter(equals=keyboards.HOUR_FORECAST))
async def send_hour_forecast(message):
    text, wtype = await weather.hourly_forecast()
    sticker = stickers.get_by_weather(wtype)
    await message.answer_sticker(sticker)
    await message.answer(text)
    logger.info(
        f"Пользователь {message.from_user['id']} получил прогноз погоды на час")


@dp.message_handler(TextFilter(equals=keyboards.TOMORROW_FORECAST))
async def send_weather(message):
    text, wtype = await weather.daily_forecast()
    sticker = stickers.get_by_weather(wtype)
    await message.answer_sticker(sticker)
    await message.answer(text)
    logger.info(
        f"Пользователь {message.from_user['id']} получил прогноз погоды на день")


# О РАССЫЛКЕ


@dp.message_handler(TextFilter(equals=keyboards.MAILING))
async def send_mailing_info(message):
    user_id = message.from_user["id"]
    text = await mailing.get_user_mailing_info(user_id)
    await message.answer(text)


class NewSub(StatesGroup):
    hour = State()
    minute = State()


@dp.message_handler(commands=["subscribe_to_mailing"])
async def subscribe_to_mailing(message):
    await NewSub.hour.set()
    await message.answer(
        "Выберите час:", reply_markup=keyboards.hour_choice)


@dp.callback_query_handler(state=NewSub.hour)
async def set_hour_callback(call, state):
    await state.update_data(hour=int(call.data))
    await NewSub.next()
    await call.message.edit_text(
        "Выберите минуты:", reply_markup=keyboards.minute_choice)


@dp.callback_query_handler(state=NewSub.minute)
async def set_minute_callback(call, state):
    async with state.proxy() as data:
        user_id = call["from"]["id"]
        time = dt.time(hour=data["hour"], minute=int(call.data))
        await db.new_subscriber(user_id, time)

    await call.message.delete()
    await bot.send_message(
        text=templates.USER_SUBSCRIBED.format(time.hour, time.minute),
        chat_id=call.message.chat.id,
    )
    logger.info(f"Пользователь {user_id} внесён в рассылку")
    await state.finish()


class ChangeTime(StatesGroup):
    hour = State()
    minute = State()


@dp.message_handler(commands=["change_time_mailing"])
async def change_time_mailing(message):
    await ChangeTime.hour.set()
    await message.answer(
        "Выберите час:", reply_markup=keyboards.hour_choice)


@dp.callback_query_handler(state=ChangeTime.hour)
async def change_hour_callback(call, state):
    await state.update_data(hour=int(call.data))
    await ChangeTime.next()
    await call.message.edit_text(
        "Выберите минуты:", reply_markup=keyboards.minute_choice)


@dp.callback_query_handler(state=ChangeTime.minute)
async def change_minute_callback(call, state):
    async with state.proxy() as data:
        user_id = call["from"]["id"]
        time = dt.time(hour=data["hour"], minute=int(call.data))
        await db.change_subscriber_mailing_time(user_id, time)

    await call.message.delete()
    await bot.send_message(
        text=templates.USER_CHANGED_MAILING_TIME.format(time.hour, time.minute),
        chat_id=call.message.chat.id,
    )
    logger.info(f"Пользователь {user_id} изменил время рассылки")
    await state.finish()


@dp.message_handler(commands=["cancel_mailing"])
async def cancel_mailing(message):
    user_id = message.from_user["id"]
    await db.delete_subscriber(user_id)
    await message.answer("Успешно удалено из подписки")
    logger.info(f"Пользователь {user_id} удалён из подписки")


# MAIN


@logger.catch(level="CRITICAL")
def main():
    # добавляем рассылку в loop
    loop = asyncio.get_event_loop()
    loop.create_task(mailing.mailing(bot, logger))
    # запускаем поллинг
    logger.info("Запуск")
    executor.start_polling(dp, loop=loop, skip_updates=True)


if __name__ == "__main__":
    main()
