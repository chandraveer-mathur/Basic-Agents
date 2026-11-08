# simulate an operation that fails twice and succeeds on the third attempt.

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class RetryState(TypedDict):
    attempts: int
    success: bool
    result: str

# simulates an operation that succeeds on the third attempt.

def perform_operation(state: RetryState) -> dict:
    attempt = state["attempts"] + 1
    print(f"Attempt: {attempt}")
    print(state)
    if attempt >= 3:
        return {
            "attempts": attempt, 
            "success": True, 
            "result": "Operation Successful"}

    return {
        "attempts": attempt, 
        "success": False, 
        "result": "Operation Failes"}

# Define Routing
def route_retry(state: RetryState) -> str:
    if state["success"]: 
        return "done"
    if state["attempts"] >= 3:
        return "failed"
    return "retry"

builder = StateGraph(RetryState)

builder.add_node("perform_operation", perform_operation)

builder.add_edge(START, "perform_operation")

builder.add_conditional_edges(
    "perform_operation",
    route_retry,
    {
       "retry": "perform_operation",
       "done": END,
       "failed": END 
    }
)

workflow = builder.compile()

result = workflow.invoke(
    {
        "attempts": 0,
        "success": False,
        "result": ""
    },
    config={
        "rescursion_limit": 10
    }
)

print(result)