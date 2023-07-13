# Telegram бот погоды Череповца

Адрес бота: [@weather35bot](https://t.me/weather35bot)

## Что позволяет бот

- Узнать текущую погоду
- Узнать прогноз на конкретный час (в пределах следующих двух дней)
- Узнать прогноз на конкретный день (в пределах следующих семи дней)
- **Подписаться на ежедневную рассылку в удобное для вас время**

Прогноз на конкретный час состоит из типа погоды, фактической и ощущаемой температур, скорости ветра (и порывов, если присутствуют), показателя влажности, показателя облачности, и предупреждений (если присутствуют).

Прогноз на конкретный день дополняется информацией о температуре каждого времени суток - утра, дня, вечера, и ночи.

## Использование

Начните диалог с ботом [@weather35bot](https://t.me/weather35bot).

Вся работа с ним будет происходить при помощи клавиатуры, которую бот выдаст вместе с его первым сообщением. В этом сообщении будет описано, за что отвечает каждая кнопка клавиатуры.

Теперь вы можете узнать текущую погоду, получить прогноз, и подписаться на рассылку.

## Мотивация

- Хочу без лишних усилий получать подробную информацию о текущей погоде.

Поэтому я выбрал Telegram. Простой интерфейс, автоматическая рассылка. Можно один раз настроить, и бот сам будет отправлять прогноз.

- Хочу иметь небольшой проект для практикования.

Периодически я возвращаюсь к этому проекту с целью улучшения кода, структуры проекта, внешнего вида и т.д. Об этих рефакторингах можно прочитать [здесь](https://github.com/Masynchin/history) под заголовками, содержащими "CheWeatherBot".

## Технологии

<!-- ### Сервер -->

### Бот

- Для работы с telegram используется [aiogram](https://github.com/aiogram/aiogram).
- Для логирования используется [loguru](https://github.com/Delgan/loguru).

### Погода

- Для получения информации о погоде используется [OpenWeatherMap](https://openweathermap.org/) с тарифом [One Call API](https://openweathermap.org/api/one-call-api).
- Для запросов к API используется [aiohttp](https://github.com/aio-libs/aiohttp).
- Для удобной работы с ответом API используется [pydantic](https://github.com/samuelcolvin/pydantic).

### Хранение подписчиков рассылки

Используется SQLite. В качестве адаптера используется [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy).

## Установка и запуск

### Переменные окружения

- `BOT_TOKEN` - токен telegram бота
- `WEATHER_API_KEY` - ключ с сайта openweathermap.org (тариф One Call API)
- `DATABASE_URL` - путь к базе данных (по умолчанию `sqlite+aiosqlite:///db/subscribers.db`)
- `RUN_TYPE` - режим работы бота (`polling` (по умолчанию) | `webhook`)

### Запуск вручную

- Основные зависимости:

~~~shell
pip install -r requirements.txt
~~~

- Зависимости для разработки (включают основные):

~~~shell
pip install -r requirements-dev.txt
~~~

Запуск бота происходит через:

~~~shell
python -m app
~~~

### Запуск Docker контейнера

Сборка контейнера:

~~~shell
docker build -t cwb .
~~~

Запуск контейнера:

~~~shell
docker run -d -it --rm \
-e BOT_TOKEN=<token> \
-e WEATHER_API_KEY=<key> \
cwb
~~~

Или с переменными из файла:

~~~shell
docker run -d -it --rm --env-file ./.env cwb
~~~

### Запуск через Docker Compose

Запуск через docker-compose:

~~~shell
docker compose up
~~~

### Логирование

Логи выводятся в консоль, а также сохраняются в папку logs (еженедельная ротация).
В файл undefined_weather_types.txt сохраняются типы погод, для которых нет стикера.
