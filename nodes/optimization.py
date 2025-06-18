# import os
# import requests
# from dotenv import load_dotenv
# from utils.coordinates import get_lat_lon  

# # Load environment variables
# load_dotenv()
# ORS_API_KEY = os.getenv("HEIGIT_API_KEY")

# def optimize_route(state: dict) -> dict:
#     poi_coordinates = state.get("poi_coordinates", {})
#     city = state.get("location", {}).get("city", "")  # ✅ properly extract city string

#     if not poi_coordinates or not city:
#         print("❌ Missing POIs or city")
#         return state

#     # ✅ Get city coordinates (start/end point)
#     try:
#         city_lat, city_lon = get_lat_lon(city)
#     except Exception as e:
#         print(f"❌ Failed to get city coordinates: {e}")
#         return state

#     jobs = []
#     job_id = 1

#     for place_name, coords in poi_coordinates.items():
#         if coords is None:
#             continue
#         if isinstance(coords, dict):
#             jobs.append({
#                 "id": job_id,
#                 "location": [coords["lon"], coords["lat"]],
#                 "description": place_name
#             })
#             job_id += 1

#     if not jobs:
#         print("❌ No valid jobs created")
#         return state

#     payload = {
#         "jobs": jobs,
#         "vehicles": [
#             {
#                 "id": 1,
#                 "profile": "driving-car",
#                 "start": [city_lon, city_lat],
#                 "end": [city_lon, city_lat]
#             }
#         ]
#     }

#     headers = {
#         'Authorization': ORS_API_KEY,
#         'Content-Type': 'application/json'
#     }

#     url = "https://api.openrouteservice.org/optimization"

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()
#         result = response.json()

#         steps = result['routes'][0]['steps']
#         route = []
#         for step in steps:
#             if step['type'] == 'start':
#                 route.append("Start")
#             elif step['type'] == 'end':
#                 route.append("End")
#             elif step['type'] == 'job':
#                 route.append(step.get('description', f"Job {step.get('id')}"))

#         print("🚗 Optimized route:")
#         print(" -> ".join(route))
#         # print(route)
#         # print(result)

#         return {
#             **state,
#             # "optimized_route": result,
#             "route": route
#         }

#     except Exception as e:
#         print(f"❌ Optimization failed: {e}")
#         return state


# nodes/optimization.py

import os
import requests
from dotenv import load_dotenv
from utils.coordinates import get_lat_lon  

# Load environment variables
load_dotenv()
ORS_API_KEY = os.getenv("HEIGIT_API_KEY")

def optimize_route(state: dict) -> dict:
    poi_coordinates = state.get("poi_coordinates", {})
    city = state.get("location", {}).get("city", "")

    if not poi_coordinates or not city:
        print("❌ Missing POIs or city")
        return state

    try:
        city_lat, city_lon = get_lat_lon(city)
    except Exception as e:
        print(f"❌ Failed to get city coordinates: {e}")
        return state

    jobs = []
    job_id = 1

    # ✅ STRICT CHECK: fail fast on any invalid coordinate
    for place_name, coords in poi_coordinates.items():
        if coords is None or not isinstance(coords, dict) or coords.get("lat") is None or coords.get("lon") is None:
            print(f"⚠️ Invalid coordinate found for: {place_name}. Falling back to non-optimized route.")
            simple_route = list(poi_coordinates.keys())
            return {
                **state,
                "route": simple_route,
                "optimized": False
            }
        else:
            jobs.append({
                "id": job_id,
                "location": [coords["lon"], coords["lat"]],
                "description": place_name
            })
            job_id += 1

    # If all coordinates are valid → proceed with optimization
    payload = {
        "jobs": jobs,
        "vehicles": [
            {
                "id": 1,
                "profile": "driving-car",
                "start": [city_lon, city_lat],
                "end": [city_lon, city_lat]
            }
        ]
    }

    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }

    url = "https://api.openrouteservice.org/optimization"

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        steps = result['routes'][0]['steps']
        route = []
        for step in steps:
            if step['type'] == 'start':
                route.append("Start")
            elif step['type'] == 'end':
                route.append("End")
            elif step['type'] == 'job':
                route.append(step.get('description', f"Job {step.get('id')}"))

        print("🚗 Optimized route:")
        print(" -> ".join(route))

        return {
            **state,
            "route": route,
            "optimized": True
        }

    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        simple_route = list(poi_coordinates.keys())
        return {
            **state,
            "route": simple_route,
            "optimized": False
        }
