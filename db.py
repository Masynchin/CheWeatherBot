from contextlib import contextmanager
import os.path
import sqlite3


@contextmanager
def open_db():
    try:
        db_name = os.path.join("db", "subscribers.db")
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        yield cursor
    finally:
        conn.commit()
        conn.close()


def new_subscriber(user_id, time):
    minutes = _to_minutes(time)
    with open_db() as cursor:
        cursor.execute(
            "INSERT INTO subscribers VALUES (?,?)", (user_id, minutes))


def change_subscriber(user_id, new_time):
    minutes = _to_minutes(new_time)
    with open_db() as cursor:
        cursor.execute(
            "UPDATE subscribers SET minutes = ? WHERE id = ?", (minutes, user_id))


def delete_subscriber(user_id):
    with open_db() as cursor:
        cursor.execute("DELETE FROM subscribers WHERE id = ?", (user_id,))


def get_by_time(time):
    minutes = _to_minutes(time)
    with open_db() as cursor:
        res = cursor.execute(
            "SELECT id FROM subscribers WHERE minutes = ?", (minutes,)
        ).fetchall()
    return map(lambda user_id: user_id[0], res)


def is_user_in_db(user_id):
    with open_db() as cursor:
        res = cursor.execute(
            "SELECT id FROM subscribers WHERE id = ?", (user_id,)
        ).fetchone()
    return bool(res)


def get_subscriber_time(user_id):
    with open_db() as cursor:
        minutes = cursor.execute(
            "SELECT minutes FROM subscribers WHERE id = ?", (user_id,)
        ).fetchone()[0]
    time = _from_minutes(minutes)
    return time


def _to_minutes(time):
    return time[0] * 60 + time[1]


def _from_minutes(minutes):
    return divmod(minutes, 60)


def check_db_exists():
    """Инициализация БД, если её не существует"""
    with open_db() as cursor, open("db/createdb.sql") as f:
        cursor.execute(f.read())


check_db_exists()
