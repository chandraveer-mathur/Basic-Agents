from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# Define state schema
class WorkflowState(TypedDict):
    request: str
    normalized_request: str
    response: str

# 2 Define the first node
def normalize_request(state: WorkflowState) -> dict:
    normalized = state["request"].strip()

    return {
        "normalized_request": normalized
    }

# 3 Define the second node 
def prepare_respone(state: WorkflowState) -> dict: 
    response = (
        f"you asked {state['normalized_request']}"
    )

    return {
        "response": response
    }

# 4. Build the graph
builder = StateGraph(WorkflowState)

builder.add_node("normalize_request", normalize_request)
builder.add_node("prepare_response", prepare_respone)

builder.add_edge(START, "normalize_request")
builder.add_edge("normalize_request", "prepare_response")
builder.add_edge("prepare_response", END)

# Compile the graph
workflow = builder.compile()

# Execute the graph
result = workflow.invoke(
    {
        "request": "    Explain LangGraph    "
    }
)

print(result)