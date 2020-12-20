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


def new_subscriber(id, time):
    minutes = _to_minutes(time)
    with open_db() as cursor:
        cursor.execute("INSERT INTO subscribers VALUES (?,?)", (id, minutes))


def change_subscriber(id, new_time):
    minutes = _to_minutes(new_time)
    with open_db() as cursor:
        cursor.execute("UPDATE subscribers SET minutes = ? WHERE id = ?", (minutes, id))


def delete_subscriber(id):
    with open_db() as cursor:
        cursor.execute("DELETE FROM subscribers WHERE id = ?", (id,))


def get_by_time(time):
    minutes = _to_minutes(time)
    with open_db() as cursor:
        res = cursor.execute(
            "SELECT id FROM subscribers WHERE minutes = ?", (minutes,)
        ).fetchall()
    return map(lambda id: id[0], res)


def is_user_in_db(id):
    with open_db() as cursor:
        res = cursor.execute(
            "SELECT id FROM subscribers WHERE id = ?", (id,)
        ).fetchone()
    return bool(res)


def get_subscriber_time(id):
    with open_db() as cursor:
        minutes = cursor.execute(
            "SELECT minutes FROM subscribers WHERE id = ?", (id,)
        ).fetchone()[0]
    time = _from_minutes(minutes)
    return time


def _to_minutes(time):
    return time[0] * 60 + time[1]


def _from_minutes(minutes):
    hours = minutes // 60
    minutes -= hours * 60
    return (hours, minutes)


def _init_db():
    with open(os.path.join("db", "createdb.sql")) as f, open_db() as cursor:
        sql = f.read()
        cursor.executescript(sql)


def check_db_exists():
    """Инициализация БД, если её не существует"""
    with open_db() as cursor:
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='subscribers'"
        )
        table_exists = cursor.fetchall()
        if not table_exists:
            _init_db()


check_db_exists()
