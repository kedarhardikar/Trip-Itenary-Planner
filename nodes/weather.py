#nodes/weather.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

def fetch_weather(state: dict) -> dict:
    """
    Node to fetch weather data for destination city.
    """
    city = state.get("location", {}).get("city", "")

    if not city:
        print(" No city found in state for weather.")
        return state

    complete_url = f"{BASE_URL}appid={WEATHER_API_KEY}&q={city}&units=metric"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        if data.get("cod") != 404:
            main = data["main"]
            weather = data["weather"][0]

            weather_data = {
                "temperature_celsius": main.get("temp"),
                "pressure_hpa": main.get("pressure"),
                "humidity_percent": main.get("humidity"),
                "description": weather.get("description")
            }

            print(f"🌦️ Weather data: {weather_data}")

            return {
                **state,
                "weather_data": weather_data
            }
        else:
            print(" City not found in weather API.")
            return state

    except Exception as e:
        print(f"Weather API call failed: {e}")
        return state