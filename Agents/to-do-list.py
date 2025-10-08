import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain import hub
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate

# --- 1. CONFIGURATION ---
TODO_FILE = "todo_list.txt"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. TOOLS SETUP (Persistent State Management) ---

def add_to_list(item: str) -> str:
    """Adds a new single task/item to the to-do list file."""
    try:
        with open(TODO_FILE, "a") as f:
            f.write(item + "\n")
        return f"Successfully added '{item}' to the to-do list."
    except Exception as e:
        return f"Error adding item: {e}"

def view_list(query: str = "") -> str:
    """Reads and returns the current items in the todo list file."""
    try:
        if not os.path.exists(TODO_FILE) or os.path.getsize(TODO_FILE) == 0:
            return "The to-do list is currently empty."
            
        with open(TODO_FILE, "r") as f:
            content = f.read().strip()
            # Format content for better display in the final response
            if content:
                items = [f"- {line}" for line in content.split('\n') if line]
                return "Current To-Do List:\n" + "\n".join(items)
            return "The to-do list is currently empty."
            
    except Exception as e:
        return f"Error viewing list: {e}"

def clear_list(query: str = "") -> str:
    """Empties the entire contents of the todo list file."""
    try:
        # Check if file exists and delete it to completely reset
        if os.path.exists(TODO_FILE):
             os.remove(TODO_FILE)
        # Create a new, empty file to ensure the path exists for next write
        with open(TODO_FILE, "w"):
            pass
            
        return "To-do list cleared successfully."
    except Exception as e:
        return f"Error clearing list: {e}"

# Wrap Python functions into LangChain Tool objects
agent_tools = [
    Tool(
        name="Add_Item",
        func=add_to_list,
        description="Useful for adding a new task to the to-do list. Input must be the exact task string."
    ),
    Tool(
        name="View_List",
        func=view_list,
        description="Useful for showing all current tasks in the list. Input is ignored (use an empty string)."
    ),
    Tool(
        name="Clear_List",
        func=clear_list,
        description="Useful for deleting all tasks from the list. Input is ignored (use an empty string)."
    ),
]

# --- 3. AGENT INITIALIZATION (Caching for Streamlit) ---

@st.cache_resource
def initialize_agent():
    # --- 3a. Brain Setup (LLM) ---
    # Ensure OPENAI_API_KEY is set in your environment or Streamlit secrets
    # Load API key
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")

    # 🚨 Check if key exists
    if not api_key:
        st.error("🚨 Please set the OPENAI_API_KEY in your .env file.")
        return None
            
    llm_brain = ChatOpenAI(temperature=0, model="gpt-3.5-turbo",openai_api_key=api_key)

    # --- 3b. Memory Setup (Conversational) ---
    # This memory object will store the history of the conversation
    agent_memory = ConversationBufferWindowMemory(
        memory_key="chat_history", 
        k=5, # Last 5 exchanges
        return_messages=True 
    )

    # --- 3c. Instructions (Prompt) & Customization ---
    SYSTEM_MESSAGE = (
        "You are a diligent and helpful To-Do List Manager Agent. "
        "Your primary goal is to use the provided tools to manage the user's to-do list stored in 'todo_list.txt'. "
        "Use the tools when the user's intent is clearly to add, view, or clear the list. "
        "Your responses should be based on the Observation from the tool or the chat history. "
        "You have access to the chat history under the key 'chat_history'."
    )
    
    # We pull the standard ReAct template and add the system message AND the chat history variable.
    prompt_template = hub.pull("hwchase17/react-chat") # Use react-chat for memory support
    
    # Create the Agent Chain (Logic)
    todo_agent = create_react_agent(
        llm=llm_brain,
        tools=agent_tools,
        prompt=prompt_template
    )

    # --- 3d. Executor (Controller) ---
    agent_executor = AgentExecutor(
        agent=todo_agent,
        tools=agent_tools,
        verbose=True, # Displaying the Thought/Action/Observation loop in the Streamlit console
        handle_parsing_errors=True,
        memory=agent_memory, # Attach the memory to the executor
    )
    
    return agent_executor

# --- 4. STREAMLIT APP LAYOUT AND LOGIC ---

# Initialize the agent and check for API key
executor = initialize_agent()
if executor is None:
    st.stop()

st.set_page_config(page_title="The ReAct-ive Task Manager 🧠", layout="centered")

st.title("The ReAct-ive Task Manager 🧠")
st.caption("A LangChain Agent using LLM reasoning and file-based tools.")

# Sidebar for tool/file status
st.sidebar.header("Tool Status")
st.sidebar.markdown(f"**To-Do File:** `{TODO_FILE}`")
st.sidebar.code(view_list())

if st.sidebar.button("Clear All Tasks (Hard Reset)"):
    clear_list()
    st.sidebar.code(view_list())
    st.rerun()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What would you like to add, view, or clear?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking and acting..."):
            # Invoke the executor (Controller)
            try:
                # The 'input' for the agent is the user's prompt
                result = executor.invoke({"input": prompt})
                response = result.get("output", "Sorry, I couldn't process that request.")
            except Exception as e:
                response = f"An execution error occurred: {e}"

        st.markdown(response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Rerun the app to update the sidebar file view
    st.rerun()