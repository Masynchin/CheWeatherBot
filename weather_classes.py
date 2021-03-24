import datetime as dt
from string import ascii_letters
from typing import List, Optional

from pydantic import BaseModel, Field, validator

import const


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
    morn: float
    day: float
    eve: float
    night: float
    min_temp: float = Field(alias="min")
    max_temp: float = Field(alias="max")

    _decorate_temp = validator("morn", "day", "eve", "night",
        "min_temp", "max_temp", allow_reuse=True)(_decorate_temp)


class DailyFeelsLike(BaseModel):
    morn: float
    day: float
    eve: float
    night: float

    _decorate_temp = validator(
        "morn", "day", "eve", "night", allow_reuse=True)(_decorate_temp)


class DailyWeather(BaseWeather):
    temp: DailyTemperature
    feels_like: DailyFeelsLike


class Alert(BaseModel):
    event: str
    description: str


def _is_english_alert(alert):
    return bool(set(alert.event) & set(ascii_letters))


class WeatherResponse(BaseModel):
    current: Weather
    hourly: List[Weather]
    daily: List[DailyWeather]
    alerts: List[Alert]

    @validator("alerts")
    def filter_alerts(cls, alerts):
        return [alert for alert in alerts if not _is_english_alert(alert)]

    def current_weather(self):
        text = (const.WEATHER_TEXT_WITH_WIND_GUST
            if self.current.wind_gust is not None else const.WEATHER_TEXT)
        return text.format(
            weather_description=self.current.weather_type.description,
            temp=self.current.temp,
            feels_like=self.current.feels_like,
            wind_speed=self.current.wind_speed,
            wind_gust=self.current.wind_gust,
            humidity=self.current.humidity,
            cloudiness=self.current.cloudiness,
        ) + self._generate_alert_text()

    def current_weather_type(self):
        return self.current.weather_type.main

    def houry_forecast(self):
        forecast = self._get_nearest_hour_forecast()
        text = (const.WEATHER_TEXT_WITH_WIND_GUST
            if forecast.wind_gust is not None else const.WEATHER_TEXT)
        return text.format(
            weather_description=forecast.weather_type.description,
            temp=forecast.temp,
            feels_like=forecast.feels_like,
            wind_speed=forecast.wind_speed,
            wind_gust=forecast.wind_gust,
            humidity=forecast.humidity,
            cloudiness=forecast.cloudiness,
        ) + self._generate_alert_text()

    def houry_forecast_type(self):
        forecast = self._get_nearest_hour_forecast()
        return forecast.weather_type.main

    def _get_nearest_hour_forecast(self):
        now = dt.datetime.now(dt.timezone.utc)
        future_forecasts = filter(lambda f: f.timestamp > now, self.hourly)
        nearest_forecast = min(future_forecasts, key=lambda f: f.timestamp)
        return nearest_forecast

    def daily_forecast(self):
        forecast = self._get_nearest_daily_forecast()
        text = (const.DAILY_FORECAST_TEXT_WITH_WIND_GUST
            if forecast.wind_gust is not None else const.DAILY_FORECAST_TEXT)
        return text.format(
            morn_temp=forecast.temp.morn,
            morn_feels_like=forecast.feels_like.morn,
            day_temp=forecast.temp.day,
            day_feels_like=forecast.feels_like.day,
            eve_temp=forecast.temp.eve,
            eve_feels_like=forecast.feels_like.eve,
            night_temp=forecast.temp.night,
            night_feels_like=forecast.feels_like.night,
            min_temp=forecast.temp.min_temp,
            max_temp=forecast.temp.max_temp,
            wind_speed=forecast.wind_speed,
            wind_gust=forecast.wind_gust,
            humidity=forecast.humidity,
            cloudiness=forecast.cloudiness,
        ) + self._generate_alert_text()

    def daily_forecast_type(self):
        forecast = self._get_nearest_daily_forecast()
        return forecast.weather_type.main

    def _get_nearest_daily_forecast(self):
        now = dt.datetime.now(dt.timezone.utc)
        future_forecasts = filter(lambda f: f.timestamp > now, self.daily)
        nearest_forecast = min(future_forecasts, key=lambda f: f.timestamp)
        return nearest_forecast

    def _generate_alert_text(self):
        if not self.alerts:
            return ""
        return "\n\n" + "\n".join(
            const.ALERT_TEXT.format(
                event=alert.event,
                description=alert.description,
            )
            for alert in self.alerts
        )
