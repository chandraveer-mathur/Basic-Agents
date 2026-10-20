# FRIDAY_v0.0.1\src\tools\weather.py

import requests
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city. Use this for weather questions."""

    try:
        # 1. Find the city's coordinates
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )
        geo_response.raise_for_status()
        locations = geo_response.json().get("results", [])

        if not locations:
            return f"Could not find the location: {city}"

        place = locations[0]
        latitude = place["latitude"]
        longitude = place["longitude"]
        name = place["name"]
        country = place.get("country", "")

        # 2. Get current weather
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            },
            timeout=10,
        )
        weather_response.raise_for_status()
        current = weather_response.json()["current"]

        # 3. Convert weather codes into readable descriptions
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy with rime",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Rain showers",
            81: "Moderate rain showers",
            82: "Heavy rain showers",
            95: "Thunderstorm",
        }

        description = weather_codes.get(
            current["weather_code"],
            "Variable weather conditions",
        )

        return (
            f"Current weather for {name}, {country}:\n"
            f"Condition: {description}\n"
            f"Temperature: {current['temperature_2m']}°C\n"
            f"Feels like: {current['apparent_temperature']}°C\n"
            f"Humidity: {current['relative_humidity_2m']}%\n"
            f"Wind speed: {current['wind_speed_10m']} km/h\n"
            f"Precipitation: {current['precipitation']} mm\n"
            f"Observation time: {current['time']}"
        )

    except requests.RequestException:
        return "The weather service is temporarily unavailable."
    except (KeyError, ValueError):
        return "The weather service returned unexpected data."