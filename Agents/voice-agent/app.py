import streamlit as st
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
import os
import datetime
import webbrowser
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
import threading

# --------------------
# Load environment
# --------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# --------------------
# Initialize text-to-speech
# --------------------
# Initialize outside the function for better performance
engine = pyttsx3.init()

def speak(text):
    """Speaks the text in a non-blocking thread."""
    def _speak():
        # Ensure the engine is initialized and configured if needed here
        try:
            # engine.stop() # Can be removed if the thread ensures single instance per call
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            # Handle error (e.g., engine already running, device error)
            print(f"TTS Error: {e}")
    
    # Run TTS in a separate thread so Streamlit UI doesn't freeze
    threading.Thread(target=_speak, daemon=True).start()


# --------------------
# Define Tools
# --------------------
def tell_time(_: str) -> str:
    """Returns the current time."""
    return datetime.datetime.now().strftime("The current time is %H:%M:%S")

def open_google(query: str) -> str:
    """Opens Google search in a new browser tab."""
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"I have opened Google search for '{query}'"

def open_youtube(query: str) -> str:
    """Opens YouTube search in a new browser tab."""
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"I have opened YouTube search for '{query}'"

tools = [
    Tool(
        name="Time",
        func=tell_time,
        description="Tell the current time when the user asks for the current time. Input is always an empty string."
    ),
    Tool(
        name="Google",
        func=open_google,
        description="Use this only when the user explicitly says to open or search on Google. The input should be the search query."
    ),
    Tool(
        name="YouTube",
        func=open_youtube,
        description="Use this only when the user explicitly says to search or open something on YouTube. The input should be the search query."
    )
]


# --------------------
# Initialize LLM + Agent
# --------------------
# Only initialize once
@st.cache_resource
def initialize_agent_system():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=api_key)
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)
    return agent

agent = initialize_agent_system()


# --------------------
# Streamlit UI
# --------------------
st.set_page_config(page_title="🎤 Voice Assistant", layout="centered")
st.title("🎙️ AI Voice Assistant")

st.markdown("Click **Start Listening** and speak your command (e.g., *'What time is it?'*, *'Open Google for Python tutorials'*).")
st.warning("Say 'stop', 'exit', 'quit', or 'goodbye' to gracefully end the assistant.")

# Initialize session state
if "response" not in st.session_state:
    st.session_state.response = ""

# Speech recognizer
recognizer = sr.Recognizer()

def listen_once():
    """Capture a single voice command."""
    with sr.Microphone() as source:
        st.info("🎧 Listening... please speak now.")
        # Reduce unnecessary ambient noise adjustment time
        # recognizer.adjust_for_ambient_noise(source) 
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            st.error("No speech detected. Timed out.")
            return None
            
    try:
        command = recognizer.recognize_google(audio).lower()
        st.success(f"🗣️ You said: {command}")
        return command
    except sr.UnknownValueError:
        # st.error("❌ Could not understand audio.") # Suppress error for cleaner UI on unknown input
        return None
    except sr.RequestError:
        st.error("⚠️ Speech recognition service error. Check your network connection.")
        return None

# Buttons
col1, col2 = st.columns(2)
with col1:
    start_btn = st.button("🎙️ Start Listening")
with col2:
    # Adding a disabled state to the stop button if needed, but keeping it simple for now
    stop_btn = st.button("🛑 Stop Assistant")

# --- Main Logic ---
if start_btn:
    command = listen_once()
    if command:
        # Check for exit commands first
        if any(word in command for word in ["stop", "exit", "quit", "goodbye"]):
            response_text = "Goodbye! Have a nice day!"
            st.session_state.response = response_text
            speak(response_text)
        else:
            # Invoke the LangChain agent
            try:
                response = agent.invoke(command)
                response_text = response["output"] # LangChain agent.invoke returns a dict
                st.session_state.response = response_text
                speak(response_text)
            except Exception as e:
                error_msg = f"An error occurred: {e}"
                st.session_state.response = error_msg
                speak("I encountered an error while processing your request.")
                st.error(error_msg)


if stop_btn:
    response_text = "Assistant stopped. Goodbye!"
    st.session_state.response = response_text
    speak(response_text)


# --- Output Display ---
if st.session_state.response:
    st.subheader("🤖 Assistant says:")
    # CORRECTED LINE: Display the actual response text.
    st.info(st.session_state.response)
    
# Clean up the output state after display if you want the box to clear on next run
# However, keeping it in state is fine for reviewing the last response.