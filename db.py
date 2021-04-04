import asyncio

from sqlalchemy import Column, Integer, Time
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import exists
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select

import config


engine = create_async_engine(config.DATABASE_URL)
Base = declarative_base()


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True)
    mailing_time = Column(Time, nullable=False)


async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession)


async def new_subscriber(subscriber_id, mailing_time):
    async with async_session() as session:
        subscriber = Subscriber(id=subscriber_id, mailing_time=mailing_time)
        session.add(subscriber)
        await session.commit()


async def change_subscriber_mailing_time(subscriber_id, new_mailing_time):
    async with async_session() as session:
        subscriber = await session.get(Subscriber, subscriber_id)
        subscriber.mailing_time = new_mailing_time
        await session.commit()


async def delete_subscriber(subscriber_id):
    async with async_session() as session:
        subscriber = await session.get(Subscriber, subscriber_id)
        await session.delete(subscriber)
        await session.commit()


async def get_subscribers_by_mailing_time(mailing_time):
    async with async_session() as session:
        statement = select(Subscriber)\
            .where(Subscriber.mailing_time == mailing_time)
        subscribers = await session.execute(statement)
        return subscribers.scalars().all()


async def is_user_in_subscription(user_id):
    async with async_session() as session:
        subscriber = await session.get(Subscriber, user_id)
        return subscriber is not None


async def get_subscriber_mailing_time(subscriber_id):
    async with async_session() as session:
        subscriber = await session.get(Subscriber, subscriber_id)
        return subscriber.mailing_time


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


loop = asyncio.get_event_loop()
loop.run_until_complete(create_db())
