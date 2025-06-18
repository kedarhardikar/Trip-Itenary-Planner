# nodes/parse_feedback_node.py

import os
import json
import re
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

# MUCH STRONGER PROMPT - prevents empty list confusion
feedback_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a travel assistant. You will receive feedback from the user after seeing a proposed itinerary.\n"
     "Extract any changes the user is requesting.\n"
     "If nothing is mentioned for a field, keep it null.\n"
     "Return your output in valid JSON format:\n"
     "{{\"destination_city\": ..., \"duration_days\": ..., \"interests\": [...]}}\n\n"
     "If interests are mentioned, return them as a list of strings."
    ),
    ("human", "Feedback: {feedback}")
])



def parse_feedback(state: dict) -> dict:
    print("INSIDE PARSE_FEEDBACK")

    feedback = state.get("human_feedback", "")

    chain = feedback_prompt | llm
    response = chain.invoke({"feedback": feedback})
    raw_output = response.content
    print("🧠 Raw LLM response (parse feedback):", raw_output)

    # Extract JSON block
    match = re.search(r'\{.*?\}', raw_output, re.DOTALL)
    if not match:
        raise ValueError(f"❌ No JSON found:\n{raw_output}")

    json_block = match.group(0)
    try:
        json_block = json_block.replace("None", "null")
        parsed = json.loads(json_block)
    except json.JSONDecodeError:
        raise ValueError(f"❌ Invalid JSON:\n{json_block}")

    # Carefully update state only for non-null fields
    new_city = parsed.get("destination_city", None)
    new_duration = parsed.get("duration_days", None)
    new_interests = parsed.get("interests", None)

    updated_state = {**state}

    if new_city is not None:
        updated_state["location"] = {"city": new_city}
    if new_duration is not None:
        updated_state["duration_days"] = new_duration

    if new_interests is not None:
        # 🧠 extra protection: only update if not empty list
        if len(new_interests) > 0:
            updated_state["interests"] = new_interests
        else:
            print("✅ No new interests provided — keeping old interests.")

    return updated_state