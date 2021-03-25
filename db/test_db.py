import sys
sys.path.insert(0, "")  # cause of `db` folder and `db` module

import pytest

import db


time = (18, 45)
minutes = 18 * 60 + 45


def test_correct_time_convert():
    assert db._to_minutes(time) == minutes
    assert db._from_minutes(minutes) == time


def test_new_subscriber():
    db.new_subscriber(subscriber_id=0, time=time)

    assert db.is_user_in_subscription(user_id=0)
    assert db.get_subscriber_time(subscriber_id=0) == time
    assert len(db.get_subscribers_by_time(time)) == 1

    db.delete_subscriber(subscriber_id=0)


def test_change_subscriber_time():
    db.new_subscriber(subscriber_id=0, time=time)
    assert db.get_subscriber_time(subscriber_id=0) == time

    new_time = (19, 45)
    db.change_subscriber_time(subscriber_id=0, new_time=new_time)

    assert db.get_subscriber_time(subscriber_id=0) == new_time

    db.delete_subscriber(subscriber_id=0)


def test_delete_subscriber():
    subscribers_before_new = db.get_subscribers_by_time(time)
    db.new_subscriber(subscriber_id=0, time=time)

    db.delete_subscriber(subscriber_id=0)
    subscribers_after_delete = db.get_subscribers_by_time(time)

    assert subscribers_before_new == subscribers_after_delete
