from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
import streamlit as st
from langchain.utilities import SerpAPIWrapper

# Load API keys
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
serp_api_key = os.getenv("SERPAPI_API_KEY")

# LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=api_key)

# Tools
def calculator_tool(query: str) -> str:
    try:
        a, operator, b = query.split()
        a, b = float(a), float(b)
        if operator == '+': return str(a + b)
        if operator == '-': return str(a - b)
        if operator == '*': return str(a * b)
        if operator == '/': return str(a / b)
        return "Error: Invalid operator"
    except:
        return "Error: Use format 'number operator number'"

search = SerpAPIWrapper(serpapi_api_key=serp_api_key)
def search_tool(query: str) -> str:
    return search.run(query)

def summarize_tool(text: str) -> str:
    return f"Summary: {text[:150]}..." if len(text) > 150 else f"Summary: {text}"

tools = [
    Tool(name="Calculator", func=calculator_tool, description="Basic arithmetic"),
    Tool(name="Web Search", func=search_tool, description="Google search"),
    Tool(name="Summarizer", func=summarize_tool, description="Summarize long text content."),
]

# Initialize agent
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# Streamlit UI
st.title("🧮 Multi-Tool Agent")
st.subheader("Your assistant for calculations, web search, and summarization!")

task = st.text_input("💡 Enter your task:")

if task:  # Only run if user entered something
    with st.spinner("Agent is thinking..."):
        response = agent.run(task)
    st.success(f"Agent response: {response}")
