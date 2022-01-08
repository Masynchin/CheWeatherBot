"""Модуль рассылки погоды.

Каждые 15 минут происходит рассылка всем её подписчикам
"""

import asyncio

from app import db
from app import stickers
from app import templates
from app import utils
from app import weather
from app.logger import logger


async def mailing(bot):
    """Отправление рассылки.

    Функция импортируется в main, где встаивается в основной loop.
    Каждые 15 минут происходит запрос к БД на наличие подписчиков с
    данным временем, и каждому отправляет прогноз погоды
    """
    while True:
        seconds_delta, next_fifteen = _get_next_fifteen_minutes()
        await asyncio.sleep(seconds_delta)

        forecast, wtype = await weather.get_current_weather()
        sticker = stickers.get_by_weather(wtype)
        subscribers = await db.get_subscribers_by_mailing_time(next_fifteen)

        for subscriber in subscribers:
            user_id = subscriber.id
            await bot.send_sticker(user_id, sticker)
            message = await bot.send_message(
                user_id, templates.MAILING_MESSAGE.format(forecast)
            )
            await unpin_all_and_pin_message(bot, message)

            logger.info(f"Пользователь {user_id} получил ежедневный прогноз")


def _get_next_fifteen_minutes():
    """Получение следующего времени рассылки.

    Функция вызывается раз в 15 минут, выдаёт количество секунд, на которое
    должна заснуть рассылка, и само время, по которому она опросит БД
    """
    now = utils.get_current_time()
    next_fifteen = utils.get_next_time_round_by_fifteen_minutes(now)
    seconds_delta = utils.get_time_difference(next_fifteen, now)
    return seconds_delta, next_fifteen.time()


async def unpin_all_and_pin_message(bot, message):
    """Открепляем все предыдущие прогнозы и прикляем новый"""
    await bot.unpin_all_chat_messages(message.chat.id)
    await bot.pin_chat_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        disable_notification=True,
    )


async def get_user_mailing_info(user_id):
    """Получаем информацию о подписке пользователя.

    Если пользователь есть в базе данных, то возвращаем его время подписки.
    Если нет, то возращаем шаблон с тем, что его нет в рассылке
    """
    is_subscriber = await db.is_user_in_subscription(user_id)
    if not is_subscriber:
        return templates.USER_NOT_IN_MAILING

    time = await db.get_subscriber_mailing_time(user_id)
    return templates.USER_IN_MAILING.format(time.hour, time.minute)
