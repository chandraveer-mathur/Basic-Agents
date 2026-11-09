# FRIDAY_LangGraph\src\nodes.py
from langchain_core.messages import SystemMessage, AIMessage

from src.config import model, MAX_ITERATIONS
from src.tools import tools

model_with_tools = model.bind_tools(tools)

SYSTEM_PROMPT = """
You are a helpful local AI research assistant.

You can answer general questions using your own knowledge.

You have access to a web search tool.

Use web search when:
- The user asks for current or recent information.
- The answer requires information you cannot reliably know.
- The user explicitly asks you to search the web.
- You need external evidence to support an answer.

When using search:
- Search with a clear and specific query.
- Read the returned results carefully.
- Do not invent facts, URLs, or sources.
- Distinguish verified information from uncertainty.
- Cite useful source URLs in your final answer.

If search results are insufficient, say so.
Do not repeatedly search with the same query without a good reason.

Keep answers clear, useful, and direct.
"""

def call_model(state): 
    messages = state["messages"]

    response = model_with_tools.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            *messages
        ]
    )

    return {
        "messages": [response],
        "iteration": state.get("iteration", 0) + 1
    }

def handle_iteration_limit(state):
    response = AIMessage(
        content=(
            "I reached the maximum number of reasoning iterations before completing the request Please narrow the question or try again."
        )
    )

    return {
        "messages": [response]
    }