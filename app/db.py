"""База данных подписчиков"""

import datetime as dt
import sqlite3

import aiosqlite


def AiosqliteConnection(path):
    """Расширение aiosqlite для поддержки `datetime.time`.
    
    Время подписчика хранится как datetime.time. Sqlite3 не поддерживает
    этот тип. SqlAlchemy под капотом добавляла поддержку, но не aiosqlite.
    Данная процедура оборачивает `aiosqlite.connect`, добавляя адаптер
    и конвертер для `datetime.time`.

    Пример использования:

    - Было:

    ~~~python
    async with aiosqlite.connect(path) as conn: ...
    ~~~

    - Стало:

    ~~~python
    async with AiosqliteConnection(path) as conn: ...
    ~~~
    """
    aiosqlite.register_adapter(dt.time, dt.time.isoformat)
    aiosqlite.register_converter(
        "time", lambda b: dt.time.fromisoformat(b.decode())
    )
    return aiosqlite.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)


class Subscribers:
    """БД с подписчиками"""

    def __init__(self, session):
        self.session = session

    async def add(self, user_id, mailing_time):
        """Регистрация в БД нового подписчика рассылки"""
        await self.session.execute(
            "INSERT INTO subscribers(id, mailing_time) VALUES(?, ?)",
            (user_id, mailing_time),
        )
        await self.session.commit()

    async def new_time(self, user_id, new_mailing_time):
        """Меняем время рассылки подписчика"""
        await self.session.execute(
            "UPDATE subscribers SET mailing_time = ? WHERE id = ?",
            (new_mailing_time, user_id),
        )
        await self.session.commit()

    async def delete(self, user_id):
        """Удаление подписчика из БД"""
        await self.session.execute(
            "DELETE FROM subscribers WHERE id = ?", (user_id,)
        )
        await self.session.commit()

    async def of_time(self, mailing_time):
        """Все подписчики с данным временем рассылки"""
        async with self.session.execute(
            "SELECT * FROM subscribers WHERE mailing_time = ?",
            (mailing_time,),
        ) as cursor:
            return await cursor.fetchall()

    async def exists(self, user_id):
        """Проверяем наличие пользователя в подписке"""
        async with self.session.execute(
            "SELECT * FROM subscribers WHERE id = ?", (user_id,)
        ) as cursor:
            return (await cursor.fetchone()) is not None

    async def time(self, user_id):
        """Время рассылки данного подписчика"""
        async with self.session.execute(
            "SELECT mailing_time FROM subscribers WHERE id = ?", (user_id,)
        ) as cursor:
            return (await cursor.fetchone())[0]


async def create_db(session):
    """Инициализируем БД"""
    await session.execute(
        """
        CREATE TABLE subscribers (
            id INTEGER NOT NULL,
            mailing_time TIME NOT NULL,
            PRIMARY KEY (id)
        );
        """
    )
    await session.commit()
