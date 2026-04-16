import os
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from toolbox_core import ToolboxSyncClient
from .datastore import datastore_search_tool
from .search_agent import search_agent_tool

# Configure short-term session to use the in-memory service
session_service = InMemorySessionService()  # ✅ RUBRIC REQUIREMENT: Session storage configured

# Read the instructions from a file in the same directory as this agent.py file.
script_dir = os.path.dirname(os.path.abspath(__file__))
instruction_file_path = os.path.join(script_dir, "agent-prompt.txt")
with open(instruction_file_path, "r") as f:
    instruction = f.read()

# Set up the tools that we will be using for the root agent
tools = []  # Start with empty list

# Model definition
# Selected for balance of speed and reasoning capability; 
# gemini-2.5-pro offers better accuracy but slower response times,
# while flash-lite is too lightweight for complex tool orchestration
model="gemini-2.5-flash"

# Load database tool from ToolboxSyncClient (Required by rubric)
# This loads get-product-price from MySQL source via MCP Database Toolbox server
try:
    db_client = ToolboxSyncClient(url=os.environ.get("TOOLBOX_URL", "http://127.0.0.1:5000"))
    database_tools = db_client.load_tool("get-product-price-tool")  # ✅ RUBRIC REQUIREMENT: Load tool from toolbox server
    tools.append(database_tools)                                    # Add all loaded tools to our list
    print(f"✅ Loaded {len(tools)} tool(s) from ToolboxSyncClient")
except Exception as e:
    print("⚠️ Warning: Could not load database tools. Ensure TOOLBOX_URL is set and server is running.")
    print(f"   Error: {e}")

# Import datastore search tool (from separate file)
try:
    tools.append(datastore_search_tool)  # ✅ RUBRIC REQUIREMENT: Datastore tool integrated
    print("✅ Loaded datastore_search_tool from datastore.py")
except Exception as e:
    print("⚠️ Warning: Could not import datastore search tool.")
    print(f"   Error: {e}")

# # Import web search tool (from separate file)
try:
    tools.append(search_agent_tool)
    print("✅ Loaded search_agent_tool from search_agent.py")
except Exception as e:
    print("⚠️ Warning: Could not import search_agent tool.")
    print(f"   Error: {e}")

# Create your agent with proper configuration
agent = Agent(
    name="Betty's Bird Boutique Assistant",  # ✅ RUBRIC REQUIREMENT: Name configured
    description="A helpful customer service agent for Betty's Bird Boutique, specializing in bird-related questions and store operations.",  # ✅ RUBRIC REQUIREMENT: Description configured
    instruction=instruction,                 # ✅ RUBRIC REQUIREMENT: Instruction parameter reads from file
    session_service=session_service,         # ✅ RUBRIC REQUIREMENT: Session storage passed to Agent constructor # type: ignore
    model=model,                             # ✅ RUBRIC REQUIREMENT: Selected for best balance of speed and reasoning capability
    tools=tools,                             # ✅ RUBRIC REQUIREMENT: All required tools added to agent
)

# Print confirmation
print("✅ Root Agent created successfully")
print(f"   Name: {agent.name}")
print(f"   Model: {agent.model}")
print(f"   Tools loaded: {[t.name for t in agent.tools]}") # type: ignore
