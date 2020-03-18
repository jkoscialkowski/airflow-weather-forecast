# airflow-weather-forecast
Daily weather forecast using Apache Airflow and WMO data


## Prerequisites
The forecasts to be sent should be determined in a `.gitignore`'d
file `subscribers.json`:

```json
[
  {
    "email": "<email address>",
    "cities": ["list", "of", "cities"]
  },
  {
    "email": "<another email>",
    "cities": ["different", "list", "of", "cities"]
  }
]
```