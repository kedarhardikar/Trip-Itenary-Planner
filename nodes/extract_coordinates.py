import os
import requests
from dotenv import load_dotenv
from requests.structures import CaseInsensitiveDict
from utils.coordinates import get_lat_lon

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_PLACES_API")
GEOCODE_API_URL = "https://api.geoapify.com/v1/geocode/search"



def coordinates(state: dict) -> dict:
    print("INSIDE EXTRACT_COORDINATES")
    places = state.get("points_of_interest", [])

    places_with_coordinates = {}

    for place in places:
        try:
            lat,lon = get_lat_lon(place)
            places_with_coordinates[place] = {"lon": lon, "lat": lat}
        except Exception as e:
            print(f" Failed to get coordinates for '{place}': {e}")
            places_with_coordinates[place] = None  # Optional: could skip or handle differently

    # print(" Places with coordinates:", places_with_coordinates)
    return {
        **state,
        "poi_coordinates": places_with_coordinates
    }
