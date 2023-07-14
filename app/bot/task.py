import asyncio
import datetime as dt

from app import mailing
from app import utils
from app.che import CheDatetime
from app.times import MailingDatetimes, SleepBetween


class MailingTask:
    """Рассылка"""

    def __init__(self, db, weather, times):
        self.db = db
        self.weather = weather
        self.times = times

    @classmethod
    def with_interval(cls, db, weather, start, delta):
        """С переданным интервалом"""
        return cls(db, weather, SleepBetween(MailingDatetimes(start, delta)))

    @classmethod
    def default(cls, db, weather):
        """Со значениями по умолчанию"""
        return cls.with_interval(
            db,
            weather,
            utils.round_time_by_fifteen_minutes(CheDatetime.current()),
            dt.timedelta(minutes=15)
        )

    def run(self, bot):
        """Добавляем асинхронную рассылку в основной event loop"""
        asyncio.create_task(
            mailing.mailing(bot, self.db, self.weather, self.times)
        )
