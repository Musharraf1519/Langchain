import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os

# --- Load API Key ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please create a .env file or set the environment variable.")
    st.stop()

# --- Streamlit UI Setup ---
st.set_page_config(page_title="KnowledgeBot", page_icon="🤖", layout="centered")
st.title("KnowledgeBot 🤖")
st.markdown("Hey there 👋 I'm KnowledgeBot — your chat companion for facts, logic, and learning. What are we tackling today?")

# --- Initialize Chat State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are KnowledgeBot, a helpful and professional AI assistant.")
    ]

# --- Initialize Chat Model ---
llm = ChatOpenAI(
    model="gpt-4o-mini",   # or "gpt-4-turbo"
    temperature=0.6,
    openai_api_key=api_key,
)

# --- Chat Interface ---
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").markdown(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").markdown(msg.content)

# User input
if prompt := st.chat_input("Type your message..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(HumanMessage(content=prompt))

    # Generate response
    with st.spinner("Thinking..."):
        response = llm.invoke(st.session_state.messages)

    # Display AI message
    st.chat_message("assistant").markdown(response.content)
    st.session_state.messages.append(AIMessage(content=response.content))
