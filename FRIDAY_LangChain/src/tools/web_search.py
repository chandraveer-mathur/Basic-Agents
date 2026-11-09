from langchain.tools import tool
from tavily import TavilyClient

from src.config import TAVILY_API_KEY

def get_tavily_client():
    """Create a Tavily client when a search is requested"""
    if not TAVILY_API_KEY:
        raise RuntimeError(
            "TAVILY_API_KEY is missing from .env"
        )

    return TavilyClient(api_key=TAVILY_API_KEY)

@tool
def web_search(query: str) -> str:

    """Search the public internet for factual information and research.

    MANDATORY USE CASES:
    - Historical results that need external verification.
    - Current news, recent events, and latest software releases.
    - Questions requiring sources or facts not reliably known.

    Do not use this tool when a dedicated existing tool is more
    appropriate, such as get_weather for weather.
    """
    query = query.strip()

    if not query:
        return "Please provide a search query"

    try:
        client = get_tavily_client()

        response = client.search(
            query=query,
            search_depth="basic",
            max_results=5,
            include_answer=False,
        )

        results = response.get("results", [])

        if not results:
            return f"No relavant web results found for: {query}"

        formatted_results = []

        for index, result in enumerate(results, start=1):
            title = result.get("title", "Untitled")
            url = result.get("url", "")
            content = result.get("content", "")

            formatted_results.append(
                f"Result {index}\n"
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Content: {content}"
            )
        
        return "\n\n".join(formatted_results)
    
    except Exception as exc:
        return f"Web seach failed: {exc}"
