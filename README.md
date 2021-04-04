# Telegram бот погоды Череповца

## Предназначение
Бот создан для получения текущей погоды и прогнозов для города Череповца

## Реализация
Бот полностью асинхронен, основан на библиотеках:
- [aiogram](https://github.com/aiogram/aiogram) - для работы с telegram
- [aiohttp](https://github.com/aio-libs/aiohttp) - для запросов к сервису данных о погоде
- [loguru](https://github.com/Delgan/loguru) - для логирования действий пользователей
- [pydantic](https://github.com/samuelcolvin/pydantic) - для удобной обработки ответов с сервиса данных о погоде
- [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) - для хранения данных времени рассылки

Сервис данных о погоде - [openweathermap](https://openweathermap.org/) (тариф One Call API)

## Использование
Переменные окружения:

`BOT_TOKEN` - токен telegram бота

`WEATHER_API_KEY` - ключ с сайта openweathermap.org (тариф One Call API)

`DATABASE_URL` - путь к базе данных (по умолчанию `sqlite+aiosqlite:///db/subscribers.db`)

Логи выводятся в консоль, а также сохраняются в папку logs (еженедельная ротация).
В файл undefined_weather_types.txt сохраняются типы погод, для которых нет стикера.
