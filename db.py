import asyncio
import os

from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import exists
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select


database_url = os.getenv(
    "DATABASE_URL", "sqlite+aiosqlite:///db/subscribers.db")
engine = create_async_engine(database_url)
Base = declarative_base()


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True)
    minutes = Column(Integer, nullable=False)


async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession)


async def new_subscriber(subscriber_id, time):
    minutes = _to_minutes(time)
    async with async_session() as session:
        subscriber = Subscriber(id=subscriber_id, minutes=minutes)
        session.add(subscriber)
        await session.commit()


async def change_subscriber_time(subscriber_id, new_time):
    minutes = _to_minutes(new_time)
    async with async_session() as session:
        subscriber = await session.get(Subscriber, subscriber_id)
        subscriber.minutes = minutes
        await session.commit()


async def delete_subscriber(subscriber_id):
    async with async_session() as session:
        subscriber = await session.get(Subscriber, subscriber_id)
        await session.delete(subscriber)
        await session.commit()


async def get_subscribers_by_time(time):
    minutes = _to_minutes(time)
    async with async_session() as session:
        statement = select(Subscriber).where(Subscriber.minutes == minutes)
        subscribers = await session.execute(statement)
        return subscribers.scalars().all()


async def is_user_in_subscription(user_id):
    async with async_session() as session:
        subscriber = await session.get(Subscriber, user_id)
        return subscriber is not None


async def get_subscriber_time(subscriber_id):
    async with async_session() as session:
        subscriber = await session.get(Subscriber, subscriber_id)
        minutes = subscriber.minutes
        return _from_minutes(minutes)


def _to_minutes(time):
    hours, minutes = time
    return hours * 60 + minutes


def _from_minutes(minutes):
    return divmod(minutes, 60)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


loop = asyncio.get_event_loop()
loop.run_until_complete(create_db())
