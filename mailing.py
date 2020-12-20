import asyncio
import datetime as dt
from random import choice

import config
import db
import weather


async def mailing(bot, logger):
    """Берём ID из БД и отправляем им прогноз погоды"""
    while True:
        seconds, next_fifteen = _get_next_fifteen_minutes()
        await asyncio.sleep(seconds)

        ids = db.get_by_time(next_fifteen)
        forecast, wtype = await weather.get_weather()
        for id in ids:
            await bot.send_sticker(id, choice(config.STICKERS[wtype]))
            msg = await bot.send_message(id, f"Ваш ежедневный прогноз 🤗\n\n{forecast}")
            await bot.pin_chat_message(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                disable_notification=True,
            )
            logger.info(f"Пользователь: {id} получил ежедневный прогноз")


def _get_next_fifteen_minutes():
    """Получаем количество секунд до слеющуюшего времени, кратного 15 минутам"""
    now = dt.datetime.now()
    next_fifteen = now.replace(
        minute=now.minute // 15 * 15, second=0, microsecond=0
    ) + dt.timedelta(minutes=15)
    seconds = (next_fifteen - dt.datetime.now()).total_seconds()
    return seconds, (next_fifteen.hour, next_fifteen.minute)


def get_user_mailing_info(user_id):
    """Получаем информацию о времени подписки пользователя"""
    if db.is_user_in_db(user_id):
        time = db.get_subscriber_time(user_id)
        text = (
            "Вы зарегистрированы в подписке\n"
            "Ваше время - {}:{:02}\n\n"
            "Поменять время - /change_time_mailing\n"
            "Отказаться от подписки - /cancel_mailing"
        ).format(*time)
    else:
        text = (
            "Вас нет в подписке\n\n"
            "Вы можете подписаться на неё по команде /subscribe_to_mailing"
        )
    return text
