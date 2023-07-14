"""Модуль для получения погоды с сайта данных о погоде"""

import time
from urllib.parse import urlencode

import aiohttp
from async_lru import alru_cache

from app.forecasts import CurrentForecast, DailyForecast, HourlyForecast
from app.weather_classes import WeatherResponse


class OwmWeather:
    """Погода с OpenWeatherMap"""

    def __init__(self, url, cache_time):
        self.url = url
        self.cache_time = cache_time

    @classmethod
    def default(cls, url):
        return cls(url, cache_time=300)

    @classmethod
    def from_geo(cls, lat, lon, api_key):
        url = "https://api.openweathermap.org/data/2.5/onecall?" + urlencode({
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric",
            "exclude": "minutely",
            "lang": "ru",
        })
        return cls.default(url)

    @classmethod
    def for_che(cls, api_key):
        return cls.from_geo(lat=59.09, lon=37.91, api_key=api_key)

    async def weather(self):
        """Кешированная погода с OpenWeatherMap"""
        return await _get_weather(self.url, time.time() // self.cache_time)

    async def current(self):
        """Получение текущей погоды - сводка и её тип (ясно, облачно и т.п.)"""
        weather = await self.weather()
        return CurrentForecast(weather.current, weather.alerts)

    async def hourly(self, timestamp):
        """
        Получение прогноза на час -
        сводка и тип погоды (ясно, облачно и т.п.)
        """
        weather = await self.weather()
        forecast = _next(weather.hourly, timestamp)
        return HourlyForecast(forecast, weather.alerts)

    async def exact_hour(self, hour):
        """
        Получение прогноза в конкретный час -
        сводка и тип погоды (ясно, облачно и т.п.)
        """
        weather = await self.weather()
        forecast = _exact_hour(weather.hourly, hour)
        return HourlyForecast(forecast, weather.alerts)

    async def daily(self, timestamp):
        """Получение прогноза на день - сводка и его тип (ясно, облачно и т.п.)"""
        weather = await self.weather()
        forecast = _next(weather.daily, timestamp)
        return DailyForecast(forecast, weather.alerts)

    async def exact_day(self, day):
        """
        Получение прогноза в конкретный день -
        сводка и тип погоды (ясно, облачно и т.п.)
        """
        weather = await self.weather()
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


@alru_cache(maxsize=1)
async def _get_weather(url, time):
    """Получение прогноза погода в виде экземляра WeatherResponse"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return WeatherResponse(**data)
