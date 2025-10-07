from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
import requests
import streamlit as st

# Load API keys
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")

# Initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=api_key)

# Define Weather Tool
def get_weather(city: str) -> str:
    """Fetch current weather information for a given city."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return f"❌ Error: {data.get('message', 'Failed to fetch weather')}"

        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        return (
            f"🌦️ **Weather in {city.title()}**\n"
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

# Initialize agent (must pass a *list* of tools)
agent = initialize_agent(
    tools=[weather_tool],
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True 
)

# Streamlit or CLI input

# Streamlit UI
st.title("🌤️ Weather Agent")
st.write("Ask about the weather in any city 🌍")

city = st.text_input("Enter your question (e.g., What's the weather in Delhi?)")


if city:
    response = agent.invoke(city)
    st.success(response["output"])