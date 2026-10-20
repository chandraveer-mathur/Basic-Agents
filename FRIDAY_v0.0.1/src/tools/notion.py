# FRIDAY_v0.0.1\src\tools\notion.py

import requests

from src.config import (NOTION_TOKEN, NOTION_PARENT_PAGE_ID)

from langchain.tools import tool

NOTION_VERSION = "2026-03-11"
BASE_URL = "https://api.notion.com/v1"

def get_headers():
    """Build the headers required by the NOTION API"""

    if not NOTION_TOKEN:
        raise RuntimeError("NOTION TOKEN is not present in .env")

    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }

def notion_request(method, endpoint, **kwargs):
    """Send a request and handle NOTION API errors"""
    response = requests.request(
        method, 
        f"{BASE_URL}{endpoint}",
        headers=get_headers(),
        timeout=20,
        **kwargs
    )

    if not response.ok:
        raise RuntimeError(
            f"Notion API error ({response.status_code}): "
            f"{response.text[:500]}"
        )
    return response.json()

def extract_page_title(page):
    """Extract a page title from its properties."""
    properties = page.get("properties", {})

    for prop in properties.values():
        if prop.get("type") == "title":
            return "".join(
                item.get("plain_text", "")
                for item in prop.get("title", [])
            )

    return "Untitled"


@tool
def search_notion_pages(query: str) -> str:
    """Search accessible Notion pages by title.
    Use when the user wants to find a page in their Notion workspace.
    """
    query = query.strip()
    if not query:
        return "Please provide a search term."

    data = notion_request(
        "POST",
        "/search",
        json={
            "query": query,
            "filter": {
                "property": "object",
                "value": "page",
            },
            "page_size": 10,
        },
    )

    pages = data.get("results", [])

    if not pages:
        return f"No Notion pages found for '{query}'."

    results = []
    for page in pages:
        results.append(
            f"Title: {extract_page_title(page)}\n"
            f"Page ID: {page['id']}\n"
            f"URL: {page.get('url', '')}"
        )

    return "\n\n".join(results)


@tool
def read_notion_page(page_id: str) -> str:
    """Read the text blocks from a Notion page using its page ID.
    Use after finding a page or when the user provides a page ID.
    """
    page_id = page_id.strip()
    if not page_id:
        return "Please provide a Notion page ID."

    data = notion_request(
        "GET",
        f"/blocks/{page_id}/children",
        params={"page_size": 100},
    )

    lines = []

    for block in data.get("results", []):
        block_type = block.get("type")
        content = block.get(block_type, {})
        rich_text = content.get("rich_text", [])

        text = "".join(
            item.get("plain_text", "")
            for item in rich_text
        )

        if text:
            lines.append(text)

    if data.get("has_more"):
        lines.append(
            "[More content exists; pagination is not yet implemented.]"
        )

    return "\n".join(lines) if lines else "No readable text blocks found."


@tool
def create_notion_page(title: str, content: str) -> str:
    """Create a new Notion page with a title and plain-text content.
    Use when the user explicitly asks to save or create a page in Notion.
    """

    print(f"[DEBUG] Title received: {title!r}")
    print(f"[DEBUG] Content length: {len(content)} characters")
    print(f"[DEBUG] Content received:\n{content}")
    
    title = title.strip()

    if not title:
        return "A page title is required."

    if not NOTION_PARENT_PAGE_ID:
        return "NOTION_PARENT_PAGE_ID is missing from .env."

    if len(title) > 2000:
        return "The title is too long (maximum 2000 characters)."

    # Notion limits each rich-text text.content value to 2000 characters.
    chunks = [
        content[i:i + 2000]
        for i in range(0, len(content), 2000)
    ]

    children = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            },
        }
        for chunk in chunks[:100]
        if chunk
    ]

    payload = {
        "parent": {"page_id": NOTION_PARENT_PAGE_ID},
        "properties": {
            "title": {
                "type": "title",
                "title": [
                    {"type": "text", "text": {"content": title}}
                ],
            }
        },
        "children": children,
    }

    page = notion_request("POST", "/pages", json=payload)

    return (
        f"Page created successfully.\n"
        f"Title: {title}\n"
        f"URL: {page.get('url', '')}\n"
        f"Page ID: {page.get('id', '')}"
    )


NOTION_TOOLS = [
    search_notion_pages,
    read_notion_page,
    create_notion_page,
]