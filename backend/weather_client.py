"""Weather lookups via Open-Meteo (free, no API key required).

Both the geocoding and forecast HTTP calls take an injected `httpx.AsyncClient`
so tests can point at a mocked transport (e.g. via respx) instead of the
network.
"""

from __future__ import annotations

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes (subset used by Open-Meteo).
WEATHER_CODES = {
    0: "Klarer Himmel",
    1: "Überwiegend klar",
    2: "Teilweise bewölkt",
    3: "Bedeckt",
    45: "Nebel",
    48: "Reifnebel",
    51: "Leichter Nieselregen",
    53: "Nieselregen",
    55: "Starker Nieselregen",
    61: "Leichter Regen",
    63: "Regen",
    65: "Starker Regen",
    71: "Leichter Schneefall",
    73: "Schneefall",
    75: "Starker Schneefall",
    80: "Regenschauer",
    81: "Regenschauer",
    82: "Heftige Regenschauer",
    95: "Gewitter",
    96: "Gewitter mit Hagel",
    99: "Gewitter mit starkem Hagel",
}


class LocationNotFoundError(Exception):
    pass


def describe_weather_code(code: int) -> str:
    return WEATHER_CODES.get(code, f"Unbekannt (Code {code})")


async def geocode(location: str, client: httpx.AsyncClient) -> tuple[float, float, str]:
    response = await client.get(
        GEOCODING_URL,
        params={"name": location, "count": 1, "language": "de", "format": "json"},
    )
    response.raise_for_status()
    results = response.json().get("results") or []
    if not results:
        raise LocationNotFoundError(f"Ort nicht gefunden: {location}")
    result = results[0]
    return result["latitude"], result["longitude"], result["name"]


async def fetch_forecast(
    latitude: float, longitude: float, client: httpx.AsyncClient, units: str = "metric"
) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "timezone": "auto",
        "forecast_days": 3,
    }
    if units == "imperial":
        params["temperature_unit"] = "fahrenheit"
        params["wind_speed_unit"] = "mph"
    response = await client.get(FORECAST_URL, params=params)
    response.raise_for_status()
    return response.json()


async def get_weather(
    location: str, units: str = "metric", client: httpx.AsyncClient | None = None
) -> dict:
    owns_client = client is None
    client = client or httpx.AsyncClient(timeout=10.0)
    try:
        latitude, longitude, resolved_name = await geocode(location, client)
        forecast = await fetch_forecast(latitude, longitude, client, units=units)
        current = forecast["current"]
        daily = forecast["daily"]
        return {
            "location": resolved_name,
            "temperature": current["temperature_2m"],
            "condition": describe_weather_code(current["weather_code"]),
            "units": units,
            "forecast": [
                {
                    "date": daily["time"][i],
                    "temperature_max": daily["temperature_2m_max"][i],
                    "temperature_min": daily["temperature_2m_min"][i],
                    "condition": describe_weather_code(daily["weather_code"][i]),
                }
                for i in range(len(daily["time"]))
            ],
        }
    finally:
        if owns_client:
            await client.aclose()
