from typing import Tuple, Union
from dataclasses import dataclass
from datetime import date

SymbolType = str


@dataclass(frozen=True)
class SymbolDescription:
    symbol: SymbolType
    description: str


@dataclass(frozen=True)
class CurrencyPair:
    domestic: SymbolType
    foreign: SymbolType


@dataclass(frozen=True)
class DateRange:
    start_date: date
    end_date: date


DateRangeType = Union[DateRange, Tuple[date, date]]


def get_date_range(date_range: DateRangeType) -> DateRange:
    if isinstance(date_range, tuple):
        return DateRange(*date_range)
    assert isinstance(date_range, DateRange)
    return date_range
