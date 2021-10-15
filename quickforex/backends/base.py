from typing import Protocol, Iterable, Union
from datetime import date

from quickforex.domain import (
    CurrencyPair,
    SymbolDescription,
    DateRange
)


class BackendBase(Protocol):
    def get_supported_symbols(self) -> list[SymbolDescription]:
        """
        :return: List of supported symbols as a list of symbol description.
        """
        ...

    def get_latest_rates(self, currency_pairs: Iterable[CurrencyPair]) -> dict[CurrencyPair, float]:
        """
        :param currency_pairs: Currency pairs for which to retrieve the exchange rates
        :return: Last exchange rate for each provided currency pair.
        """
        ...

    def get_latest_rate(self, currency_pair: CurrencyPair) -> float:
        """
        :param currency_pair:
        :return: Last exchange rate for the provided currency pair.
        """
        return self.get_latest_rates([currency_pair])[currency_pair]

    def get_historical_rates(self,
                             currency_pairs: Iterable[CurrencyPair],
                             as_of: date) -> dict[CurrencyPair, float]:
        """
        :param currency_pairs:
        :param as_of:
        :return: Historical exchange rate for each provided currency pair.
        """
        ...

    def get_historical_rate(self,
                            currency_pair: CurrencyPair,
                            as_of: date) -> float:
        """
        :param currency_pair:
        :param as_of:
        :return: Historical exchange rate for the provided currency pair.
        """
        return self.get_historical_rates([currency_pair], as_of)[currency_pair]

    def get_rates_time_series(self,
                              currency_pairs: Union[Iterable[CurrencyPair], CurrencyPair],
                              *date_range_args: Union[
                                  DateRange, date,
                                  tuple[date, date]
                              ]) -> dict[CurrencyPair, dict[date, float]]:
        """
        :param currency_pairs: Currency pairs for which to retrieve the exchange rates. This argument can either be
            a list of of currency pairs or a single currency pair.
        :param date_range_args: Date range over which the exchange rates should be retrieved. This argument can either
            be provided as:
                - Two date objects
                - A single two-tuple of date objects
                - A single DateRange object
        :return:
        """
        ...
