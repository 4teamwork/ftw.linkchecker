from ftw.linkchecker import LOGGER_NAME
from ftw.linkchecker.pool_with_logging import PoolWithLogging
from functools import partial
from multiprocessing import cpu_count
from plone.dexterity.utils import safe_utf8
import logging
import requests
import time


class StatusChecker(object):

    def __init__(self, external_link_objs, timeout_config):
        self.total_time = 0
        self.broken_external_links = []

        self._external_link_objs = external_link_objs
        self._timeout_config = timeout_config

    def work_through_urls(self, processes=cpu_count()):
        # prepare worker function and pool
        part_get_uri_response = partial(_get_uri_response, timeout=self._timeout_config)
        pool = PoolWithLogging(processes=processes, logger_name=LOGGER_NAME)

        start_time = _millis()
        self._external_link_objs = pool.map(
            part_get_uri_response, self._external_link_objs)
        pool.close()
        self.total_time = _millis() - start_time

        self._filter_broken_links()

    def _filter_broken_links(self):
        self.broken_external_links = filter(
            lambda link_obj: link_obj.is_broken, self._external_link_objs)


def _millis():
    return int(round(time.time() * 1000))


def _get_uri_response(external_link_obj, timeout):
    """This is the multiprocessing worker function. It has to be top level in
    order to be pickable.
    """

    logger = logging.getLogger(LOGGER_NAME)
    logger.info(safe_utf8(
        u'Head request to {}'.format(external_link_obj.link_target)))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    error = None
    response = None
    start_time = _millis()
    try:
        response = requests.head(safe_utf8(external_link_obj.link_target),
                                 timeout=timeout,
                                 headers=headers,
                                 allow_redirects=False,
                                 verify=False)
    except requests.exceptions.Timeout:
        error = 'Timeout'
    except requests.exceptions.TooManyRedirects:
        error = 'Too many redirects'
    except requests.exceptions.ConnectionError:
        error = 'Connection Error'
    except Exception as e:
        error = e.message

    time = _millis() - start_time

    if response and response.status_code == 200 \
            or 'resolveuid' in external_link_obj.link_target:
        external_link_obj.is_broken = False
    else:
        external_link_obj.is_broken = True
        external_link_obj.status_code = getattr(response, 'status_code', None)
        external_link_obj.content_type = headers.get('Content-Type', None)
        external_link_obj.response_time = time
        external_link_obj.error_message = error

    return external_link_obj
