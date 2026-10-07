# weather_tool.py
import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

def get_forecast(city: str, days: int = 3) -> dict:
    # 1. City name -> coordinates
    geo = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=10)
    geo.raise_for_status()
    results = geo.json().get("results")
    if not results:
        return {"error": f"Could not find city: {city}"}
    place = results[0]

    # 2. Coordinates -> forecast
    resp = requests.get(FORECAST_URL, params={
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "forecast_days": days,
    }, timeout=10)
    resp.raise_for_status()
    d = resp.json()["daily"]

    return {
        "city": place["name"],
        "country": place.get("country"),
        "forecast": [
            {
                "date": d["time"][i],
                "max_c": d["temperature_2m_max"][i],
                "min_c": d["temperature_2m_min"][i],
                "rain_mm": d["precipitation_sum"][i],
            }
            for i in range(len(d["time"]))
        ],
    }

if __name__ == "__main__":
    for city in ["Gurugram", "Mumbai", "London", "Gurgaonn", "asdfgh"]:
        print(city, "->", get_forecast(city, days=2))
        print()