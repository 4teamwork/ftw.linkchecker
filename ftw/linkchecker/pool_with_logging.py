from multiprocessing.pool import Pool
import logging
import multiprocessing
import sys

RUN = 0
CLOSE = 1
TERMINATE = 2

# python version dependent import
# python < 3.2 does not provide methods in std. lib
if sys.version_info < (3, 2):
    from logutils.queue import QueueHandler, QueueListener
else:
    from logging.handlers import QueueHandler, QueueListener


class PoolWithLogging(Pool):
    """Custom multiprocessing Pool logging using the defined logger
    This class is though as an extension of 'multiprocessing.Pool' to be able
    to use the logger in the worker function of doing multiprocessing.
    """

    def __init__(self, processes=None, logger_name=None):
        if not logger_name:
            logger_name = __name__
        self.logger_name = logger_name
        self.queue_handler = None
        self.stream_handler = None

        # start queue_listener
        self.mp_queue_listener, mp_queue = self.logger_init()

        # prepare and call original Pool init
        initargs = tuple([mp_queue])
        initializer = self.add_queue_handler(mp_queue)
        super(PoolWithLogging, self).__init__(processes=processes,
                                              initializer=initializer,
                                              initargs=initargs)

    def close(self):
        # close pool
        super(PoolWithLogging, self).close()
        # stop queue listener
        self.mp_queue_listener.stop()
        # remove previously added queue handler
        logger = logging.getLogger(self.logger_name)
        logger.removeHandler(self.queue_handler)
        logger.addHandler(self.stream_handler)

    def add_queue_handler(self, mp_queque):
        # all records from worker processes go to
        # queue_handler and then into mp_queue.
        self.queue_handler = QueueHandler(mp_queque)
        # add queue_handler to logger
        logger = logging.getLogger(self.logger_name)
        # add class handler
        logger.addHandler(self.queue_handler)

    def logger_init(self):
        mp_queue = multiprocessing.Queue()
        # extract stream handler from logger, temp. remove from logger but send
        # to queue listener - on closing Pool stream handler is added again
        logger = logging.getLogger(self.logger_name)
        stream_handlers = [x for x in logger.handlers
                           if type(x) == logging.StreamHandler]
        # this is necessary if we don't want to setup the hander in tests
        if stream_handlers:
            self.stream_handler = stream_handlers[0]

        logger.removeHandler(self.stream_handler)
        # queue_listener gets records from the queue
        # and sends them to the the logger stream handler.
        mp_queue_listener = QueueListener(mp_queue, self.stream_handler)
        mp_queue_listener.start()

        return mp_queue_listener, mp_queue
