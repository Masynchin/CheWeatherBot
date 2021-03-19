import datetime as dt

import aiohttp

import const
from weather_classes import WeatherResponse


async def current_weather():
    weather = await get_weather()
    return (weather.current_weather(), weather.current_weather_type())


async def hourly_forecast():
    weather = await get_weather()
    return (weather.houry_forecast(), weather.houry_forecast_type())


async def daily_forecast():
    weather = await get_weather()
    return (weather.daily_forecast(), weather.daily_forecast_type())


async def get_weather():
    """Кеширование результатов погоды раз в 5 минут"""
    now = dt.datetime.now()
    time = (now.hour, now.minute // 5 * 5)
    return await _get_weather(time)


def cached(old_weather):
    cached_dict = {}

    async def cached_weather(time):
        cached_forecast = cached_dict.get(time)
        if cached_forecast:
            return cached_forecast
        else:
            cached_dict.clear()

            new_forecast = await old_weather()
            cached_dict[time] = new_forecast
            return new_forecast

    return cached_weather


@cached
async def _get_weather():
    async with aiohttp.ClientSession() as session:
        async with session.get(const.URL) as response:
            data = await response.json()
            return WeatherResponse(**data)
