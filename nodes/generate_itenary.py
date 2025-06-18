# nodes/generate_itinerary.py

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(
    model="llama3-70b-8192",
    api_key=groq_api_key,
    temperature=0.4
)

# Create prompt template
itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     """You are a professional travel planner.
     You are given a visit order (optimized OR unoptimized).
     Your task is to divide this into a clear day-by-day itinerary.
     
Instructions:
- Always respect the number of days.
- Try to balance the number of places per day.
- If route is unoptimized, still build a valid itinerary.
- Do not explain anything. Only return the day-wise plan.
"""
    ),
    ("human", 
     """City: {location}
Duration: {duration_days} days
Interests: {interests}
Visit Order (may be optimized or simple list):
{route}

Generate the day-wise itinerary:"""
    )
])

def itenary(state: dict) -> dict:
    print("INSIDE GENERATE ITINERARY")

    route = state.get("route", [])
    duration_days = state.get("duration_days", 1)
    interests = ", ".join(state.get("interests", []))
    location = state.get("location", {}).get("city", "")

    if not route:
        print(" No valid route, falling back to simple listing.")
        state["final_itenary"] = f"Trip to {location} for {duration_days} days. Unfortunately, no places could be suggested."
        return state

    poi_list = "\n".join(f"- {place}" for place in route)

    # Build chain
    chain = itinerary_prompt | llm
    response = chain.invoke({
        "location": location,
        "duration_days": duration_days,
        "interests": interests,
        "route": poi_list
    })

    raw_output = response.content
    print(f" Final Itinerary:\n{raw_output}")

    return {
        **state,
        "final_itenary": raw_output
    }
