"""Модуль для получения погоды с сайта данных о погоде"""

import time

import aiohttp
from async_lru import alru_cache

from app import config
from app import templates
from app import utils
from app.weather_classes import WeatherResponse


async def get_current_weather():
    """Получение текущей погоды - сводка и её тип (ясно, облачно и т.п.)"""
    weather = await get_weather()
    template = (
        templates.WEATHER_WITH_WIND_GUST
        if weather.current.wind_gust is not None
        else templates.WEATHER
    )
    return _get_forecast_info(weather.current, template, weather.alerts)


async def get_hourly_forecast():
    """
    Получение прогноза на час -
    сводка и тип погоды (ясно, облачно и т.п.)
    """
    weather = await get_weather()
    forecast = _get_next_forecast(weather.hourly)
    template = (
        templates.WEATHER_WITH_WIND_GUST
        if forecast.wind_gust is not None
        else templates.WEATHER
    )
    return _get_forecast_info(forecast, template, weather.alerts)


def _get_next_forecast(forecasts):
    """Получение данных о погоде в следующее время.

    Используется для получения прогноза на следующий час или следующий день
    """
    now = utils.get_current_time()
    future_forecasts = filter(lambda f: f.timestamp > now, forecasts)
    nearest_forecast = min(future_forecasts, key=lambda f: f.timestamp)
    return nearest_forecast


async def get_exact_hour_forecast(hour):
    """
    Получение прогноза в конкретный час -
    сводка и тип погоды (ясно, облачно и т.п.)
    """
    weather = await get_weather()
    forecast = _get_exact_hour_forecast(weather.hourly, hour)
    template = (
        templates.WEATHER_WITH_WIND_GUST
        if forecast.wind_gust is not None
        else templates.WEATHER
    )
    return _get_forecast_info(forecast, template, weather.alerts)


def _get_exact_hour_forecast(forecasts, hour):
    """Получение данных о прогнозе погоды в конкретный час"""
    for forecast in forecasts:
        if forecast.timestamp == hour:
            return forecast


async def get_daily_forecast():
    """Получение прогноза на день - сводка и его тип (ясно, облачно и т.п.)"""
    weather = await get_weather()
    forecast = _get_next_forecast(weather.daily)
    template = (
        templates.DAILY_FORECAST_WITH_WIND_GUST
        if forecast.wind_gust is not None
        else templates.DAILY_FORECAST
    )
    return _get_forecast_info(forecast, template, weather.alerts)


async def get_exact_day_forecast(day):
    """
    Получение прогноза в конкретный день -
    сводка и тип погоды (ясно, облачно и т.п.)
    """
    weather = await get_weather()
    forecast = _get_exact_day_forecast(weather.daily, day)
    template = (
        templates.DAILY_FORECAST_WITH_WIND_GUST
        if forecast.wind_gust is not None
        else templates.DAILY_FORECAST
    )
    return _get_forecast_info(forecast, template, weather.alerts)


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


def _get_forecast_info(forecast, template, alerts):
    """Получение текстовой сводки погоды и её тип"""
    text = template.format(forecast=forecast) + _generate_alert_text(alerts)
    weather_type = forecast.weather_type.main
    return text, weather_type


def _generate_alert_text(alerts):
    """Генерация текста с предупреждениями"""
    if not alerts:
        return ""

    return "\n\n" + "\n".join(
        templates.ALERT.format(alert=alert) for alert in alerts
    )
