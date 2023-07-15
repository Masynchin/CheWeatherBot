import asyncio
import datetime as dt

import pytest
import pytest_asyncio

from app.db import Subscribers, async_session, create_db


mailing_time = dt.time(hour=18, minute=45)


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def session():
    """Инициализация ДБ для тестов этого модуля"""
    async with async_session() as session:
        await create_db()
        yield session


@pytest.mark.asyncio
async def test_add(session):
    db = Subscribers(session)

    await db.add(user_id=0, mailing_time=mailing_time)

    assert await db.exists(user_id=0)
    assert await db.time(user_id=0) == mailing_time
    assert len(await db.of_time(mailing_time)) == 1

    await db.delete(user_id=0)


@pytest.mark.asyncio
async def test_change_subscriber_time(session):
    db = Subscribers(session)

    await db.add(user_id=0, mailing_time=mailing_time)
    assert await db.time(user_id=0) == mailing_time

    new_mailing_time = dt.time(hour=19, minute=45)
    await db.new_time(user_id=0, new_mailing_time=new_mailing_time)
    assert await db.time(user_id=0) == new_mailing_time

    await db.delete(user_id=0)


@pytest.mark.asyncio
async def test_delete(session):
    db = Subscribers(session)

    before = await db.of_time(mailing_time)
    await db.add(user_id=0, mailing_time=mailing_time)

    await db.delete(user_id=0)
    after = await db.of_time(mailing_time)

    assert before == after
