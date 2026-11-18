from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from tools import TOOLS

MODEL_NAME = "llama3.2"

SYSTEM_PROMPT = (
    "You are a helpful local assistant running on the user's computer. "
    "You have tools for files, system info, math, and the current date/time. "
    "Rules:\n"
    "1. Call ONE tool at a time. Wait for its result before deciding the next step.\n"
    "2. Never guess a value that a previous tool should provide. "
    "Use the exact result the tool returned.\n"
    "3. Only call a tool when the user's request needs it. "
    "For greetings and personal information, reply directly.\n"
    "4. When all steps are done, summarize what happened accurately."
)

def build_agent():
    llm = ChatOllama(model=MODEL_NAME, temperature=0)
    memory = MemorySaver()
    return create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )