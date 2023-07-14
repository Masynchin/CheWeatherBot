import datetime as dt

from aiogram.filters import (
    Command as CommandFilter,
    StateFilter,
    Text as TextFilter,
)
from aiogram.filters.logic import and_f as And
from aiogram.fsm.state import State, StatesGroup

from app.bot.ext import CallbackRoute, ErrorRoute, MessageRoute
from app import db
from app import keyboards
from app import mailing
from app import stickers
from app import templates
from app.che import CheDate, CheDatetime
from app.logger import logger


# START И ПОМОЩЬ

class Welcome(MessageRoute):
    """Приветсвенное сообщение с клавиатурой и информацией о командах"""

    def __init__(self):
        super().__init__(
            filter=And(CommandFilter("start"), StateFilter(None)),
            handler=self.handle,
        )

    async def handle(self, message):
        await message.answer(
            templates.WELCOME,
            parse_mode="MARKDOWN",
            reply_markup=keyboards.MainKeyboard(),
        )
        logger.info("Пользователь {} выполнил /start", message.from_user.id)


class Info(MessageRoute):
    """Информационное сообщение со всеми основными командами"""

    def __init__(self):
        super().__init__(
            filter=TextFilter(keyboards.HELP), handler=self.handle
        )

    async def handle(self, message):
        await message.answer(templates.INFO, parse_mode="MARKDOWN")


# ПРОГНОЗ

class Weather(MessageRoute):
    """Отправка текущей погоды"""

    def __init__(self, weather):
        self.weather = weather

        super().__init__(
            filter=And(TextFilter(keyboards.WEATHER), StateFilter(None)),
            handler=self.handle,
        )

    async def handle(self, message):
        forecast = await self.weather.current()
        await message.answer_sticker(forecast.sticker())
        await message.answer(forecast.format())
        logger.info(
            "Пользователь {} получил текущую погоду", message.from_user.id
        )


class HourForecast(MessageRoute):
    """Отправка прогноза на следующий час"""

    def __init__(self, weather):
        self.weather = weather

        super().__init__(
            filter=And(TextFilter(keyboards.HOUR_FORECAST), StateFilter(None)),
            handler=self.handle,
        )

    async def handle(self, message):
        timestamp = CheDatetime.current()
        forecast = await self.weather.hourly(timestamp)
        await message.answer_sticker(forecast.sticker())
        await message.answer(forecast.format())
        logger.info(
            "Пользователь {} получил прогноз погоды на час",
            message.from_user.id,
        )


class ChooseForecastHour(StatesGroup):
    """Состояние пользователя при выборе конкретного часа прогноза"""

    hour = State()


class ExactHourForecast(MessageRoute):
    """
    Пользователь нажал на кнопку прогноза в конкретный час.
    Отправляем клавиатуру с двенадцатью ближайшими часами
    """

    def __init__(self):
        super().__init__(
            filter=And(
                TextFilter(keyboards.EXACT_HOUR_FORECAST), StateFilter(None)
            ),
            handler=self.handle,
        )

    async def handle(self, message, state):
        await state.set_state(ChooseForecastHour.hour)
        await message.answer(
            "Выберите час прогноза:",
            reply_markup=keyboards.ForecastHourChoice.current(),
        )


class HandleExactHourForecast(CallbackRoute):
    """Отправка прогноза на час, выбранный пользователем"""

    def __init__(self, weather):
        self.weather = weather
        super().__init__(
            filter=StateFilter(ChooseForecastHour.hour),
            handler=self.handle,
        )

    async def handle(self, call, state):
        await state.clear()

        hour = CheDatetime.from_timestamp(call.data)
        forecast = await self.weather.exact_hour(hour)

        hour = hour.strftime("%H:%M")
        await call.message.edit_text(f"Прогноз на {hour}")
        await call.message.answer_sticker(forecast.sticker())
        await call.message.answer(forecast.format())
        logger.info(
            "Пользователь {} получил прогноз погоды на {} часов",
            call.from_user.id,
            hour,
        )


class DailyForecast(MessageRoute):
    """Отправка прогноза на день"""

    def __init__(self, weather):
        self.weather = weather

        super().__init__(
            filter=And(
                TextFilter(keyboards.TOMORROW_FORECAST), StateFilter(None)
            ),
            handler=self.handle,
        )

    async def handle(self, message):
        timestamp = CheDatetime.current()
        forecast = await self.weather.daily(timestamp)
        await message.answer_sticker(forecast.sticker())
        await message.answer(forecast.format())
        logger.info(
            "Пользователь {} получил прогноз погоды на день",
            message.from_user.id,
        )


class ChooseForecastDay(StatesGroup):
    """Состояние пользователя при выборе конкретного дня прогноза"""

    day = State()


class SendExactDayForecast(MessageRoute):
    """
    Пользователь нажал на кнопку прогноза в конкретный день.
    Отправляем клавиатуру со следующими семью днями
    """

    def __init__(self):
        super().__init__(
            filter=And(
                TextFilter(keyboards.EXACT_DAY_FORECAST), StateFilter(None)
            ),
            handler=self.handle,
        )

    async def handle(self, message, state):
        await state.set_state(ChooseForecastDay.day)
        await message.answer(
            "Выберите день прогноза:",
            reply_markup=keyboards.ForecastDayChoice.current(),
        )


class HandleExactDayForecast(CallbackRoute):
    """Отправка прогноза на день, выбранный пользователем"""

    def __init__(self, weather):
        self.weather = weather

        super().__init__(
            filter=StateFilter(ChooseForecastDay.day),
            handler=self.handle,
        )

    async def handle(self, call, state):
        await state.clear()

        day = CheDate.from_ordinal(call.data)
        forecast = await self.weather.exact_day(day)

        day = day.format()
        await call.message.edit_text(f"Прогноз на {day}")
        await call.message.answer_sticker(forecast.sticker())
        await call.message.answer(forecast.format())
        logger.info(
            "Пользователь {} получил прогноз погоды на {}",
            call.from_user.id,
            day,
        )


# О РАССЫЛКЕ

class MailingInfo(MessageRoute):
    """Отправка информации о подписке пользователя на рассылку.

    Отправляем время рассылки, если зарегистрирован, или шаблон с тем,
    что его нет в рассылке, если его нет в рассылке
    """

    def __init__(self):
        super().__init__(
            filter=And(TextFilter(keyboards.MAILING), StateFilter(None)),
            handler=self.handle,
        )

    async def handle(self, message):
        user_id = message.from_user.id
        mailing_info = await mailing.get_user_mailing_info(user_id)
        await message.answer(mailing_info)


class NewSub(StatesGroup):
    """Состояния пользователя при выборе времени для регистрации в рассылке"""

    hour = State()
    minute = State()


class SubscribeToMailing(MessageRoute):
    """
    Пользователь решил зарегистрироваться в рассылке,
    отправляем клавиатуру с выбором часа рассылки
    """

    def __init__(self):
        super().__init__(
            filter=And(
                CommandFilter("subscribe_to_mailing"), StateFilter(None)
            ),
            handler=self.handle,
        )

    async def handle(self, message, state):
        await state.set_state(NewSub.hour)
        await message.answer(
            "Выберите час:", reply_markup=keyboards.HourChoiceKeyboard()
        )


class SetMailingHour(CallbackRoute):
    """
    После выбора часа рассылки отправляем
    клавиатуру с выбором минуты рассылки
    """

    def __init__(self):
        super().__init__(filter=StateFilter(NewSub.hour), handler=self.handle)

    async def handle(self, call, state):
        await state.update_data(hour=int(call.data))
        await call.message.edit_text(
            "Выберите минуты:", reply_markup=keyboards.MinuteChoiceKeyboard()
        )
        await state.set_state(NewSub.minute)


class SetMinuteMailing(CallbackRoute):
    """Пользователь выбрал час и минуту рассылки, регистрируем его в БД"""

    def __init__(self):
        super().__init__(
            filter=StateFilter(NewSub.minute), handler=self.handle
        )

    async def handle(self, call, state):
        data = await state.get_data()
        user_id = call.from_user.id
        time = dt.time(hour=data["hour"], minute=int(call.data))
        await db.new_subscriber(user_id, time)

        await state.clear()
        await call.message.delete()  # удаляем клавитуру выбора минуты расылки
        await call.message.answer(
            templates.USER_SUBSCRIBED.format(time.hour, time.minute)
        )
        logger.info("Пользователь {} внесён в рассылку", user_id)


class ChangeTime(StatesGroup):
    """Состояния пользователя при изменении времени рассылки"""

    hour = State()
    minute = State()


class ChangeTimeMailing(MessageRoute):
    """
    Пользователь решил поменять время рассылки,
    отправляем клавиатуру с выбором нового часа рассылки
    """

    def __init__(self):
        super().__init__(
            filter=And(
                CommandFilter("change_time_mailing"), StateFilter(None)
            ),
            handler=self.handle,
        )

    async def handle(self, message, state):
        await message.answer(
            "Выберите час:", reply_markup=keyboards.HourChoiceKeyboard()
        )
        await state.set_state(ChangeTime.hour)


class ChangeHourMailing(CallbackRoute):
    """
    После выбора нового часа рассылки отправляем
    клавиатуру с выбором новой минуты рассылки
    """

    def __init__(self):
        super().__init__(
            filter=StateFilter(ChangeTime.hour), handler=self.handle
        )

    async def handle(self, call, state):
        await state.update_data(hour=int(call.data))
        await state.set_state(ChangeTime.minute)
        await call.message.edit_text(
            "Выберите минуты:", reply_markup=keyboards.MinuteChoiceKeyboard()
        )


class ChangeMinuteMailing(CallbackRoute):
    """Пользователь выбрал новые час и минуту рассылки, обновляем его в БД"""

    def __init__(self):
        super().__init__(
            filter=StateFilter(ChangeTime.minute), handler=self.handle
        )

    async def handle(self, call, state):
        data = await state.get_data()
        user_id = call.from_user.id
        time = dt.time(hour=data["hour"], minute=int(call.data))
        await db.change_subscriber_mailing_time(user_id, time)

        await state.clear()
        await call.message.delete()
        await call.message.answer(
            templates.USER_CHANGED_MAILING_TIME.format(time.hour, time.minute),
        )
        logger.info("Пользователь {} изменил время рассылки", user_id)


class CancelMailing(MessageRoute):
    """Пользователь решил отписаться от рассылки, удаляем из БД"""

    def __init__(self):
        super().__init__(
            filter=And(CommandFilter("cancel_mailing"), StateFilter(None)),
            handler=self.handle,
        )

    async def handle(self, message):
        user_id = message.from_user.id
        await db.delete_subscriber(user_id)
        await message.answer("Успешно удалено из подписки")
        logger.info("Пользователь {} удалён из подписки", user_id)


# ОБРАБОТКА ОШИБОК

class Errors(ErrorRoute):
    """Обработка непредвиденных ошибок"""

    def __init__(self):
        super().__init__(filter=(lambda: True), handler=self.handle)

    async def handle(self, update):
        await update.message.answer_sticker(stickers.MAINTAINCE_STICKER)
        await update.message.answer(templates.MAINTAINCE_MESSAGE)
        logger.exception("Произошла непредвиденная ошибка!")
        return True
