from .weather import get_weather
from .time import get_current_date_time
from .notion import NOTION_TOOLS

ALL_TOOLS = [
    get_weather,
    get_current_date_time,
    *NOTION_TOOLS
]