import os
from urllib.parse import urlencode


URL = "https://api.openweathermap.org/data/2.5/onecall?" + urlencode({
    "lat": 59.09,
    "lon": 37.91,
    "appid": os.getenv("WEATHER_API_KEY"),
    "units": "metric",
    "exclude": "minutely",
    "lang": "ru",
})


# NOFF значит "not official", сделан не командой художников Telegram
# NAM  значит "not animated"

STICKERS = {
    "Clouds": (
        "CAACAgIAAxkBAAO6X6qd5_H2c0Y2-BVG8SNOyr49K7UAAhd3AAKezgsAAasT8H7jMjQUHgQ",  # NOFF
    ),
    "Rain": (
        "CAACAgIAAxkBAAOkX6lhlZV6aMKJ14jLAAG8waq9xvneAAI9AQACMNSdERD3ygdxko_uHgQ",
        "CAACAgIAAxkBAAOnX6lig43GAz5okVxxdCFi4ds_z6MAArIBAAJWnb0KODnd6BWt4QYeBA",
        "CAACAgIAAxkBAAO3X6qakjSAMKWGE9K9PvstMnVbQ7kAAgx3AAKezgsAAdl0EAUWfhaRHgQ",  # NOFF
    ),
    "Snow": (
        "CAACAgIAAxkBAAOoX6linckMdNC_cnxvBc5qTuxN-p0AAgkBAAJWnb0K1mZcg9c_qB0eBA",
        "CAACAgIAAxkBAAOrX6ljHh_ISPAqu5PznXRgf9-n6UgAAtgAAzDUnRGZmYKVaEQuKh4E",
        "CAACAgIAAxkBAAOwX6qSn6XFcpKHEpg9gCcy3Wh1sEAAAh93AAKezgsAAXtRCiVhuD3PHgQ",  # NOFF
    ),
    "Hot": (
        "CAACAgIAAxkBAAOpX6lixA0F4Afu__6YqbNzDl3S3lIAAlUAA61lvBSgZXBhikQl4R4E",
        "CAACAgIAAxkBAAOyX6qS6UhjpQ1DMyLjM_njdRTni0gAAiJ3AAKezgsAAeVLCR2h1FcJHgQ",  # NOFF
        "CAACAgIAAxkBAAO1X6qTOBAijWiQ2WKMKs6VdVwxyc8AAiZ3AAKezgsAAa9M0LmacOK0HgQ",  # NOFF
    ),
    "Thunder": (
        "CAACAgIAAxkBAAOqX6li4HA16-5vftTMAat63iObFTMAAqsAAzDUnRHOX5OAFZJfkR4E",
        "CAACAgIAAxkBAAO2X6qZ5aSwur3pLf1Wi-lmBy99mwUAAg13AAKezgsAASRlrppXpQ5XHgQ",  # NOFF
    ),
}

UNDEFINED_WEATHER_STICKER = (
    "CAACAgIAAxkBAAOvX6qShv5X4ZSPVo01Si0F4EEDNQYAAiN3AAKezgsAAXvV5IAzLNuCHgQ"  # NOFF
)
MAINTAINCE_STICKER = (
    "CAACAgIAAxkBAAOzX6qTAfXKDu2AHZeIsvL5hOqaOjQAAid3AAKezgsAAbn1MA3HuSrzHgQ"  # NOFF
)


class MissingSaveDict(dict):
    """
    Если попался тип погоды, для которого нет стикера - отправляем дефолтный и
    записываем данный тип погоды в файлик
    """

    def __missing__(self, key):
        with open("undefined_weather_types.txt", "a") as file:
            file.write(f"\n{key}")
        return (UNDEFINED_WEATHER_STICKER,)


STICKERS = MissingSaveDict(STICKERS)


WEATHER = "Текущая погода \N{glowing star}"
HOUR_FORECAST = "В ближайший час \N{sun behind cloud}"
TOMORROW_FORECAST = "На завтра \N{cloud}"
MAILING = "О рассылке \N{open mailbox with raised flag}"
HELP = "Помощь \N{books}"

WELCOME_TEXT = (
    "Это бот, позволяющий получить информацию о погоде в Череповце\n\n"
    "Этой командой (/start) вам выдаётся клавиатура, "
    "на которой расположены основные команды:\n\n"
    f"*{WEATHER}* - позволяет получить данные о текущей погоде\n"
    f"*{HOUR_FORECAST}* - позволяет получить прогноз погоды на ближайший час\n"
    f"*{TOMORROW_FORECAST}* - позволяет получить прогноз погоды на завтра\n"
    f"*{MAILING}* - позволяет узнать о подписке на ежедневный прогноз погоды\n"
    f"*{HELP}* - поможет разобраться с управлением"
)

INFO_TEXT = (
    "Бот, позволяющий получить погоду Череповца\n\n"
    "Основные функции бота:\n"
    f"*{WEATHER}* - получить текущую погоду\n"
    f"*{HOUR_FORECAST}* - получить прогноз погоды на ближайший час\n"
    f"*{TOMORROW_FORECAST}* - получить прогноз погоды на завтра\n"
    f"*{MAILING}* - получить информацию о рассылке\n\n"
    "Эти команды расположены на клавиатуре, "
    "которую бот выдаёт при вводе команды /start. "
    "Если у вас её нет, то нажмите на эту команду"
)

USER_IN_SUBSCRIBE = (
    "Вы зарегистрированы в подписке\n"
    "Ваше время - {}:{:02}\n\n"
    "Поменять время - /change_time_mailing\n"
    "Отказаться от подписки - /cancel_mailing"
)

USER_NOT_IN_SUBSCRIBE = (
    "Вас нет в подписке\n\n"
    "Вы можете подписаться на неё по команде /subscribe_to_mailing"
)

WEATHER_TEXT = (
    "{weather_description}\n\n"
    "Температура: {temp}\n"
    "Ощущается как: {feels_like}\n\n"
    "Ветер: {wind_speed}\n"
    "Влажность: {humidity}\n"
    "Облачность: {cloudiness}"
)

WEATHER_TEXT_WITH_WIND_GUST = WEATHER_TEXT.replace(
    "Ветер: {wind_speed}", "Ветер: {wind_speed} (порывы до {wind_gust})")

DAILY_FORECAST_TEXT = (
    "Утром: {morn_temp} (ощущается как {morn_feels_like})\n"
    "Днём: {day_temp} (ощущается как {day_feels_like})\n"
    "Вечером: {eve_temp} (ощущается как {eve_feels_like})\n"
    "Ночью: {night_temp} (ощущается как {night_feels_like})\n\n"
    "Минимальная температура: {min_temp}, максимальная: {max_temp}\n\n"
    "Ветер: {wind_speed}\n"
    "Влажность: {humidity}\n"
    "Облачность: {cloudiness}"
)

DAILY_FORECAST_TEXT_WITH_WIND_GUST = DAILY_FORECAST_TEXT.replace(
    "Ветер: {wind_speed}", "Ветер: {wind_speed} (порывы до {wind_gust})")

ALERT_TEXT = "⚠ {event} ({description})"
