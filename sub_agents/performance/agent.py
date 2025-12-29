import os
from google.adk.agents import LlmAgent
from google.genai import types
from .prompts import INSTRUCTION

agent = LlmAgent(
    name="performance_analyst",
    model=os.getenv("VERTEX_MODEL", "gemini-2.0-flash"),
    description="Performance specialist for תמי4: diagnose campaign performance & recommend actions (Hebrew JSON).",
    instruction=INSTRUCTION,
    tools=[],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, 
        response_mime_type="application/json"
    ),
)
