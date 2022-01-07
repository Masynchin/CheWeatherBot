import pytest

from app.db import create_db


@pytest.fixture(autouse=True)
async def init_db():
    """Инициализация ДБ для каждого теста"""
    await create_db()
    yield
