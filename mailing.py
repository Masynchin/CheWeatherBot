import asyncio
import datetime as dt
from random import choice

import pytz

import const
import db
import weather


async def mailing(bot, logger):
    """Ежепятнадцатиминутная рассылка"""
    while True:
        seconds_delta, next_fifteen = _get_next_fifteen_minutes()
        await asyncio.sleep(seconds_delta)

        subscribers = await db.get_subscribers_by_time(next_fifteen)
        forecast, wtype = await weather.current_weather()
        for subscriber in subscribers:
            user_id = subscriber.id
            await bot.send_sticker(user_id, choice(const.STICKERS[wtype]))
            msg = await bot.send_message(
                user_id, f"Ваш ежедневный прогноз 🤗\n\n{forecast}")
            logger.info(f"Пользователь {user_id} получил ежедневный прогноз")

            await bot.pin_chat_message(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                disable_notification=True,
            )


def _get_next_fifteen_minutes():
    """Получаем количество секунд до слеющуюшего времени, кратного 15 минутам"""
    now = _get_now()
    next_fifteen = now.replace(
        minute=now.minute // 15 * 15, second=0, microsecond=0
    ) + dt.timedelta(minutes=15)
    seconds_delta = (next_fifteen - _get_now()).total_seconds()
    return seconds_delta, (next_fifteen.hour, next_fifteen.minute)


def _get_now():
    return dt.datetime.now(pytz.timezone("Europe/Moscow"))


async def get_user_mailing_info(user_id):
    """Получаем информацию о подписке пользователя"""
    is_subscriber = await db.is_user_in_subscription(user_id)
    if is_subscriber:
        time = await db.get_subscriber_time(user_id)
        text = const.USER_IN_SUBSCRIBE.format(*time)
    else:
        text = const.USER_NOT_IN_SUBSCRIBE
    return text
