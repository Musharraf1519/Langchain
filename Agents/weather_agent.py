#Weather_agent.py
from dotenv import load_dotenv
import os
import requests
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType

# Load API keys from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")

# Initialize LLM
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=api_key
)

# Weather function
def get_weather(city: str) -> str:
    """Fetch weather info for a city"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        data = requests.get(url).json()

        if data.get("cod") != 200:
            return f"❌ Error: {data.get('message', 'Failed to fetch weather')}"

        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        return (
            f"🌤️ Weather in {city.title()}\n"
            f"- Condition: {weather}\n"
            f"- Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"- Humidity: {humidity}%"
        )
    except Exception as e:
        return f"⚠️ Error fetching weather: {str(e)}"

# Define Tool
weather_tool = Tool(
    name="Weather Info",
    func=get_weather,
    description="Get the current weather of any city in the world."
)

# Initialize agent with parsing error handling
agent = initialize_agent(
    tools=[weather_tool],
    llm=llm,
    agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True  # ensures agent retries on parsing failures
)

# Streamlit UI
st.title("🌤️ Weather Agent")
st.write("Ask about the weather in any city 🌍")

user_input = st.text_input("Enter your question (e.g., What's the weather in Delhi?)")

if user_input:
    try:
        # Try agent first
        response = agent.run(user_input)
    except Exception as e:
        # Fallback: call tool directly
        response = get_weather(user_input)

    st.success(response)
