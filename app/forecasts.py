"""Модуль с классами прогноза погоды"""

from app import stickers
from app import templates


class BaseForecast:
    """Базовый класс прогноза погоды.

    Содержит общие функции для получение прогноза в виде текста и стикер,
    характеризующий тип погоды.

    Наследуемые классы должны реализовать метод `get_template()`
    """

    def __init__(self, forecast, alerts):
        self.forecast = forecast
        self.alerts = alerts

    def format(self):
        """Получаем прогноз в текстовом виде.

        Этот текст отправляется пользователю
        """
        template = self.get_template()
        return template.format(forecast=self.forecast) + _format_alerts(
            self.alerts
        )

    def get_sticker(self):
        """Получаем стикер, отражающий тип погоды.

        Этот стикер отправляется вместе с сообщением прогноза
        """
        weather_type = self.forecast.weather_type.main
        return stickers.get_by_weather(weather_type)


class CurrentForecast(BaseForecast):
    """Прогноз текущей погоды"""

    def get_template(self):
        """Выбираем шаблон в зависимости от наличия данных о порыве ветра"""
        return (
            templates.WEATHER_WITH_WIND_GUST
            if self.forecast.wind_gust is not None
            else templates.WEATHER
        )


class HourlyForecast(BaseForecast):
    """Прогноз погоды в конкретный час"""

    def get_template(self):
        """Выбираем шаблон в зависимости от наличия данных о порыве ветра"""
        return (
            templates.WEATHER_WITH_WIND_GUST
            if self.forecast.wind_gust is not None
            else templates.WEATHER
        )


class DailyForecast(BaseForecast):
    """Прогноз погоды в конкретный день"""

    def get_template(self):
        """Выбираем шаблон в зависимости от наличия данных о порыве ветра"""
        return (
            templates.DAILY_FORECAST_WITH_WIND_GUST
            if self.forecast.wind_gust is not None
            else templates.DAILY_FORECAST
        )


def _format_alerts(alerts):
    """Форматирование предупреждений в прогнозе.

    Данный текст присоединяется к тексту прогноза
    """
    if not alerts:
        return ""

    return "\n\n" + "\n".join(
        templates.ALERT.format(alert=alert) for alert in alerts
    )
