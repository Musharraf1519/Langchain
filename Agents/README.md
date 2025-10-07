# LangChain Agents Collection

This repository contains several **LangChain-powered AI agents** built with Python and Streamlit. Each agent demonstrates a practical application of **tool-using agents** and **LLM integration**.

---

## 📂 Agents Included

### 1. Genius Calculator Agent 🧮
- **Purpose:** Perform basic arithmetic operations like addition, subtraction, multiplication, and division.  
- **Tools:** Calculator Tool  
- **LLM Model:** ChatOpenAI (gpt-3.5-turbo)  
- **Features:**
  - Streamlit UI with text input for math queries.
  - Handles multi-step arithmetic tasks (e.g., `"12 * 12 and then add 5"`).  
- **Usage:**
```bash
  streamlit run genius_calculator_agent.py
```

---

### 2. Multi-Tool Agent 🧩
- **Purpose:** Multi-functional assistant that can calculate, search the web, and summarize text.
- **Tools:**
    1. Calculator Tool �
    2. Web Search Tool 🌐 (SerpAPIWrapper)
    3. Summarizer Tool ✂️
- LLM Model: ChatOpenAI (gpt-3.5-turbo)
- Features:
  - Handles complex tasks combining multiple tools.
  - Streamlit UI with a text area for multi-step tasks.
- Usage:
```bash
  streamlit run multi_tool_agent.py
```

---

### 3. Weather Agent 🌤️
- **Purpose:** Fetches real-time weather information for any city worldwide.
- **Tools:** Weather Info Tool
- LLM Model: ChatOpenAI (gpt-3.5-turbo)
- Features:
  - Streamlit UI with city input.
  - Fetches temperature, humidity, weather condition, and feels-like temperature using OpenWeather API.
  - Handles parsing errors gracefully with handle_parsing_errors=True.
- Usage:
```bash
streamlit run weather_agent.py
```

---

## ⚡ Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/langchain-agents.git
cd langchain-agents
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_api_key      # For Multi-Tool Agent
WEATHER_API_KEY=your_openweathermap_key   # For Weather Agent
```
---

## 🛠️ Dependencies
- Python 3.10+
- Streamlit
- LangChain
- LangChain OpenAI integration (langchain-openai)
- Requests (Weather Agent)
- dotenv

---

## 🔗 References
- LangChain Documentation
- OpenAI API
- SerpAPI
- OpenWeather API

---

## 💡 Notes
- Always keep your API keys private and store them in .env.
- Use AgentType.ZERO_SHOT_REACT_DESCRIPTION for flexible multi-tool agent execution.
- Streamlit session states allow persisting conversation/memory across user inputs for interactive apps.

---

## 👨‍💻 Author

<b>Musharraf Hussain Khan</b><br>
[GitHub](https://github.com/Musharraf1519)<br>
[LinkedIn](https://www.linkedin.com/in/musharraf-hussain-khan/)<br>
Email: musharrafhussainkhann@gmail.com

---

## **⭐ If you found this project useful, consider giving it a star!**
