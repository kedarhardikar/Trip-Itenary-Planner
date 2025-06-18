from langgraph.graph import StateGraph, END
from typing import TypedDict
from nodes.extraction import extract1
from nodes.extract_interests import interests
from nodes.extract_places import places
from nodes.extract_coordinates import coordinates
from nodes.dist_matrix import distance_matrix
from nodes.optimization import optimize_route
from nodes.weather import fetch_weather
from nodes.news import fetch_news
from nodes.generate_itenary import itenary
from nodes.human_approval import approval
from nodes.parse_feedback import parse_feedback
from nodes.calendar_node import create_calendar_events
from nodes.suggest_arrival_transport import suggest_travel






# ✅ Define state schema
class AgentState(TypedDict):
    user_input: str
    location: dict
    duration_days: int
    interests: list
    weather: dict
    news: dict
    research: str
    points_of_interest: list
    poi_coordinates: dict
    dist_matrix: list
    route: list
    final_itenary: str
    human_decision: str
    human_feedback: str
    message_history: list
    optimized: bool
    calendar_success: bool
    trip_start_date: str               # ✅ REQUIRED!
    departure_city: str                # Optional but useful
    travel_suggestion: dict               # Optional (LLM may fill)


def check_optimization(state: AgentState) -> str:
    return "optimized" if state.get("optimized", False) else "fallback"


# ✅ Conditional edge function
def check_human_decision(state: AgentState) -> str:
    return state.get("human_decision", "replan")


# ✅ Build LangGraph
builder = StateGraph(AgentState)

builder.add_node("Extract", extract1)
builder.add_node("Interest Extraction", interests)
builder.add_node("Places Extraction", places)
builder.add_node("Weather Fetch", fetch_weather)
builder.add_node("News Fetch", fetch_news)
builder.add_node("Coordinate Extraction", coordinates)
builder.add_node("Matrix Calculation", distance_matrix)
builder.add_node("Optimize Routes", optimize_route)
builder.add_node("Generate Itenary", itenary)
builder.add_node("Human Approval", approval)
builder.add_node("Parse Feedback", parse_feedback)
builder.add_node("Calendar Event Creation", create_calendar_events)
builder.add_node("Suggest Arrival Transport", suggest_travel)



# Graph flow
builder.set_entry_point("Extract")
builder.add_edge("Extract", "Interest Extraction")
builder.add_edge("Interest Extraction", "Places Extraction")
builder.add_edge("Places Extraction", "Weather Fetch")
builder.add_edge("Weather Fetch", "News Fetch")
builder.add_edge("News Fetch", "Coordinate Extraction")
builder.add_edge("Coordinate Extraction","Matrix Calculation")
builder.add_edge("Matrix Calculation", "Optimize Routes")
builder.add_conditional_edges(
    "Optimize Routes",
    check_optimization,
    {
        "optimized": "Generate Itenary",
        "fallback": "Generate Itenary"
    }
)

builder.add_edge("Generate Itenary", "Human Approval")

# ✅ Add conditional branching after human approval
builder.add_conditional_edges(
    "Human Approval",
    check_human_decision,
    {
        "approve": "Calendar Event Creation",
        "replan": "Parse Feedback"   # ✅ fully looped back
    }
)
# After parsing feedback, go back to extract
builder.add_edge("Parse Feedback", "Interest Extraction")
builder.add_edge("Calendar Event Creation", "Suggest Arrival Transport")
builder.add_edge("Suggest Arrival Transport", END)



# ✅ Compile graph
app = builder.compile()

from datetime import datetime

# ✅ Get user inputs
user_input = input("📝 Describe your travel plan (e.g., 'I want to visit Mumbai for 2 days and I love beaches'): ").strip()
departure_city = input("📍 Your Departure City: ").strip()
trip_start_date = input("📅 Trip Start Date (YYYY-MM-DD): ").strip()

# ✅ Validate trip_start_date
try:
    datetime.strptime(trip_start_date, "%Y-%m-%d")
except ValueError:
    raise ValueError("⚠️ Invalid date format. Use YYYY-MM-DD.")


initial_state = {
    "user_input": user_input,
    "departure_city": departure_city,               # ⬅️ Added manually for now
    "trip_start_date": trip_start_date,        # ⬅️ Added manually for now
    "location": {"city": ""},
    "duration_days": 0,
    "interests": [],
    "weather": {},
    "news": {},
    "research": "",
    "points_of_interest": [],
    "poi_coordinates": {},
    "dist_matrix": [],
    "route": [],
    "final_itenary": "",
    "human_decision": "",
    "human_feedback": "",
    "message_history": [],
    "optimized": False,
    "reaching_method": "",                  # ⬅️ Optional: LLM will populate this
    "travel_suggestion": {}
}

# ✅ Driver loop to handle multiple HITL feedback rounds

current_state = initial_state

while True:
    current_state = app.invoke(current_state)
    if current_state.get("human_decision") == "approve":
        break

print("\n🎯 FINAL ITINERARY:")
print(current_state.get("final_itenary", "No itinerary was generated."))

if current_state.get("calendar_success"):
    print("📅 Itinerary successfully saved to Google Calendar.")
else:
    print("⚠️ Calendar save failed or was skipped.")



# ✅ Final output
# print("\n🎯 FINAL STATE:")
# print(final_state)