# quickforex

[![PyPI version](https://badge.fury.io/py/quickforex.svg)](https://badge.fury.io/py/quickforex) [![Test](https://github.com/jean-edouard-boulanger/python-quickforex/actions/workflows/test.yml/badge.svg)](https://github.com/jean-edouard-boulanger/python-quickforex/actions/workflows/test.yml) [![codecov](https://codecov.io/gh/jean-edouard-boulanger/python-quickforex/branch/master/graph/badge.svg?token=E8LALNP22Z)](https://codecov.io/gh/jean-edouard-boulanger/python-quickforex)

Quick and easy access to foreign exchange rates. By default, this API uses 
[exchangerate.host](https://exchangerate.host/#/) as backend.

## Getting started

### Using `quickforex` from a Python script

#### Get the last available rate for a single currency pair

```python
from quickforex import CurrencyPair
import quickforex


quickforex.get_latest_rate("EUR/USD")  # -> Decimal(1.16)
quickforex.get_latest_rate("EURUSD")
quickforex.get_latest_rate("EUR", "USD")
quickforex.get_latest_rate(("EUR", "USD"))
quickforex.get_latest_rate(CurrencyPair("EUR", "USD"))
```

#### Get the last available rate for multiple currency pairs

```python
from quickforex import CurrencyPair
import quickforex

quickforex.get_latest_rate("EUR/USD", "EUR/GBP")  # -> {CurrencyPair("EUR", "USD"): Decimal(1.16), CurrencyPair("EUR", "GBP"): Decimal(0.84)}
quickforex.get_latest_rate(["EUR/USD", "EUR/GBP"])
```

#### Get the historical rate for one or more currency pairs

```python
from datetime import date
from quickforex import CurrencyPair
import quickforex

quickforex.get_historical_rate("BTC/USD", as_of=date(year=2021, month=1, day=1))  # -> Decimal(29388.20)
quickforex.get_historical_rates("EUR/USD", "EUR/GBP", as_of=date(year=2021, month=1, day=1))  # -> {CurrencyPair("EUR", "USD"): Decimal(1.21), CurrencyPair("EUR", "GBP"): Decimal(0.89)}
```

#### Get the rates for one or more currency pairs between two historical dates

```python
from datetime import date
from quickforex import CurrencyPair
import quickforex

quickforex.get_rates_time_series(
    "EURUSD", "EURGBP",
    start_date=date(year=2020, month=1, day=1),
    end_date=date(year=2021, month=1, day=1)
)

# -> {
#    CurrencyPair("EUR", "USD"): {
#        date(year=2020, month=1, day=1): Decimal(1.12), 
#        ..., 
#        date(year=2021, month=1, day=1): Decimal(1.21)
#    },
#    CurrencyPair("EUR", "GBP"): { ... }
# }
```

### Using `quickforex` from the command line

#### Get the last available rate for one or more currency pairs

```shell
❯ quickforex latest EURUSD EURGBP

{
    "EUR": {
        "GBP": 0.846354,
        "USD": 1.164798
    }
}
```

#### Get the historical rate for one or more currency pairs

```shell
❯ quickforex history --date 2020-01-01 EURUSD EURGBP

{
    "EUR": {
        "GBP": 0.8462,
        "USD": 1.1221
    }
}
```

#### Get the rates for one or more currency pairs between two historical dates

```shell
❯ quickforex series --from 2020-01-01 --to 2020-12-31 EURGBP EURUSD GBPJPY

{
    "EUR": {
        "GBP": {
            "2020-01-01": 0.8462,
            "2020-01-02": 0.8466,
            "2020-01-03": 0.8495,
            ...
            "2020-12-30": 0.903111,
            "2020-12-31": 0.892135
        },
        "USD": { ... }
    },
    "GBP": {"JPY": { ... }}
}

```
