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
│
├── knowledgebot.py       # Main chatbot script<br>
├── .env                  # Environment file (stores API key)<br>
├── requirements.txt      # Project dependencies<br>
└── README.md             # Documentation file<br>