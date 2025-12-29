import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from tami4_agent.agent import root_agent

# Initialize FastAPI app
app = get_fast_api_app(
    agent=root_agent,
    web=True  # Enables the ADK Web UI
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"Starting Tami4 Agent on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
