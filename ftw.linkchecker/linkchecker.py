from multiprocessing import Pool
import time
import requests
import urls_testing
import os
import sys

urls = urls_testing.urls
number_of_processes = len(urls)
timeout = 1


def millis():
    return int(round(time.time() * 1000))


def get_uri_responses(urls):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    error = None
    response = None
    start_time = millis()
    try:
        response = requests.head(urls.get('destination'),
                                 timeout=timeout,
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
    result = {
        'origin': urls.get('origin'),
        'destination': urls.get('destination'),
        'data': response,
        'error': error,
    }
    result.update({'time': time})

    return result


def limit_cpu():
    try:
        sys.getwindowsversion()
    except AttributeError:
        isWindows = False
    else:
        isWindows = True

    if isWindows:
        import win32api
        import win32process
        import win32con

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(
            handle, win32process.BELOW_NORMAL_PRIORITY_CLASS)
    else:
        os.nice(19)


def work_through_urls():
    pool = Pool(number_of_processes, limit_cpu)
    start_time = millis()
    results = pool.map(get_uri_responses, urls)
    total_time = millis() - start_time
    result_collection = []
    for result in results:
        status_code = None
        header_location = None
        content_type = None
        if result.get('data'):
            if result.get('data').status_code:
                status_code = result.get('data').status_code
            if result.get('data').headers.get('Location', ''):
                header_location = result.get(
                    'data').headers.get('Location', '')
            if result.get('data').headers.get('Content-Type', ''):
                content_type = result.get(
                    'data').headers.get('Content-Type', '')
        del result['data']
        result.update({
                      'status code': status_code,
                      'header location': header_location,
                      'content type': content_type,
                      })
        result_collection.append(result)
    return [total_time, result_collection]


if __name__ == '__main__':
    print(work_through_urls())
