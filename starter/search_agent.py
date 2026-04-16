import os
from google.adk import Agent
from google.adk.tools import AgentTool, google_search

# Definition of an agent tool that accesses Grounding with Google Search

# Read the instructions from a file in the same directory as this file.
script_dir = os.path.dirname(os.path.abspath(__file__))
instruction_file_path = os.path.join(script_dir, "search-prompt.txt")
with open(instruction_file_path, "r") as f:
    instruction = f.read()

# Model definition
# Selected for balance of speed and reasoning capability; 
# gemini-2.5-pro offers better accuracy but slower response times,
# while flash-lite is too lightweight for complex tool orchestration
model="gemini-2.5-flash"

tools = [
    google_search
]

# Completed: Implement - Create search agent with Google Search grounding
search_agent = Agent(
    name="web_search_agent",
    description="Specializes in answering general bird-related questions using web search grounding.",
    instruction=instruction,
    model=model,
    tools=tools, # type: ignore
)

search_agent_tool = AgentTool(agent=search_agent)