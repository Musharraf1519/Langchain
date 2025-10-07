from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
import streamlit as st

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Tool
def calculator_tool(query: str) -> str:
    try:
        a, operator, b = query.split()
        a, b = float(a), float(b)
        if operator == '+':
            return str(a + b)
        elif operator == '-':
            return str(a - b)
        elif operator == '*':
            return str(a * b)
        elif operator == '/':
            return str(a / b)
        else:
            return "Error: Invalid operator"
    except:
        return "Error: Use format 'number operator number'"

tools = [
    Tool(name="Calculator", func=calculator_tool, description="Perform basic arithmetic operations")
]

# LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=api_key)

# Initialize agent
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# Streamlit UI
st.title("🧮 Genius Calculator Agent")
st.subheader("Your friendly assistant to crunch numbers and solve arithmetic tasks!")

# Creative text input
task = st.text_input("💡 Enter your math task (e.g., '12 * 12' or '20 + 5' or 12 * 12 and then add 5):")

if task:
    response = agent.invoke(task)
    st.success(f"✨ Results:\n {response}")
