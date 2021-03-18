import datetime as dt
import re

import aiohttp

import const


async def get_weather():
    """Снаружи вызваем без аргументов, а тут используем кеширование"""
    now = dt.datetime.now()
    hours, minutes = now.hour, now.minute
    minutes = minutes // 5 * 5
    time = (hours, minutes)

    return await _get_weather(time)


def cached(old_weather):
    """Кешируем результаты раз в 5 минут"""
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
    current = data["current"]

    temp       = _to_temp(current["temp"])
    temp_like  = _to_temp(current["feels_like"])
    wind_speed = current["wind_speed"]
    wind_gust  = current.get("wind_gust", wind_speed)
    clouds     = current["clouds"]

    description = current["weather"][0]
    weather_description = description["description"].capitalize()
    weather_type = description["main"]

    pattern = (
        f"{weather_description}\n\n"
        f"Температура: {temp}\n"
        f"Ощущается как: {temp_like}\n\n"
        f"Ветер: {wind_speed} м/с\n"
        f"Облачность: {clouds}%"
    )

    if (wind_gust := current.get("wind_gust")) :
        pattern = re.sub(
            r"(Ветер:.+?м/с)", r"\1" + f" (порывы до {wind_gust} м/с)", pattern
        )
    return pattern, weather_type


def _to_temp(temp):
    temp = round(temp)
    return f"+{temp}°" if temp > 0 else f"{temp}°"
