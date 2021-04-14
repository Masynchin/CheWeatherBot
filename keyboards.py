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
MAILING = "О рассылке \N{open mailbox with raised flag}"
HELP = "Помощь \N{books}"


def _create_main_keyboard():
    """Основная клавиатура. Создаётся на месте"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        KeyboardButton(WEATHER),
        KeyboardButton(HOUR_FORECAST),
    )
    keyboard.row(
        KeyboardButton(EXACT_HOUR_FORECAST),
        KeyboardButton(TOMORROW_FORECAST),
    )
    keyboard.row(
        KeyboardButton(MAILING),
        KeyboardButton(HELP),
    )
    return keyboard


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
        InlineKeyboardButton(minute, callback_data=minute) for minute in minutes
    ])
    return inline_keyboard


def forecast_hour_choice():
    """Inline-клавиатура для выбора минуты рассылки. Вызывается из main"""
    start_time = utils.get_current_time()
    start_time = utils.round_time_by_hours(start_time)

    inline_keyboard = InlineKeyboardMarkup()
    hours = utils.get_next_twelve_hours(start_time)
    for row in zip(hours[:4], hours[4:8], hours[8:]):
        row = [InlineKeyboardButton(b, callback_data=b) for b in row]
        inline_keyboard.row(*row)

    return inline_keyboard


main = _create_main_keyboard()
hour_choice = _create_hour_choice_keyboard()
minute_choice = _create_minute_choice_keyboard()
