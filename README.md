**Telegram бот погоды Череповца**

Переменные окружения:

`BOT_TOKEN` - токен telegram бота

`WEATHER_API_KEY` - ключ с сайта openweathermap.org (One Call API)

`DATABASE_URL` - путь к базе данных (по умолчанию `sqlite:///db/subscribers.db`)

Логи выводятся в консоль, а также сохраняются в папку logs (еженедельная ротация).
В файл undefined_weather_types.txt сохраняются типы погод, для которых нет стикера.
