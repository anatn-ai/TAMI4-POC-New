import os
from google.adk.agents import LlmAgent
from google.genai import types
from .prompts import INSTRUCTION

agent = LlmAgent(
    name="creative_agent",
    model=os.getenv("VERTEX_MODEL", "gemini-2.0-flash"),
    description="Creative strategist for תמי4: turns creative performance data into insights + test plan (Hebrew JSON).",
    instruction=INSTRUCTION,
    tools=[], 
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, 
        response_mime_type="application/json"
    ),
)
