from app import db

from aiohttp.web import Application, run_app
from aiogram.dispatcher.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)


class Webhook:
    def __init__(
        self, dp, tasks, webhook_url, webhook_path, webapp_host, webapp_port
    ):
        self.dp = dp
        self.tasks = tasks
        self.webhook_url = webhook_url
        self.webhook_path = webhook_path
        self.webapp_host = webapp_host
        self.webapp_port = webapp_port

    def run(self, bot):
        """Запуск бота в режиме webhook"""
        self.dp.startup.register(on_startup(bot, self.webhook_url, self.tasks))
        app = Application()
        SimpleRequestHandler(dispatcher=self.dp, bot=bot).register(
            app, path=self.webhook_path
        )
        setup_application(app, self.dp)
        run_app(app, host=self.webapp_host, port=self.webapp_port)


def on_startup(bot, webhook_url, tasks):
    async def on_startup():
        """Функция перед запуском бота в режиме webhook"""
        await bot.set_webhook(webhook_url, drop_pending_updates=True)
        await db.create_db()
        for task in tasks:
            task.run(bot)

    return on_startup
