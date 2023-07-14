from app.db import create_db


class Polling:
    def __init__(self, dp, tasks):
        self.dp = dp
        self.tasks = tasks

    def run(self, bot):
        self.dp.startup.register(on_startup(bot, self.tasks))
        self.dp.run_polling(bot)


def on_startup(bot, tasks):
    """Функция перед запуском бота в режиме polling"""
    async def on_startup():
        await create_db()
        for task in tasks:
            task.run(bot)

    return on_startup
