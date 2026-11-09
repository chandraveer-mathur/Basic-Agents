# FRIDAY_v0.0.1\src\agent.py

from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from src.config import OLLAMA_MODEL
from src.tools import ALL_TOOLS
from src.prompt import SYSTEM_PROMPT

# Connect with LLM 
def create_friday_agent():
    model = ChatOllama(
        model="qwen2.5:3b",
        temperature=0,
    )

    agent = create_agent(
        model=model,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        name="friday"
    )

    return agent