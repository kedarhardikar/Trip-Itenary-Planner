# nodes/llm_place_suggestion_node.py

import json
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama3-70b-8192",
    api_key=groq_api_key,
    temperature=0.0
)

# Place suggestion prompt
place_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a travel agent assistant.
You must suggest interesting places based on:
- User location
- User interests
- Duration of stay

Rules:
- Suggest 4 places per day of stay.
- Total places = duration × 4.
- Include variety based on interests.
- Try to give full names and addresses (if possible).
- Output must be only a valid Python list of strings.
- Each Place must be a valid string with valid opening and closing quotation marks ("Place")
- If no good matches, return an empty list [].
- DO NOT add any explanation or text outside list.

Example:
location: "Mumbai", interests: ["sightseeing"], duration: 3 
-> ["Wankhede Stadium, Mumbai",
 "Gateway of India, Mumbai",
   ... total 12 places]
"""
    ),
    ("human", "location: {location}, interests: {interests}, duration: {duration}")
])

def places(state: dict) -> dict:
    print("INSIDE PLACES EXTRACTION")
    location = state["location"]["city"]
    duration = state["duration_days"]
    interests = state["interests"]

    chain = place_prompt | llm
    response = chain.invoke({
        "location": location,
        "interests": interests,
        "duration": duration
    })
    raw_output = response.content
    print(" Raw LLM response (places):", raw_output)

    # Validate list output
    try:
        places = json.loads(raw_output)
        if not isinstance(places, list):
            raise ValueError("Not a valid list")
    except Exception as e:
        raise ValueError(f"❌ Failed to parse places: {raw_output}") from e

    return {
        **state,
        "points_of_interest": places
    }