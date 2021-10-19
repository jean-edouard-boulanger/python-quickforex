from typing import Any

import pytest
import deepdiff
import json

from quickforex.command_line import command_line_entrypoint


def assert_no_diff(expected: dict[Any, Any], outcome: dict[Any, Any]):
    diff = deepdiff.DeepDiff(outcome, expected)
    if diff:
        pytest.fail(
            f"found differences: {diff}" f" expected={expected}" f" outcome={outcome}"
        )


@pytest.mark.parametrize(
    "args,expected_output",
    [
        (
            ["--format", "json:pretty", "providers"],
            {
                "exchangerate.host": {
                    "description": " Provider backed by exchangerate.host ",
                    "identifier": "exchangerate.host",
                    "settings_required": False,
                    "settings_schema": [
                        {
                            "default_value": 6,
                            "has_default": True,
                            "name": "decimal_places",
                            "nullable": False,
                            "required": False,
                            "setting_type": "int",
                        },
                        {
                            "default_value": None,
                            "has_default": True,
                            "name": "source",
                            "nullable": True,
                            "required": False,
                            "setting_type": "str",
                        },
                    ],
                }
            },
        ),
        (
            [
                "--format",
                "json:pretty",
                "--provider",
                "dummy:return_rate:2.0",
                "latest",
                "EUR/USD",
            ],
            {"EUR": {"USD": 2.0}},
        ),
        (
            [
                "--format",
                "json:pretty",
                "--provider",
                "dummy:return_rate:2.0",
                "latest",
                "EUR/USD",
                "EURGBP",
                "USD/JPY",
            ],
            {"EUR": {"USD": 2.0, "GBP": 2.0}, "USD": {"JPY": 2.0}},
        ),
        (
            [
                "--format",
                "json:pretty",
                "--provider",
                "dummy:return_rate:2.0",
                "history",
                "--date",
                "2021-01-01",
                "EUR/USD",
            ],
            {"EUR": {"USD": 2.0}},
        ),
        (
            [
                "--format",
                "json:pretty",
                "--provider",
                "dummy:return_rate:2.0",
                "history",
                "--date",
                "2021-01-01",
                "EUR/USD",
                "EURGBP",
                "USD/JPY",
            ],
            {"EUR": {"USD": 2.0, "GBP": 2.0}, "USD": {"JPY": 2.0}},
        ),
        (
            [
                "--format",
                "json:pretty",
                "--provider",
                "dummy:return_rate:2.0",
                "series",
                "--from",
                "2021-01-01",
                "--to",
                "2021-01-07",
                "EUR/USD",
            ],
            {
                "EUR": {
                    "USD": {
                        "2021-01-01": 2.0,
                        "2021-01-02": 2.0,
                        "2021-01-03": 2.0,
                        "2021-01-04": 2.0,
                        "2021-01-05": 2.0,
                        "2021-01-06": 2.0,
                        "2021-01-07": 2.0,
                    },
                }
            },
        ),
        (
            [
                "--format",
                "json:pretty",
                "--provider",
                "dummy:return_rate:2.0",
                "series",
                "--from",
                "2021-01-01",
                "--to",
                "2021-01-07",
                "EUR/USD",
                "GBP/EUR",
            ],
            {
                "EUR": {
                    "USD": {
                        "2021-01-01": 2.0,
                        "2021-01-02": 2.0,
                        "2021-01-03": 2.0,
                        "2021-01-04": 2.0,
                        "2021-01-05": 2.0,
                        "2021-01-06": 2.0,
                        "2021-01-07": 2.0,
                    },
                },
                "GBP": {
                    "EUR": {
                        "2021-01-01": 2.0,
                        "2021-01-02": 2.0,
                        "2021-01-03": 2.0,
                        "2021-01-04": 2.0,
                        "2021-01-05": 2.0,
                        "2021-01-06": 2.0,
                        "2021-01-07": 2.0,
                    },
                },
            },
        ),
    ],
)
def test_command_line(args: list[str], expected_output: dict[Any, Any]):
    output = json.loads(command_line_entrypoint(args))
    assert_no_diff(expected_output, output)
