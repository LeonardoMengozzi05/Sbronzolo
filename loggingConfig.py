import logging
from logging.handlers import RotatingFileHandler

with open("./logs/sbronzolo.log", "a", encoding="utf-8") as f:
    f.write("--- NEW SESSION ---\n")

logger = logging.getLogger('sbronzolo')
logger.setLevel(logging.INFO)

def logClient(client, message):
    logger.info(
        "client_%s %s",
        client.token[:8],
        message
    )

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