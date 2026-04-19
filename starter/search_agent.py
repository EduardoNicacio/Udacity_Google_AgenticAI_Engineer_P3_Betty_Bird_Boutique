import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import google_search, AgentTool

# Load environment variables from .env
load_dotenv()

# Model definition
# Selected for balance of speed and reasoning capability;
# gemini-2.5-pro offers better accuracy but slower response times,
# while flash-lite is too lightweight for complex tool orchestration
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Definition of an agent tool that accesses Grounding with Google Search
# Read the instructions from a file in the same directory as this file.
script_dir = os.path.dirname(os.path.abspath(__file__))
instruction_file_path = os.path.join(script_dir, "search-prompt.txt")
with open(instruction_file_path, "r") as f:
    instruction = f.read()

tools = [google_search]  # ✅ Grounding enabled by default in ADK

# Completed: Implement - Create search agent with Google Search grounding
search_agent = Agent(
    name="search_with_grounding",
    description="Specializes in answering general bird-related questions using web search grounding.",
    instruction=instruction,
    model=model,
    tools=tools,  # type: ignore
)

search_with_grounding = AgentTool(agent=search_agent)
