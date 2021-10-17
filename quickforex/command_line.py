from typing import Protocol, Any
from collections import defaultdict
from argparse import ArgumentParser, ArgumentTypeError
from datetime import date, datetime
from decimal import Decimal
import enum
import json

from quickforex.backend import BackendBase, ExchangeRateHostBackend
from quickforex import CurrencyPair, DateRange

DATE_FORMAT = "%Y-%m-%d"
DATE_FORMAT_HUMAN = "yyyy-mm-dd, 2021-12-31"


class OutputFormat(enum.Enum):
    TABLE = enum.auto()
    JSON = enum.auto()
    JSON_PRETTY = enum.auto()
    CSV = enum.auto()

    @staticmethod
    def parse(format_str: str) -> "OutputFormat":
        mapping = {
            "table": OutputFormat.TABLE,
            "json": OutputFormat.JSON,
            "json:pretty": OutputFormat.JSON_PRETTY,
            "csv": OutputFormat.CSV,
        }
        format_str = format_str.strip().lower()
        if format_str not in mapping:
            raise ArgumentTypeError(f"unexpected formatter type: {format_str}")
        return mapping[format_str]


class Formatter(Protocol):
    def format_rates(self, rates: dict[CurrencyPair, Decimal]) -> str:
        ...

    def format_rates_time_series(
        self, time_series: dict[CurrencyPair, dict[date, Decimal]]
    ) -> str:
        ...


class JSONFormatter(Formatter):
    def __init__(self, pretty: bool = False):
        self._pretty = pretty

    def _json_dumps(self, data: Any) -> str:
        return json.dumps(data, indent=4 if self._pretty else 0, sort_keys=True)

    def format_rates(self, rates: dict[CurrencyPair, Decimal]) -> str:
        output: dict[str, dict[str, float]] = defaultdict(dict)
        for pair, rate in rates.items():
            output[pair.domestic][pair.foreign] = float(rate)
        return self._json_dumps(output)

    def format_rates_time_series(
        self, time_series: dict[CurrencyPair, dict[date, Decimal]]
    ) -> str:
        output: dict[str, dict[str, dict[str, float]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        for pair, series in time_series.items():
            for dt, rate in series.items():
                output[pair.domestic][pair.foreign][dt.strftime(DATE_FORMAT)] = float(
                    rate
                )
        return self._json_dumps(output)


class FormatterFactory(object):
    @staticmethod
    def create(output_format: OutputFormat) -> Formatter:
        return {
            OutputFormat.JSON: lambda: JSONFormatter(pretty=False),
            OutputFormat.JSON_PRETTY: lambda: JSONFormatter(pretty=True),
        }[output_format]()


def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def parse_currency_pairs(pairs_str: list[str]) -> set[CurrencyPair]:
    pairs: list[CurrencyPair] = []
    for pair_str in pairs_str:
        if "," in pair_str:
            pairs += list(parse_currency_pairs(pair_str.split(",")))
        else:
            pairs.append(CurrencyPair.parse(pair_str.strip()))
    return set(pairs)


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="QuickForex command line tool: fetch exchange rates from the command line"
    )
    parser.add_argument(
        "--format",
        default=OutputFormat.JSON_PRETTY,
        help="Output format (default: JSON)",
    )
    modes_parser = parser.add_subparsers(dest="mode", help="QuickForex mode")
    last_mode_parser = modes_parser.add_parser(
        "last",
        help="Retrieve the last available exchange rate for the provided currency pair.s",
    )
    currency_pairs_kwargs = {
        "type": str,
        "nargs": "+",
        "help": (
            f"List of currency pairs (format: {CurrencyPair.HUMAN_READABLE_STR_FORMAT}),"
            f" space and/or comma-separated."
        ),
    }
    last_mode_parser.add_argument("currency_pairs", **currency_pairs_kwargs)
    hist_mode_parser = modes_parser.add_parser(
        "history",
        help="Retrieve the exchange rate(s) for the provided currency pair(s) at a given historical date.",
    )
    hist_mode_parser.add_argument("currency_pairs", **currency_pairs_kwargs)
    hist_mode_parser.add_argument(
        "--date",
        type=parse_date,
        dest="as_of",
        required=True,
        help=f"Historical date (format: {DATE_FORMAT_HUMAN})",
    )
    series_mode_parser = modes_parser.add_parser(
        "series",
        help="Retrieve all the exchange rates for the provided currency pair(s) between two dates.",
    )
    series_mode_parser.add_argument("currency_pairs", **currency_pairs_kwargs)
    series_mode_parser.add_argument(
        "--from",
        dest="start_date",
        type=parse_date,
        required=True,
        help=f"First date (format: {DATE_FORMAT_HUMAN})",
    )
    series_mode_parser.add_argument(
        "--to",
        dest="end_date",
        type=parse_date,
        default=date.today(),
        help=f"Last date (format: {DATE_FORMAT_HUMAN}",
    )
    return parser


def last_mode_entrypoint(
    settings: Any,
    currency_pairs: set[CurrencyPair],
    backend: BackendBase,
    output_formatter: Formatter,
) -> str:
    rates = backend.get_latest_rates(currency_pairs)
    return output_formatter.format_rates(rates)


def hist_mode_entrypoint(
    settings: Any,
    currency_pairs: set[CurrencyPair],
    backend: BackendBase,
    output_formatter: Formatter,
):
    rates = backend.get_historical_rates(
        currency_pairs=currency_pairs, as_of=settings.as_of
    )
    return output_formatter.format_rates(rates)


def series_mode_entrypoint(
    settings: Any,
    currency_pairs: set[CurrencyPair],
    backend: BackendBase,
    output_formatter: Formatter,
):
    series = backend.get_rates_time_series(
        currency_pairs=currency_pairs,
        date_range=DateRange(
            start_date=settings.start_date, end_date=settings.end_date
        ),
    )
    return output_formatter.format_rates_time_series(series)


def main():
    parser = create_parser()
    settings = parser.parse_args()
    if not settings.mode:
        parser.error("Please select a mode")
    currency_pairs = parse_currency_pairs(settings.currency_pairs)
    output_formatter = FormatterFactory.create(settings.format)
    mode_entrypoint = {
        "last": last_mode_entrypoint,
        "history": hist_mode_entrypoint,
        "series": series_mode_entrypoint,
    }[settings.mode]
    print(
        mode_entrypoint(
            settings=settings,
            currency_pairs=currency_pairs,
            backend=ExchangeRateHostBackend(),
            output_formatter=output_formatter,
        )
    )


if __name__ == "__main__":
    main()
