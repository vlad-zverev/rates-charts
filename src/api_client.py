import datetime
import logging
from json import loads
from typing import NamedTuple

from aiohttp import ClientSession, ClientResponseError

from .exceptions import CurrencyApiError, trace


class CurrencyRates(NamedTuple):
    currency: str
    rates: dict[str, float]
    date: datetime.date


class CurrencyApiClient:
    def __init__(self, base_url: str, api_version: str):
        self._base_url = f'{base_url}@{api_version}'

    async def _get(self, session: ClientSession, endpoint: str) -> dict or None:
        try:
            async with session.get(self._base_url + endpoint) as response:
                if not response.ok:
                    response.raise_for_status()
                data = await response.read()
                return loads(data)
        except ClientResponseError as e:
            logging.exception(f'Error while fetching CurrencyAPI {endpoint}: {trace(e)}')
        except BaseException as e:
            logging.exception(f'Unhandled error CurrencyAPI {endpoint}: {trace(e)}')
        raise CurrencyApiError(endpoint)

    async def get_currency_rates_for_date(
            self, session: ClientSession,
            date: str = '2022-05-18',
            base_currency: str = 'usd'
    ) -> CurrencyRates:
        response = await self._get(session, f'/{date}/currencies/{base_currency}.min.json')
        logging.debug(f'Raw response: {response}')
        return CurrencyRates(
            currency=base_currency,
            rates=response[base_currency],
            date=datetime.datetime.strptime(response['date'], '%Y-%m-%d')
        )
