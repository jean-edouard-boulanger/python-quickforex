from typing import Iterable, Optional
from decimal import Decimal
from datetime import date

from dataclasses import dataclass

from quickforex.domain import CurrencyPair, DateRange
from quickforex.providers.factory import registered_provider
from quickforex.providers import ProviderBase


@dataclass
class Settings:
    return_rate: float = 1.0


@registered_provider
class DummyProvider(ProviderBase):
    """Dummy provider"""

    identifier = "dummy"

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or Settings()

    def get_latest_rates(
        self, currency_pairs: Iterable[CurrencyPair]
    ) -> dict[CurrencyPair, Decimal]:
        """
        :param currency_pairs: Currency pairs for which to retrieve the exchange rates
        :return: Last exchange rate for each provided currency pair.
        """
        return {pair: self._settings.return_rate for pair in currency_pairs}

    def get_latest_rate(self, currency_pair: CurrencyPair) -> Decimal:
        """
        :param currency_pair:
        :return: Last exchange rate for the provided currency pair.
        """
        return self.get_latest_rates([currency_pair])[currency_pair]

    def get_historical_rates(
        self, currency_pairs: Iterable[CurrencyPair], as_of: date
    ) -> dict[CurrencyPair, Decimal]:
        """
        :param currency_pairs:
        :param as_of:
        :return: Historical exchange rate for each provided currency pair.
        """
        return self.get_latest_rates(currency_pairs)

    def get_historical_rate(self, currency_pair: CurrencyPair, as_of: date) -> Decimal:
        """
        :param currency_pair:
        :param as_of:
        :return: Historical exchange rate for the provided currency pair.
        """
        return self.get_latest_rates([currency_pair])[currency_pair]

    def get_rates_time_series(
        self, currency_pairs: Iterable[CurrencyPair], date_range: DateRange
    ) -> dict[CurrencyPair, dict[date, Decimal]]:
        """
        :param currency_pairs: Currency pairs for which to retrieve the exchange rates. This argument can either be
            a list of of currency pairs or a single currency pair.
        :param date_range: Date range over which the exchange rates should be retrieved.
        :return:
        """
        return {
            pair: {dt: self._settings.return_rate for dt in date_range}
            for pair in currency_pairs
        }
