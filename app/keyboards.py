"""Модуль с клавиатурами для пользователей.

Содержит все клавиатуры и их команды ('Помощь', 'О рассылке' и т.д.)
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from more_itertools import chunked

from app import utils
from app.che import CheDatetime


# команды на клавиатуре, импортируются в main
WEATHER = "Текущая погода \N{glowing star}"
HOUR_FORECAST = "В ближайший час \N{sun behind cloud}"
EXACT_HOUR_FORECAST = "В ... часов \N{cloud}"
TOMORROW_FORECAST = "На завтра \N{umbrella with rain drops}"
EXACT_DAY_FORECAST = "В конкретный день \N{closed umbrella}"
MAILING = "О рассылке \N{postbox}"
HELP = "Помощь \N{books}"


class MainKeyboard(ReplyKeyboardMarkup):
    """Основная клавиатура"""

    def __init__(self):
        super().__init__([
            [KeyboardButton(WEATHER), KeyboardButton(HOUR_FORECAST)],
            [
                KeyboardButton(EXACT_HOUR_FORECAST),
                KeyboardButton(TOMORROW_FORECAST),
            ],
            [KeyboardButton(EXACT_DAY_FORECAST)],
            [KeyboardButton(MAILING), KeyboardButton(HELP)],
        ], resize_keyboard=True)


class HourChoiceKeyboard(InlineKeyboardMarkup):
    """Inline-клавиатура для выбора часа рассылки"""

    def __init__(self):
        hours = range(6, 24)
        buttons = [HourButton(hour) for hour in hours]
        rows = chunked(buttons, 3)
        super().__init__(inline_keyboard=rows)


class HourButton(InlineKeyboardButton):
    """Кнопка клавиатуры выбора часа"""

    def __init__(self, hour):
        super().__init__(f"{hour:02}", callback_data=f"{hour:02}")


class MinuteChoiceKeyboard(InlineKeyboardMarkup):
    """Inline-клавиатура для выбора минуты рассылки"""

    def __init__(self):
        minutes = range(0, 60, 15)
        buttons = [MinuteButton(minute) for minute in minutes]
        super().__init__(inline_keyboard=[buttons])


class MinuteButton(InlineKeyboardButton):
    """Кнопка клавиатуры выбора минуты"""

    def __init__(self, minute):
        super().__init__(f"{minute:02}", callback_data=f"{minute:02}")


class ForecastHourChoice(InlineKeyboardMarkup):
    """Inline-клавиатура для выбора минуты рассылки"""

    def __init__(self, start_from):
        hours = utils.get_next_twelve_hours(start_from)
        buttons = [ForecastHourButton(hour) for hour in hours]
        rows = chunked(buttons, 3)
        super().__init__(inline_keyboard=rows)

    @classmethod
    def current(cls):
        return cls(CheDatetime.current())


class ForecastHourButton(InlineKeyboardButton):
    def __init__(self, hour):
        super().__init__(f"{hour:%H:%M}", callback_data=hour.timestamp())


class ForecastDayChoice(InlineKeyboardMarkup):
    """Inline-клавиатура для выбора дня рассылки. Вызывается из main"""

    def __init__(self, start_from):
        days = utils.get_next_seven_days(start_from)
        buttons = [ForecastDayButton(day) for day in days]
        rows = chunked(buttons, 1)
        super().__init__(inline_keyboard=rows)

    @classmethod
    def current(cls):
        return cls(CheDatetime.current())


class ForecastDayButton(InlineKeyboardButton):
    def __init__(self, day):
        super().__init__(
            utils.format_date_as_day(day), callback_data=day.timestamp()
        )
