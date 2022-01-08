"""Модуль для получения погоды с сайта данных о погоде"""

import time

import aiohttp
from async_lru import alru_cache

from app import config
from app.forecasts import CurrentForecast, DailyForecast, HourlyForecast
from app.weather_classes import WeatherResponse


async def get_current_weather():
    """Получение текущей погоды - сводка и её тип (ясно, облачно и т.п.)"""
    weather = await get_weather()
    return CurrentForecast(weather.current, weather.alerts)


async def get_hourly_forecast(timestamp):
    """
    Получение прогноза на час -
    сводка и тип погоды (ясно, облачно и т.п.)
    """
    weather = await get_weather()
    forecast = _get_next_forecast(weather.hourly, timestamp)
    return HourlyForecast(forecast, weather.alerts)


def _get_next_forecast(forecasts, timestamp):
    """Получение данных о погоде в следующее время.

    Используется для получения прогноза на следующий час или следующий день
    """
    future_forecasts = filter(lambda f: f.timestamp > timestamp, forecasts)
    nearest_forecast = min(future_forecasts, key=lambda f: f.timestamp)
    return nearest_forecast


async def get_exact_hour_forecast(hour):
    """
    Получение прогноза в конкретный час -
    сводка и тип погоды (ясно, облачно и т.п.)
    """
    weather = await get_weather()
    forecast = _get_exact_hour_forecast(weather.hourly, hour)
    return HourlyForecast(forecast, weather.alerts)


def _get_exact_hour_forecast(forecasts, hour):
    """Получение данных о прогнозе погоды в конкретный час"""
    for forecast in forecasts:
        if forecast.timestamp == hour:
            return forecast


async def get_daily_forecast(timestamp):
    """Получение прогноза на день - сводка и его тип (ясно, облачно и т.п.)"""
    weather = await get_weather()
    forecast = _get_next_forecast(weather.daily, timestamp)
    return DailyForecast(forecast, weather.alerts)


async def get_exact_day_forecast(day):
    """
    Получение прогноза в конкретный день -
    сводка и тип погоды (ясно, облачно и т.п.)
    """
    weather = await get_weather()
    forecast = _get_exact_day_forecast(weather.daily, day)
    return DailyForecast(forecast, weather.alerts)


def _get_exact_day_forecast(forecasts, day):
    """Получение данных о прогнозе на конкретный день"""
    for forecast in forecasts:
        if forecast.timestamp.date() == day.date():
            return forecast


async def get_weather():
    """Кеширование результатов погоды раз в 5 минут.

    Функция вызывает _get_weather() но с аргументом времени, по которому
    происходит кеширование результата ответа погодного сервера
    """
    return await _get_weather(time.time() // 300)


@alru_cache(maxsize=1)
async def _get_weather(time):
    """Получение прогноза погода в виде экземляра WeatherResponse"""
    async with aiohttp.ClientSession() as session:
        async with session.get(config.WEATHER_API_URL) as response:
            data = await response.json()
            return WeatherResponse(**data)
