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


def get_next_twelve_hours(start_hour):
    """Получаем следующие 12 часов в виде HH:MM"""
    hours = [start_hour + dt.timedelta(hours=i) for i in range(1, 13)]
    return [hour.strftime("%H:%M") for hour in hours]


def get_next_time_round_by_fifteen_minutes(time):
    """Получение следующего времени, кратного 15 минутам.

    Например: 09:22:654321 -> 09:30:00
    """
    time = _round_time_by_fifteen_minutes(time)
    return time + dt.timedelta(minutes=15)


def _round_time_by_fifteen_minutes(time):
    """Округляем время до кратного 15 минутам.

    Например: 15.37.123456 -> 15.30.00
    """
    return time.replace(minute=time.minute // 15 * 15, second=0, microsecond=0)


def get_time_difference(time1, time2):
    """Получаем количество секунд между двумя временами"""
    return (time1 - time2).total_seconds()
