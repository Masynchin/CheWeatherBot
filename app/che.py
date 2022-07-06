"""Модуль для работы со временем Череповца"""

import datetime as dt

import pytz


class CheDatetime(dt.datetime):
    """Время в Череповце"""

    @classmethod
    def from_dt(cls, date):
        """Создание класса из dt.datetime"""
        return cls(
            date.year,
            date.month,
            date.day,
            date.hour,
            date.minute,
            date.second,
            date.microsecond,
            date.tzinfo,
        )

    @classmethod
    def current(cls):
        """Текущее время по Москве (часовой пояс Череповца)"""
        return cls.from_dt(dt.datetime.now(pytz.timezone("Europe/Moscow")))

    @classmethod
    def from_timestamp(cls, timestamp):
        """Перевод таймштампа из JSON'а колбэка в CheDatetime

        Например: '16892286320.0' -> CheDatetime(...)
        """
        return cls.from_dt(
            dt.datetime.fromtimestamp(
                int(float(timestamp)), pytz.timezone("Europe/Moscow")
            )
        )

    def until(self, other):
        """Получаем количество секунд до времени в будущем"""
        return (other - self).total_seconds()
