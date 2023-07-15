from contextlib import suppress

from app.db import create_db


class Polling:
    """Запуск бота в режиме polling"""

    def __init__(self, dp, tasks):
        self.dp = dp
        self.tasks = tasks

    async def run(self, bot):
        self.dp.startup.register(on_startup(bot, self.tasks))
        with suppress(KeyboardInterrupt, SystemExit):
            await self.dp.start_polling(bot)


def on_startup(bot, tasks):
    """Функция перед запуском бота в режиме polling"""

    async def on_startup():
        await create_db()
        for task in tasks:
            task.run(bot)

    return on_startup
