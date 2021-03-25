import os

from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import exists


engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///db/subscribers.db"))
Base = declarative_base()


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True)
    minutes = Column(Integer, nullable=False)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def new_subscriber(subscriber_id, time):
    minutes = _to_minutes(time)
    with Session() as session:
        subscriber = Subscriber(id=subscriber_id, minutes=minutes)
        session.add(subscriber)
        session.commit()


def change_subscriber_time(subscriber_id, new_time):
    minutes = _to_minutes(new_time)
    with Session() as session:
        subscriber = session.query(Subscriber).get(subscriber_id)
        subscriber.minutes = minutes
        session.commit()


def delete_subscriber(subscriber_id):
    with Session() as session:
        subscriber = session.query(Subscriber).get(subscriber_id)
        session.delete(subscriber)
        session.commit()


def get_subscribers_by_time(time):
    minutes = _to_minutes(time)
    with Session() as session:
        subscribers = session.query(Subscriber)\
            .filter(Subscriber.minutes == minutes).all()
        return subscribers


def is_user_in_subscription(user_id):
    with Session() as session:
        is_exists = session.query(
            exists().where(Subscriber.id == user_id)).scalar()
        return is_exists


def get_subscriber_time(subscriber_id):
    with Session() as session:
        subscriber = session.query(Subscriber).get(subscriber_id)
        minutes = subscriber.minutes
        return _from_minutes(minutes)


def _to_minutes(time):
    hours, minutes = time
    return hours * 60 + minutes


def _from_minutes(minutes):
    return divmod(minutes, 60)
