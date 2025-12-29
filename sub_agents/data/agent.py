import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.genai import types
from .prompts import INSTRUCTION
from .tools import get_bigquery_toolset

load_dotenv()

# Build agent kwargs
agent_kwargs = dict(
    model=os.getenv("VERTEX_MODEL", "gemini-2.0-flash"),
    name="data_agent",
    description="Queries BigQuery (read-only) and returns structured JSON results for the orchestrator.",
    instruction=INSTRUCTION,
    tools=[get_bigquery_toolset()],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,
        top_p=1.0,
    ),
)

agent = LlmAgent(**agent_kwargs)
