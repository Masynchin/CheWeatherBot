"""Модуль с клавиатурами для пользователей.

Содержит все клавиатуры и их команды ('Помощь', 'О рассылке' и т.д.)
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import utils


# команды на клавиатуре, импортируются в main
WEATHER = "Текущая погода \N{glowing star}"
HOUR_FORECAST = "В ближайший час \N{sun behind cloud}"
EXACT_HOUR_FORECAST = "В ... часов \N{cloud}"
TOMORROW_FORECAST = "На завтра \N{umbrella with rain drops}"
EXACT_DAY_FORECAST = "В конкретный день \N{closed umbrella}"
MAILING = "О рассылке \N{postbox}"
HELP = "Помощь \N{books}"


def _create_main_keyboard():
    """Основная клавиатура. Создаётся на месте"""
    buttons = [
        [KeyboardButton(WEATHER), KeyboardButton(HOUR_FORECAST)],
        [
            KeyboardButton(EXACT_HOUR_FORECAST),
            KeyboardButton(TOMORROW_FORECAST),
        ],
        [KeyboardButton(EXACT_DAY_FORECAST)],
        [KeyboardButton(MAILING), KeyboardButton(HELP)],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def _create_hour_choice_keyboard():
    """Inline-клавиатура для выбора часа рассылки. Создаётся на месте"""
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
    """Inline-клавиатура для выбора минуты рассылки. Создаётся на месте"""
    inline_keyboard = InlineKeyboardMarkup()
    minutes = [f"{minute:02}" for minute in range(0, 60, 15)]
    inline_keyboard.row(*[
        InlineKeyboardButton(minute, callback_data=minute)
        for minute in minutes
    ])
    return inline_keyboard


def forecast_hour_choice():
    """Inline-клавиатура для выбора минуты рассылки. Вызывается из main"""
    inline_keyboard = InlineKeyboardMarkup()
    hours = utils.get_next_twelve_hours()
    hours_splitted_by_three_columns = zip(hours[:4], hours[4:8], hours[8:])

    for row in hours_splitted_by_three_columns:
        inline_keyboard.row(*[
            InlineKeyboardButton(
                utils.format_date_as_hour(hour),
                callback_data=hour.timestamp(),
            )
            for hour in row
        ])

    return inline_keyboard


def forecast_day_choice():
    """Inline-клавиатура для выбора дня рассылки. Вызывается из main"""
    inline_keyboard = InlineKeyboardMarkup()
    for day in utils.get_next_seven_days():
        text = utils.format_date_as_day(day)
        timestamp = day.timestamp()
        button = InlineKeyboardButton(text, callback_data=timestamp)
        inline_keyboard.row(button)

    return inline_keyboard


main = _create_main_keyboard()
hour_choice = _create_hour_choice_keyboard()
minute_choice = _create_minute_choice_keyboard()
