from typing import Union
from datetime import date

from quickforex.domain import DateRange


def make_date_range(*date_range_args: Union[ DateRange, date, tuple[date, date]]) -> DateRange:
    if len(date_range_args) == 1 and isinstance(date_range_args[0], DateRange):
        return date_range_args[0]
    if len(date_range_args) == 1 and isinstance(date_range_args[0], tuple):
        assert len(date_range_args[0]) == 2
        return DateRange(*date_range_args[0])
    assert len(date_range_args) == 2
    return DateRange(date_range_args[0], date_range_args[1])
