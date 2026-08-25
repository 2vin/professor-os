import random
import time

import requests

from .runtime import monitor


RETRYABLE_STATUS = set([408, 409, 425, 429, 500, 502, 503, 504])


def request_with_retry(method, url, max_attempts=5, base_delay=2.0, timeout=60, **kwargs):
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            if response.status_code not in RETRYABLE_STATUS:
                return response

            last_error = requests.HTTPError(
                'HTTP {0} from {1}'.format(response.status_code, url), response=response
            )
            if attempt == max_attempts:
                return response

            retry_after = response.headers.get('Retry-After')
            if retry_after and retry_after.isdigit():
                delay = min(float(retry_after), 60.0)
            else:
                delay = min(base_delay * (2 ** (attempt - 1)), 30.0)
                delay += random.uniform(0.0, 0.5)
            monitor.retry(attempt, max_attempts, round(delay, 1),
                          'Temporary HTTP {0}; retrying API call ({1}/{2}).'.format(
                              response.status_code, attempt, max_attempts))
            time.sleep(delay)
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_error = exc
            if attempt == max_attempts:
                raise
            delay = min(base_delay * (2 ** (attempt - 1)), 30.0)
            delay += random.uniform(0.0, 0.5)
            monitor.retry(attempt, max_attempts, round(delay, 1),
                          'Network/DNS connection failed; retrying ({0}/{1}) in {2:.1f}s.'.format(
                              attempt, max_attempts, delay))
            time.sleep(delay)

    if last_error:
        raise last_error
    raise RuntimeError('Request failed without a response.')
