from quickforex.providers import (
    ProviderBase,
    ProviderMetadata,
    SettingFieldDescription,
    ExchangeRateHostProvider,
)
from quickforex.errors import QuickForexError
from quickforex.domain import CurrencyPair, DateRange
from quickforex.api import (
    Api,
    get_latest_rates,
    get_latest_rate,
    get_historical_rates,
    get_historical_rate,
    get_rates_time_series,
    get_default_provider_type,
    get_installed_provider,
    install_provider,
    install_provider_with_id,
)


__version__ = "0.1.2"


__all__ = [
    "Api",
    "get_latest_rates",
    "get_latest_rate",
    "get_historical_rates",
    "get_historical_rate",
    "get_rates_time_series",
    "get_default_provider_type",
    "get_installed_provider",
    "install_provider",
    "install_provider_with_id",
    "CurrencyPair",
    "DateRange",
    "ProviderBase",
    "ProviderMetadata",
    "SettingFieldDescription",
    "ExchangeRateHostProvider",
    "QuickForexError",
]
