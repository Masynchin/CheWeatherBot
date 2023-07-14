import asyncio
import datetime as dt

from app import mailing
from app import utils
from app.che import CheDatetime
from app.times import MailingDatetimes, SleepBetween


class MailingTask:
    """Рассылка"""

    def __init__(self, weather, times):
        self.weather = weather
        self.times = times

    @classmethod
    def with_interval(cls, weather, start, delta):
        """С переданным интервалом"""
        return cls(weather, SleepBetween(MailingDatetimes(start, delta)))

    @classmethod
    def default(cls, weather):
        """Со значениями по умолчанию"""
        return cls.with_interval(
            weather,
            utils.round_time_by_fifteen_minutes(CheDatetime.current()),
            dt.timedelta(minutes=15)
        )

    def run(self, bot):
        """Добавляем асинхронную рассылку в основной event loop"""
        asyncio.create_task(mailing.mailing(bot, self.weather, self.times))
