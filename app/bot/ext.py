"""Расширение - class-based хендлеры для aiogram.

Пример миграции с обычного хендлера на class-based:

- До:

~~~
@router.message(TextFilter("Hello!"))
async def answer(message):
   await message.answer("Hola, amigos!")
~~~

- После:

~~~
class Answer(MessageRoute):
    def __init__(self):
        super().__init__(filter=TextFilter("Hello!"), handler=self.handle)

    async def handle(self, message):
        await message.answer("Hola, amigos!")

Answer().register(router)
~~~

У хендлера появился конструктор, и в него теперь можно
передавать зависимости, в отличии от статичной функции.
"""

from abc import ABC, abstractmethod


class Route(ABC):
    """Абстрактный класс хендлера.
    
    Наследник должен переопределить метод `register`.
    """

    def __init__(self, filter, handler):
        self.filter = filter
        self.handler = handler

    @abstractmethod
    def register(self, router):
        """Регистрация хендлера в роутере."""


class MessageRoute(Route):
    """Хендлер событий `Message`.
    
    Аналог `@router.message()`.
    """

    def register(self, router):
        router.message(self.filter)(self.handler)

class CallbackRoute(Route):
    """Хендлер событий `CallbackQuery`.
    
    Аналог `@router.message()`.
    """

    def register(self, router):
        router.callback_query(self.filter)(self.handler)

class ErrorRoute(Route):
    """Хендлер событий `Exception`.
    
    Аналог `@router.errors()`.
    """

    def register(self, router):
        router.errors(self.filter)(self.handler)
