from typing import Iterable, Union
from datetime import date
from decimal import Decimal

from quickforex.utils import (
    parse_currency_pairs_args,
    parse_currency_pair_args,
    parse_date_range_kwargs,
)
from quickforex.backend import BackendBase, ExchangeRateHostBackend
from quickforex.domain import CurrencyPairType, CurrencyPair, DateRange


_INSTALLED_BACKEND: BackendBase = ExchangeRateHostBackend()


def _backend() -> BackendBase:
    return _INSTALLED_BACKEND


class Api(object):
    def __init__(self, backend: BackendBase):
        self._backend = backend

    def get_latest_rate(self, *currency_pair_args: CurrencyPairType) -> Decimal:
        """Retrieve the last available rate for the given currency pair

        Examples:

            api.get_latest_rate("EUR/USD")
            api.get_latest_rate("EUR", "USD")
            api.get_latest_rate(("EUR", "USD"))
            api.get_latest_rate(CurrencyPair("EUR", "USD"))

        :param currency_pair_args: Currency pair in either format:
            - Single str argument "<domestic>/<foreign>": "EUR/USD"
            - Two str arguments "<domestic>", "<foreign>": "EUR", "USD"
            - Single tuple[str, str] argument ("<domestic>", "<foreign>"): ("EUR", "USD")
            - Single quickforex.CurrencyPair argument: quickforex.CurrencyPair("EUR", "USD")
        :return: Last exchange rate for the provided currency pair.
        """
        return self._backend.get_latest_rate(
            currency_pair=parse_currency_pair_args(*currency_pair_args)
        )

    def get_latest_rates(
        self, *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType]
    ) -> dict[CurrencyPair, Decimal]:
        """Retrieve the last available rate for each given currency pair

        Examples:

            api.get_latest_rates("EUR/USD", "EUR/GBP")
            api.get_latest_rates(("EUR", "USD"), ("EUR", "GBP"))
            api.get_latest_rates(CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP"))
            api.get_latest_rates({CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")})
            api.get_latest_rates([CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")])
            api.get_latest_rates([CurrencyPair("EUR", "USD"), ("EUR", "GBP")])

        :param currency_pairs_args: List of currency pairs. Each individual argument can be:
            - str "<domestic>/<foreign>": "EUR/USD"
            - tuple[str, str] ("<domestic>", "<foreign>"): ("EUR", "USD")
            - quickforex.CurrencyPair: quickforex.CurrencyPair("EUR", "USD")
            - An iterable (list, set) with any of the previous argument type.
        :return: Last exchange rate for each provided currency pair.
        """
        ...
        return self._backend.get_latest_rates(
            currency_pairs=parse_currency_pairs_args(*currency_pairs_args)
        )

    def get_historical_rate(
        self, *currency_pair_args: CurrencyPairType, as_of: date
    ) -> Decimal:
        """Retrieve the last available rate for the given currency pair
        :param currency_pair_args: Currency pair in either format:
            - Single str argument "<domestic>/<foreign>": "EUR/USD"
            - Two str arguments "<domestic>", "<foreign>": "EUR", "USD"
            - Single tuple[str, str] argument ("<domestic>", "<foreign>"): ("EUR", "USD")
            - Single quickforex.CurrencyPair argument: quickforex.CurrencyPair("EUR", "USD")
        :param as_of:
        :return: Historical exchange rate for the provided currency pair.
        """
        return self._backend.get_historical_rate(
            currency_pair=parse_currency_pair_args(*currency_pair_args), as_of=as_of
        )

    def get_historical_rates(
        self,
        *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType],
        as_of: date
    ) -> dict[CurrencyPair, Decimal]:
        """
        :param currency_pairs:
        :param as_of:
        :return: Historical exchange rate for each provided currency pair.
        """
        return self._backend.get_historical_rates(
            currency_pairs=parse_currency_pairs_args(*currency_pairs_args), as_of=as_of
        )

    def get_rates_time_series(
        self,
        *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType],
        **date_range_kwargs: Union[DateRange, date]
    ) -> dict[CurrencyPair, dict[date, Decimal]]:
        """
        :param currency_pairs_args: Currency pairs for which to retrieve the exchange rates. This argument can either be
            a list of of currency pairs or a single currency pair.
        :param date_range_kwargs:
        :return:
        """
        return self._backend.get_rates_time_series(
            currency_pairs=parse_currency_pairs_args(*currency_pairs_args),
            date_range=parse_date_range_kwargs(**date_range_kwargs),
        )


def get_latest_rate(*currency_pair_args: CurrencyPair) -> Decimal:
    """
    :param currency_pair:
    :return: Last exchange rate for the provided currency pair.
    """
    return Api(_backend()).get_latest_rate(*currency_pair_args)


def get_latest_rates(
    *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType]
) -> dict[CurrencyPair, Decimal]:
    """
    :param currency_pairs_args: Currency pairs for which to retrieve the exchange rates
    :return: Last exchange rate for each provided currency pair.
    """
    ...
    return Api(_backend()).get_latest_rates(*currency_pairs_args)


def get_historical_rate(*currency_pair_args: CurrencyPairType, as_of: date) -> Decimal:
    """
    :param currency_pair:
    :param as_of:
    :return: Historical exchange rate for the provided currency pair.
    """
    return Api(_backend()).get_historical_rate(*currency_pair_args, as_of=as_of)


def get_historical_rates(
    *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType],
    as_of: date
) -> dict[CurrencyPair, Decimal]:
    """
    :param currency_pairs_args:
    :param as_of:
    :return: Historical exchange rate for each provided currency pair.
    """
    return Api(_backend()).get_historical_rates(*currency_pairs_args, as_of=as_of)


def get_rates_time_series(
    *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType],
    **date_range_kwargs: Union[DateRange, date]
) -> dict[CurrencyPair, dict[date, Decimal]]:
    """
    :param currency_pairs_args: Currency pairs for which to retrieve the exchange rates. This argument can either be
        a list of of currency pairs or a single currency pair.
    :param date_range_kwargs:
    :return:
    """
    return Api(_backend()).get_rates_time_series(
        *currency_pairs_args, **date_range_kwargs
    )
