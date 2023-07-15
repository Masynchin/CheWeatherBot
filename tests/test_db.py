import asyncio
import datetime as dt

import pytest

from app.db import Subscribers, create_db


mailing_time = dt.time(hour=18, minute=45)


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
async def init_db():
    """Инициализация ДБ для тестов этого модуля"""
    await create_db()
    yield


@pytest.mark.asyncio
async def test_add():
    db = Subscribers()

    await db.add(subscriber_id=0, mailing_time=mailing_time)

    assert await db.exists(user_id=0)
    assert await db.time(subscriber_id=0) == mailing_time
    assert len(await db.of_time(mailing_time)) == 1

    await db.delete(subscriber_id=0)


@pytest.mark.asyncio
async def test_change_subscriber_time():
    db = Subscribers()

    await db.add(subscriber_id=0, mailing_time=mailing_time)
    assert await db.time(subscriber_id=0) == mailing_time

    new_mailing_time = dt.time(hour=19, minute=45)
    await db.new_time(subscriber_id=0, new_mailing_time=new_mailing_time)
    assert await db.time(subscriber_id=0) == new_mailing_time

    await db.delete(subscriber_id=0)


@pytest.mark.asyncio
async def test_delete():
    db = Subscribers()

    before = await db.of_time(mailing_time)
    await db.add(subscriber_id=0, mailing_time=mailing_time)

    await db.delete(subscriber_id=0)
    after = await db.of_time(mailing_time)

    assert before == after
