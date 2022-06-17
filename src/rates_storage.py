import asyncio
import datetime

import pandas as pd
from aiohttp import ClientSession

from .api_client import CurrencyApiClient, CurrencyRates
from .exceptions import StorageError


class RatesStorage:
	def __init__(self, api: CurrencyApiClient):
		self._api = api
		self._rates: dict[str, pd.DataFrame] = {}

	@property
	def rates(self):
		return self._rates

	async def update(self, dates: list[datetime.date], currencies: list[str]) -> None:
		currencies_rates = {currency: list() for currency in currencies}
		async with ClientSession() as session:
			results = await asyncio.gather(
				*[
					asyncio.ensure_future(
						self._api.get_currency_rates_for_date(
							session=session,
							date=date.strftime('%Y-%m-%d'),
							base_currency=currency,
						)
					)
					for date in dates
					for currency in currencies
				], return_exceptions=True
			)
			for result in results:
				if isinstance(result, CurrencyRates):
					currencies_rates[result.currency].append({'date': result.date, **result.rates})

		for currency, rates in currencies_rates.items():
			if not rates:
				raise StorageError(currency)
			df = pd.DataFrame(rates)
			df = df.sort_values(by=['date'], ascending=True)
			df.reset_index(inplace=True)
			currencies_rates[currency] = df

		self._rates = currencies_rates
