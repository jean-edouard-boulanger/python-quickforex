from datetime import date, timedelta

import pytest

from quickforex.domain import CurrencyPair, DateRange


today = date.today()
yesterday = today - timedelta(days=1)


def test_construct_currency_pair():
    currency_pair = CurrencyPair("EUR", "USD")
    assert currency_pair.domestic == "EUR"
    assert currency_pair.foreign == "USD"


@pytest.mark.parametrize(
    "bad_args",
    [
        (),
        ("EUR",),
        ("EUR", "USD", "GBP"),
        ("EUR", None),
        (None, "GBP"),
        ("JPY", ""),
        ("", "JPY"),
        ("EUR", 1),
        (1, "GBP"),
    ],
)
def test_construct_currency_pair_bad_inputs(bad_args):
    with pytest.raises((ValueError, TypeError)):
        CurrencyPair(*bad_args)


def test_reverse_currency_pair():
    currency_pair = CurrencyPair("EUR", "USD").reversed()
    assert currency_pair.domestic == "USD"
    assert currency_pair.foreign == "EUR"


@pytest.mark.parametrize(
    "pair_str,expected",
    [
        ("EURUSD", CurrencyPair("EUR", "USD")),
        ("JPY/GBP", CurrencyPair("JPY", "GBP")),
        ("BTC/USDT", CurrencyPair("BTC", "USDT")),
    ],
)
def test_parse_currency_pair(pair_str: str, expected: CurrencyPair):
    assert CurrencyPair.parse(pair_str) == expected


@pytest.mark.parametrize(
    "bad_pair_str", ["", "EUR", "EURUS", "EUR/USD/BTC", "GBP/", "EUR//USD"]
)
def test_parse_currency_pair_bad_inputs(bad_pair_str):
    with pytest.raises(ValueError):
        CurrencyPair.parse(bad_pair_str)


@pytest.mark.parametrize(
    "start_date,end_date",
    [(yesterday, today), (today, today + timedelta(days=365)), (today, today)],
)
def test_construct_date_range(start_date: date, end_date: date):
    date_range = DateRange(start_date, end_date)
    assert date_range.start_date == start_date
    assert date_range.end_date == end_date


@pytest.mark.parametrize(
    "bad_args", [(), (today,), (today, yesterday), (yesterday, today, today)]
)
def test_construct_date_range(bad_args):
    with pytest.raises((ValueError, TypeError)):
        DateRange(*bad_args)


@pytest.mark.parametrize(
    "date_range",
    [
        DateRange(
            start_date=date(year=2021, month=1, day=1),
            end_date=date(year=2021, month=12, day=31),
        ),
        DateRange(start_date=today, end_date=today),
        DateRange(start_date=yesterday, end_date=today),
    ],
)
def test_iter_date_range(date_range: DateRange):
    all_dates = list(dt for dt in date_range)
    assert len(all_dates) == (date_range.end_date - date_range.start_date).days + 1
    for i in range(len(all_dates) - 1):
        assert all_dates[i] + timedelta(days=1) == all_dates[i + 1]
