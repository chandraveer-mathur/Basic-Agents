from .weather import get_weather
from .time import get_current_date_time
from .notion import NOTION_TOOLS
from .web_search import web_search

ALL_TOOLS = [
    get_weather,
    get_current_date_time,
    *NOTION_TOOLS,
    web_search
]