from typing import Optional, Type
from datetime import date, timedelta
import dataclasses

import pytest

from quickforex.domain import DateRange, CurrencyPair
from quickforex.utils import (
    get_dataclass_field_default_value,
    dataclass_field_has_default,
    is_dataclass_field_required,
    is_optional_type,
    extract_optional_type,
    parse_currency_pairs_args,
    parse_date_range_kwargs,
    parse_currency_pair_args,
    currency_pair_of_tuple,
    filter_kwargs,
)


today = date.today()
yesterday = today - timedelta(days=1)


@pytest.fixture()
def test_dataclass() -> tuple[Type, dict[str, dataclasses.Field]]:
    @dataclasses.dataclass
    class TestDC:
        field0: bool
        field1: int = 1
        field2: str = dataclasses.field(default_factory=lambda: "test")

    return TestDC, {f.name: f for f in dataclasses.fields(TestDC)}


def test_currency_pair_of_tuple():
    assert currency_pair_of_tuple(("EUR", "USD")) == CurrencyPair("EUR", "USD")


@pytest.mark.parametrize("bad_input", [(), ("EUR",), ("EUR", "USD", "GBP"), ("EUR", 2)])
def test_currency_pair_of_tuple_bad_inputs(bad_input):
    with pytest.raises((ValueError, TypeError)):
        currency_pair_of_tuple(bad_input)


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


def test_get_dataclass_field_default_value(test_dataclass):
    _, fields = test_dataclass
    with pytest.raises(ValueError):
        get_dataclass_field_default_value(fields["field0"])
    assert get_dataclass_field_default_value(fields["field1"]) == 1
    assert get_dataclass_field_default_value(fields["field2"]) == "test"


@pytest.mark.parametrize(
    "t,expected",
    [
        (int, False),
        (type(None), False),
        (str, False),
        (Optional[int], True),
        (Optional[list[int]], True),
    ],
)
def test_is_optional_type(t: Type, expected: bool):
    assert is_optional_type(t) is expected


@pytest.mark.parametrize(
    "t,expected",
    [(Optional[int], int), (Optional[str], str), (Optional[list[int]], list[int])],
)
def test_extract_optional_type(t: Type, expected: Type):
    assert extract_optional_type(t) == expected


def test_dataclass_field_has_default(
    test_dataclass: tuple[Type, dict[str, dataclasses.Field]]
):
    _, fields = test_dataclass
    assert not dataclass_field_has_default(fields["field0"])
    assert dataclass_field_has_default(fields["field1"])
    assert dataclass_field_has_default(fields["field2"])


def test_is_dataclass_field_required(
    test_dataclass: tuple[Type, dict[str, dataclasses.Field]]
):
    _, fields = test_dataclass
    assert is_dataclass_field_required(fields["field0"])
    assert not is_dataclass_field_required(fields["field1"])
    assert not is_dataclass_field_required(fields["field2"])
