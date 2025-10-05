import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from dotenv import load_dotenv
import os

# --- Configuration & Initialization ---

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Check if API Key is available
if not api_key:
    st.error("OPENAI_API_KEY not found. Please create a .env file or set the environment variable.")
    st.stop()

# Streamlit UI Setup
st.set_page_config(page_title="KnowledgeBot", page_icon="🤖", layout="centered")
st.title("KnowledgeBot 🤖")
st.markdown("Ask me anything! I will remember our conversation history across multiple turns.")


# Use st.session_state to persist the conversation chain and memory
if 'conversation' not in st.session_state:
    # Initialize the LLM 
    chat_model = ChatOpenAI(model_name="gpt-5-nano", temperature=0.6, openai_api_key=api_key)

    # Create memory with the specified key
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Define the custom prompt, correctly utilizing the 'chat_history' memory key
    custom_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a professional and helpful AI assistant. You remember what the user says and provide clear, concise answers."
        ),
        # The ConversationChain will automatically populate {chat_history} and {input}
        HumanMessagePromptTemplate.from_template(
            "Conversation so far:\n{chat_history}\n\nUser: {input}"
        )
    ])

    # Create and store the conversation chain in session state
    st.session_state.conversation = ConversationChain(
        llm=chat_model,
        prompt=custom_prompt,
        memory=memory,
        verbose=False # Set to True to see how the chain processes the prompt
    )

# --- Conversation Logic ---

# Retrieve the conversation object from session state
conversation = st.session_state.conversation

# Input from user
user_input = st.text_input("Your message:", key="user_input_key")

if user_input:
    # 1. Get the response from the LLM
    # The .predict method returns a string in this configuration
    response = conversation.predict(input=user_input)

    # 2. Display the response
    st.markdown("---")
    st.markdown(f"**🤖 KnowledgeBot:** {response}")
    st.markdown("---")


# # Optional: Show conversation history for verification
# if conversation.memory.chat_memory.messages:
#     st.markdown("### Conversation History (For Debugging)")
#     # LangChain stores history as HumanMessage and AIMessage objects
#     for msg in conversation.memory.chat_memory.messages:
#         role = "👤 You" if msg.type == "human" else "🤖 AI"
#         st.markdown(f"**{role}:** {msg.content}")

#     # Button to clear the history
#     if st.button("Clear Conversation History"):
#         conversation.memory.clear()
#         st.session_state.conversation = conversation # Update session state
#         st.rerun() # Rerun the script to reflect the changes
