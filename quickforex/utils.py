from typing import Union, Iterable, Any, Type
from datetime import date
import dataclasses
import typing
import json

from quickforex.domain import DateRange, CurrencyPairType, CurrencyPair


def currency_pair_of_tuple(ccy_pair: tuple[str, str]) -> CurrencyPair:
    error_message = (
        f"'{ccy_pair}' tuple is not a valid currency pair"
        f" (expected: '(<domestic:string>, <foreign:string>)')"
    )
    assert isinstance(ccy_pair, tuple)
    if len(ccy_pair) != 2:
        raise ValueError(error_message)
    return CurrencyPair(*ccy_pair)


def make_currency_pair(ccy_pair: CurrencyPairType) -> CurrencyPair:
    if isinstance(ccy_pair, CurrencyPair):
        return ccy_pair
    if isinstance(ccy_pair, str):
        return CurrencyPair.parse(ccy_pair)
    if isinstance(ccy_pair, tuple):
        return currency_pair_of_tuple(ccy_pair)
    raise ValueError(
        f"could not create currency pair from object '{ccy_pair}': unsupported format"
    )


def parse_currency_pairs_args(
    *currency_pairs_args: Union[Iterable[CurrencyPairType], CurrencyPairType]
) -> set[CurrencyPair]:
    currency_pairs: set[CurrencyPair] = set()
    for item in currency_pairs_args:
        print(type(item))
        if isinstance(item, (CurrencyPair, str, tuple)):
            currency_pairs.add(make_currency_pair(item))
        elif isinstance(item, Iterable):
            for sub_item in item:
                currency_pairs.add(make_currency_pair(sub_item))
        else:
            raise ValueError(
                f"invalid currency pair argument {item}, expected iterable, found {type(item).__name__}"
            )
    return currency_pairs


def parse_currency_pair_args(*currency_pair_args: CurrencyPairType) -> CurrencyPair:
    args_count = len(currency_pair_args)
    if args_count not in {1, 2}:
        raise ValueError(
            f"invalid number of arguments ({args_count}) to form a single currency pair, expected"
            f" either 2 arguments or type str ('EUR', 'USD') or a single argument of type"
            f" quickforex.CurrencyPair or str ('EUR/USD') or tuple[str, str] (tuple('EUR', 'USD'))."
            f" This was found instead: {currency_pair_args}"
        )
    if args_count == 2:
        return CurrencyPair(*currency_pair_args)
    return make_currency_pair(currency_pair_args[0])


def filter_kwargs(keep_args: Iterable[str], kwargs: dict[str, Any]) -> dict[str, Any]:
    return {arg: kwargs[arg] for arg in set(keep_args) if arg in kwargs}


def parse_date_range_kwargs(**kwargs: Union[DateRange, date]) -> DateRange:
    date_range_arg = "date_range"
    start_date_arg = "start_date"
    end_date_arg = "end_date"
    date_range_kwargs = filter_kwargs(
        keep_args=[date_range_arg, start_date_arg, end_date_arg], kwargs=kwargs
    )
    error_message = (
        f"invalid arguments ({date_range_kwargs}) to form a date range. Expected either argument '{date_range_arg}' to"
        f" be set to a quickforex.DateRange object or '{start_date_arg}' and '{end_date_arg}' to be set to date"
        f" objects."
    )
    if date_range_arg in date_range_kwargs:
        if start_date_arg in date_range_kwargs or end_date_arg in date_range_kwargs:
            raise ValueError(error_message)
        return date_range_kwargs[date_range_arg]
    if start_date_arg not in date_range_kwargs or end_date_arg not in date_range_kwargs:
        raise ValueError(error_message)
    return DateRange(
        start_date=date_range_kwargs[start_date_arg],
        end_date=date_range_kwargs[end_date_arg],
    )


def pretty_dump(data: Any) -> str:
    return json.dumps(data, indent=4)


def is_optional_type(t: Type) -> bool:
    return typing.get_origin(t) is Union and type(None) in typing.get_args(t)


def extract_optional_type(t: Type) -> Type:
    assert is_optional_type(t)
    return typing.get_args(t)[0]


def dataclass_field_has_default(field: dataclasses.Field) -> bool:
    return (
        field.default != dataclasses.MISSING
        or field.default_factory != dataclasses.MISSING
    )


def is_dataclass_field_required(field: dataclasses.Field) -> bool:
    return not dataclass_field_has_default(field)


def get_dataclass_field_default_value(field: dataclasses.Field) -> Any:
    if field.default != dataclasses.MISSING:
        return field.default
    if field.default_factory != dataclasses.MISSING:
        return field.default_factory()
    raise ValueError(f"dataclass field {field.name} does not have a default value")
