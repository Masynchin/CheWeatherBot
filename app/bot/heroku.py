import os

from app.bot.webhook import Webhook


class Heroku(Webhook):
    def __init__(self, dp, tasks, app_name, webhook_path, webapp_port):
        webhook_url = f"https://{app_name}.herokuapp.com{webhook_path}"
        super().__init__(
            dp,
            tasks,
            webhook_url=webhook_url,
            webhook_path=webhook_path,
            webapp_host="0.0.0.0",
            webapp_port=webapp_port,
        )

    @classmethod
    def from_env(cls, dp, tasks, bot_token):
        app_name = os.getenv("HEROKU_APP_NAME")
        webhook_path = f"/webhook/{bot_token}"
        webapp_port = int(os.getenv("PORT"))
        return cls(dp, tasks, app_name, webhook_path, webapp_port)
