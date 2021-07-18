import datetime as dt
import sys

sys.path.insert(0, "app")

import pytest

import db


mailing_time = dt.time(hour=18, minute=45)


@pytest.mark.asyncio
async def test_new_subscriber():
    await db.new_subscriber(subscriber_id=0, mailing_time=mailing_time)

    assert await db.is_user_in_subscription(user_id=0)
    assert (
        await db.get_subscriber_mailing_time(subscriber_id=0) == mailing_time
    )
    assert len(await db.get_subscribers_by_mailing_time(mailing_time)) == 1

    await db.delete_subscriber(subscriber_id=0)


@pytest.mark.asyncio
async def test_change_subscriber_time():
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
    subscribers_before_new = await db.get_subscribers_by_mailing_time(
        mailing_time
    )
    await db.new_subscriber(subscriber_id=0, mailing_time=mailing_time)

    await db.delete_subscriber(subscriber_id=0)
    subscribers_after_delete = await db.get_subscribers_by_mailing_time(
        mailing_time
    )

    assert subscribers_before_new == subscribers_after_delete
