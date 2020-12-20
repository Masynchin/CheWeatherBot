from loguru import logger


logger.add(
    sink='logs/log.log',
    format="{time:DD-MM-YYYY at HH:mm:ss} | {level} | {message}",
    rotation='1 week',
    compression='zip',
)
