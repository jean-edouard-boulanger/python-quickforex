from typing import Protocol, Iterable, runtime_checkable
from datetime import date
from decimal import Decimal

from quickforex.domain import CurrencyPair, DateRange


@runtime_checkable
class ProviderBase(Protocol):
    identifier: str

    def get_latest_rates(
        self, currency_pairs: Iterable[CurrencyPair]
    ) -> dict[CurrencyPair, Decimal]:
        """
        :param currency_pairs: Currency pairs for which to retrieve the exchange rates
        :return: Last exchange rate for each provided currency pair.
        """
        ...

    def get_latest_rate(self, currency_pair: CurrencyPair) -> Decimal:
        """
        :param currency_pair:
        :return: Last exchange rate for the provided currency pair.
        """
        ...

    def get_historical_rates(
        self, currency_pairs: Iterable[CurrencyPair], as_of: date
    ) -> dict[CurrencyPair, Decimal]:
        """
        :param currency_pairs:
        :param as_of:
        :return: Historical exchange rate for each provided currency pair.
        """
        ...

    def get_historical_rate(self, currency_pair: CurrencyPair, as_of: date) -> Decimal:
        """
        :param currency_pair:
        :param as_of:
        :return: Historical exchange rate for the provided currency pair.
        """
        ...

    def get_rates_time_series(
        self, currency_pairs: Iterable[CurrencyPair], date_range: DateRange
    ) -> dict[CurrencyPair, dict[date, Decimal]]:
        """
        :param currency_pairs: Currency pairs for which to retrieve the exchange rates. This argument can either be
            a list of of currency pairs or a single currency pair.
        :param date_range: Date range over which the exchange rates should be retrieved.
        :return:
        """
        ...
