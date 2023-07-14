"""Модуль для работы с временем рассылки"""

import asyncio

from more_itertools import iterate
from placeholder import _

from app.che import CheDatetime


class MailingDatetimes:
    """Поток времени рассылки"""

    def __init__(self, start, delta):
        self.start = start
        self.delta = delta

    def __iter__(self):
        return iterate(_ + self.delta, self.start)


class SleepBetween:
    """Поток времени рассылки, выдающий его только при наступлении"""

    def __init__(self, origin):
        self.origin = origin

    async def __aiter__(self):
        """Выдаём время рассылки, только когда оно наступит"""
        for mailing_time in self.origin:
            await asyncio.sleep(CheDatetime.current().until(mailing_time))
            yield mailing_time
