"""Модуль с классом обработки ответа с погодного сервера.

Содержит основной класс - WeatherResponse, которий используется
для получения сводки погоды в виде текста
"""

import datetime as dt
from string import ascii_letters
from typing import List, Optional

from pydantic import BaseModel, Field, validator

import templates


class WeatherDescription(BaseModel):
    main: str
    description: str

    @validator("description")
    def capitalize_description(cls, description):
        return description.capitalize()


def _decorate_temp(temp: float) -> str:
    return f"+{temp}°" if temp > 0 else f"{temp}°"


class BaseWeather(BaseModel):
    timestamp: dt.datetime = Field(alias="dt")
    humidity: int
    cloudiness: int = Field(alias="clouds")
    wind_speed: float
    wind_gust: Optional[float] = None
    weather_type: List[WeatherDescription] = Field(alias="weather")

    @validator("wind_speed", "wind_gust")
    def decorate_temperate(cls, wind):
        return f"{wind} м/с"

    @validator("cloudiness", "humidity")
    def decorate_percentage(cls, percentage):
        return f"{percentage}%"

    @validator("weather_type")
    def first_element_from_list(cls, weather_type):
        return weather_type[0]


class Weather(BaseWeather):
    temp: float
    feels_like: float

    _decorate_temp = validator(
        "temp", "feels_like", allow_reuse=True)(_decorate_temp)


class DailyTemperature(BaseModel):
    morn_temp: float = Field(alias="morn")
    day_temp: float = Field(alias="day")
    eve_temp: float = Field(alias="eve")
    night_temp: float = Field(alias="night")
    min_temp: float = Field(alias="min")
    max_temp: float = Field(alias="max")

    _decorate_temp = validator("morn_temp", "day_temp", "eve_temp",
        "night_temp", "min_temp", "max_temp", allow_reuse=True)(_decorate_temp)


class DailyFeelsLike(BaseModel):
    morn_feels_like: float = Field(alias="morn")
    day_feels_like: float = Field(alias="day")
    eve_feels_like: float = Field(alias="eve")
    night_feels_like: float = Field(alias="night")

    _decorate_temp = validator("morn_feels_like", "day_feels_like",
        "eve_feels_like", "night_feels_like", allow_reuse=True)(_decorate_temp)


class DailyWeather(BaseWeather):
    temp: DailyTemperature
    feels_like: DailyFeelsLike


class Alert(BaseModel):
    event: str
    description: str


def _is_english_alert(alert):
    return bool(set(alert.event) & set(ascii_letters))


class WeatherResponse(BaseModel):
    """Класс, преобразующий ответ с погодного сайта в удобный формат.

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
        if alerts is None:
            return []
        return [alert for alert in alerts if not _is_english_alert(alert)]

    def current_weather(self):
        text = (templates.WEATHER_WITH_WIND_GUST
            if self.current.wind_gust is not None else templates.WEATHER)

        return text.format(
            **self.current.weather_type.dict(),
            **self.current.dict()
        ) + self._generate_alert_text()

    def current_weather_type(self):
        return self.current.weather_type.main

    def houry_forecast(self):
        forecast = self._get_nearest_hour_forecast()
        text = (templates.WEATHER_WITH_WIND_GUST
            if forecast.wind_gust is not None else templates.WEATHER)

        return text.format(
            **forecast.weather_type.dict(),
            **forecast.dict()
        ) + self._generate_alert_text()

    def houry_forecast_type(self):
        forecast = self._get_nearest_hour_forecast()
        return forecast.weather_type.main

    def _get_nearest_hour_forecast(self):
        now = dt.datetime.now(dt.timezone.utc)
        future_forecasts = filter(lambda f: f.timestamp > now, self.hourly)
        nearest_forecast = min(future_forecasts, key=lambda f: f.timestamp)
        return nearest_forecast

    def exact_hour_forecast(self, hour):
        forecast = self._get_exact_hour_forecast(hour)
        text = (templates.WEATHER_WITH_WIND_GUST
            if forecast.wind_gust is not None else templates.WEATHER)

        return text.format(
            **forecast.weather_type.dict(),
            **forecast.dict()
        ) + self._generate_alert_text()

    def exact_hour_forecast_type(self, hour):
        forecast = self._get_exact_hour_forecast(hour)
        return forecast.weather_type.main

    def _get_exact_hour_forecast(self, hour):
        forecast = [f for f in self.hourly if f.timestamp.time() == hour][0]
        return forecast

    def daily_forecast(self):
        forecast = self._get_nearest_daily_forecast()
        text = (templates.DAILY_FORECAST_WITH_WIND_GUST
            if forecast.wind_gust is not None else templates.DAILY_FORECAST)

        return text.format(
            **forecast.dict(),
            **forecast.feels_like.dict(),
            **forecast.temp.dict(),
        ) + self._generate_alert_text()

    def daily_forecast_type(self):
        forecast = self._get_nearest_daily_forecast()
        return forecast.weather_type.main

    def _get_nearest_daily_forecast(self):
        now = dt.datetime.now(dt.timezone.utc)
        future_forecasts = filter(lambda f: f.timestamp > now, self.daily)
        nearest_forecast = min(future_forecasts, key=lambda f: f.timestamp)
        return nearest_forecast

    def exact_day_forecast(self, day):
        forecast = self._get_exact_day_forecast(day)
        text = (templates.DAILY_FORECAST_WITH_WIND_GUST
            if forecast.wind_gust is not None else templates.DAILY_FORECAST)

        return text.format(
            **forecast.dict(),
            **forecast.feels_like.dict(),
            **forecast.temp.dict(),
        ) + self._generate_alert_text()

    def exact_day_forecast_type(self, day):
        forecast = self._get_exact_day_forecast(day)
        return forecast.weather_type.main

    def _get_exact_day_forecast(self, day):
        forecast = [f for f in self.daily if f.timestamp.date() == day.date()][0]
        return forecast

    def _generate_alert_text(self):
        if not self.alerts:
            return ""
        return "\n\n" + "\n".join(
            templates.ALERT.format(**alert.dict())
            for alert in self.alerts
        )
