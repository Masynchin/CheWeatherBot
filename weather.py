"""Модуль для получения погоды с сайта данных о погоде"""

import datetime as dt

import aiohttp

import config
from weather_classes import WeatherResponse


async def get_current_weather():
    """Получение текущей погоды - сводка и её тип (ясно, облачно и т.п.)"""
    weather = await get_weather()
    return (weather.current_weather(), weather.current_weather_type())


async def get_hourly_forecast():
    """Получение прогноза на час - сводка и его тип (ясно, облачно и т.п.)"""
    weather = await get_weather()
    return (weather.houry_forecast(), weather.houry_forecast_type())


async def get_daily_forecast():
    """Получение прогноза на день - сводка и его тип (ясно, облачно и т.п.)"""
    weather = await get_weather()
    return (weather.daily_forecast(), weather.daily_forecast_type())


async def get_weather():
    """Кеширование результатов погоды раз в 5 минут.

    Функция вызывает _get_weather() но с аргументом времени, по которому
    происходит кеширование результата ответа погодного сервера
    """
    now = dt.datetime.now()
    time = (now.hour, now.minute // 5 * 5)
    return await _get_weather(time)


def cached(old_weather):
    """Декоратор для кеширования функций _get_weather() по времени"""
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
    """Получение прогноза погода в виде экземляра WeatherResponse"""
    async with aiohttp.ClientSession() as session:
        async with session.get(config.WEATHER_API_URL) as response:
            data = await response.json()
            return WeatherResponse(**data)
