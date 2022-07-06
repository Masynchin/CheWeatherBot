import json
import datetime as dt
from functools import lru_cache
from unittest.mock import patch

import pytest

from app import weather
from app.weather_classes import WeatherResponse


@lru_cache
def mock_response():
    with open("tests/response.json", encoding="u8") as f:
        return WeatherResponse(**json.load(f))


def _create_timestamp(timestamp):
    return dt.datetime.utcfromtimestamp(timestamp).replace(
        tzinfo=dt.timezone.utc
    )


@pytest.fixture
def timestamp():
    # current.dt в response.json
    return _create_timestamp(1641528599)


@pytest.fixture
def hour_timestamp():
    # один из hourly.dt в response.json
    return _create_timestamp(1641535200)


@pytest.fixture
def day_timestamp():
    # один из daily.dt в response.json
    return _create_timestamp(1641632400)


@pytest.mark.asyncio
@patch("app.weather.get_weather", return_value=mock_response())
async def test_same_allerts(_mock, timestamp, hour_timestamp, day_timestamp):
    """
    Все прогнозы относятся к одним данным, поэтому
    предупреждения для всех одинаковы
    """
    current = await weather.current()
    hourly = await weather.hourly(timestamp)
    exact_hour = await weather.exact_hour(hour_timestamp)
    daily = await weather.daily(timestamp)
    exact_day = await weather.exact_day(day_timestamp)

    assert (
        current.alerts
        == hourly.alerts
        == exact_hour.alerts
        == daily.alerts
        == exact_day.alerts
    )
    assert len(current.alerts) == 1

    alert = current.alerts[0]
    assert alert.event == "Гололедно - изморозевое отложение"
    assert alert.description == "местами гололед, на дорогах гололедица"


@pytest.mark.asyncio
@patch("app.weather.get_weather", return_value=mock_response())
async def test_current(_mock):
    forecast = await weather.current()
    forecast_data = forecast.forecast

    assert forecast_data.temp == -9.08
    assert forecast_data.feels_like == -14.51


@pytest.mark.asyncio
@patch("app.weather.get_weather", return_value=mock_response())
async def test_hourly(_mock, timestamp):
    forecast = await weather.hourly(timestamp)
    forecast_data = forecast.forecast

    assert forecast_data.temp == -10.49
    assert forecast_data.feels_like == -15.2


@pytest.mark.asyncio
@patch("app.weather.get_weather", return_value=mock_response())
async def test_exact_hour(_mock, hour_timestamp):
    forecast = await weather.exact_hour(hour_timestamp)
    forecast_data = forecast.forecast

    assert forecast_data.temp == -12.41
    assert forecast_data.feels_like == -17.49


@pytest.mark.asyncio
@patch("app.weather.get_weather", return_value=mock_response())
async def daily(_mock, timestamp):
    forecast = await weather.exact_day(timestamp)
    forecast_data = forecast.forecast

    assert forecast_data.temp.day_temp == -13.89
    assert forecast_data.feels_like.day_feels_like == -19.35


@pytest.mark.asyncio
@patch("app.weather.get_weather", return_value=mock_response())
async def test_exact_day(_mock, day_timestamp):
    forecast = await weather.exact_day(day_timestamp)
    forecast_data = forecast.forecast

    assert forecast_data.temp.day_temp == -15.74
    assert forecast_data.feels_like.day_feels_like == -21.9
