import datetime as dt
from typing import List, Optional

import aiohttp
from pydantic import BaseModel, Field, validator

import const


class WeatherDescription(BaseModel):
    main: str
    description: str

    @validator("description")
    def capitalize_description(cls, description):
        return description.capitalize()


class BaseWeather(BaseModel):
    temp: float
    feels_like: float
    humidity: int
    cloudiness: int = Field(alias="clouds")
    wind_speed: float
    wind_gust: Optional[float] = None
    weather_type: List[WeatherDescription] = Field(alias="weather")

    @validator("temp", "feels_like")
    def decorate_temperature(cls, temp):
        return f"+{temp}°" if temp > 0 else f"{temp}°"

    @validator("wind_speed", "wind_gust")
    def decorate_temperate(cls, wind):
        return f"{wind} м/с"

    @validator("cloudiness", "humidity")
    def decorate_percentage(cls, percentage):
        return f"{percentage}%"

    @validator("weather_type")
    def first_element_from_list(cls, weather_type):
        return weather_type[0]

    def as_text(self):
        return (
            f"{self.weather_type.description}\n\n"
            f"Температура: {self.temp}\n"
            f"Ощущается как: {self.feels_like}\n\n"
            f"Ветер: {self.wind_speed}\n" if self.wind_gust is None
                else f"Ветер: {self.wind_speed} (порывы до {self.wind_gust})\n"
            f"Влажность: {self.humidity}\n"
            f"Облачность: {self.cloudiness}"
        )


class CurrentWeather(BaseWeather):
    ...


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
            return _parse_data(data)


def _parse_data(data: dict):
    weather = CurrentWeather(**data["current"])
    return (weather.as_text(), weather.weather_type.main)
