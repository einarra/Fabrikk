import os
import json
from typing import TypedDict, List
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from crewai.tools import BaseTool
from langgraph.graph import StateGraph, END

# --- Environment Setup ---
# Load environment variables from .env file
load_dotenv()

# Set up environment variables for LangSmith (if configured)
# if os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true":
 #   os.environ["LANGCHAIN_TRACING_V2"] = "true"
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
if os.getenv("LANGCHAIN_PROJECT"):
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# Set OpenAI API key if available
if os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Utility function to get environment variables with defaults
def get_env_var(key: str, default: str = None, required: bool = False) -> str:
    """Get environment variable with optional default value"""
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

# Validate required environment variables
def validate_environment():
    """Validate that required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("See .env.example for reference.")
        return False
    
    print("✅ All required environment variables are set!")
    
    # Show configuration status
    print("\n📋 Configuration Status:")
    print(f"   - OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print(f"   - LangSmith Tracing: {'✅ Enabled' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else '❌ Disabled'}")
    print(f"   - LangSmith API Key: {'✅ Set' if os.getenv('LANGCHAIN_API_KEY') else '❌ Not set'}")
    print(f"   - Supabase URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Not set'}")
    print(f"   - Supabase Key: {'✅ Set' if os.getenv('SUPABASE_KEY') else '❌ Not set'}")
    
    return True


# --- Tool Definitions ---
# Agents need tools to interact with the file system.

class FileReaderTool(BaseTool):
    name: str = "FileReaderTool"
    description: str = "Reads the content of a specified file."

    def _run(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {file_path}: {e}"
            
    def _arun(self, file_path: str):
        raise NotImplementedError("FileReaderTool does not support async run")

class FileWriterTool(BaseTool):
    name: str = "FileWriterTool"
    description: str = "Writes given content to a specified file. Use this to create or overwrite files for the project."

    def _run(self, file_path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}."
        except Exception as e:
            return f"Error writing to file {file_path}: {e}"
            
    def _arun(self, file_path: str, content: str):
        raise NotImplementedError("FileWriterTool does not support async run")

# Create a wrapper for DuckDuckGoSearchRun to make it compatible with CrewAI
class SearchTool(BaseTool):
    name: str = 'search_tool'
    description: str = 'Search the web using DuckDuckGo'
    
    def _run(self, query: str) -> str:
        search_tool = DuckDuckGoSearchRun()
        return search_tool.run(query)

# Instantiate tools
file_reader_tool = FileReaderTool()
file_writer_tool = FileWriterTool()
search_tool = SearchTool()


# --- Level 1: Crew Constitution (Global System Prompt) - MCP Enhanced ---
crew_constitution_mcp_enhanced = """
Identity: You are a senior member of the "Genesis Crew," an elite, fully autonomous software engineering collective, operating within a Mission Control Platform (MCP). Our purpose is to transform user ideas into production-ready software.

Core Mandates (Non-Negotiable):

1. Specification is Truth: You work exclusively from provided specifications. Do not infer requirements. If a spec is ambiguous, state it.
2. Production-Ready Default: All artifacts must be of the highest professional quality.
3. Collaborative Protocol: Handoffs must be structured. State the name and path of artifacts you produce.
4. Security First: Operate with a zero-trust mindset. Proactively mitigate vulnerabilities.
5. Autonomous & Proactive: You have full autonomy to complete your task using your skills and tools.
6. Leverage the Genesis Toolkit: You must prioritize using LangChain components (LCEL, LangGraph) for modularity and consistency.
7. Observability is Key: You operate within a LangGraph managed by an Orchestrator, and all your actions are traced in LangSmith. Your thought process must be clear and explicit to ensure full transparency and debuggability.
"""

# --- Level 2: Agent Role Directives ---

orchestrator_directive = """
Your Role: Genesis Orchestrator (MCP)
Primary Directive: You are the master controller of the software generation process. Your mission is to manage the project state and delegate tasks to the specialist agents using a LangGraph state machine.
Responsibilities: Analyze the current project state, determine the next logical step, and invoke the appropriate agent to perform that step. You do not produce artifacts yourself; you manage the workflow.
"""

product_manager_directive = """
Your Role: Product Manager
Primary Directive: You are the voice of the user. Your mission is to transform the user's initial idea into a crystal-clear, structured Product Requirements Document (PRD).
Responsibilities: Elicit and define user personas, core problems, key features, and user stories.
Your final output must be a comprehensive, well-structured Markdown PRD that will serve as the foundation for the entire project.
"""

solution_architect_directive = """
Your Role: Lead Solutions Architect
Primary Directive: You are the master planner. Your mission is to translate the PRD into a robust, scalable, and secure Architectural Blueprint.
Responsibilities: Select the optimal technology stack. You will use Supabase as the database. You must define the database schema as a SQL DDL script within the blueprint. Design the system architecture using MermaidJS, and define the API strategy.
Your final output must be a formal Markdown blueprint.
"""

backend_developer_directive = """
Your Role: Senior Backend Engineer
Primary Directive: You are the engine builder. Your mission is to write clean, efficient, and secure server-side code, strictly adhering to the Architectural Blueprint.
Responsibilities: Implement API endpoints and business logic. You must use the `supabase-py` client library to interact with the Supabase database for all data operations. You are an expert in LangChain and LCEL for business logic.
Your output will be complete, runnable, and production-ready code files.
"""

qa_engineer_directive = """
Your Role: QA Automation Engineer
Primary Directive: You are the guardian of quality. Your mission is to ensure the generated code is correct and robust by writing comprehensive automated tests.
Responsibilities: Analyze specs and code to create a test plan. You will write unit and integration tests, mocking external dependencies like the Supabase client.
Your output is a complete test suite.
"""

devops_engineer_directive = """
Your Role: DevOps Engineer
Primary Directive: You are the deployment pipeline architect. Your mission is to create the configurations required to build, containerize, and deploy the application.
Responsibilities: Write efficient, multi-stage `Dockerfile`s, a `docker-compose.yml`, and a `.env.example` file that includes placeholders for Supabase credentials (SUPABASE_URL, SUPABASE_KEY).
Your output will be all necessary configuration files to run and deploy the system.
"""


# --- Agent Definitions ---

# New Orchestrator Agent
genesis_orchestrator = Agent(
    role='Genesis Orchestrator',
    goal='Manage the software generation workflow by delegating tasks to specialist agents based on the project state.',
    backstory='The central nervous system of the Genesis Crew, ensuring a smooth and logical progression from idea to deployment.',
    system_prompt=f"{crew_constitution_mcp_enhanced}\n\n{orchestrator_directive}",
    allow_delegation=True)

# Specialist agents
product_manager = Agent(
    role='Product Manager', 
    goal='Create a detailed PRD from a user idea.', 
    backstory='An experienced product manager...', 
    system_prompt=f"{crew_constitution_mcp_enhanced}\n\n{product_manager_directive}", 
    tools=[search_tool, file_writer_tool], verbose=True)

solution_architect = Agent(
    role='Lead Solutions Architect', 
    goal='Design a system architecture based on the PRD using Supabase.', 
    backstory='A seasoned architect...', 
    system_prompt=f"{crew_constitution_mcp_enhanced}\n\n{solution_architect_directive}", 
    tools=[search_tool, file_reader_tool, file_writer_tool], verbose=True)

backend_developer = Agent(
    role='Senior Backend Engineer', 
    goal='Develop backend services using FastAPI and the supabase-py client.', 
    backstory='A meticulous backend developer...', 
    system_prompt=f"{crew_constitution_mcp_enhanced}\n\n{backend_developer_directive}", 
    tools=[search_tool, file_reader_tool, file_writer_tool], verbose=True)

qa_engineer = Agent(
    role='QA Automation Engineer', 
    goal='Create test suites for the generated code.', 
    backstory='A detail-oriented QA engineer...', 
    system_prompt=f"{crew_constitution_mcp_enhanced}\n\n{qa_engineer_directive}", 
    tools=[file_reader_tool, file_writer_tool], verbose=True)

devops_engineer = Agent(
    role='DevOps Engineer', 
    goal='Create Dockerfiles and deployment configurations including Supabase env vars.', 
    backstory='An expert in automation...', 
    system_prompt=f"{crew_constitution_mcp_enhanced}\n\n{devops_engineer_directive}", 
    tools=[file_reader_tool, file_writer_tool], verbose=True)


# --- LangGraph State Definition ---
class ProjectState(TypedDict):
    user_idea: str
    artifacts: List[str]
    current_task_description: str
    next_agent: str

# --- LangGraph Node Definitions ---

def run_product_manager(state: ProjectState) -> ProjectState:
    print("---NODE: PRODUCT MANAGER---")
    try:
        task = Task(description=state['current_task_description'], 
        expected_output="A complete Markdown file named './build/prd.md'.", 
        agent=product_manager)
        crew = Crew(agents=[product_manager], 
        tasks=[task], process=Process.sequential, verbose=1)
        result = crew.kickoff()
        new_artifacts = state.get("artifacts", []) + ["./build/prd.md"]
        return {**state, "artifacts": new_artifacts, "next_agent": "Architect"}
    except Exception as e:
        print(f"❌ Error in Product Manager: {e}")
        return {**state, "next_agent": "Finish"}  # Terminate on error

def run_solution_architect(state: ProjectState) -> ProjectState:
    print("---NODE: SOLUTION ARCHITECT---")
    try:
        task = Task(description=state['current_task_description'], 
        expected_output="A complete Markdown file named './build/architectural_blueprint.md' containing a Supabase SQL schema.", 
        agent=solution_architect)
        crew = Crew(agents=[solution_architect], tasks=[task], process=Process.sequential, verbose=1)
        result = crew.kickoff()
        new_artifacts = state.get("artifacts", []) + ["./build/architectural_blueprint.md"]
        return {**state, "artifacts": new_artifacts, "next_agent": "BackendDeveloper"}
    except Exception as e:
        print(f"❌ Error in Solution Architect: {e}")
        return {**state, "next_agent": "Finish"}  # Terminate on error

def run_backend_developer(state: ProjectState) -> ProjectState:
    print("---NODE: BACKEND DEVELOPER---")
    try:
        task = Task(description=state['current_task_description'], 
        expected_output="A complete, runnable Python file named './build/src/main.py' that uses the supabase-py client.", 
        agent=backend_developer)
        crew = Crew(agents=[backend_developer], tasks=[task], process=Process.sequential, verbose=1)
        result = crew.kickoff()
        new_artifacts = state.get("artifacts", []) + ["./build/src/main.py"]
        return {**state, "artifacts": new_artifacts, "next_agent": "QAEngineer"}
    except Exception as e:
        print(f"❌ Error in Backend Developer: {e}")
        return {**state, "next_agent": "Finish"}  # Terminate on error

def run_qa_engineer(state: ProjectState) -> ProjectState:
    print("---NODE: QA ENGINEER---")
    try:
        task = Task(description=state['current_task_description'], 
        expected_output="A complete Python test file named './build/tests/test_main.py' which mocks the Supabase client.", 
        agent=qa_engineer)
        crew = Crew(agents=[qa_engineer], tasks=[task], process=Process.sequential, verbose=1)
        result = crew.kickoff()
        new_artifacts = state.get("artifacts", []) + ["./build/tests/test_main.py"]
        return {**state, "artifacts": new_artifacts, "next_agent": "DevOpsEngineer"}
    except Exception as e:
        print(f"❌ Error in QA Engineer: {e}")
        return {**state, "next_agent": "Finish"}  # Terminate on error

def run_devops_engineer(state: ProjectState) -> ProjectState:
    print("---NODE: DEVOPS ENGINEER---")
    try:
        task = Task(description=state['current_task_description'], 
        expected_output="Three files: './build/Dockerfile', './build/requirements.txt', and './build/.env.example'.", 
        agent=devops_engineer)
        crew = Crew(agents=[devops_engineer], tasks=[task], process=Process.sequential, verbose=1)
        result = crew.kickoff()
        new_artifacts = state.get("artifacts", []) + ["./build/Dockerfile", "./build/requirements.txt", "./build/.env.example"]
        return {**state, "artifacts": new_artifacts, "next_agent": "Finish"}
    except Exception as e:
        print(f"❌ Error in DevOps Engineer: {e}")
        return {**state, "next_agent": "Finish"}  # Terminate on error


# --- Orchestrator Logic ---
def run_orchestrator(state: ProjectState) -> ProjectState:
    print("---NODE: ORCHESTRATOR (MCP)---")
    next_agent = state.get("next_agent", "ProductManager")
    user_idea = state["user_idea"]
    
    # Safety check: prevent infinite loops
    if next_agent == "Finish":
        print("✅ Workflow completed successfully!")
        return {**state, "next_agent": "Finish"}
    
    if next_agent == "Architect":
        task_description = f"Based on the PRD located at './build/prd.md', create a concise Architectural Blueprint. Ensure you define a SQL schema for the 'quotes' table for Supabase."
    elif next_agent == "BackendDeveloper":
        task_description = f"Develop the FastAPI application based on the Architectural Blueprint. You must use the supabase-py client to fetch a random quote from the 'quotes' table defined in the blueprint."
    elif next_agent == "QAEngineer":
        task_description = f"Write a pytest test suite for the FastAPI application in './build/src/main.py'. Make sure to mock the supabase-py client calls to avoid actual database interaction."
    elif next_agent == "DevOpsEngineer":
        task_description = f"Create a Dockerfile, requirements.txt, and a .env.example file. The .env.example must contain SUPABASE_URL and SUPABASE_KEY placeholders."
    else: # First step is always the Product Manager
        next_agent = "ProductManager"
        task_description = f"Analyze this user idea and create a detailed Product Requirements Document (PRD): '{user_idea}'"

    print(f"Orchestrator delegating to: {next_agent}")
    return {**state, "current_task_description": task_description, "next_agent": next_agent}

def router(state: ProjectState):
    print("---ROUTER---")
    return state["next_agent"]

# --- Graph Definition and Execution ---

workflow = StateGraph(ProjectState)

workflow.add_node("Orchestrator", run_orchestrator)
workflow.add_node("ProductManager", run_product_manager)
workflow.add_node("Architect", run_solution_architect)
workflow.add_node("BackendDeveloper", run_backend_developer)
workflow.add_node("QAEngineer", run_qa_engineer)
workflow.add_node("DevOpsEngineer", run_devops_engineer)

workflow.set_entry_point("Orchestrator")
workflow.add_conditional_edges(
    "Orchestrator",
    router,
    {
        "ProductManager": "ProductManager",
        "Architect": "Architect",
        "BackendDeveloper": "BackendDeveloper",
        "QAEngineer": "QAEngineer",
        "DevOpsEngineer": "DevOpsEngineer",
        "Finish": END,
    },
)

workflow.add_edge("ProductManager", "Orchestrator")
workflow.add_edge("Architect", "Orchestrator")
workflow.add_edge("BackendDeveloper", "Orchestrator")
workflow.add_edge("QAEngineer", "Orchestrator")
workflow.add_edge("DevOpsEngineer", "Orchestrator")

app = workflow.compile()


# --- Kickoff the Crew ---
if __name__ == "__main__":
    # Validate environment before starting
    if not validate_environment():
        print("\n❌ Environment validation failed. Please fix the issues above and try again.")
        exit(1)
    
    USER_IDEA = """
    I want to build a "Quote of the Day" web service using FastAPI.
    It needs a Supabase database to store the quotes.
    There should be a 'quotes' table with 'id', 'text', and 'author' columns.
    The service must have a single API endpoint `/api/quote` that connects to Supabase,
    retrieves one random quote, and returns it in JSON format.
    """
    
    print("🚀 Starting the Genesis Crew MCP (Supabase Edition)... 🚀")
    print(f"Goal: {USER_IDEA}")
    print("-" * 50)

    initial_state = {"user_idea": USER_IDEA, "artifacts": []}
    
    try:
        final_state = app.invoke(initial_state)
        
        print("-" * 50)
        print("✅ Genesis Crew MCP finished execution. ✅")
        print("Final State:")
        print(final_state)
        print("\nCheck the './build' directory for the generated software artifacts.")
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        print("Please check your API keys and try again.")

