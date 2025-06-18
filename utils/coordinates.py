import os
import requests
from dotenv import load_dotenv
from requests.structures import CaseInsensitiveDict

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_PLACES_API")
GEOCODE_API_URL = "https://api.geoapify.com/v1/geocode/search"

def get_lat_lon(location_text: str) -> tuple:
    """
    Given a location text string, returns (latitude, longitude) tuple.
    Raises ValueError if no location found.
    """
    url = f"{GEOCODE_API_URL}?text={location_text}&apiKey={GEOAPIFY_API_KEY}"
    # print(url)
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    features = data.get("features", [])
    if not features:
        raise ValueError(f"No results found for location '{location_text}'")

    lon, lat = features[0]["geometry"]["coordinates"]
    return lat, lon
