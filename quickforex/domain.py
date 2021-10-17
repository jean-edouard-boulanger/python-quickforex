from typing import Tuple, Union, Iterator
from dataclasses import dataclass
from datetime import date, timedelta


SymbolType = str


@dataclass(frozen=True)
class CurrencyPair:
    domestic: SymbolType
    foreign: SymbolType

    def reversed(self) -> "CurrencyPair":
        return CurrencyPair(domestic=self.foreign, foreign=self.domestic)

    def __post_init__(self) -> None:
        if not isinstance(self.domestic, SymbolType):
            raise TypeError(
                f"invalid currency pair: domestic currency ({self.domestic})"
                f" has unexpected type {type(self.domestic).__name__}, expected {SymbolType.__name__}"
            )
        if not isinstance(self.foreign, SymbolType):
            raise TypeError(
                f"invalid currency pair: domestic currency ({self.foreign})"
                f" has unexpected type {type(self.foreign).__name__}, expected {SymbolType.__name__}"
            )
        if not self.domestic or not self.foreign:
            raise ValueError(
                f"invalid currency pair {self}: domestic and foreign currency must both be defined"
            )


@dataclass(frozen=True)
class DateRange:
    start_date: date
    end_date: date

    def __post_init__(self) -> None:
        if not isinstance(self.start_date, date):
            raise TypeError(
                f"start date ({self.start_date}) has unexpected type {type(self.start_date).__name__},"
                f" expected date instead"
            )
        if not isinstance(self.start_date, date):
            raise ValueError(
                f"end date ({self.end_date}) has unexpected type {type(self.end_date).__name__},"
                f" expected date instead"
            )
        if self.start_date > self.end_date:
            raise ValueError(
                f"Invalid date range {self}: start date must be before or the same as end date"
            )

    def __len__(self) -> int:
        return (self.end_date - self.start_date).days + 1

    def __getitem__(self, index: int) -> date:
        if index >= len(self):
            raise IndexError(str(index))
        return self.start_date + timedelta(days=index)

    def __contains__(self, dt: date) -> bool:
        return self.start_date <= dt <= self.end_date

    def __iter__(self) -> Iterator[date]:
        current_date = self.start_date
        while current_date <= self.end_date:
            yield current_date
            current_date += timedelta(days=1)


DateRangeType = Union[DateRange, Tuple[date, date]]


CurrencyPairType = Union[CurrencyPair, Tuple[str, str], str]
