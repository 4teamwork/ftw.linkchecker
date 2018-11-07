from multiprocessing import Pool
import time
import requests
import urls_testing

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


def work_through_urls():
    pool = Pool(processes=number_of_processes)
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
