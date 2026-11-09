# FRIDAY_v0.0.1\src\tool_logger.py
from langchain_core.callbacks import BaseCallbackHandler

class ToolLooger(BaseCallbackHandler):
    """Log tool calls and their results."""

    def on_tool_start(
            self,
            serialized,
            input_str,
            *,
            run_id,
            parent_run_id=None,
            **kwargs,
    ):
        tool_name = serialized.get("name", "unknown_tool")

        print(f"\n[TOOL START] {tool_name}")
        print(f"[TOOL INPUT] {input_str}")

    def on_tool_end(
            self,
            output,
            *,
            run_id,
            parent_run_id=None,
            **kwargs,
    ):
        print(f"[TOOL END] Result: {output}")

    def on_tool_error(
            self, 
            error, 
            *, 
            run_id, parent_run_id = None, 
            **kwargs):
        print(f"[TOOL ERROR] {error}")
