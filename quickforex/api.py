from typing import Iterable, Union, Optional, Any, Type
from datetime import date
from decimal import Decimal

from quickforex.providers.base import ProviderBase
from quickforex.providers.exchangerate_host import ExchangeRateHostProvider
from quickforex.providers.provider_metadata import ProviderMetadata
from quickforex.providers import factory as providers_factory
from quickforex.domain import CurrencyPairType, CurrencyPair, DateRange
from quickforex.utils import (
    parse_currency_pairs_args,
    parse_currency_pair_args,
    parse_date_range_kwargs,
)

_DEFAULT_PROVIDER: ProviderBase = ExchangeRateHostProvider
_INSTALLED_PROVIDER: ProviderBase = _DEFAULT_PROVIDER()


def _provider() -> ProviderBase:
    return _INSTALLED_PROVIDER


def _create_provider(**kwargs) -> ProviderBase:
    if "provider_id" in kwargs:
        settings_overrides = {
            field: value for field, value in kwargs.items() if field != "provider_id"
        }
        settings_overrides = settings_overrides if len(settings_overrides) > 0 else None
        return providers_factory.create_provider(
            provider_id=kwargs["provider_id"], settings_overrides=settings_overrides
        )
    elif "provider" in kwargs:
        return kwargs["provider"]
    return _provider()


class Api(object):
    def __init__(self, **kwargs):
        """QuickForex API.

        Examples:

            api = Api()
            # Use the provider available by default (this is what you want in most cases)

            api = Api(provider_id="exchangerate.host", source="ecb")
            # Use a provider instance created from its identifier (and optional provider-specific settings overrides)

            api = Api(provider=existing_provider_instance)
            # Use a specific provider instance

        :param kwargs: Either:
            - provider (existing provider instance) argument
            - provider_id as well as any additional provider-specific settings
            - No argument (use the default provider)
        """
        self._provider = _create_provider(**kwargs)

    def get_latest_rate(self, *currency_pair_args: CurrencyPairType) -> Decimal:
        """Retrieve the last available rate for the given currency pair

        Examples:

            api.get_latest_rate("EUR/USD")
            api.get_latest_rate("EUR", "USD")
            api.get_latest_rate(("EUR", "USD"))
            api.get_latest_rate(CurrencyPair("EUR", "USD"))

        :param currency_pair_args: Currency pair in either format:
            - Single str argument "<domestic>/<foreign>": "EUR/USD"
            - Single str argument "<domestic:3><foreign:3>": "EURUSD"
            - Two str arguments "<domestic>", "<foreign>": "EUR", "USD"
            - Single tuple[str, str] argument ("<domestic>", "<foreign>"): ("EUR", "USD")
            - Single quickforex.CurrencyPair argument: quickforex.CurrencyPair("EUR", "USD")
        :return: Last exchange rate for the provided currency pair.
        """
        return self._provider.get_latest_rate(
            currency_pair=parse_currency_pair_args(*currency_pair_args)
        )

    def get_latest_rates(
        self, *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType]
    ) -> dict[CurrencyPair, Decimal]:
        """Retrieve the last available rate for each given currency pair

        Examples:

            api.get_latest_rates("EUR/USD", "EUR/GBP")
            api.get_latest_rates("EURUSD", "BTC/USDT")
            api.get_latest_rates(("EUR", "USD"), ("EUR", "GBP"))
            api.get_latest_rates(CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP"))
            api.get_latest_rates({CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")})
            api.get_latest_rates([CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")])
            api.get_latest_rates([CurrencyPair("EUR", "USD"), ("EUR", "GBP")])

        :param currency_pairs_args: List of currency pairs. Each individual argument can be:
            - str "<domestic>/<foreign>": "EUR/USD"
            - str "<domestic:3><foreign:3>": "EURUSD"
            - tuple[str, str] ("<domestic>", "<foreign>"): ("EUR", "USD")
            - quickforex.CurrencyPair: quickforex.CurrencyPair("EUR", "USD")
            - An iterable (list, set) with any of the previous argument type.
        :return: Last exchange rate for each provided currency pair.
        """
        return self._provider.get_latest_rates(
            currency_pairs=parse_currency_pairs_args(*currency_pairs_args)
        )

    def get_historical_rate(
        self, *currency_pair_args: CurrencyPairType, as_of: date
    ) -> Decimal:
        """Retrieve the exchange rate for the given currency pair at a given historical date.

        Examples:

            api.get_historical_rate("EUR/USD", as_of=date(year=2021, month=1, day=1))
            api.get_historical_rate("EURUSD", as_of=date(year=2021, month=1, day=1))
            api.get_historical_rate("EUR", "USD", as_of=date(year=2021, month=1, day=1))
            api.get_historical_rate(("EUR", "USD"), as_of=date(year=2021, month=1, day=1))
            api.get_historical_rate(CurrencyPair("EUR", "USD"), as_of=date(year=2021, month=1, day=1))

        :param currency_pair_args: Currency pair in either format:
            - Single str argument "<domestic>/<foreign>": "EUR/USD"
            - Single str argument "<domestic:3><foreign:3>": "EURUSD"
            - Two str arguments "<domestic>", "<foreign>": "EUR", "USD"
            - Single tuple[str, str] argument ("<domestic>", "<foreign>"): ("EUR", "USD")
            - Single quickforex.CurrencyPair argument: quickforex.CurrencyPair("EUR", "USD")
        :param as_of: Historical date
        :return: Historical exchange rate for the provided currency pair.
        """
        return self._provider.get_historical_rate(
            currency_pair=parse_currency_pair_args(*currency_pair_args), as_of=as_of
        )

    def get_historical_rates(
        self,
        *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType],
        as_of: date
    ) -> dict[CurrencyPair, Decimal]:
        """Retrieve the exchange rate for the given currency pair at a given historical date.
        :param currency_pairs_args: List of currency pairs. Each individual argument can be:
            - str "<domestic>/<foreign>": "EUR/USD"
            - str "<domestic:3><foreign:3>": "EURUSD"
            - tuple[str, str] ("<domestic>", "<foreign>"): ("EUR", "USD")
            - quickforex.CurrencyPair: quickforex.CurrencyPair("EUR", "USD")
            - An iterable (list, set) with any of the previous argument type.
        :param as_of: Historical date
        :return: Historical exchange rate for each provided currency pair.
        """
        return self._provider.get_historical_rates(
            currency_pairs=parse_currency_pairs_args(*currency_pairs_args), as_of=as_of
        )

    def get_rates_time_series(
        self,
        *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType],
        **date_range_kwargs: Union[DateRange, date]
    ) -> dict[CurrencyPair, dict[date, Decimal]]:
        """Retrieve the historical rates for one or more currency pairs between two dates.

        Examples:

            api.get_rates_time_series(
                "EUR/USD",
                start_date=date(year=2020, month=1, day=1),
                end_date=date(year=2021, month=1, day=1)
            )

            api.get_rates_time_series(
                "EUR/USD", "EURUSD"
                start_date=date(year=2020, month=1, day=1),
                end_date=date(year=2021, month=1, day=1)
            )

        :param currency_pairs_args: List of currency pairs. Each individual argument can be:
            - str "<domestic>/<foreign>": "EUR/USD"
            - str "<domestic:3><foreign:3>": "EURUSD"
            - tuple[str, str] ("<domestic>", "<foreign>"): ("EUR", "USD")
            - quickforex.CurrencyPair: quickforex.CurrencyPair("EUR", "USD")
            - An iterable (list, set) with any of the previous argument type.
        :param date_range_kwargs: Date range, can be either:
            - Single 'date_range' (type: quickforex.DateRange) argument
            - Both 'start_date' (type: datetime.date) and 'end_date' (type: datetime.date) arguments
        :return: Historical exchange rate for each provided currency pair for the provided date range.
        """
        return self._provider.get_rates_time_series(
            currency_pairs=parse_currency_pairs_args(*currency_pairs_args),
            date_range=parse_date_range_kwargs(**date_range_kwargs),
        )

    @property
    def provider_metadata(self) -> ProviderMetadata:
        return ProviderMetadata.from_provider_type(self._provider)


def get_latest_rate(*currency_pair_args: CurrencyPair) -> Decimal:
    """Retrieve the last available rate for the given currency pair

    Examples:

        quickforex.get_latest_rate("EUR/USD")
        quickforex.get_latest_rate("EUR", "USD")
        quickforex.get_latest_rate(("EUR", "USD"))
        quickforex.get_latest_rate(CurrencyPair("EUR", "USD"))

    :param currency_pair_args: Currency pair in either format:
        - Single str argument "<domestic>/<foreign>": "EUR/USD"
        - Single str argument "<domestic:3><foreign:3>": "EURUSD"
        - Two str arguments "<domestic>", "<foreign>": "EUR", "USD"
        - Single tuple[str, str] argument ("<domestic>", "<foreign>"): ("EUR", "USD")
        - Single quickforex.CurrencyPair argument: quickforex.CurrencyPair("EUR", "USD")
    :return: Last exchange rate for the provided currency pair.
    """
    return Api().get_latest_rate(*currency_pair_args)


def get_latest_rates(
    *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType]
) -> dict[CurrencyPair, Decimal]:
    """Retrieve the last available rate for each given currency pair

    Examples:

        quickforex.get_latest_rates("EUR/USD", "EUR/GBP")
        quickforex.get_latest_rates("EURUSD", "BTC/USDT")
        quickforex.get_latest_rates(("EUR", "USD"), ("EUR", "GBP"))
        quickforex.get_latest_rates(CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP"))
        quickforex.get_latest_rates({CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")})
        quickforex.get_latest_rates([CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")])
        quickforex.get_latest_rates([CurrencyPair("EUR", "USD"), ("EUR", "GBP")])

    :param currency_pairs_args: List of currency pairs. Each individual argument can be:
        - str "<domestic>/<foreign>": "EUR/USD"
        - str "<domestic:3><foreign:3>": "EURUSD"
        - tuple[str, str] ("<domestic>", "<foreign>"): ("EUR", "USD")
        - quickforex.CurrencyPair: quickforex.CurrencyPair("EUR", "USD")
        - An iterable (list, set) with any of the previous argument type.
    :return: Last exchange rate for each provided currency pair.
    """
    return Api().get_latest_rates(*currency_pairs_args)


def get_historical_rate(*currency_pair_args: CurrencyPairType, as_of: date) -> Decimal:
    """Retrieve the last available rate for the given currency pair
    :param currency_pair_args: Currency pair in either format:
        - Single str argument "<domestic>/<foreign>": "EUR/USD"
        - Two str arguments "<domestic>", "<foreign>": "EUR", "USD"
        - Single tuple[str, str] argument ("<domestic>", "<foreign>"): ("EUR", "USD")
        - Single quickforex.CurrencyPair argument: quickforex.CurrencyPair("EUR", "USD")
    :param as_of: Historical date
    :return: Historical exchange rate for the provided currency pair.
    """
    return Api().get_historical_rate(*currency_pair_args, as_of=as_of)


def get_historical_rates(
    *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType],
    as_of: date
) -> dict[CurrencyPair, Decimal]:
    """
    :param currency_pairs_args:
    :param as_of: Historical date
    :return: Historical exchange rate for each provided currency pair.
    """
    return Api().get_historical_rates(*currency_pairs_args, as_of=as_of)


def get_rates_time_series(
    *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType],
    **date_range_kwargs: Union[DateRange, date]
) -> dict[CurrencyPair, dict[date, Decimal]]:
    """Retrieve the historical rates for one or more currency pairs between two dates.
    :param currency_pairs_args: List of currency pairs. Each individual argument can be:
        - str "<domestic>/<foreign>": "EUR/USD"
        - str "<domestic:3><foreign:3>": "EURUSD"
        - tuple[str, str] ("<domestic>", "<foreign>"): ("EUR", "USD")
        - quickforex.CurrencyPair: quickforex.CurrencyPair("EUR", "USD")
        - An iterable (list, set) with any of the previous argument types.
    :param date_range_kwargs: Date range, can either be:
        - Single 'date_range' (type: quickforex.DateRange) argument
        - Both 'start_date' (type: datetime.date) and 'end_date' (type: datetime.date) arguments
    :return: Historical exchange rate for each provided currency pair for the provided date range.
    """
    return Api().get_rates_time_series(*currency_pairs_args, **date_range_kwargs)


def install_provider(provider: ProviderBase) -> None:
    """Install an alternative provider to query foreign exchange rates. Note that calling this function is not needed
        to use the QuickForex API because a provider is installed by default.

    :param provider: Installed provider.
    """
    global _INSTALLED_PROVIDER
    _INSTALLED_PROVIDER = provider


def install_provider_with_id(
    provider_id: str, settings_overrides: Optional[dict[str, Any]] = None
) -> None:
    """Install an alternative provider to query foreign exchange rates. Note that calling this function is not needed
        to use the QuickForex API because a provider is installed by default.

    Examples:

        quickforex.install_provider_with_id("exchangerate.host", decimal_places=8)

    :param provider_id: Installed provider.
    :param settings_overrides: Additional settings passed to the chosen provider.
    """
    install_provider(
        providers_factory.create_provider(
            provider_id=provider_id, settings_overrides=settings_overrides
        )
    )


def get_installed_provider() -> ProviderBase:
    """Retrieve the provider instance currently in use.

    :return: Currently installed provider
    """
    return _INSTALLED_PROVIDER


def get_default_provider_type() -> Type[ProviderBase]:
    """Retrieve the type of provider used by default.

    :return: Type of provider used by default
    """
    return _DEFAULT_PROVIDER
