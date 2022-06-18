import logging
from json import load

import humanize
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from .rates_storage import RatesStorage


class Colors:
    GREEN = '#2FA01D'
    RED = '#EE5F48'
    LIGHT_BLUE = '#A1C0EE'
    BLUE = '#216BA5'
    DARK_BLUE = '#071F45'
    SOFT_BLUE = '#192C4A'


class ChartsPDFBuilder:
    def __init__(
            self, storage: RatesStorage,
            base_currencies: list[str], quote_currencies: list[str],
            plots_style: str = 'seaborn',
    ):
        with open('pdf_metadata.json') as metadata:
            self._metadata = load(metadata)

        self._storage = storage
        self._base_currencies = base_currencies
        self._quote_currencies = quote_currencies
        self._set_styles(plots_style)

    def compose_pdf(self, file_path: str = 'rates.pdf') -> None:
        """ Generate new PDF-file with exchange rates plots """
        rates = self._storage.rates
        with PdfPages(file_path) as pdf:
            self._create_title_page(pdf)
            for base_currency in self._base_currencies:
                df = rates[base_currency]
                for quote_currency in self._quote_currencies:
                    self._create_page(pdf, df, base_currency, quote_currency)
            pdf.infodict().update(self._metadata)
            logging.info(f'Data compiled into PDF with charts: [{file_path}]')

    def _create_page(
            self, pdf: PdfPages,
            df: pd.DataFrame,
            base_currency: str, quote_currency: str
    ) -> None:
        """ Create single pdf-page with plot """
        currency_rates = df[quote_currency]
        dates = df['date']

        self._create_plot(currency_rates, dates)
        self._set_annotations(currency_rates, dates)
        self._set_labels()
        self._format_dates(dates)
        self._set_title(base_currency, quote_currency)

        pdf.savefig(facecolor=Colors.SOFT_BLUE)
        plt.close()

    @staticmethod
    def _create_plot(currency_rates: pd.Series, dates: pd.Series) -> None:
        """ Create chart with lines (red or green depending on rates trend) """
        first_rate = currency_rates.iloc[0]
        last_rate = currency_rates.iloc[-1]
        plt.plot(
            dates,
            currency_rates,
            Colors.GREEN if last_rate > first_rate else Colors.RED,
            linewidth=int(100 / len(dates)) + 1,
        )

    def _create_title_page(self, pdf: PdfPages) -> None:
        page = plt.figure()
        page.clf()
        base_currencies_txt = ' '.join([currency.upper() for currency in self._base_currencies])
        quote_currencies_txt = ' '.join([currency.upper() for currency in self._quote_currencies])
        page.text(0.5, 0.5, 'Exchange Rates Charts', size=38, ha='center')
        page.text(0.5, 0.4, base_currencies_txt, size=16, ha='center')
        page.text(0.5, 0.35, 'with', size=12, ha='center')
        page.text(0.5, 0.3, quote_currencies_txt, size=16, ha='center')
        pdf.savefig(facecolor=Colors.SOFT_BLUE)
        plt.close()

    @staticmethod
    def _set_styles(plots_style: str) -> None:
        plt.style.use(plots_style)
        mpl.rcParams['grid.color'] = Colors.BLUE
        mpl.rcParams['text.color'] = Colors.LIGHT_BLUE
        mpl.rcParams['xtick.color'] = Colors.LIGHT_BLUE
        mpl.rcParams['ytick.color'] = Colors.LIGHT_BLUE
        mpl.rcParams['axes.labelcolor'] = Colors.LIGHT_BLUE
        plt.rcParams['axes.facecolor'] = Colors.DARK_BLUE

    def _set_annotations(self, currency_rates: pd.Series, dates: pd.Series) -> None:
        plt.annotate(
            f'Min: {self._format_num(currency_rates.min())}\n'
            f'Max: {self._format_num(currency_rates.max())}\n'
            f'Avg: {self._format_num(currency_rates.mean())}',
            xy=(dates.min(), currency_rates.max()),
            fontsize=12,
        )

    @staticmethod
    def _format_num(num: float) -> str:
        if num < 100:
            precision = 2
        elif num > 200:
            precision = 0
        else:
            precision = 1
        return humanize.intcomma(round(num, precision) if precision else int(num))

    @staticmethod
    def _set_labels() -> None:
        plt.ylabel('rate')
        plt.xlabel('date')

    @staticmethod
    def _set_title(base_currency: str, quote_currency: str) -> None:
        plt.title(f'{base_currency.upper()}-{quote_currency.upper()}')

    @staticmethod
    def _format_dates(dates: pd.Series) -> None:
        """ Prettify dates """
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=int(len(dates) / 10)))
        plt.xticks(rotation=30, fontweight='light', fontsize='x-small')
