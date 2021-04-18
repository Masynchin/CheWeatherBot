"""Модуль для получения погоды с сайта данных о погоде"""

import aiohttp
from async_lru import alru_cache

import config
import utils
from weather_classes import WeatherResponse


async def get_current_weather():
    """Получение текущей погоды - сводка и её тип (ясно, облачно и т.п.)"""
    weather = await get_weather()
    return (weather.current_weather(), weather.current_weather_type())


async def get_hourly_forecast():
    """
    Получение прогноза на час -
    сводка и тип погоды (ясно, облачно и т.п.)
    """
    weather = await get_weather()
    return (weather.houry_forecast(), weather.houry_forecast_type())


async def get_exact_hour_forecast(hour):
    """
    Получение прогноза в конкретный час -
    сводка и тип погоды (ясно, облачно и т.п.)
    """
    weather = await get_weather()
    return (
        weather.exact_hour_forecast(hour),
        weather.exact_hour_forecast_type(hour)
    )


async def get_daily_forecast():
    """Получение прогноза на день - сводка и его тип (ясно, облачно и т.п.)"""
    weather = await get_weather()
    return (weather.daily_forecast(), weather.daily_forecast_type())


async def get_exact_day_forecast(day):
    """
    Получение прогноза в конкретный день -
    сводка и тип погоды (ясно, облачно и т.п.)
    """
    weather = await get_weather()
    return (
        weather.exact_day_forecast(day),
        weather.exact_day_forecast_type(day)
    )


async def get_weather():
    """Кеширование результатов погоды раз в 5 минут.

    Функция вызывает _get_weather() но с аргументом времени, по которому
    происходит кеширование результата ответа погодного сервера
    """
    now = utils.get_current_time()
    time = (now.hour, now.minute // 5 * 5)
    return await _get_weather(time)


@alru_cache(maxsize=1)
async def _get_weather(time):
    """Получение прогноза погода в виде экземляра WeatherResponse"""
    async with aiohttp.ClientSession() as session:
        async with session.get(config.WEATHER_API_URL) as response:
            data = await response.json()
            return WeatherResponse(**data)
