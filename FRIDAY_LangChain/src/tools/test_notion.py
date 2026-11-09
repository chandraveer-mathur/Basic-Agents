# src/tools/test_notion.py

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Project root:
# FRIDAY_v0.0.1/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

# Load the .env file from the project root, regardless of
# the directory from which this script is launched.
load_dotenv(ENV_FILE, override=True)

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "").strip()
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "").strip()

BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"
TIMEOUT = 20

session = requests.Session()


def check(condition, success_message, failure_message):
    """Print a consistent test result."""
    if condition:
        print(f"[PASS] {success_message}")
        return True

    print(f"[FAIL] {failure_message}")
    return False


def api_request(method, endpoint, **kwargs):
    """Send a request and display useful, safe diagnostics."""
    url = f"{BASE_URL}{endpoint}"

    try:
        response = session.request(
            method=method,
            url=url,
            headers={
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
            timeout=TIMEOUT,
            **kwargs,
        )
    except requests.exceptions.Timeout:
        print("[FAIL] Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        print("[FAIL] Could not connect to Notion. Check your internet.")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"[FAIL] Request error: {exc}")
        return None

    if not response.ok:
        try:
            details = response.json()
            code = details.get("code", "unknown")
            message = details.get("message", response.text[:300])
        except ValueError:
            code = "unknown"
            message = response.text[:300]

        print(
            f"[FAIL] {method} {endpoint} returned "
            f"HTTP {response.status_code}"
        )
        print(f"       API code: {code}")
        print(f"       Message: {message}")
        print(f"       Request ID: {response.headers.get('x-request-id', 'not provided')}")

        if response.status_code == 401:
            print("       Check that NOTION_TOKEN is the actual current")
            print("       access token, not a placeholder or integration ID.")
        elif response.status_code == 403:
            print("       Check integration capabilities and page access.")
        elif response.status_code == 404:
            print("       Check the page ID and whether the integration")
            print("       has access to that page.")

        return None

    try:
        return response.json()
    except ValueError:
        print("[FAIL] Notion returned a non-JSON success response.")
        return None


def main():
    print("=" * 60)
    print("FRIDAY - Notion API diagnostic")
    print("=" * 60)

    # TEST 1: Configuration
    print("\n1. Configuration")

    check(
        ENV_FILE.is_file(),
        f".env file found: {ENV_FILE}",
        f".env file not found: {ENV_FILE}",
    )

    check(
        BASE_URL == "https://api.notion.com/v1",
        f"Base URL: {BASE_URL}",
        "Unexpected base URL.",
    )

    check(
        bool(NOTION_VERSION),
        f"Notion API version configured: {NOTION_VERSION}",
        "Notion API version is missing.",
    )

    if not NOTION_TOKEN:
        print("[FAIL] NOTION_TOKEN is missing or empty.")
        print("       Add NOTION_TOKEN=your_actual_token to .env")
        return

    if any(
        marker in NOTION_TOKEN.lower()
        for marker in ("your_actual_token", "paste_token", "placeholder")
    ):
        print("[FAIL] NOTION_TOKEN appears to be a placeholder.")
        return

    print(f"[PASS] Token loaded (length: {len(NOTION_TOKEN)} characters).")
    print("       Token value hidden for security.")

    # TEST 2: Authentication
    print("\n2. Authentication - GET /users/me")

    user = api_request("GET", "/users/me")

    if user is None:
        print("\nStopping: authentication/API test failed.")
        print("Fix this failure before testing search or page creation.")
        return

    bot = user.get("bot", {})
    owner = bot.get("owner", {}) if isinstance(bot, dict) else {}

    print(f"[PASS] Notion accepted the token.")
    print(f"       Connection name: {bot.get('name', 'not provided')}")
    print(f"       Owner type: {owner.get('type', 'not provided')}")

    # TEST 3: Search
    print("\n3. Page search - POST /search")

    query = os.getenv("NOTION_TEST_QUERY", "Hello").strip() or "Hello"

    search_data = api_request(
        "POST",
        "/search",
        json={
            "query": query,
            "filter": {
                "property": "object",
                "value": "page",
            },
            "page_size": 5,
        },
    )

    if search_data is not None:
        pages = search_data.get("results", [])
        print(f"[PASS] Search request succeeded for: {query!r}")
        print(f"       Matching accessible pages: {len(pages)}")

        for page in pages:
            title = "Untitled"
            for prop in page.get("properties", {}).values():
                if prop.get("type") == "title":
                    title = "".join(
                        part.get("plain_text", "")
                        for part in prop.get("title", [])
                    )
                    break

            print(f"       - {title}")
            print(f"         ID: {page.get('id', 'unknown')}")

        if not pages:
            print("       No matching pages; this is not an authentication error.")

    # TEST 4: Parent page access
    print("\n4. Parent page configuration and access")

    if not PARENT_PAGE_ID:
        print("[SKIP] NOTION_PARENT_PAGE_ID is not configured.")
        print("       Add a page ID to .env to test page access and creation.")
    else:
        parent = api_request("GET", f"/pages/{PARENT_PAGE_ID}")

        if parent is not None:
            print("[PASS] Parent page is accessible.")
            print(f"       Page ID: {parent.get('id', 'unknown')}")
            print(f"       URL: {parent.get('url', 'not provided')}")

    # TEST 5: Optional write test
    print("\n5. Optional page-creation test")

    create_enabled = (
        os.getenv("NOTION_TEST_CREATE_PAGE", "").strip().lower()
        == "true"
    )

    if not create_enabled:
        print("[SKIP] No page will be created by default.")
        print("       To enable, set NOTION_TEST_CREATE_PAGE=true in .env")
        return

    if not PARENT_PAGE_ID:
        print("[SKIP] Cannot create a page without a parent page ID.")
        return

    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    test_title = f"FRIDAY API Test - {timestamp}"

    payload = {
        "parent": {"page_id": PARENT_PAGE_ID},
        "properties": {
            "title": {
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": test_title},
                    }
                ],
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "FRIDAY Notion API test succeeded."
                            },
                        }
                    ]
                },
            }
        ],
    }

    created = api_request("POST", "/pages", json=payload)

    if created is not None:
        print("[PASS] Test page created.")
        print(f"       Title: {test_title}")
        print(f"       URL: {created.get('url', 'not provided')}")
        print(f"       ID: {created.get('id', 'not provided')}")
        print("       This created a real page in your workspace.")

    print("\nDiagnostic complete.")


if __name__ == "__main__":
    main()
