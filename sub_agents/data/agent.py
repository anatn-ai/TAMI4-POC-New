import os
from google.adk.agents import LlmAgent
from .prompts import INSTRUCTION
from .tools import get_bigquery_toolset

agent = LlmAgent(
    name="data_agent",
    model=os.getenv("VERTEX_MODEL", "gemini-2.0-flash"),
    description="Queries BigQuery (read-only) and returns structured JSON results for the orchestrator.",
    instruction=INSTRUCTION,
    tools=[get_bigquery_toolset()],
)
