from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    user_request: str
    messages: list
    tool_results: Annotated[list, operator.add]
    iteration: int
    is_valid: bool 
    status: str
    final_answer: str

# Create nodes
def validate_request(state: AgentState) -> dict:
    request = state['user_request']

    if not request or not request.strip():
        return {
            "is_valid": False,
            "status": "invalid_request"
        }

    return {
        "is_valid": True,
        "status": "running"
    }
