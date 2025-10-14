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
engine = pyttsx3.init()

# def speak(text):
#     engine.say(text)
#     engine.runAndWait()

def speak(text):
    def _speak():
        engine.stop()      # stop any previous speech
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()


# --------------------
# Define Tools
# --------------------
def tell_time(_: str) -> str:
    return datetime.datetime.now().strftime("Current time: %H:%M:%S")

def open_google(query: str) -> str:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Opened Google search for '{query}'"

def open_youtube(query: str) -> str:
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Opened YouTube search for '{query}'"

tools = [
    Tool(
        name="Time",
        func=tell_time,
        description="Tell the current time when the user asks for it."
    ),
    Tool(
        name="Google",
        func=open_google,
        description="Use this only when the user explicitly says to open or search on Google."
    ),
    Tool(
        name="YouTube",
        func=open_youtube,
        description="Use this only when the user explicitly says to search or open something on YouTube."
    )
]



# --------------------
# Initialize LLM + Agent
# --------------------
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=api_key)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)

# --------------------
# Streamlit UI
# --------------------
st.set_page_config(page_title="🎤 Voice Assistant", layout="centered")
st.title("🎙️ AI Voice Assistant")

st.markdown("Click **Start Listening** and speak your command (e.g., *'What time is it?'*, *'Open Google for Python tutorials'*).")
st.warning("Say 'stop', 'exit', or 'quit' to end the assistant.")

# Initialize session state
if "listening" not in st.session_state:
    st.session_state.listening = False
if "response" not in st.session_state:
    st.session_state.response = ""

# Speech recognizer
recognizer = sr.Recognizer()

def listen_once():
    """Capture a single voice command."""
    with sr.Microphone() as source:
        st.info("🎧 Listening... please speak now.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        st.success(f"🗣️ You said: {command}")
        return command
    except sr.UnknownValueError:
        st.error("❌ Could not understand audio.")
        return None
    except sr.RequestError:
        st.error("⚠️ Speech recognition service error.")
        return None

# Buttons
col1, col2 = st.columns(2)
with col1:
    start_btn = st.button("🎙️ Start Listening")
with col2:
    stop_btn = st.button("🛑 Stop Assistant")

# Logic
if start_btn:
    command = listen_once()
    if command:
        if any(word in command for word in ["stop", "exit", "quit", "goodbye"]):
            st.session_state.response = "Goodbye! Have a nice day!"
            speak(st.session_state.response)
        else:
            response = agent.invoke(command)
            st.session_state.response = str(response)
            speak(st.session_state.response)

if stop_btn:
    st.session_state.response = "Assistant stopped."
    speak("Goodbye! Assistant stopped.")


# Output
if st.session_state.response:
    st.subheader("🤖 Assistant says:")
    st.success(f"Goodbye! {st.session_state.response}")
