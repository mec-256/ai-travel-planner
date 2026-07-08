# tools/attraction_tool.py

import os
import logging
from langchain_core.tools import tool
from tavily import TavilyClient

logger = logging.getLogger(__name__)


@tool
def search_attractions(city: str) -> str:
    """
    Search for major tourist attractions.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        logger.error("[TOOL ERROR] TAVILY_API_KEY not configured.")
        return "ERROR: TAVILY_API_KEY not configured."

    client = TavilyClient(api_key=api_key)

    logger.info(f"[TOOL CALL] Running search_attractions for: {city}")
    
    query = f"""
    top tourist attractions in {city}
    ticket prices
    opening hours
    """

    try:
        response = client.search(
            query=query,
            max_results=5,
            search_depth="advanced",
            include_images=True
            # Note: timeout is only used if underlying lib supports it
        )

        results = response.get("results", [])
        images = response.get("images", [])

        if not results:
            return f"No attractions found in {city}"

        output = "ATTRACTIONS\n\n"

        for idx, item in enumerate(results[:5], start=1):
            img_str = f"Image: {images[idx-1]}\n" if (idx-1) < len(images) else ""
            output += (
                f"{idx}. {item.get('title','Unknown')}\n"
                f"{img_str}"
                f"{item.get('content','')[:250]}\n\n"
            )

        return output

    except Exception as e:
        logger.error(f"Error fetching attraction data: {e}", exc_info=True)
        return f"Attraction search failed: {str(e)}"