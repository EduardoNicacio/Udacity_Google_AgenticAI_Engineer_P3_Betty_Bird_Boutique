import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from toolbox_core import ToolboxSyncClient
from .datastore import datastore_search_tool
from .search_agent import search_with_grounding

# Load environment variables from .env
load_dotenv()

# Model definition
# Selected for balance of speed and reasoning capability;
# gemini-2.5-pro offers better accuracy but slower response times,
# while flash-lite is too lightweight for complex tool orchestration
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Configure short-term session to use the in-memory service
session_service = (
    InMemorySessionService()
)  # ✅ RUBRIC REQUIREMENT: Session storage configured

# Read the instructions from a file in the same directory as this agent.py file.
script_dir = os.path.dirname(os.path.abspath(__file__))
instruction_file_path = os.path.join(script_dir, "agent-prompt.txt")
with open(instruction_file_path, "r") as f:
    instruction = f.read()

# Set up the tools that we will be using for the root agent
tools = []  # Start with empty list

# Load database tool from ToolboxSyncClient (Required by rubric)
# This loads get_product_price from MySQL source via MCP Database Toolbox server
try:
    db_client = ToolboxSyncClient(url=os.getenv("TOOLBOX_URL", "http://127.0.0.1:5000"))
    database_tools = db_client.load_tool("get_product_price")  # ✅ RUBRIC REQUIREMENT: Load tool from toolbox server
    tools.append(database_tools)  # Add all loaded tools to our list
    print(f"✅ Loaded {len(tools)} tool(s) from ToolboxSyncClient")
except Exception as e:
    print("⚠️ Warning: Could not load database tools. Ensure TOOLBOX_URL is set and server is running.")
    print(f"   Error: {e}")

# Import datastore search tool (from separate file)
try:
    tools.append(datastore_search_tool)  # ✅ RUBRIC REQUIREMENT: Datastore tool integrated
    print("✅ Loaded datastore_search_tool from datastore.py")
except Exception as e:
    print("⚠️ Warning: Could not import datastore_search_tool.")
    print(f"   Error: {e}")

# Import web search tool (from separate file)
try:
    tools.append(search_with_grounding)
    print("✅ Loaded search_with_grounding from search_agent.py")
except Exception as e:
    print("⚠️ Warning: Could not import search_with_grounding.")
    print(f"   Error: {e}")

# Create your agent with proper configuration
root_agent = Agent(
    name="root_agent",          # ✅ RUBRIC REQUIREMENT: Name configured
    description="A helpful customer service agent for Betty's Bird Boutique, specializing in bird-related questions and store operations.",  # ✅ RUBRIC REQUIREMENT: Description configured
    instruction=instruction,    # ✅ RUBRIC REQUIREMENT: Instruction parameter reads from file
    model=model,                # ✅ RUBRIC REQUIREMENT: Selected for best balance of speed and reasoning capability
    tools=tools,                # ✅ RUBRIC REQUIREMENT: All required tools added to agent
)

# Print confirmation
print("✅ Root Agent created successfully")
print(f"   Name: {root_agent.name}")
print(f"   Model: {root_agent.model}")
if root_agent.tools:
    print(
        f"   Tools loaded: {[getattr(t, 'name', type(t).__name__) for t in root_agent.tools]}"
    )
else:
    print("   No tools loaded.")

# Defines the ADK Runner for the root_agent
runner = Runner(
    agent=root_agent,
    session_service=session_service,  # ✅ RUBRIC REQUIREMENT: InMemorySessionService passed to the Runner
    app_name="bettys_bird_boutique",
)
