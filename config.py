import os


BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

URL = (
    "https://api.openweathermap.org/data/2.5/onecall?"
    "lat={lat}&lon={lon}&appid={key}&units=metric&exclude={exclude}&lang={lang}".format(
        lat=59.09, lon=37.91, key=WEATHER_API_KEY, exclude="minutely,daily", lang="ru"
    )
)


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

# NOFF значит "not official", сделан не командой художников Telegram
# NAM  значит "not animated"

UNDEFINED_STICKER = (
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
        return (UNDEFINED_STICKER,)


STICKERS = MissingSaveDict(STICKERS)


WEATHER = "Погода \N{sun behind cloud}"
MAILING = "О рассылке \N{open mailbox with raised flag}"
HELP = "Помощь \N{books}"
