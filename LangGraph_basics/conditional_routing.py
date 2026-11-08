from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
class AgentState(TypedDict):
    question: str
    is_valid: bool
    response: str

def validate_question(state: AgentState) -> dict:
    question = state['question'].strip()

    return {
        "is_valid" : bool(question)
    }

def process_question(state: AgentState) -> dict:
    question = state['question']

    return {
        "response": f"Processed {question}"
    }

def reject_question(state: AgentState) -> dict:
    question = state['question']

    return {
        "response" : f"Question rejected, as empty"
    }


def route_question(state: AgentState) -> str:
    if state['is_valid']:
        return "process"

    return "reject"

builder = StateGraph(AgentState)

builder.add_node("validate", validate_question)
builder.add_node("process", process_question)
builder.add_node("reject", reject_question)

builder.add_edge(START, "validate")

builder.add_conditional_edges(
    "validate",
    route_question,
    {
        "process": "process",
        "reject": "reject"
    }
)

builder.add_edge("process", END)
builder.add_edge("reject", END)

workflow = builder.compile()

result = workflow.invoke({
    "question" :  "",
    "is_valid" : "",
    "response": ""
})


print(result)