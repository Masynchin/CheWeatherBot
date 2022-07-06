"""Модуль рассылки погоды.

Каждые 15 минут происходит рассылка всем её подписчикам
"""

from app import db
from app import templates
from app import weather
from app.logger import logger


async def mailing(bot, mailing_times):
    """Отправление рассылки.

    Функция импортируется в main, где встраивается в основной loop.
    Каждые 15 минут происходит запрос к БД на наличие подписчиков с
    данным временем, и каждому отправляет прогноз погоды
    """
    async for mailing_time in mailing_times:
        await send_mailing(bot, mailing_time.time())


async def send_mailing(bot, mailing_time):
    """Отправляем рассылку пользователям с данным временем"""
    forecast = await weather.current()
    message_text = templates.MAILING_MESSAGE.format(forecast.format())
    sticker = forecast.sticker()
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
