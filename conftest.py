from requests.exceptions import ChunkedEncodingError


def pytest_set_filtered_exceptions():
    """
    pytest-retry: Any test will be retried if it fails due to ChunkedEncodingError,
    which occurs due to runregistry not being able to serve many hardcore requests
    at the same time.
    """
    return [ChunkedEncodingError]
