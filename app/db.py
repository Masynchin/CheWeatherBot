"""База данных подписчиков"""

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

class Subscribers:
    """БД с подписчиками"""

    def __init__(self, session):
        self.session = session

    async def add(self, user_id, mailing_time):
        """Регистрация в БД нового подписчика рассылки"""
        subscriber = Subscriber(id=user_id, mailing_time=mailing_time)
        self.session.add(subscriber)
        await self.session.commit()

    async def new_time(self, user_id, new_mailing_time):
        """Меняем время рассылки подписчика"""
        subscriber = await self.session.get(Subscriber, user_id)
        subscriber.mailing_time = new_mailing_time
        await self.session.commit()

    async def delete(self, user_id):
        """Удаление подписчика из БД"""
        subscriber = await self.session.get(Subscriber, user_id)
        await self.session.delete(subscriber)
        await self.session.commit()

    async def of_time(self, mailing_time):
        """Все подписчики с данным временем рассылки"""
        statement = select(Subscriber).where(
            Subscriber.mailing_time == mailing_time
        )
        subscribers = await self.session.execute(statement)
        return subscribers.scalars().all()

    async def exists(self, user_id):
        """Проверяем наличие пользователя в подписке"""
        subscriber = await self.session.get(Subscriber, user_id)
        return subscriber is not None

    async def time(self, user_id):
        """Время рассылки данного подписчика"""
        subscriber = await self.session.get(Subscriber, user_id)
        return subscriber.mailing_time


async def create_db():
    """Инициализируем БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
