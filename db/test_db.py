import sys
sys.path.insert(0, "")  # cause of `db` folder and `db` module

import pytest

import db


time = (18, 45)
minutes = 18 * 60 + 45


def test_correct_time_convert():
    assert db._to_minutes(time) == minutes
    assert db._from_minutes(minutes) == time


@pytest.mark.asyncio
async def test_new_subscriber():
    await db.new_subscriber(subscriber_id=0, time=time)

    assert await db.is_user_in_subscription(user_id=0)
    assert await db.get_subscriber_time(subscriber_id=0) == time
    assert len(await db.get_subscribers_by_time(time)) == 1

    await db.delete_subscriber(subscriber_id=0)


@pytest.mark.asyncio
async def test_change_subscriber_time():
    await db.new_subscriber(subscriber_id=0, time=time)
    assert await db.get_subscriber_time(subscriber_id=0) == time

    new_time = (19, 45)
    await db.change_subscriber_time(subscriber_id=0, new_time=new_time)
    assert await db.get_subscriber_time(subscriber_id=0) == new_time

    await db.delete_subscriber(subscriber_id=0)


@pytest.mark.asyncio
async def test_delete_subscriber():
    subscribers_before_new = await db.get_subscribers_by_time(time)
    await db.new_subscriber(subscriber_id=0, time=time)

    await db.delete_subscriber(subscriber_id=0)
    subscribers_after_delete = await db.get_subscribers_by_time(time)

    assert subscribers_before_new == subscribers_after_delete
