"""Стикеры, прикрепляемые к прогнозам погоды.

Все стикеры, разбитые по типу погоды, находятся в файле stickers.json.
Также там находятся стикеры нераспознанной погоды (_UNDEFINED_WEATHER_STICKERS)
и стикер для случая, когда возникла непредвиденная ошибка (MAINTAINCE_STICKER)
"""

import json
from random import choice


def _load_stickers():
    """Загрузка стикеров из stickers.json"""
    with open("stickers.json", encoding="u8") as f:
        return json.load(f)


_STICKERS = _load_stickers()

MAINTAINCE_STICKER = _STICKERS["maintainceSticker"]
_UNDEFINED_WEATHER_STICKERS = _STICKERS["undefinedWeatherStickers"]
_WEATHER_TYPES = _STICKERS["weatherTypes"]


def get_by_weather(weather_type):
    """Случайный стикер по типу погоды, либо стикер нераспознанной погоды"""
    if weather_type not in _WEATHER_TYPES:
        _log_undefined_weather_type(weather_type)
        return choice(_UNDEFINED_WEATHER_STICKERS)
    return choice(_WEATHER_TYPES[weather_type])


def _log_undefined_weather_type(weather_type):
    """Запись типа погоды, для которого нет стикера"""
    with open("undefined_weather_types.txt", "a") as f:
        f.write(f"{weather_type}\n")
