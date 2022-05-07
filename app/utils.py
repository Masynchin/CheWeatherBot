"""Модуль с вспомогательными функциями"""

import datetime as dt

import pytz


def get_current_time():
    """Текущее время по Москве (часовой пояс Череповца)"""
    return dt.datetime.now(pytz.timezone("Europe/Moscow"))


def round_time_by_hours(time):
    """Округляем время до кратного часу.

    Например: 23.44.123456 -> 23.00.00
    """
    return time.replace(minute=0, second=0, microsecond=0)


def get_next_twelve_hours(start_from):
    """Получаем следующие 12 часов в виде HH:MM"""
    start_hour = round_time_by_hours(start_from)
    return [start_hour + dt.timedelta(hours=i) for i in range(1, 13)]


def round_time_by_fifteen_minutes(time):
    """Округляем время до кратного 15 минутам.

    Например: 15.37.123456 -> 15.30.00
    """
    return time.replace(minute=time.minute // 15 * 15, second=0, microsecond=0)


def get_time_until(time):
    """Получаем количество секунд до времени в будущем"""
    return (time - get_current_time()).total_seconds()


def get_next_seven_days(start_from):
    """Получаем следующие семь дней начиная от завтрашнего"""
    start_day = _round_date_by_day(start_from)
    return [start_day + dt.timedelta(days=i) for i in range(1, 8)]


def _round_date_by_day(date):
    """Округляем dt.datetime до дня

    Например 23.02.21 12:34:56 -> 23.02.21 00:00:00
    """
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def convert_json_timestamp_to_datetime(json_timestamp):
    """Перевод таймштампа из JSON'а колбэка в dt.datetime

    Например: '16892286320.0' -> dt.datetime(...)
    """
    timestamp = int(float(json_timestamp))
    return dt.datetime.fromtimestamp(timestamp, pytz.timezone("Europe/Moscow"))


def format_date_as_day(date):
    """Преобразуем dt.datetime в строку вида 'день - дд.мм'

    Например: dt.datetime(..day=15, month=4..) -> 'Четверг - 22.04'
    """
    weekday = get_weekday_name_from_datetime(date)
    return date.strftime(f"{weekday} - %d.%m")


def get_weekday_name_from_datetime(date):
    """Получаем день недели на русском из dt.datetime"""
    current_date = date.astimezone(pytz.timezone("Europe/Moscow"))
    weekday_index = current_date.weekday()
    return [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ][weekday_index]
