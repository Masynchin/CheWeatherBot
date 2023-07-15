"""Классы времени для Череповца"""

import datetime as dt

import pytz


class CheDatetime(dt.datetime):
    """Датавремя в Череповце"""

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

    def date(self):
        """Дата времени"""
        return CheDate.from_date(super().date())

    def until(self, other):
        """Получаем количество секунд до времени в будущем"""
        return (other - self).total_seconds()


class CheDate(dt.date):
    """Дата в Череповце"""

    @classmethod
    def from_date(cls, date):
        """Создание класса из dt.date"""
        return cls(date.year, date.month, date.day)

    @classmethod
    def from_ordinal(cls, ordinal):
        """Создание класса по номеру в грегорианском календаре"""
        return cls.from_date(dt.date.fromordinal(int(ordinal)))

    def ordinal(self):
        """Номер в григорианском календаре"""
        return self.toordinal()

    def format(self):
        """Представление в виде 'день - дд.мм'"""
        return self.strftime(f"{self.weekday()} - %d.%m")

    def weekday(self):
        """День недели"""
        return [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье",
        ][super().weekday()]
