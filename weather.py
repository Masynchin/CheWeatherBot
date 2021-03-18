import datetime as dt

import aiohttp

import const


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
    current = data["current"]

    temp       = _to_temp(current["temp"])
    temp_like  = _to_temp(current["feels_like"])
    wind_speed = current["wind_speed"]
    clouds     = current["clouds"]

    description = current["weather"][0]
    weather_description = description["description"].capitalize()
    weather_type = description["main"]

    message = (
        f"{weather_description}\n\n"
        f"Температура: {temp}\n"
        f"Ощущается как: {temp_like}\n\n"
        f"Ветер: {wind_speed} м/с\n"
        f"Облачность: {clouds}%"
    )

    if wind_gust := current.get("wind_gust"):
        substr = f"Ветер: {wind_speed} м/с\n"
        new_substr = f"Ветер: {wind_speed} м/с (порывы до {wind_gust} м/с)\n"
        message = message.replace(substr, new_substr)

    return message, weather_type


def _to_temp(temp):
    temp = round(temp)
    return f"+{temp}°" if temp > 0 else f"{temp}°"
