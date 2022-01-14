import datetime as dt

from app import mailing


def test_iterate_mailing_time_starts_from_next_fifteen():
    base = dt.datetime(2000, 1, 1, 7, 30, 0)
    starts_from = (
        base + dt.timedelta(seconds=100),
        base + dt.timedelta(milliseconds=1),
        base + dt.timedelta(minutes=15) - dt.timedelta(milliseconds=1),
    )
    expected = dt.datetime.combine(base, dt.time(7, 45, 0))

    for start_from in starts_from:
        assert next(mailing.iterate_mailing_time(start_from)) == expected


def test_iterate_mailing_time_step_always_same():
    expected = dt.timedelta(minutes=15)
    starts_from = (
        dt.datetime(2000, 1, 1, 7, 30, 0),
        dt.datetime(2000, 1, 1, 23, 45, 0),
    )

    for start_from in starts_from:
        gen = mailing.iterate_mailing_time(start_from)
        start = next(gen)
        next_ = next(gen)
        assert (next_ - start) == expected
