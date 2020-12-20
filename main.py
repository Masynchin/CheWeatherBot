from aiogram import Bot, Dispatcher, executor
from aiogram.types.message import ContentType, ParseMode
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text as TextFilter
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import asyncio
from random import choice
from re import fullmatch

import config
import db
import keyboards
from logger import logger
import mailing
import weather


bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# START И ПОМОЩЬ


@dp.message_handler(commands=["start"])
async def send_welcome(message):
    text = (
        "Это бот, позволяющий получить информацию о погоде в Череповце\n\n"
        "Этой командой (/start) вам выдаётся клавиатура, "
        "на которой расположены основные команды:\n\n"
        f"*{config.WEATHER}* - позволяет получить прогноз погоды\n"
        f"*{config.MAILING}* - позволяет узнать о подписке на ежедневный прогноз погоды\n"
        f"*{config.HELP}* - поможет разобраться с управлением"
    )
    await message.answer(
        text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.main
    )
    logger.info(f'Пользователь {message.from_user["id"]} выполнил /start')


@dp.message_handler(TextFilter(equals=config.HELP))
async def send_info(message):
    info = (
        "Бот, позволяющий получить погоду Череповца\n\n"
        "Основные функции бота:\n"
        f"*{config.WEATHER}* - получить текущую погоду и прогноз\n"
        f"*{config.MAILING}* - получить информацию о рассылке\n\n"
        "Эти команды расположены на клавиатуре, "
        "которую бот выдаёт при вводе команды /start. "
        "Если у вас её нет, то нажмите на эту команду"
    )
    await message.answer(info, parse_mode=ParseMode.MARKDOWN)


# ПРОГНОЗ


@dp.message_handler(TextFilter(equals=config.WEATHER))
async def send_weather(message):
    text, wtype = await weather.get_weather()
    await message.answer_sticker(choice(config.STICKERS[wtype]))
    await message.answer(text)
    logger.info(f'Пользователь {message.from_user["id"]} получил прогноз погоды')


# О РАССЫЛКЕ


@dp.message_handler(TextFilter(equals=config.MAILING))
async def send_mailing_info(message):
    user_id = message.from_user["id"]
    text = mailing.get_user_mailing_info(user_id)
    await message.answer(text)


class NewSub(StatesGroup):
    hour = State()
    minute = State()


@dp.message_handler(commands=["subscribe_to_mailing"])
async def subscribe_to_mailing(message):
    await NewSub.hour.set()
    await message.answer("Выберите час:", reply_markup=keyboards.hour_choice)


@dp.callback_query_handler(state=NewSub.hour)
async def set_hour_callback(call, state):
    await state.update_data(hour=int(call.data))
    await NewSub.next()
    await call.message.edit_text(
        "Выберите минуты:", reply_markup=keyboards.minute_choice
    )


@dp.callback_query_handler(state=NewSub.minute)
async def set_minute_callback(call, state):
    async with state.proxy() as data:
        time = (data["hour"], int(call.data))
    user_id = call["from"]["id"]
    db.new_subscriber(user_id, time)

    await call.message.delete()
    await bot.send_message(
        text="Вы подписались на рассылку по времени {}:{:02}".format(*time),
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
        "Выберите час:", reply_markup=keyboards.hour_choice
    )


@dp.callback_query_handler(state=ChangeTime.hour)
async def change_hour_callback(call, state):
    await state.update_data(hour=int(call.data))
    await ChangeTime.next()
    await call.message.edit_text(
        "Выберите минуты:", reply_markup=keyboards.minute_choice
    )


@dp.callback_query_handler(state=ChangeTime.minute)
async def change_minute_callback(call, state):
    async with state.proxy() as data:
        time = (data["hour"], int(call.data))
    user_id = call["from"]["id"]
    db.change_subscriber(user_id, time)

    await call.message.delete()
    await bot.send_message(
        text="Вы изменили время рассылки на {}:{:02}".format(*time),
        chat_id=call.message.chat.id,
    )
    logger.info(f"Пользователь {user_id} изменил время рассылки")
    await state.finish()


@dp.message_handler(commands=["cancel_mailing"])
async def cancel_mailing(message):
    user_id = message.from_user["id"]
    db.delete_subscriber(user_id)
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
