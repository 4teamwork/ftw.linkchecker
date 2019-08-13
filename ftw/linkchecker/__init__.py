from zope.i18nmessageid import MessageFactory
import logging

_ = MessageFactory('ftw.linkchecker')
LOGGER_NAME = 'ftw.linkchecker'


def setup_logger(path=None):
    log_formatter = logging.Formatter('%(asctime)s - %(process)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    if not path:
        return

    file_handler = logging.FileHandler(path, mode='a')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    return


def initialize(context):
    pass
