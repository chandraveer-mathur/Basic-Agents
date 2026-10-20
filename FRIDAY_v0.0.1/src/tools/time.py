from langchain.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo

@tool
def get_current_time(timezone: str = "Asia/Kolkata") -> str:
    """Get the current date and time in India Standard Time (IST).
    Use this whenever the user asks for the current time in India,
    including Kolkata, Delhi, or the current time in India generally.
    """

    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return now.strftime("%A, %d %B %Y, %I:%M:%S %p IST")
