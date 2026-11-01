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

# Build graph
builder = StateGraph(ResearchState)

# Add nodes
builder.add_node("search_source_one", search_source_one)
builder.add_node("search_source_two", search_source_two)

# Add edges
builder.add_edge(START, "search_source_one")
builder.add_edge("search_source_one", "search_source_two")
builder.add_edge("search_source_two", END)

workflow = builder.compile()

result = workflow.invoke({
    "question": "What is LangGraph",
    "search_results": []
})

print(result)