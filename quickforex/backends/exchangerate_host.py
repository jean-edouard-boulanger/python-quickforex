from typing import Any, Optional, Iterable, Union
from collections import defaultdict
from datetime import date, datetime, timedelta
import requests

from quickforex.logger import get_module_logger
from quickforex.utils import make_date_range
from quickforex.backends.base import BackendBase
from quickforex.domain import (
    CurrencyPair,
    SymbolType,
    SymbolDescription,
    DateRange
)
import json


API_URL = "https://api.exchangerate.host"
DATE_FORMAT = "%Y-%m-%d"


logger = get_module_logger(__name__)


def _group_pairs_by_domestic_currency(pairs: set[CurrencyPair]) -> dict[SymbolType, list[SymbolType]]:
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
        next_date = min(current_date + timedelta(days=interval_days), date_range.end_date)
        yield DateRange(current_date, next_date)
        current_date = next_date + timedelta(days=1)


class Requester(object):
    def __init__(self, api_url: str):
        self._api_url = api_url

    @staticmethod
    def _handle_response(response: requests.Response) -> Any:
        response.raise_for_status()
        response_payload = response.json()
        logger.debug(f"received response {json.dumps(response_payload)}")
        if not response_payload["success"]:
            raise RuntimeError(f"received error response from exchangerate.host: {response_payload}")
        return response_payload

    def get(self, endpoint: str, params: Optional[dict[str, str]] = None) -> Any:
        resource_url = f"{self._api_url}/{endpoint}"
        logger.debug(f"sending request to {resource_url} with params={json.dumps(params)}")
        response = requests.get(resource_url, params=params)
        return self._handle_response(response)


class ExchangeRateHostBackend(BackendBase):
    """ Forex backend backed by exchangerate.host
    """
    def __init__(self, requester: Optional[Requester] = None):
        self._requester = requester or Requester(API_URL)

    def get_supported_symbols(self) -> list[SymbolDescription]:
        response = self._requester.get("symbols")
        return [
            SymbolDescription(
                symbol=item["code"],
                description=item["description"]
            )
            for item in response["symbols"].values()
        ]

    def _get_rates(self, currency_pairs: Iterable[CurrencyPair], as_of: Optional[date] = None):
        currency_pairs = set(pair for pair in currency_pairs)
        remaining_pairs = set(pair for pair in currency_pairs)
        groups = _group_pairs_by_domestic_currency(currency_pairs)
        rates: dict[CurrencyPair, float] = {}
        for domestic_currency, foreign_currencies in groups.items():
            response = self._requester.get(_format_date(as_of) if as_of else "latest", params={
                "base": domestic_currency,
                "symbols": ",".join(foreign_currencies)
            })
            base_currency = response["base"]
            if base_currency != domestic_currency:
                raise RuntimeError(f"api responded with unexpected base currency '{domestic_currency}'"
                                   f" (expected '{base_currency}')")
            for foreign_currency, rate in response["rates"].items():
                currency_pair = CurrencyPair(base_currency, foreign_currency)
                remaining_pairs.remove(currency_pair)
                rates[currency_pair] = rate
        if remaining_pairs:
            formatted_pairs = ", ".join(f"{pair.domestic}{pair.foreign}" for pair in remaining_pairs)
            raise RuntimeError(f"api did not return rate for the following currency pairs: {formatted_pairs}")
        return rates

    def get_latest_rates(self, currency_pairs: Iterable[CurrencyPair]) -> dict[CurrencyPair, float]:
        return self._get_rates(currency_pairs)

    def get_historical_rates(self,
                             currency_pairs: Iterable[CurrencyPair],
                             as_of: date) -> dict[CurrencyPair, float]:
        return self._get_rates(currency_pairs, as_of)

    def get_rates_time_series(self,
                              currency_pairs: Union[Iterable[CurrencyPair], CurrencyPair],
                              *date_range_args: Union[
                                  DateRange, date,
                                  tuple[date, date]
                              ]) -> dict[CurrencyPair, dict[date, float]]:
        date_range = make_date_range(*date_range_args)
        assert date_range.end_date <= date.today()
        currency_pairs = [currency_pairs] if isinstance(currency_pairs, CurrencyPair) else currency_pairs
        currency_pairs = set(pair for pair in currency_pairs)
        groups = _group_pairs_by_domestic_currency(currency_pairs)
        series: dict[CurrencyPair, dict[date, float]] = defaultdict(dict)
        for current_range in _iter_date_range_chunks(date_range, interval_days=365):
            for domestic_currency, foreign_currencies in groups.items():
                response = self._requester.get("timeseries", params={
                    "start_date": _format_date(current_range.start_date),
                    "end_date": _format_date(current_range.end_date),
                    "base": domestic_currency,
                    "symbols": ",".join(foreign_currencies)
                })
                for date_str, rates_by_symbol in response["rates"].items():
                    current_date = _parse_date(date_str)
                    for foreign_currency, rate in rates_by_symbol.items():
                        currency_pair = CurrencyPair(domestic_currency, foreign_currency)
                        series[currency_pair][current_date] = rate
        return series
