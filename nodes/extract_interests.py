# nodes/llm_interest_extraction_node.py

import json
import os
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

# The interest extraction prompt
interest_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a strict travel interest classifier. You must extract relevant user interests from natural language input.

Instructions:
- Only return a valid Python list of strings.
- If nothing matches, return an empty list.
- Do not explain anything. Return only the list.
- Be as specific as you can

Example:
["tourism", "sport", "history"]
"""),
    ("human", "Input: {user_input}")
])

def interests(state: dict) -> dict:
    user_input = state.get("user_input")
    print("INSIDE INTEREST EXTRACTION")

    chain = interest_prompt | llm
    response = chain.invoke({"user_input": user_input})
    raw_output = response.content
    print(" Raw LLM response (interests):", raw_output)

    # Validate list output
    try:
        interests = json.loads(raw_output)
        if not isinstance(interests, list):
            raise ValueError("Not a valid list")
    except Exception as e:
        raise ValueError(f" Failed to parse interests: {raw_output}") from e

    return {
        **state,
        "interests": interests
    }
