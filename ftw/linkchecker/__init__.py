from zope.i18nmessageid import MessageFactory
import logging
import os
import sys

_ = MessageFactory('ftw.linkchecker')


def setup_logger(path=None):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not path:
        return logger
    elif os.path.isfile(path):
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        return logger
    else:
        logger.info('Invalid logging path!')
        sys.exit(1)


def initialize(context):
    pass
