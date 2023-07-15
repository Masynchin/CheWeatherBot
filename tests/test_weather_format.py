import asyncio
import copy
import json
import datetime as dt

import pytest
from async_lru import alru_cache

from app.weather import OwmWeather
from app.weather_classes import WeatherResponse


class FakeApi:
    @alru_cache
    async def __call__(self):
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
async def test_no_exceptions_at_format(timestamp):
    weather = OwmWeather(FakeApi())

    forecasts = await asyncio.gather(
        weather.current(),
        weather.hourly(timestamp),
        weather.daily(timestamp),
    )

    for forecast in forecasts:
        forecast.format()


@pytest.mark.asyncio
async def test_templates_depends_on_wind_gust_existence(timestamp):
    weather = OwmWeather(FakeApi())

    forecasts = await asyncio.gather(
        weather.current(),
        weather.hourly(timestamp),
        weather.daily(timestamp),
    )

    for forecast in forecasts:
        with_wind_gust = copy.deepcopy(forecast)
        with_wind_gust.forecast.wind_gust = 10.0

        without_wind_gust = copy.deepcopy(forecast)
        without_wind_gust.forecast.wind_gust = None

        assert without_wind_gust.format() != with_wind_gust.format()


@pytest.mark.asyncio
async def test_stickers(timestamp):
    weather = OwmWeather(FakeApi())

    forecasts = await asyncio.gather(
        weather.current(),
        weather.hourly(timestamp),
        weather.daily(timestamp),
    )

    for forecast in forecasts:
        with_wind_gust = copy.deepcopy(forecast)
        with_wind_gust.forecast.wind_gust = 10.0

        without_wind_gust = copy.deepcopy(forecast)
        without_wind_gust.forecast.wind_gust = None

        assert without_wind_gust.format() != with_wind_gust.format()
