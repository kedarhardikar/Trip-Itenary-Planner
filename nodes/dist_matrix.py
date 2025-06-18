import os
import requests
from dotenv import load_dotenv

load_dotenv()

HEIGIT_KEY = os.getenv("HEIGIT_API_KEY")
ORS_MATRIX_URL = "https://api.openrouteservice.org/v2/matrix/driving-car"

def distance_matrix(state: dict) -> dict:
    print("INSIDE DIST MATRX CALCULATION")
    poi_coordinates = state.get("poi_coordinates", {})

    # Build API-ready locations list
    locations = [
        [coords["lon"], coords["lat"]] for coords in poi_coordinates.values() if coords is not None
    ]

    if len(locations) < 2:
        raise ValueError("❌ Need at least 2 locations to compute distance matrix.")

    headers = {
        "Authorization": HEIGIT_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }

    body = {
        "locations": locations,
        "metrics": ["distance"],  # You can also add "duration" if you want travel time
        "units": "km"
    }

    try:
        response = requests.post(ORS_MATRIX_URL, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Distance matrix API failed: {e}")
        # Simply return state and allow graph to proceed
        return { **state, "distance_matrix": None }


    distances = data.get("distances", [])
    print("Distance Matrix:", distances)

    # Return updated state
    return {
        **state,
        "dist_matrix": distances,
        # "matrix_locations": locations  # Save for next node (routing)
    }
