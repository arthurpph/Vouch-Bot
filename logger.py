import logging


def get_logger():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    logger.addHandler(handler)

    return logger
