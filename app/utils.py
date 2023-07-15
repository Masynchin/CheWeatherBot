"""Модуль с вспомогательными функциями"""

import datetime as dt


def round_time_by_hours(time):
    """Время, округлённое до часа.

    Например: 23.44.123456 -> 23.00.00
    """
    return time.replace(minute=0, second=0, microsecond=0)


def get_next_twelve_hours(start_from):
    """Следующие 12 часов в виде HH:MM"""
    start_hour = round_time_by_hours(start_from)
    return [start_hour + dt.timedelta(hours=i) for i in range(1, 13)]


def round_time_by_fifteen_minutes(time):
    """Время, кратное 15 минутам.

    Например: 15.37.123456 -> 15.30.00
    """
    return time.replace(minute=time.minute // 15 * 15, second=0, microsecond=0)


def get_next_seven_days(start_from):
    """Следующие семь дней начиная с завтрашнего"""
    return [start_from + dt.timedelta(days=i) for i in range(1, 8)]
