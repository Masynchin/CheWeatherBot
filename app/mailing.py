"""Модуль рассылки погоды.

Каждые 15 минут происходит рассылка всем её подписчикам
"""

import asyncio
import datetime as dt

from app import db
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
    start_from = utils.get_current_time()
    for mailing_time in iterate_mailing_time(start_from):
        await sleep_until(mailing_time)
        await send_mailing(bot, mailing_time.time())


def iterate_mailing_time(start_from):
    """Итерируемся по времени рассылок начиная с ближайшей следующей"""
    start_from = utils.round_time_by_fifteen_minutes(start_from)
    while True:
        start_from += dt.timedelta(minutes=15)
        yield start_from


async def sleep_until(sleep_to):
    """Спим до определённого времени"""
    await asyncio.sleep(utils.get_time_until(sleep_to))


async def send_mailing(bot, mailing_time):
    """Отправляем рассылку пользователям с данным временем"""
    forecast = await weather.get_current_weather()
    message_text = templates.MAILING_MESSAGE.format(forecast.format())
    sticker = forecast.get_sticker()
    subscribers = await db.get_subscribers_by_mailing_time(mailing_time)

    for subscriber in subscribers:
        user_id = subscriber.id
        await bot.send_sticker(user_id, sticker)
        message = await bot.send_message(user_id, message_text)
        await unpin_all_and_pin_message(bot, message)

        logger.info(f"Пользователь {user_id} получил ежедневный прогноз")


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
