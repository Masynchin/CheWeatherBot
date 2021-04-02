from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


WEATHER = "Текущая погода \N{glowing star}"
HOUR_FORECAST = "В ближайший час \N{sun behind cloud}"
TOMORROW_FORECAST = "На завтра \N{cloud}"
MAILING = "О рассылке \N{open mailbox with raised flag}"
HELP = "Помощь \N{books}"


def _create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton(WEATHER))
    keyboard.row(
        KeyboardButton(HOUR_FORECAST),
        KeyboardButton(TOMORROW_FORECAST)
    )
    keyboard.row(
        KeyboardButton(MAILING),
        KeyboardButton(HELP),
    )
    return keyboard


def _create_hour_choice_keyboard():
    inline_keyboard = InlineKeyboardMarkup()
    hours = [f"{hour:02}" for hour in range(24)]
    for i in range(0, 24, 6):
        buttons = [
            InlineKeyboardButton(hour, callback_data=hour)
            for hour in hours[i:i+6]
        ]
        inline_keyboard.row(*buttons)
    return inline_keyboard


def _create_minute_choice_keyboard():
    inline_keyboard = InlineKeyboardMarkup()
    minutes = [f"{minute:02}" for minute in range(0, 60, 15)]
    inline_keyboard.row(*[
        InlineKeyboardButton(minute, callback_data=minute) for minute in minutes
    ])
    return inline_keyboard


main = _create_main_keyboard()
hour_choice = _create_hour_choice_keyboard()
minute_choice = _create_minute_choice_keyboard()
