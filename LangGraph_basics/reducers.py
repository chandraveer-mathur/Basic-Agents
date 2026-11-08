import operator
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

class ResearchState(TypedDict):
    question: str
    search_results: Annotated[list[str], operator.add]

def search_source_one(state: ResearchState) -> dict:
    return {
        "search_results": ["Result from search one"]
    }

def search_source_two(state: ResearchState) -> dict:
    return {
        "search_results": ["Result from search two"]
    }

def search_source_three(state: ResearchState) -> dict:
    return {
        "search_results": ["Result from seach three"]
    }

# Build graph
builder = StateGraph(ResearchState)

# Add nodes
builder.add_node("node1", search_source_one)
builder.add_node("node2", search_source_two)
builder.add_node("node3", search_source_three)

# Add edges
builder.add_edge(START, "node1")
builder.add_edge("node1", "node2")
builder.add_edge("node2", "node3")
builder.add_edge("node3", END)

workflow = builder.compile()

result = workflow.invoke({
    "question": "What is LangGraph",
    "search_results": []
})

print(result)