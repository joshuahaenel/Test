import httpx
import pytest
import respx

from backend import weather_client

GEOCODING_RESPONSE = {
    "results": [{"latitude": 52.52, "longitude": 13.405, "name": "Berlin"}]
}

FORECAST_RESPONSE = {
    "current": {"temperature_2m": 21.3, "weather_code": 1},
    "daily": {
        "time": ["2026-07-01", "2026-07-02"],
        "temperature_2m_max": [24.0, 22.5],
        "temperature_2m_min": [14.0, 13.2],
        "weather_code": [1, 61],
    },
}


@respx.mock
async def test_get_weather_happy_path():
    respx.get(weather_client.GEOCODING_URL).mock(
        return_value=httpx.Response(200, json=GEOCODING_RESPONSE)
    )
    respx.get(weather_client.FORECAST_URL).mock(
        return_value=httpx.Response(200, json=FORECAST_RESPONSE)
    )

    result = await weather_client.get_weather("Berlin")

    assert result["location"] == "Berlin"
    assert result["temperature"] == 21.3
    assert result["condition"] == "Überwiegend klar"
    assert len(result["forecast"]) == 2
    assert result["forecast"][1]["condition"] == "Leichter Regen"


@respx.mock
async def test_get_weather_location_not_found():
    respx.get(weather_client.GEOCODING_URL).mock(
        return_value=httpx.Response(200, json={"results": []})
    )

    with pytest.raises(weather_client.LocationNotFoundError):
        await weather_client.get_weather("Nirgendwo12345")


def test_describe_weather_code_unknown():
    assert "Unbekannt" in weather_client.describe_weather_code(999)
