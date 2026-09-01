"""A small, dependency-free CLI weather application using Open-Meteo."""

from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CODES = {
    0: "Clear sky", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog",
    48: "Rime fog", 51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain", 71: "Light snow", 73: "Snow",
    75: "Heavy snow", 80: "Rain showers", 81: "Rain showers", 82: "Heavy rain showers", 95: "Thunderstorm",
}


class WeatherError(RuntimeError):
    """A user-friendly error when location or weather data cannot be fetched."""


def fetch_json(url: str, params: dict[str, str | int | float]) -> dict:
    request_url = f"{url}?{urlencode(params)}"
    try:
        with urlopen(request_url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise WeatherError("Could not fetch live weather. Check your internet connection and try again.") from exc


def find_location(city: str) -> dict:
    data = fetch_json(GEOCODING_URL, {"name": city, "count": 1, "language": "en", "format": "json"})
    results = data.get("results", [])
    # The API accepts "City, Country". Make a friendly second attempt for "City Country" input.
    if not results and "," not in city and " " in city:
        city, country = city.rsplit(" ", 1)
        data = fetch_json(GEOCODING_URL, {"name": f"{city}, {country}", "count": 1, "language": "en", "format": "json"})
        results = data.get("results", [])
    if not results:
        raise WeatherError(f"I could not find a location named '{city}'. Try adding a country, for example: Delhi, India.")
    return results[0]


def get_current_weather(city: str) -> dict:
    location = find_location(city)
    data = fetch_json(FORECAST_URL, {
        "latitude": location["latitude"], "longitude": location["longitude"],
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
        "timezone": "auto",
    })
    current = data.get("current")
    if not current:
        raise WeatherError("The weather service returned no current conditions.")
    return {"location": location, "current": current}


def format_weather(report: dict) -> str:
    location, current = report["location"], report["current"]
    place = ", ".join(part for part in (location.get("name"), location.get("admin1"), location.get("country")) if part)
    condition = WEATHER_CODES.get(current.get("weather_code"), "Unknown conditions")
    return (
        f"Weather for {place}\nCondition: {condition}\n"
        f"Temperature: {current['temperature_2m']}°C (feels like {current['apparent_temperature']}°C)\n"
        f"Humidity: {current['relative_humidity_2m']}%\nWind: {current['wind_speed_10m']} km/h\n"
        f"Observed: {current.get('time', 'unknown')}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Show current weather for a city.")
    parser.add_argument("city", nargs="+", help="City name, optionally with country (e.g. Delhi, India)")
    args = parser.parse_args()
    try:
        print(format_weather(get_current_weather(" ".join(args.city))))
    except WeatherError as exc:
        print(f"Weather App: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
