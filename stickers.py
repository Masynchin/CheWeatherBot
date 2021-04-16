"""Модуль со стикерами, прикрепляемыми к прогнозам погоды.

Все стикеры, разбитые по типу погоды, находятся в файле stickers.json.
Также там находится стикер нераспознанной погоды (UNDEFINED_WEATHER_STICKER)
и стикер для ситуаций, когда упал сервер (MAINTAINCE_STICKER)
"""

import json
from random import choice


def _load_stickers():
    """Загрузка стикеров из stickers.json"""
    with open("stickers.json", encoding="u8") as f:
        return json.load(f)


STICKERS = _load_stickers()

UNDEFINED_WEATHER_STICKERS = STICKERS["undefinedWeatherStickers"]
MAINTAINCE_STICKER = STICKERS["maintainceSticker"]
STICKERS = STICKERS["weatherTypes"]


def get_by_weather(weather_type):
    """
    Получаем случайный стикер по типу погоды,
    либо отправляем стикер нераспознанной погоды
    """
    if weather_type not in STICKERS:
        _log_undefined_weather_type(weather_type)
        return choice(UNDEFINED_WEATHER_STICKERS)
    return choice(STICKERS[weather_type])


def _log_undefined_weather_type(weather_type):
    """Запись типа погоды для которого нет стикера"""
    with open("undefined_weather_types.txt", "a") as f:
        f.write(f"{weather_type}\n")
