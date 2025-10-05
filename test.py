from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# Step 1: create memory
memory = ConversationBufferMemory(return_messages=True)

# Step 2: create a prompt that uses memory
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful chatbot."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
]) #multiple message roles (system, human, AI, memory placeholders).

# Step 3: create the LLM
llm = ChatOpenAI(model="gpt-5-nano", temperature=0)

# Step 4: function to chat
def chat(user_input):
    # Load memory history
    history = memory.load_memory_variables({})["history"]
    # Format prompt
    messages = prompt.format_messages(history=history, input=user_input)
    # Get LLM response
    response = llm.invoke(messages)
    # Save turn into memory
    memory.save_context({"input": user_input}, {"output": response.content})
    return response.content

# Try chatting
print(chat("Hello, my name is Khan."))
print(chat("Can you remind me what my name is?"))
