import logging
# List of available tools for the agent
# You can register tools using register_tool().
from agents import FunctionTool

API_KEY = 'AIzaSyCximcJIGoBex9H43hNoz7WLYnPutrLCZA'

from typing import List, Dict, Any

logger = logging.getLogger("uvicorn.error")

registered_tools: List[Any] = []

def register_tool(tool: Any):
    """Register a tool (dict or FunctionTool)."""
    logger.info(f"Registering tool: {getattr(tool, 'name', tool.get('name', 'unknown'))}")
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

DATA = ''
CLAIMS = ''

def new_fact_check(query, language_code='en-US'):
    endpoint = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'
    params = {
        'key': API_KEY,
        'query': query,
        'languageCode': language_code
    }

    response = requests.get(endpoint, params=params)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return

    DATA = response.json()
    CLAIMS = DATA.get('claims', [])


def get_counts(text):
    new_fact_check(text)
    verdict_counter = {}

    for claim in CLAIMS:
        for review in claim.get('claimReview', []):
            # Use alternateName or textualRating
            verdict = review.get("textualRating") or review.get("reviewRating", {}).get("alternateName", "Unknown")
            verdict_counter[verdict] += 1

    return verdict_counter


def get_rating_value_histogram(text):
    new_fact_check(text)
    histogram = {}

    for claim in CLAIMS:
        for review in claim.get('claimReview', []):
            rating = review.get('reviewRating', {}).get('ratingValue')
            if rating:
                histogram[rating] += 1
            else:
                histogram['Unknown'] += 1

    return histogram


def get_sources(text):
    new_fact_check(text)
    sources = set()  # use a set to avoid duplicates

    for claim in CLAIMS:
        for review in claim.get('claimReview', []):
            source = review.get('publisher', {}).get('name')
            if source:
                sources.add(source)

    return list(sources)


def get_urls(text):
    new_fact_check(text)
    urls = []

    for claim in CLAIMS:
        for review in claim.get('claimReview', []):
            url = review.get('url')
            if url:
                urls.append(url)

    return urls

register_tool(FunctionTool(
    name="counts",
    description="Processes claim and get textual review",
    params_json_schema={"type": "object"},
    on_invoke_tool=get_counts,
))

register_tool(FunctionTool(
    name="rating",
    description="Processes claim and get review on the liability of the claim",
    params_json_schema={"type": "object"},
    on_invoke_tool=get_rating_value_histogram,
))

register_tool(FunctionTool(
    name="sources",
    description="Processes claim and get the resources",
    params_json_schema={"type": "object"},
    on_invoke_tool=get_sources,
))

register_tool(FunctionTool(
    name="urls",
    description="Processes claim and get the url of the resources articles",
    params_json_schema={"type": "object"},
    on_invoke_tool=get_urls,
))

def get_tool_descriptions() -> List[Dict[str, str]]:
    """Return a list of dicts with name and description for the prompt."""
    logger.info("Getting tool descriptions for prompt.")
    descs = []
    for tool in registered_tools:
        # If it's a FunctionTool, get name/description attributes
        name = getattr(tool, 'name', None) or tool.get('name')
        desc = getattr(tool, 'description', None) or tool.get('description')
        if name and desc:
            descs.append({"name": name, "description": desc})
    return descs 