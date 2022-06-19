import datetime as dt

from app.times import MailingDatetimes


def test_mailing_times_same_delta():
    delta = dt.timedelta(minutes=15)
    starts = (
        dt.datetime(2000, 1, 1, 7, 30, 0),
        dt.datetime(2000, 1, 1, 23, 45, 0),
    )

    for start in starts:
        mailing_times = iter(MailingDatetimes(start, delta))
        first = next(mailing_times)
        second = next(mailing_times)
        assert (second - first) == delta
