import os
import inspect
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool

# Sub-agents
from .sub_agents.data.agent import agent as data_agent
from .sub_agents.research.agent import agent as research_agent
from .sub_agents.performance.agent import agent as performance_agent
from .sub_agents.creative.agent import agent as creative_agent

# Shared Tools
from .tools.visualization import plot_and_save_artifacts
from .prompts import ORCHESTRATOR_INSTRUCTION

load_dotenv()

# Wrap function tool
plot_tool = FunctionTool(plot_and_save_artifacts)

# Build Root Agent
agent_kwargs = dict(
    name="orchestrator_agent",
    model=os.getenv("VERTEX_MODEL", "gemini-2.0-flash"),
    description="Control-plane orchestrator for תמי4 marketing system",
    tools=[
        AgentTool(agent=data_agent),
        AgentTool(agent=research_agent),
        AgentTool(agent=performance_agent),
        AgentTool(agent=creative_agent),
        plot_tool,
    ],
)

# Handle ADK version differences for 'instruction' param
sig = inspect.signature(LlmAgent)
if "instructions" in sig.parameters:
    agent_kwargs["instructions"] = ORCHESTRATOR_INSTRUCTION
else:
    agent_kwargs["instruction"] = ORCHESTRATOR_INSTRUCTION

root_agent = LlmAgent(**agent_kwargs)
