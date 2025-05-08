# List of available tools for the agent
# You can register tools using register_tool().

from typing import List, Dict, Any

registered_tools: List[Any] = []

def register_tool(tool: Any):
    """Register a tool (dict or FunctionTool)."""
    registered_tools.append(tool)

# Example: Registering a simple tool (dict)
register_tool({
    "name": "image_classifier",
    "description": "Classifies images as REAL or AI-generated (FAKE)."
})

register_tool({
    "name": "text_classifier",
    "description": "Classifies text as REAL or FAKE using linguistic and factual analysis."
})

# Example: Registering a FunctionTool (uncomment and adapt as needed)
# from agents import FunctionTool
# def dummy_func(ctx, args):
#     return "result"
# register_tool(FunctionTool(
#     name="process_user",
#     description="Processes extracted user data",
#     params_json_schema={"type": "object"},
#     on_invoke_tool=dummy_func,
# ))

def get_tool_descriptions() -> List[Dict[str, str]]:
    """Return a list of dicts with name and description for the prompt."""
    descs = []
    for tool in registered_tools:
        # If it's a FunctionTool, get name/description attributes
        name = getattr(tool, 'name', None) or tool.get('name')
        desc = getattr(tool, 'description', None) or tool.get('description')
        if name and desc:
            descs.append({"name": name, "description": desc})
    return descs 