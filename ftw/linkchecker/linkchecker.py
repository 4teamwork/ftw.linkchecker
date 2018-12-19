from multiprocessing import Pool
import os
import requests
import time

TIMEOUT = 1


def millis():
    return int(round(time.time() * 1000))


def get_uri_response(url_item):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    error = None
    response = None
    start_time = millis()
    try:
        response = requests.head(url_item[2],
                                 timeout=TIMEOUT,
                                 headers=headers,
                                 allow_redirects=False)
    except requests.exceptions.Timeout:
        error = 'Timeout'
    except requests.exceptions.TooManyRedirects:
        error = 'Too many redirects'
    except requests.exceptions.ConnectionError:
        error = 'Connection Error'
    except requests.exceptions.RequestException as e:
        error = e

    time = millis() - start_time

    attachment = extract_header_information(response)

    result = [
        url_item[0],
        url_item[1],
        url_item[2],
        attachment['status code'],
        attachment['content type'],
        time,
        attachment['header location'],
        error,
    ]

    return result


def limit_cpu():
    os.nice(19)


def extract_header_information(response):
    attachment = {
        'status code': None,
        'header location': None,
        'content type': None,
    }
    if not response:
        return attachment

    attachment['status code'] = response.status_code

    headers = response.headers
    if headers:
        attachment['header location'] = headers.get('Location', None)
        attachment['content type'] = headers.get('Content-Type', None)
    return attachment


def work_through_urls(urls):
    pool = Pool(initializer=limit_cpu)
    start_time = millis()
    results = pool.map(get_uri_response, urls)
    total_time = millis() - start_time
    return [total_time, results]
