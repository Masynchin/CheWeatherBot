"""Модуль с логгером.

Все сообщения выводятся в консоль и папку logs
"""

from loguru import logger


logger.add(
    encoding="u8",
    sink="logs/log.log",
    format="{time:DD-MM-YYYY at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
    compression="zip",
)
