from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from config import OLLAMA_MODEL
from tools import ALL_TOOLS

SYSTEM_PROMPT = """
You are FRIDAY, a helpful personal AI assistant.

Your responsibilities:
- Understand the user's request and respond clearly.
- Use available tools when they are needed for accurate information.
- Use get_weather for current weather questions.
- Use get_current_time for current date and time questions.
- Ask a clarifying question if required information is missing.
- Never invent tool results or claim an action succeeded if it failed.
- If a tool returns an error, explain the problem honestly.
- For general questions, answer directly without unnecessary tool calls.
- Do not claim you can access calendars, email, files, or other services
  unless a suitable tool is actually available.
"""

# Connect with LLM 
def create_friday_agent():
    model = ChatOllama(
        model="qwen2.5:3b",
        temperature=0
    )

    agent = create_agent(
        model=model,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        name="friday"
    )

    return agent