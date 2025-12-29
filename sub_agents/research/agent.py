import os
from google.adk.agents import LlmAgent
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.genai import types
from .prompts import INSTRUCTION

agent = LlmAgent(
    name="research_agent",
    model=os.getenv("VERTEX_MODEL", "gemini-2.0-flash"),
    description="Search-grounded web research agent (Hebrew output).",
    instruction=INSTRUCTION,
    tools=[GoogleSearchTool()],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        top_p=1.0,
        response_mime_type="application/json"
    ),
)
