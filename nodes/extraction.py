# nodes/llm_planning_node.py

import json
import re
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

# Updated system prompt to support follow-ups
prompt1 = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a travel assistant helping users create or revise travel plans. "
        "Extract structured trip info as JSON from the latest user input only. "
        "The format should be: {{ duration_days, destination_city }}."
    ),
    (
        "human",
        "Input: {user_input}\n\n"
        "Return a valid JSON like this:\n"
        "{{\"duration_days\": 3, \"destination_city\": \"Pune\"}}"
    )
])





def extract1(state: dict) -> dict:
    print(f"INSIDE EXTRACTION1")
    # print(state["message_history"])

    user_input = state.get("user_input")
    message_history = state.get("message_history", [])

# Append current user input only if not duplicate
    if not message_history or message_history[-1] != {"role": "user", "content": user_input}:
        message_history.append({"role": "user", "content": user_input})

    # Run LLM with only current input
    chain = prompt1 | llm
    response = chain.invoke({"user_input": user_input})
    raw_output = response.content
    # print("Raw LLM response:", raw_output)

    # Extract just the JSON part
    match = re.search(r'\{.*?\}', raw_output, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON block found in LLM response:\n{raw_output}")
    json_block = match.group(0)

    try:
        json_block = json_block.replace("None", "null")
        info = json.loads(json_block)
        # print(info)
    except json.JSONDecodeError:
        raise ValueError(f"Extracted block is not valid JSON:\n{json_block}")

    city = info.get("destination_city")
    duration = info.get("duration_days")
    # lat, lon = get_lat_lon(city)

    # if lat is None or lon is None:
    #     raise ValueError(f"Could not find lat/lon for city: {city}")

    # print(f"SUCCESS: City: {city}, lat/lon: ({lat}, {lon})\nINFO: {info}")
    print(f"SUCCESS: City: {city}, \nINFO: {info}")

    # Append assistant reply to message history
    message_history.append({"role": "assistant", "content": raw_output})

    return {
        **state,
        # "location": {"city": city, "lat": lat, "lon": lon},
        "location": {"city":city},
        "duration_days": duration,
        "message_history": message_history
    }


