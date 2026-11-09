# FRIDAY_LangGraph\src\graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from src.state import AgentState
from src.nodes import call_model, handle_iteration_limit
from src.tools import tools
from src.config import MAX_ITERATIONS

# Conditional routing method
def route_after_model(state):
    last_message = state["messages"][-1]

    # Model wants to call one or more tools
    if last_message.tool_calls:
        # Do not execute another round of tools
        # if the model call budget has been exhausted
        if state["iteration"] >= MAX_ITERATIONS:
            return "limit"
        
        return "tools"

    # No tool calls indicates model has produced the final response
    return "end"

builder = StateGraph(AgentState)

# Register node
builder.add_node("agent", call_model)

builder.add_node(
    "tools",
    ToolNode(
        tools,
        handle_tool_errors=True
    )
)

builder.add_node(
    "iteration_limit",
    handle_iteration_limit
)

# Define the graph flow
builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    route_after_model,
    {
        "tools": "tools",
        "limit": "iteration_limit",
        "end": END
    }
)

builder.add_edge("tools", "agent")

builder.add_edge("iteration_limit", END)

# Compile
agent_graph = builder.compile()