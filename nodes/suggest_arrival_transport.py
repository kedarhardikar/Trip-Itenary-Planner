#nodes/suggest_arrival_transport.py
import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from datetime import datetime, timedelta

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama3-70b-8192",
    api_key=groq_api_key,
    temperature=0.3,
)

# Travel planning prompt
travel_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a travel planner assistant that helps suggest how a person should travel from their departure city to their destination city.

Instructions:
- Suggest a realistic travel mode (e.g., flight, train, bus, car).
- Suggest the best arrival point (airport/station/area) in the destination city.
- Estimate when they should leave from their departure city to reach on the morning of the trip start date.
- Return a JSON object with 4 fields: travel_mode, arrival_place, departure_time, reasoning.
- departure_time should be in ISO format: YYYY-MM-DDTHH:MM:SS.
- Be concise, but include a sentence of reasoning.
- Output only valid JSON. Do NOT explain anything else outside JSON.

Example Output:
{{
  "travel_mode": "Train",
  "arrival_place": "Chhatrapati Shivaji Maharaj Terminus, Mumbai",
  "departure_time": "2025-08-12T23:00:00",
  "reasoning": "Taking a night train from Pune allows timely arrival and avoids morning rush."
}}
"""),
    ("human", "Departure: {departure_city}\nDestination: {destination_city}\nTrip Start Date: {trip_start_date}")
])

def suggest_travel(state: dict) -> dict:
    print("Generating travel suggestion...")

    departure_city = state.get("departure_city")
    destination_city = state.get("location")
    trip_start_date = state.get("trip_start_date")

    if not (departure_city and destination_city and trip_start_date):
        print(" Missing required travel data.")
        return {**state, "travel_suggestion": {}}

    # Invoke chain
    chain = travel_prompt | llm
    response = chain.invoke({
        "departure_city": departure_city,
        "destination_city": destination_city,
        "trip_start_date": trip_start_date
    })

    raw_output = response.content
    print("Raw LLM output (travel):", raw_output)

    try:
        travel_suggestion = json.loads(raw_output)
    except Exception as e:
        raise ValueError(f" Failed to parse travel suggestion: {raw_output}") from e

    return {
        **state,
        "travel_suggestion": travel_suggestion
    }