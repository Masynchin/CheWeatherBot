import json
from random import choice


def _load_stickers():
    with open("stickers.json", encoding="u8") as f:
        return json.load(f)


STICKERS = _load_stickers()

UNDEFINED_WEATHER_STICKER = STICKERS["undefinedWeatherSticker"]
MAINTAINCE_STICKER = STICKERS["maintainceSticker"]
STICKERS = STICKERS["weatherTypes"]


def get_by_weather(weather_type):
    if weather_type not in STICKERS:
        _log_undefined_weather_type(weather_type)
        return UNDEFINED_WEATHER_STICKER
    return choice(STICKERS[weather_type])


def _log_undefined_weather_type(weather_type):
    with open("undefined_weather_types.txt", "a") as f:
        f.write(f"\n{key}")
