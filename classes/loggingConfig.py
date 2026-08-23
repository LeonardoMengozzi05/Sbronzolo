from logging.handlers import RotatingFileHandler
import logging

logger = logging.getLogger('sbronzolo')
logger.setLevel(logging.INFO)

def logClient(client, message):
    logger.info(
        "client_%s %s",
        client.token[:8],
        message
    )

def logAlcol(message):
    logger.info(message)

handler = RotatingFileHandler(
    'logs/sbronzolo.log',
    maxBytes=5_000_000,
    backupCount=3
)

formatter = logging.Formatter(
    '%(asctime)s | %(message)s'
)

handler.setFormatter(formatter)
logger.addHandler(handler)