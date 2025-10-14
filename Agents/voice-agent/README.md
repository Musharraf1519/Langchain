# 🎙️ AI Voice Assistant (LangChain + Streamlit)

A simple yet powerful **voice-controlled AI assistant** built using  
🧠 **LangChain**, 🎤 **SpeechRecognition**, 💬 **OpenAI GPT**, and 🎧 **pyttsx3**.

This app lets you **speak commands** like:
> "What time is it?"  
> "Open Google and search for Python tutorials"  
> "Search data analysis on YouTube"  
> "Stop" (to exit)

---

## 🚀 Features
- 🎙️ **Voice input** using the microphone
- 🗣️ **Speech output** using `pyttsx3`
- 🤖 **Intelligent command understanding** via OpenAI’s GPT model
- 🌐 **Integrated actions** like:
  - Telling current time
  - Opening Google search
  - Opening YouTube search
- 🖥️ **Streamlit interface** — click to start listening
- 🛑 Say “stop”, “exit”, or “quit” to end the session

---

## 🧩 Project Structure
voice-agent/<br>
├─ app.py # Main Streamlit app<br>
├─ .env # Contains your OpenAI API key<br>
├─ requirements.txt # All dependencies<br>
└─ README.md # Documentation<br>

---

## ⚙️ Setup Instructions

### 1️⃣ Clone or create the project folder
```bash
git clone https://github.com/yourusername/voice-agent.git
cd voice-agent
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate       # On Windows
# OR
source venv/bin/activate    # On Mac/Linux
```
### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 4️⃣ Add your OpenAI API key
Create a file named .env in the project folder and add:
```ini
OPENAI_API_KEY=your_openai_api_key_here
```
### 5️⃣ Run the app
```bash
streamlit run app.py
```

---

## 🗣️ How to Use

1. Click "Start Listening" in the Streamlit UI.
2. Speak a command, for example:
     - “What time is it?”
     - “Open Google and search for pandas library”
     - “Search Python tutorials on YouTube”
3. The assistant will:
     - Recognize your voice
     - Understand your intent
     - Execute the correct tool or respond directly
     - Speak the response back to you
4. Say “stop”, “exit”, or “quit” to end the session.

---

## 🧠 Tech Stack

| Component                               | Purpose                                |
| --------------------------------------- | -------------------------------------- |
| **Streamlit**                           | Web-based interface                    |
| **SpeechRecognition**                   | Convert voice → text                   |
| **pyttsx3**                             | Convert text → speech                  |
| **LangChain**                           | Build an intelligent agent with tools  |
| **OpenAI GPT (via `langchain_openai`)** | Understand and respond to user queries |
| **dotenv**                              | Securely load API keys                 |
| **webbrowser**                          | Open Google/YouTube searches           |

---

## ⚠️ Common Issues & Fixes
🔸 Error: RuntimeError: run loop already started

Use this safe threaded speak() function:
```python
import threading

def speak(text):
    def _speak():
        engine.stop()
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()
```

---

## 🧰 requirements.txt
```nginx
streamlit
speechrecognition
pyttsx3
python-dotenv
langchain-openai
openai
```

---

## 👨‍💻 Author

**Musharraf Hussain Khan**
AI | Data | LangChain | Streamlit Projects
📧 [Email me](mailto:musharrafhussainkhann@gmail.com)
[GitHub](https://github.com/Musharraf1519)
[LinkedIn](https://www.linkedin.com/in/musharraf-hussain-khan/)


---

## **⭐ If you found this project useful, give it a star and share it with other AI learners!**
