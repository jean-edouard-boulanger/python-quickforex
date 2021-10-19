from typing import Protocol, Any
from collections import defaultdict
from argparse import ArgumentParser, ArgumentTypeError
from datetime import date, datetime
from decimal import Decimal
import enum
import json
import sys

from quickforex.providers.factory import ProviderMetadata
from quickforex.providers.base import ProviderBase
from quickforex.providers.exchangerate_host import ExchangeRateHostProvider
from quickforex.providers.dummy import DummyProvider
from quickforex.providers import factory as providers_factory
from quickforex.domain import CurrencyPair, DateRange

DATE_FORMAT = "%Y-%m-%d"
DATE_FORMAT_HUMAN = "yyyy-mm-dd, 2021-12-31"
PROVIDER_SETTINGS_HUMAN = "provider_id:field1:value1:field2:value2 (example: fcsapi:api_key:g2j3hg4nbv42h3g42kjg)"


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

    def format_providers(self, providers: list[ProviderMetadata]) -> str:
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

    def format_providers(self, providers: list[ProviderMetadata]) -> str:
        return self._json_dumps(
            {
                entry.identifier: {
                    "identifier": entry.identifier,
                    "description": entry.description,
                    "settings_required": entry.settings_required,
                    "settings_schema": [
                        {
                            "name": field.name,
                            "required": field.required,
                            "nullable": field.nullable,
                            "has_default": field.has_default,
                            "default_value": field.default_value
                            if field.has_default
                            else None,
                            "setting_type": field.setting_type.__name__,
                        }
                        for field in entry.settings_schema
                    ]
                    if entry.settings_type
                    else None,
                }
                for entry in providers
                if entry.identifier is not DummyProvider.identifier
            }
        )


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


def create_provider_impl(provider_str: str) -> ProviderBase:
    def enquote(s: str) -> str:
        return f"'{s}'"

    generic_error = (
        f"invalid provider input '{provider_str}',"
        f" expected format: {PROVIDER_SETTINGS_HUMAN}"
    )
    items = provider_str.split(":")
    if len(items) < 1:
        raise ArgumentTypeError(generic_error)
    provider_id = items.pop(0)
    if len(items) % 2 != 0:
        raise ArgumentTypeError(
            f"{generic_error} (badly formatted settings fields overrides)"
        )
    raw_overrides: dict[str, str] = {}
    for i in range(len(items) - 1):
        if i % 2 == 0:
            raw_overrides[items[i]] = items[i + 1]
    meta = providers_factory.get_provider_metadata(provider_id)
    if not meta.exposes_settings and raw_overrides:
        raise ArgumentTypeError(
            f"provider '{provider_id}' does not expose settings,"
            f" but settings {raw_overrides} were provided"
        )
    overrides = None
    if meta.exposes_settings and raw_overrides:
        overrides = {}
        settings_schema = meta.settings_schema
        provided_fields = set(list(raw_overrides.keys()))
        available_fields = set(field.name for field in settings_schema)
        unexpected_fields = provided_fields.difference(available_fields)
        if unexpected_fields:
            raise ArgumentTypeError(
                f"unexpected settings fields {', '.join(enquote(f) for f in unexpected_fields)}"
                f" were provided"
            )
        for field in settings_schema:
            if field.name in raw_overrides:
                overrides[field.name] = field.parse_str_override(
                    raw_overrides[field.name]
                )
    return providers_factory.create_provider(provider_id, overrides)


def create_provider(provider_str: str) -> ProviderBase:
    try:
        return create_provider_impl(provider_str)
    except Exception as e:
        raise ArgumentTypeError(str(e))


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="QuickForex command line tool: fetch exchange rates from the command line"
    )
    parser.add_argument(
        "--format",
        type=OutputFormat.parse,
        default=OutputFormat.JSON_PRETTY,
        help="Output format (default: JSON)",
    ),
    default_provider = ExchangeRateHostProvider
    parser.add_argument(
        "--provider",
        default=ExchangeRateHostProvider(),
        type=create_provider,
        help=(
            f"Provider used to fetch exchange rates (default: {default_provider.identifier})."
            f" The list of available providers can be found by running 'quickforex providers'."
            f" Additional settings can be provided with this syntax:"
            f" quickforex --provider {PROVIDER_SETTINGS_HUMAN}"
        ),
    )
    modes_parser = parser.add_subparsers(dest="mode", help="QuickForex mode")
    last_mode_parser = modes_parser.add_parser(
        "latest",
        help="Retrieve the last available exchange rate for the provided currency pairs",
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
    modes_parser.add_parser(
        "providers",
        help="Display information about available data providers",
    )
    return parser


def latest_mode_entrypoint(
    settings: Any,
    currency_pairs: set[CurrencyPair],
    provider: ProviderBase,
    output_formatter: Formatter,
) -> str:
    rates = provider.get_latest_rates(currency_pairs)
    return output_formatter.format_rates(rates)


def hist_mode_entrypoint(
    settings: Any,
    currency_pairs: set[CurrencyPair],
    provider: ProviderBase,
    output_formatter: Formatter,
) -> str:
    rates = provider.get_historical_rates(
        currency_pairs=currency_pairs, as_of=settings.as_of
    )
    return output_formatter.format_rates(rates)


def series_mode_entrypoint(
    settings: Any,
    currency_pairs: set[CurrencyPair],
    provider: ProviderBase,
    output_formatter: Formatter,
) -> str:
    series = provider.get_rates_time_series(
        currency_pairs=currency_pairs,
        date_range=DateRange(
            start_date=settings.start_date, end_date=settings.end_date
        ),
    )
    return output_formatter.format_rates_time_series(series)


def providers_entrypoint(output_formatter: Formatter) -> str:
    return output_formatter.format_providers(
        providers=providers_factory.get_available_providers()
    )


def command_line_entrypoint(args: list[str]):
    parser = create_parser()
    settings = parser.parse_args(args)
    if not settings.mode:
        parser.error("Please select a mode")
    output_formatter = FormatterFactory.create(settings.format)
    if settings.mode == "providers":
        return providers_entrypoint(output_formatter)
    currency_pairs = parse_currency_pairs(settings.currency_pairs)
    mode_entrypoint = {
        "latest": latest_mode_entrypoint,
        "history": hist_mode_entrypoint,
        "series": series_mode_entrypoint,
    }[settings.mode]
    return mode_entrypoint(
        settings=settings,
        currency_pairs=currency_pairs,
        provider=settings.provider,
        output_formatter=output_formatter,
    )


def main():
    print(command_line_entrypoint(sys.argv[1:]))


if __name__ == "__main__":
    main()
