from datetime import date, timedelta

import pytest

from quickforex.domain import DateRange, CurrencyPair
from quickforex.utils import (
    parse_currency_pairs_args,
    parse_date_range_kwargs,
    parse_currency_pair_args,
    currency_pair_of_tuple,
    currency_pair_of_str,
    filter_kwargs,
)


today = date.today()
yesterday = today - timedelta(days=1)


def test_currency_pair_of_tuple():
    assert currency_pair_of_tuple(("EUR", "USD")) == CurrencyPair("EUR", "USD")


@pytest.mark.parametrize("bad_input", [(), ("EUR",), ("EUR", "USD", "GBP"), ("EUR", 2)])
def test_currency_pair_of_tuple_bad_inputs(bad_input):
    with pytest.raises((ValueError, TypeError)):
        currency_pair_of_tuple(bad_input)


def test_currency_pair_of_str():
    assert currency_pair_of_str("EUR/USD") == CurrencyPair("EUR", "USD")


@pytest.mark.parametrize("bad_input", ["", "EUR", "EUR/", "EUR/USD/GBP"])
def test_currency_pair_of_str_bad_inputs(bad_input: str):
    with pytest.raises((ValueError, TypeError)):
        currency_pair_of_str(bad_input)


@pytest.mark.parametrize(
    "args,expected",
    [
        ((CurrencyPair("EUR", "USD"),), CurrencyPair("EUR", "USD")),
        (("EUR", "USD"), CurrencyPair("EUR", "USD")),
        (("EUR/GBP",), CurrencyPair("EUR", "GBP")),
        ((("GBP", "JPY"),), CurrencyPair("GBP", "JPY")),
    ],
)
def test_parse_currency_pair_args(args, expected: CurrencyPair):
    assert parse_currency_pair_args(*args) == expected


@pytest.mark.parametrize(
    "bad_args", [(), ("EUR",), ("EUR", "USD", "GBP"), (b"EUR", b"USD")]
)
def test_parse_currency_pair_args_bad_inputs(bad_args):
    with pytest.raises((ValueError, TypeError)):
        parse_currency_pair_args(*bad_args)


@pytest.mark.parametrize(
    "args,expected",
    [
        ((), set()),
        (([],), set()),
        (([], []), set()),
        ((["EUR/USD"],), {CurrencyPair("EUR", "USD")}),
        (
            (["EUR/USD", ("EUR", "GBP")],),
            {CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")},
        ),
        (
            (["EUR/USD", ("EUR", "GBP"), CurrencyPair("JPY", "NOK")],),
            {
                CurrencyPair("EUR", "USD"),
                CurrencyPair("EUR", "GBP"),
                CurrencyPair("JPY", "NOK"),
            },
        ),
        (("EUR/USD",), {CurrencyPair("EUR", "USD")}),
        (
            ("EUR/USD", "EUR/GBP"),
            {CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")},
        ),
        (
            ("EUR/USD", ("EUR", "GBP")),
            {CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")},
        ),
        (
            ("EUR/USD", ("EUR", "GBP"), CurrencyPair("USD", "JPY")),
            {
                CurrencyPair("EUR", "USD"),
                CurrencyPair("EUR", "GBP"),
                CurrencyPair("USD", "JPY"),
            },
        ),
        (
            (CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")),
            {CurrencyPair("EUR", "USD"), CurrencyPair("EUR", "GBP")},
        ),
        (
            ("EUR/USD", ["EUR/GBP", CurrencyPair("GBP", "EUR")], ("JPY", "NOK")),
            {
                CurrencyPair("EUR", "USD"),
                CurrencyPair("EUR", "GBP"),
                CurrencyPair("GBP", "EUR"),
                CurrencyPair("JPY", "NOK"),
            },
        ),
    ],
)
def test_parse_currency_pairs_args(args, expected):
    assert parse_currency_pairs_args(*args) == expected


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({"start_date": yesterday, "end_date": today}, DateRange(yesterday, today)),
        (
            {"start_date": yesterday, "end_date": today, "unrelated": None},
            DateRange(yesterday, today),
        ),
        ({"date_range": DateRange(yesterday, today)}, DateRange(yesterday, today)),
        (
            {"date_range": DateRange(yesterday, today), "unrelated": None},
            DateRange(yesterday, today),
        ),
    ],
)
def test_parse_date_range_kwargs(kwargs, expected: DateRange):
    assert parse_date_range_kwargs(**kwargs) == expected


@pytest.mark.parametrize(
    "bad_kwargs",
    [
        {"start_date": today, "end_date": yesterday},
        {
            "start_date": yesterday,
            "end_date": today,
            "date_range": DateRange(yesterday, today),
        },
        {"start_date": yesterday},
        {"end_date": yesterday},
        {"unrelated": None},
    ],
)
def test_parse_date_range_kwargs_bad_inputs(bad_kwargs):
    with pytest.raises(ValueError):
        parse_date_range_kwargs(**bad_kwargs)


@pytest.mark.parametrize(
    "input_kwargs,keep_kwargs,expected_kwargs",
    [
        ({}, [], {}),
        ({"k1": "v1"}, ["k1"], {"k1": "v1"}),
        ({}, ["k1", "k2", "k3"], {}),
        ({"k1": "v1", "k2": "v2", "k3": "v3"}, ["k1", "k3"], {"k1": "v1", "k3": "v3"}),
        ({"k1": "v1", "k2": "v2", "k3": "v3"}, ["k2", "k4"], {"k2": "v2"}),
        ({"k1": "v1", "k2": "v2", "k3": "v3"}, ["k4", "k5"], {}),
    ],
)
def test_filter_kwargs(input_kwargs, keep_kwargs, expected_kwargs):
    output_kwargs = filter_kwargs(keep_kwargs, input_kwargs)
    assert output_kwargs == expected_kwargs
