# FRIDAY_v0.0.1\src\tools\notion.py

import requests
import re 

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
    """Find Notion pages by their title or related search terms.

    Use this tool when the user wants to locate a page by its name,
    find a page whose ID is unknown, or discover matching pages before
    reading one.

    Args:
        query: The page title or distinctive words from the title.
            For example, "MAIN THEORY" or "LangChain notes".

    Returns:
        Matching page titles, page IDs, and URLs.
        If a page is found and the user wants its contents, pass the
        selected page ID to get_notion_page_content.
        If several pages match, ask the user to choose.
        If no pages match, report that no matching pages were found.
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
    """Read the text content of a Notion page using its page ID.

    Use this tool when the page ID is already known, supplied by the
    user, or returned by search_notion_pages.

    Do not use a page title as the page_id argument. If only the title
    is known, search for the page first.

    Args:
        page_id: The Notion page UUID, with or without hyphens.

    Returns:
        The readable text from the page's direct child blocks.
        The result may be incomplete if the page has more than the
        supported number of blocks or contains nested content.
    """
    # Keep your existing implementation below.
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

    Use only when the user explicitly asks to create or save a page.
    Do not use this tool to search for or update an existing page.

    Args:
        title: The title of the new page.
        content: The text content to add to the page.

    Returns:
        A success message with the created page's title, URL, and ID,
        or an error explaining why creation failed.
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




@tool
def get_notion_page_content(
    page_title: str = "",
    page_id: str = "",
) -> str:
    """Retrieve the text content of a Notion page by title or page ID.

    Use when the user wants to read, summarize, explain, or analyze
    the contents of a Notion page.

    Provide either page_title or page_id:
    - If page_id is supplied, retrieve that page directly.
    - If page_title is supplied, search Notion and resolve the title
      to a page ID before retrieving its content.

    Do not ask the user for a page ID when a title can be searched.

    If multiple pages have the same exact title, return their titles
    and IDs so the user can select the intended page.
    If no exact title match exists, return the available search
    candidates rather than silently selecting an unrelated page.

    Args:
        page_title: The title of the page to retrieve.
        page_id: The Notion page UUID, with or without hyphens.

    Returns:
        The page's readable direct-child text, or a message explaining
        why the page could not be resolved or read.
    """
    page_title = page_title.strip()
    page_id = page_id.strip()

    if bool(page_title) == bool(page_id):
        return "Provide exactly one of page_title or page_id."

    if page_title:
        data = notion_request(
            "POST",
            "/search",
            json={
                "query": page_title,
                "filter": {
                    "property": "object",
                    "value": "page",
                },
                "page_size": 100,
            },
        )

        pages = data.get("results", [])

        exact_matches = [
            page for page in pages
            if extract_page_title(page).casefold()
            == page_title.casefold()
        ]

        if len(exact_matches) > 1:
            candidates = [
                f"Title: {extract_page_title(p)}\nID: {p['id']}"
                for p in exact_matches
            ]
            return (
                "Multiple pages have this exact title. "
                "Ask the user to choose:\n\n"
                + "\n\n".join(candidates)
            )

        if len(exact_matches) == 1:
            page_id = exact_matches[0]["id"]
        else:
            if not pages:
                return f"No Notion pages found for '{page_title}'."

            candidates = [
                f"Title: {extract_page_title(p)}\n"
                f"ID: {p['id']}\n"
                f"URL: {p.get('url', '')}"
                for p in pages
            ]
            return (
                f"No exact title match for '{page_title}'. "
                "Review these search candidates and select the "
                "correct page:\n\n"
                + "\n\n".join(candidates)
            )

    # Accept standard UUIDs and 32-character UUIDs without hyphens.
    normalized_id = page_id.replace("-", "")

    if not re.fullmatch(r"[0-9a-fA-F]{32}", normalized_id):
        return "The supplied page ID is not a valid UUID."

    page_id = (
        f"{normalized_id[:8]}-{normalized_id[8:12]}-"
        f"{normalized_id[12:16]}-{normalized_id[16:20]}-"
        f"{normalized_id[20:]}"
    )

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

    if not lines:
        return (
            "The page was retrieved, but no readable direct-child "
            "text blocks were found."
        )

    return "\n".join(lines)


NOTION_TOOLS = [
    search_notion_pages,
    read_notion_page,
    create_notion_page,
    get_notion_page_content,
]