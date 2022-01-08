"""Модуль, отвещающий за всю работу с базой данных.

Содержит в себе модель подписчика рассылки, а также функции,
отправляющие запросы напрямую в БД
"""

from sqlalchemy import Column, Integer, Time
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, sessionmaker

from app import config


engine = create_async_engine(config.DATABASE_URL)
Base = declarative_base()


class Subscriber(Base):
    """Модель подписчика рассылки"""

    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True)
    mailing_time = Column(Time, nullable=False)


async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def new_subscriber(subscriber_id, mailing_time):
    """Регистрация в БД нового подписчика рассылки"""
    async with async_session() as session:
        subscriber = Subscriber(id=subscriber_id, mailing_time=mailing_time)
        session.add(subscriber)
        await session.commit()


async def change_subscriber_mailing_time(subscriber_id, new_mailing_time):
    """Меняем время рассылки подписчика"""
    async with async_session() as session:
        subscriber = await session.get(Subscriber, subscriber_id)
        subscriber.mailing_time = new_mailing_time
        await session.commit()


async def delete_subscriber(subscriber_id):
    """Удаление подписчика из БД"""
    async with async_session() as session:
        subscriber = await session.get(Subscriber, subscriber_id)
        await session.delete(subscriber)
        await session.commit()


async def get_subscribers_by_mailing_time(mailing_time):
    """Получение всех подписчиков с определённым временем рассылки"""
    async with async_session() as session:
        statement = select(Subscriber).where(
            Subscriber.mailing_time == mailing_time
        )
        subscribers = await session.execute(statement)
        return subscribers.scalars().all()


async def is_user_in_subscription(user_id):
    """Проверяем наличие пользователя в подписке"""
    async with async_session() as session:
        subscriber = await session.get(Subscriber, user_id)
        return subscriber is not None


async def get_subscriber_mailing_time(subscriber_id):
    """Получение времени рассылки конкретного подписчика"""
    async with async_session() as session:
        subscriber = await session.get(Subscriber, subscriber_id)
        return subscriber.mailing_time


async def create_db():
    """Инициализируем БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
