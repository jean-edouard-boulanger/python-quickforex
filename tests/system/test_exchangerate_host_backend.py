from datetime import date
from decimal import Decimal

import pytest

from quickforex.domain import CurrencyPair, DateRange
from quickforex.backend.exchangerate_host import ExchangeRateHostBackend


BackendType = ExchangeRateHostBackend
HISTORICAL_DATE = date(year=2020, month=2, day=5)
HISTORICAL_RANGE = DateRange(
    date(year=2019, month=1, day=1), date(year=2021, month=1, day=1)
)


@pytest.fixture
def backend() -> BackendType:
    return BackendType()


def assert_valid_rate(rate: Decimal):
    assert isinstance(rate, Decimal)
    assert rate > 0


def assert_valid_rates(
    requested_rates: set[CurrencyPair], rates: dict[CurrencyPair, Decimal]
):
    assert isinstance(rates, dict)
    assert len(rates) == len(requested_rates)
    assert all(pair in rates for pair in requested_rates)
    [assert_valid_rate(rate) for rate in rates.values()]


def assert_valid_rate_series(
    requested_date_range: DateRange, series: dict[date, Decimal]
):
    expected_dates = list(dt for dt in requested_date_range)
    assert len(series) == len(expected_dates)
    assert list(series.keys()) == expected_dates
    [assert_valid_rate(rate) for rate in series.values()]


def test_get_latest_rates(backend: BackendType):
    currency_pairs = {
        CurrencyPair("EUR", "USD"),
        CurrencyPair("EUR", "JPY"),
        CurrencyPair("GBP", "AUD"),
    }
    rates = backend.get_latest_rates(currency_pairs=currency_pairs)
    assert_valid_rates(requested_rates=currency_pairs, rates=rates)


def test_get_latest_rate(backend: BackendType):
    currency_pair = CurrencyPair("EUR", "USD")
    rate = backend.get_latest_rate(currency_pair)
    assert_valid_rate(rate)


def test_get_historical_rates(backend: BackendType):
    currency_pairs = {
        CurrencyPair("EUR", "USD"),
        CurrencyPair("EUR", "JPY"),
        CurrencyPair("GBP", "AUD"),
    }
    rates = backend.get_historical_rates(
        currency_pairs=currency_pairs, as_of=HISTORICAL_DATE
    )
    assert_valid_rates(requested_rates=currency_pairs, rates=rates)


def test_get_historical_rate(backend: BackendType):
    currency_pair = CurrencyPair("EUR", "USD")
    rate = backend.get_historical_rate(
        currency_pair=currency_pair, as_of=HISTORICAL_DATE
    )
    assert_valid_rate(rate)


def test_get_rates_time_series(backend: BackendType):
    currency_pairs = {
        CurrencyPair("EUR", "USD"),
        CurrencyPair("EUR", "JPY"),
        CurrencyPair("GBP", "AUD"),
    }
    rates = backend.get_rates_time_series(
        currency_pairs=currency_pairs, date_range=HISTORICAL_RANGE
    )
    assert len(rates) == len(currency_pairs)
    assert all(pair in rates for pair in currency_pairs)
    [assert_valid_rate_series(HISTORICAL_RANGE, series) for series in rates.values()]
