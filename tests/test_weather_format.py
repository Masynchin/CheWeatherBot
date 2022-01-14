import asyncio
import copy
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


@pytest.mark.asyncio
@patch("app.weather.get_weather", return_value=mock_response())
async def test_no_exceptions_at_format(_mock, timestamp):
    forecasts = await asyncio.gather(
        weather.get_current_weather(),
        weather.get_hourly_forecast(timestamp),
        weather.get_daily_forecast(timestamp),
    )

    for forecast in forecasts:
        forecast.format()


@pytest.mark.asyncio
@patch("app.weather.get_weather", return_value=mock_response())
async def test_templates_depends_on_wind_gust_existence(_mock, timestamp):
    forecasts = await asyncio.gather(
        weather.get_current_weather(),
        weather.get_hourly_forecast(timestamp),
        weather.get_daily_forecast(timestamp),
    )

    for forecast in forecasts:
        with_wind_gust = copy.deepcopy(forecast)
        with_wind_gust.forecast.wind_gust = 10.0

        without_wind_gust = copy.deepcopy(forecast)
        without_wind_gust.forecast.wind_gust = None

        assert without_wind_gust.format() != with_wind_gust.format()


@pytest.mark.asyncio
@patch("app.weather.get_weather", return_value=mock_response())
async def test_stickers(_mock, timestamp):
    forecasts = await asyncio.gather(
        weather.get_current_weather(),
        weather.get_hourly_forecast(timestamp),
        weather.get_daily_forecast(timestamp),
    )

    for forecast in forecasts:
        with_wind_gust = copy.deepcopy(forecast)
        with_wind_gust.forecast.wind_gust = 10.0

        without_wind_gust = copy.deepcopy(forecast)
        without_wind_gust.forecast.wind_gust = None

        assert without_wind_gust.format() != with_wind_gust.format()
