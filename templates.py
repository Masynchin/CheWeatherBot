"""Модуль с текстовыми шаблонами.

Содержит шаблоны для приветствия бота, прогнозов погод,
погодных предпреждений и состояний пользователя по отношению к рассылке
"""

import keyboards


WELCOME = (
    "Это бот, позволяющий получить информацию о погоде в Череповце\n\n"
    "Этой командой (/start) вам выдаётся клавиатура, "
    "на которой расположены основные команды:\n\n"
    f"*{keyboards.WEATHER}* - позволяет получить данные о текущей погоде\n"
    f"*{keyboards.HOUR_FORECAST}* - позволяет получить прогноз погоды на ближайший час\n"
    f"*{keyboards.EXACT_HOUR_FORECAST}* - позволяет получить прогноз погоды "
    "в конкретный час, в пределах следующих 12 часов\n"
    f"*{keyboards.TOMORROW_FORECAST}* - позволяет получить прогноз погоды на завтра\n"
    f"*{keyboards.EXACT_DAY_FORECAST}* - позволяет получить прогноз погоды "
    "в конкретный день, в пределах следующей недели\n"
    f"*{keyboards.MAILING}* - позволяет узнать о подписке на ежедневный прогноз погоды\n"
    f"*{keyboards.HELP}* - поможет разобраться с управлением"
)

INFO = (
    "Бот, позволяющий получить погоду Череповца\n\n"
    "Основные функции бота:\n"
    f"*{keyboards.WEATHER}* - получить текущую погоду\n"
    f"*{keyboards.HOUR_FORECAST}* - получить прогноз погоды на ближайший час\n"
    f"*{keyboards.EXACT_HOUR_FORECAST}* - получить прогноз погоды в конкретный час\n"
    f"*{keyboards.TOMORROW_FORECAST}* - получить прогноз погоды на завтра\n"
    f"*{keyboards.EXACT_DAY_FORECAST}* - получить прогноз погоды в конкретный день\n"
    f"*{keyboards.MAILING}* - получить информацию о рассылке\n\n"
    "Эти команды расположены на клавиатуре, "
    "которую бот выдаёт в ответ на команду /start. "
    "Если у вас её нет, то нажмите на эту команду"
)

USER_IN_MAILING = (
    "Вы зарегистрированы в подписке\n"
    "Ваше время - {}:{:02}\n\n"
    "Поменять время - /change_time_mailing\n"
    "Отказаться от подписки - /cancel_mailing"
)

USER_NOT_IN_MAILING = (
    "Вас нет в подписке\n\n"
    "Вы можете подписаться на неё по команде /subscribe_to_mailing"
)

USER_SUBSCRIBED = "Вы подписались на рассылку по времени {}:{:02}"
USER_CHANGED_MAILING_TIME = "Вы изменили время рассылки на {}:{:02}"

WEATHER = (
    "{forecast.weather_type.description}\n\n"
    "Температура: {forecast.temp}\n"
    "Ощущается как: {forecast.feels_like}\n\n"
    "Ветер: {forecast.wind_speed}\n"
    "Влажность: {forecast.humidity}\n"
    "Облачность: {forecast.cloudiness}"
)

WEATHER_WITH_WIND_GUST = WEATHER.replace(
    "Ветер: {forecast.wind_speed}",
    "Ветер: {forecast.wind_speed} (порывы до {forecast.wind_gust})"
)

DAILY_FORECAST = (
    "{forecast.weather_type.description}\n\n"
    "Утром: {forecast.temp.morn_temp} "
        "(ощущается как {forecast.feels_like.morn_feels_like})\n"
    "Днём: {forecast.temp.day_temp} "
        "(ощущается как {forecast.feels_like.day_feels_like})\n"
    "Вечером: {forecast.temp.eve_temp} "
        "(ощущается как {forecast.feels_like.eve_feels_like})\n"
    "Ночью: {forecast.temp.night_temp} "
        "(ощущается как {forecast.feels_like.night_feels_like})\n\n"
    "Минимальная температура: {forecast.temp.min_temp}, "
        "максимальная: {forecast.temp.max_temp}\n\n"
    "Ветер: {forecast.wind_speed}\n"
    "Влажность: {forecast.humidity}\n"
    "Облачность: {forecast.cloudiness}"
)

DAILY_FORECAST_WITH_WIND_GUST = DAILY_FORECAST.replace(
    "Ветер: {forecast.wind_speed}",
    "Ветер: {forecast.wind_speed} (порывы до {forecast.wind_gust})"
)

ALERT = "⚠ {alert.event} ({alert.description})"

MAILING_MESSAGE = "Ваш ежедневный прогноз \N{smiling face with smiling eyes}\n\n{}"

MAINTAINCE_MESSAGE = "Произошла непредвиденная ошибка. Мастера уже в пути!"
