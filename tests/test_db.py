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
async def test_new_subscriber():
    db = Subscribers()

    await db.new_subscriber(subscriber_id=0, mailing_time=mailing_time)

    assert await db.is_user_in_subscription(user_id=0)
    assert (
        await db.get_subscriber_mailing_time(subscriber_id=0) == mailing_time
    )
    assert len(await db.get_subscribers_by_mailing_time(mailing_time)) == 1

    await db.delete_subscriber(subscriber_id=0)


@pytest.mark.asyncio
async def test_change_subscriber_time():
    db = Subscribers()

    await db.new_subscriber(subscriber_id=0, mailing_time=mailing_time)
    assert (
        await db.get_subscriber_mailing_time(subscriber_id=0) == mailing_time
    )

    new_mailing_time = dt.time(hour=19, minute=45)
    await db.change_subscriber_mailing_time(
        subscriber_id=0, new_mailing_time=new_mailing_time
    )
    assert (
        await db.get_subscriber_mailing_time(subscriber_id=0)
        == new_mailing_time
    )

    await db.delete_subscriber(subscriber_id=0)


@pytest.mark.asyncio
async def test_delete_subscriber():
    db = Subscribers()

    before = await db.get_subscribers_by_mailing_time(mailing_time)
    await db.new_subscriber(subscriber_id=0, mailing_time=mailing_time)

    await db.delete_subscriber(subscriber_id=0)
    after = await db.get_subscribers_by_mailing_time(mailing_time)

    assert before == after
