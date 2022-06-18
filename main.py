import asyncio
import datetime
import logging
import traceback
from os import environ, path
from sys import stdout

from dotenv import load_dotenv

from src import CurrencyApiClient, ChartsPDFBuilder, RatesStorage

load_dotenv(path.join(path.abspath(path.dirname(__file__)), '.env'))

logging.basicConfig(
    level=environ.get('LOG_LEVEL'),
    format='%(asctime)s %(levelname)s (%(levelno)s) %(message)s',
    stream=stdout,
)

DATES = [datetime.date.today() - datetime.timedelta(days=days + 1) for days in range(int(environ.get('INTERVAL_DAYS')))]
BASE_CURRENCIES = environ.get('BASE_CURRENCIES').split(',')
QUOTE_CURRENCIES = environ.get('QUOTE_CURRENCIES').split(',')
PDF_FILE_PATH = environ.get('PDF_FILE_PATH')


async def main():
    """ App entrypoint """

    storage = RatesStorage(
        api=CurrencyApiClient(
            base_url=environ.get('BASE_API_URL'),
            api_version=environ.get('CURRENCY_API_VERSION'),
        )
    )

    pdf_builder = ChartsPDFBuilder(
        storage=storage,
        base_currencies=BASE_CURRENCIES,
        quote_currencies=QUOTE_CURRENCIES,
        plots_style=environ.get('PLOTS_STYLE'),
    )

    await storage.update(DATES, BASE_CURRENCIES)

    pdf_builder.compose_pdf(file_path=PDF_FILE_PATH)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except BaseException as e:
        logging.exception(f'Unhandled error: {e} {traceback.format_exc()}')
