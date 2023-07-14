"""Модуль для получения погоды с сайта данных о погоде"""

import time

import aiohttp
from async_lru import alru_cache

from app import config
from app.forecasts import CurrentForecast, DailyForecast, HourlyForecast
from app.weather_classes import WeatherResponse


class OwmWeather:
    """Погода с OpenWeatherMap"""

    async def current(self):
        """Получение текущей погоды - сводка и её тип (ясно, облачно и т.п.)"""
        weather = await get_weather()
        return CurrentForecast(weather.current, weather.alerts)

    async def hourly(self, timestamp):
        """
        Получение прогноза на час -
        сводка и тип погоды (ясно, облачно и т.п.)
        """
        weather = await get_weather()
        forecast = _next(weather.hourly, timestamp)
        return HourlyForecast(forecast, weather.alerts)

    async def exact_hour(self, hour):
        """
        Получение прогноза в конкретный час -
        сводка и тип погоды (ясно, облачно и т.п.)
        """
        weather = await get_weather()
        forecast = _exact_hour(weather.hourly, hour)
        return HourlyForecast(forecast, weather.alerts)

    async def daily(self, timestamp):
        """Получение прогноза на день - сводка и его тип (ясно, облачно и т.п.)"""
        weather = await get_weather()
        forecast = _next(weather.daily, timestamp)
        return DailyForecast(forecast, weather.alerts)

    async def exact_day(self, day):
        """
        Получение прогноза в конкретный день -
        сводка и тип погоды (ясно, облачно и т.п.)
        """
        weather = await get_weather()
        forecast = _exact_day(weather.daily, day)
        return DailyForecast(forecast, weather.alerts)


def _next(forecasts, timestamp):
    """Получение данных о погоде в следующее время.

    Используется для получения прогноза на следующий час или следующий день
    """
    future_forecasts = filter(lambda f: f.timestamp > timestamp, forecasts)
    nearest_forecast = min(future_forecasts, key=lambda f: f.timestamp)
    return nearest_forecast


def _exact_hour(forecasts, hour):
    """Получение данных о прогнозе погоды в конкретный час"""
    for forecast in forecasts:
        if forecast.timestamp == hour:
            return forecast


def _exact_day(forecasts, day):
    """Получение данных о прогнозе на конкретный день"""
    for forecast in forecasts:
        if forecast.timestamp.date() == day:
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
