from typing import Iterable, Union, Type
from datetime import date

from quickforex.backends.base import BackendBase
from quickforex.backends.exchangerate_host import ExchangeRateHostBackend
from quickforex.domain import (
    CurrencyPair,
    SymbolDescription,
    DateRange
)


Api: Type[BackendBase] = ExchangeRateHostBackend
INSTALLED_BACKEND: BackendBase = Api()


def _backend() -> BackendBase:
    return INSTALLED_BACKEND


def get_supported_symbols() -> list[SymbolDescription]:
    """
    :return: List of supported symbols as a list of symbol description.
    """
    return _backend().get_supported_symbols()


def get_latest_rates(currency_pairs: Iterable[CurrencyPair]) -> dict[CurrencyPair, float]:
    """
    :param currency_pairs: Currency pairs for which to retrieve the exchange rates
    :return: Last exchange rate for each provided currency pair.
    """
    ...
    return _backend().get_latest_rates(currency_pairs)


def get_latest_rate(currency_pair: CurrencyPair) -> float:
    """
    :param currency_pair:
    :return: Last exchange rate for the provided currency pair.
    """
    return _backend().get_latest_rate(currency_pair)


def get_historical_rates(currency_pairs: Iterable[CurrencyPair],
                         as_of: date) -> dict[CurrencyPair, float]:
    """
    :param currency_pairs:
    :param as_of:
    :return: Historical exchange rate for each provided currency pair.
    """
    return _backend().get_historical_rates(currency_pairs, as_of)


def get_historical_rate(currency_pair: CurrencyPair, as_of: date) -> float:
    """
    :param currency_pair:
    :param as_of:
    :return: Historical exchange rate for the provided currency pair.
    """
    return _backend().get_historical_rate(currency_pair, as_of)


def get_rates_time_series(currency_pairs: Union[Iterable[CurrencyPair], CurrencyPair],
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
    return _backend().get_rates_time_series(currency_pairs, *date_range_args)
