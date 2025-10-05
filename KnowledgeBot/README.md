# 🤖 KnowledgeBot — LangChain-Powered Chatbot

KnowledgeBot is an interactive chatbot built using **LangChain**, **Streamlit**, and **OpenAI's GPT-5 Nano model**.  
It remembers your past messages using **conversation memory** and provides clear, context-aware answers.

---

## 🚀 Features
- 🧠 **Conversational Memory** — Remembers what you said earlier  
- 💬 **Natural Chat Flow** — Powered by GPT-5 Nano  
- ⚙️ **LangChain Integration** — Uses ConversationChain and Prompt Templates  
- 🌐 **Streamlit UI** — Clean, interactive chat interface  

---

## 🧩 Tech Stack
- **Python 3.10+**
- **LangChain**
- **OpenAI (GPT-5 Nano)**
- **Streamlit**
- **dotenv**

---

## 🧠 System Architecture

Below is a simple diagram showing how KnowledgeBot works under the hood:

```text
                ┌──────────────────────┐
                │        User          │
                │ (Inputs a question)  │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │      Streamlit UI    │
                │ (Handles frontend)   │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │      LangChain       │
                │ (ConversationChain,  │
                │  Prompt Templates)   │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │      GPT-5 Model     │
                │ (Generates Response) │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   ConversationMemory │
                │ (Stores Chat History)│
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │     Streamlit UI     │
                │ (Displays Response)  │
                └──────────────────────┘
```
---

## 📁 Folder Structure
Langchain/<br>
├── knowledgebot.py       # Main chatbot script<br>
├── .env                  # Environment file (stores API key)<br>
├── requirements.txt      # Project dependencies<br>
└── README.md             # Documentation file<br>

---

## ⚙️ Setup Instructions

1. Clone the Repository
```bash
git clone https://github.com/Musharraf1519/Langchain.git
cd Langchain
```

2. Create and Activate a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Create a .env File
    In the project root, create a file named .env and add your OpenAI API key like this:
    ```ini
    OPENAI_API_KEY=your_openai_api_key_here
    ```

**⚠️ Important: Never commit your .env file to GitHub. It contains sensitive credentials.**

5. Run the Chatbot
    To start the Streamlit app:
```bash
    streamlit run knowledgebot.py
    ```


Then open the displayed local URL (usually http://localhost:8501) in your browser.

💬 Example Interaction
User: Hello!
AI: Hi there! How can I assist you today?
User: Remember my name is Musharraf.
AI: Got it, Musharraf! Nice to meet you.
User: What’s my name?
AI: Your name is Musharraf.

🧰 Troubleshooting

Invalid API Key

Ensure .env file exists in the same directory as knowledgebot.py

Verify the key is active on OpenAI’s API Dashboard

Module Not Found

Run:

pip install -U langchain langchain-openai streamlit python-dotenv

📘 References

LangChain Docs

Streamlit Docs

OpenAI API Docs

🧑‍💻 Author

Musharraf Khan
Building AI-powered apps with Python, LangChain & Streamlit
🔗 GitHub

## **⭐ If you found this project useful, consider giving it a star!**
