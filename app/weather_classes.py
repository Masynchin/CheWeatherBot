"""Модуль с классом обработки ответа с погодного сервера.

Содержит основной класс - WeatherResponse, который преобразует JSON ответ API
в python-структуру.

Ссылка на пример ответа API:
https://openweathermap.org/api/one-call-api#example
"""

import datetime as dt
from string import ascii_letters
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class WeatherDescription(BaseModel):
    """Представление описания погоды.

    Структура в API:
    {
      "main": str  ("Clouds", "Rain", ...)
      "description": str  ("few clouds", ...)
      ...
    }
    """

    main: str
    description: str

    @validator("description")
    def capitalize_description(cls, description):
        """Добавляем заглавную букву в поле `description`"""
        return description.capitalize()


def _decorate_temp(temp: float) -> str:
    """Превращаем численное значение температуры в строку.

    -10 -> "-10°"
    10 -> "+10°"
    """
    return f"+{temp}°" if temp > 0 else f"{temp}°"


class BaseWeather(BaseModel):
    """Базовое представление погоды.

    Базовый класс представления погоды, от которого наследуются конкретные
    для своего времени представления (представление для текущей погоды,
    дневной погоды и т.д.).

    Структура в API:
    {
      "dt": int (UTC timestamp) (1618317040, ...)
      "humidity": int  (62, ...)
      "clouds": int  (0, ...)
      "wind_speed": float  (6.0, ...)
      "wind_gust": float?  (10.2, ...)
      "weather": [WeatherDescription]
      ...
    }
    """

    timestamp: dt.datetime = Field(alias="dt")
    humidity: int
    cloudiness: int = Field(alias="clouds")
    wind_speed: float
    wind_gust: Optional[float] = None
    weather_type: List[WeatherDescription] = Field(alias="weather")

    @validator("wind_speed", "wind_gust")
    def decorate_temperate(cls, wind):
        """Превращаем численное значение скорости ветра в строку.

        10.2 -> "10.2 м/с"
        """
        return f"{wind} м/с"

    @validator("cloudiness", "humidity")
    def decorate_percentage(cls, percentage):
        """Превращаем численное значение процентов в строку.

        10 -> "10%"
        """
        return f"{percentage}%"

    @validator("weather_type")
    def first_element_from_list(cls, weather_type):
        """Используем только первое описание погоды.

        Достаём из массива значений поля `weather_type` (алиас к `weather`)
        только первый элемент
        """
        return weather_type[0]


class Weather(BaseWeather):
    """Представление погоды.

    Структура в API:
    {
      ...
      "temp": float  (20.72, ...)
      "feels_like": float  (19.33, ...)
      ...
    }
    """

    temp: float
    feels_like: float

    _decorate_temp = validator("temp", "feels_like", allow_reuse=True)(
        _decorate_temp
    )


class DailyTemperature(BaseModel):
    """Представление действительной температуры для дневной погоды.

    Структура в API:
    {
      "day": float  (26.78, ...)
      "min": float  (13.92, ...)
      "max": float  (27.49, ...)
      "night": float  (16.78, ...)
      "eve": float  (25.41, ...)
      "morn": float  (18.2, ...)
    }
    """

    morn_temp: float = Field(alias="morn")
    day_temp: float = Field(alias="day")
    eve_temp: float = Field(alias="eve")
    night_temp: float = Field(alias="night")
    min_temp: float = Field(alias="min")
    max_temp: float = Field(alias="max")

    _decorate_temp = validator(
        "morn_temp",
        "day_temp",
        "eve_temp",
        "night_temp",
        "min_temp",
        "max_temp",
        allow_reuse=True,
    )(_decorate_temp)


class DailyFeelsLike(BaseModel):
    """Представление ощущаемой температуры для дневной погоды.

    Структура в API:
    {
      "day": float  (26.75, ...)
      "night": float  (15.85, ...)
      "eve": float  (25.02, ...)
      "morn": float  (18.24, ...)
    }
    """

    morn_feels_like: float = Field(alias="morn")
    day_feels_like: float = Field(alias="day")
    eve_feels_like: float = Field(alias="eve")
    night_feels_like: float = Field(alias="night")

    _decorate_temp = validator(
        "morn_feels_like",
        "day_feels_like",
        "eve_feels_like",
        "night_feels_like",
        allow_reuse=True,
    )(_decorate_temp)


class DailyWeather(BaseWeather):
    """Представление дневной погоды.

    Структура в API:
    {
      ...
      "temp": DailyTemperature
      "feels_like": DailyFeelsLike
      ...
    }
    """

    temp: DailyTemperature
    feels_like: DailyFeelsLike


class Alert(BaseModel):
    """Представление предупреждения.

    Структура в API:
    {
      "event": str  ("Ветер", ...)
      "description": str  ("местами порывы 15-20 м/с", ...)
      ...
    }
    """

    event: str
    description: str


def _is_english_alert(alert):
    """Написано ли предупреждение на английском"""
    return bool(set(alert.event) & set(ascii_letters))


class WeatherResponse(BaseModel):
    """Класс, преобразующий ответ с погодного сайта в python-структуру.

    Предназначен для получения сводки погоды/прогноза в виде текста.
    Предоставляет числовые данные - температура, ветренность, облачность,
    влажность и скорость ветра. Также выдаёт предупреждения, если таковые есть
    """

    current: Weather
    hourly: List[Weather]
    daily: List[DailyWeather]
    alerts: List[Alert] = None

    @validator("alerts")
    def filter_alerts(cls, alerts):
        """Оставляем только предупрежденя написанные на русском"""
        if alerts is None:
            return []
        return [alert for alert in alerts if not _is_english_alert(alert)]
