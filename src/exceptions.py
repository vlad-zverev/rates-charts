import logging
import traceback


def trace(exception: BaseException = None) -> str:
    exc_info = ", ".join(f'{exception}'.splitlines()) if exception else ''
    return exc_info + ", ".join(traceback.format_exc().splitlines())


class CurrencyApiError(Exception):
    def __init__(self, endpoint: str):
        logging.exception(f'Error occurred {endpoint}')


class StorageError(Exception):
    def __init__(self, currency: str):
        logging.exception(f'Fetched no data for currency `{currency}`')
