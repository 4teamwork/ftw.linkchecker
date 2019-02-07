from multiprocessing import Pool
import os
import requests
import time


def millis():
    return int(round(time.time() * 1000))


def get_uri_response(external_link_obj):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    error = None
    response = None
    start_time = millis()
    try:
        response = requests.head(external_link_obj.link_target,
                                 timeout=TIMEOUT,
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

    time = millis() - start_time

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


def limit_cpu():
    os.nice(19)


def work_through_urls(external_link_objs, timeout_config):
    global TIMEOUT
    TIMEOUT = timeout_config
    pool = Pool(initializer=limit_cpu)
    start_time = millis()
    external_link_objs = pool.map(get_uri_response, external_link_objs)
    total_time = millis() - start_time
    return external_link_objs, total_time
