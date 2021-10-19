from typing import Any, Optional, Iterable
from dataclasses import dataclass
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal

from quickforex.providers.factory import registered_provider
from quickforex.providers.base import ProviderBase
from quickforex.http_requester import HttpRequesterBase
from quickforex.errors import QuickForexError
from quickforex.logger import get_module_logger
from quickforex.domain import CurrencyPair, SymbolType, DateRange


API_URL = "https://api.exchangerate.host"
DATE_FORMAT = "%Y-%m-%d"
DECIMAL_PLACES = 6


logger = get_module_logger(__name__)


def _group_pairs_by_domestic_currency(
    pairs: set[CurrencyPair],
) -> dict[SymbolType, list[SymbolType]]:
    groups: dict[SymbolType, list[SymbolType]] = defaultdict(list)
    for pair in pairs:
        groups[pair.domestic].append(pair.foreign)
    return groups


def _format_date(dt: date) -> str:
    return dt.strftime(DATE_FORMAT)


def _parse_date(dt_str: str) -> date:
    return datetime.strptime(dt_str, DATE_FORMAT).date()


def _iter_date_range_chunks(date_range: DateRange, interval_days: int):
    assert date_range.start_date <= date_range.end_date
    assert interval_days > 0
    current_date = date_range.start_date
    while current_date < date_range.end_date:
        next_date = min(
            current_date + timedelta(days=interval_days), date_range.end_date
        )
        yield DateRange(current_date, next_date)
        current_date = next_date + timedelta(days=1)


class Requester(HttpRequesterBase):
    def __init__(self, api_url: str):
        super().__init__(api_url)

    def response_check_hook(self, response_payload: Any) -> None:
        if not response_payload["success"]:
            raise QuickForexError(
                f"received error response from exchangerate.host: {response_payload}"
            )


@dataclass
class Settings:
    decimal_places: int = 6
    source: Optional[str] = None


@registered_provider
class ExchangeRateHostProvider(ProviderBase):
    """Provider backed by exchangerate.host"""

    identifier = "exchangerate.host"

    def __init__(
        self, requester: Optional[Requester] = None, settings: Optional[Settings] = None
    ):
        self._requester = requester or Requester(API_URL)
        self._settings = settings or Settings()

    def _get_rates(
        self, currency_pairs: Iterable[CurrencyPair], as_of: Optional[date] = None
    ):
        currency_pairs = set(pair for pair in currency_pairs)
        remaining_pairs = set(pair for pair in currency_pairs)
        groups = _group_pairs_by_domestic_currency(currency_pairs)
        rates: dict[CurrencyPair, Decimal] = {}
        for domestic_currency, foreign_currencies in groups.items():
            response = self._requester.get(
                _format_date(as_of) if as_of else "latest",
                params={
                    "base": domestic_currency,
                    "symbols": ",".join(foreign_currencies),
                    "places": DECIMAL_PLACES,
                },
            )
            base_currency = response["base"]
            if base_currency != domestic_currency:
                raise QuickForexError(
                    f"server responded with unexpected base currency '{base_currency}'"
                    f" (expected '{domestic_currency}')"
                )
            for foreign_currency, rate in response["rates"].items():
                currency_pair = CurrencyPair(base_currency, foreign_currency)
                remaining_pairs.remove(currency_pair)
                rates[currency_pair] = Decimal(rate)
        if remaining_pairs:
            formatted_pairs = ", ".join(
                f"{pair.domestic}{pair.foreign}" for pair in remaining_pairs
            )
            raise QuickForexError(
                f"server did not return rate for the following currency pairs: {formatted_pairs}"
            )
        return rates

    def get_latest_rates(
        self, currency_pairs: Iterable[CurrencyPair]
    ) -> dict[CurrencyPair, Decimal]:
        return self._get_rates(currency_pairs)

    def get_latest_rate(self, currency_pair: CurrencyPair) -> Decimal:
        return self.get_latest_rates([currency_pair])[currency_pair]

    def get_historical_rates(
        self, currency_pairs: Iterable[CurrencyPair], as_of: date
    ) -> dict[CurrencyPair, Decimal]:
        return self._get_rates(currency_pairs, as_of)

    def get_historical_rate(self, currency_pair: CurrencyPair, as_of: date) -> Decimal:
        return self.get_historical_rates([currency_pair], as_of)[currency_pair]

    def get_rates_time_series(
        self, currency_pairs: Iterable[CurrencyPair], date_range: DateRange
    ) -> dict[CurrencyPair, dict[date, Decimal]]:
        assert date_range.end_date <= date.today()
        currency_pairs = (
            [currency_pairs]
            if isinstance(currency_pairs, CurrencyPair)
            else currency_pairs
        )
        currency_pairs = set(pair for pair in currency_pairs)
        groups = _group_pairs_by_domestic_currency(currency_pairs)
        series: dict[CurrencyPair, dict[date, Decimal]] = defaultdict(dict)
        for current_range in _iter_date_range_chunks(date_range, interval_days=365):
            for domestic_currency, foreign_currencies in groups.items():
                response = self._requester.get(
                    "timeseries",
                    params={
                        "start_date": _format_date(current_range.start_date),
                        "end_date": _format_date(current_range.end_date),
                        "base": domestic_currency,
                        "symbols": ",".join(foreign_currencies),
                        "places": DECIMAL_PLACES,
                    },
                )
                for date_str, rates_by_symbol in response["rates"].items():
                    current_date = _parse_date(date_str)
                    for foreign_currency, rate in rates_by_symbol.items():
                        currency_pair = CurrencyPair(
                            domestic_currency, foreign_currency
                        )
                        series[currency_pair][current_date] = Decimal(rate)
        return series
