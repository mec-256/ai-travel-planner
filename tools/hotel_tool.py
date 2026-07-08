# tools/hotel_tool.py

import os
import logging
from langchain_core.tools import tool
from tavily import TavilyClient

logger = logging.getLogger(__name__)


@tool
def search_hotels(city: str) -> str:
    """
    Search for hotels in a city including prices, ratings and locations.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        logger.error("[TOOL ERROR] TAVILY_API_KEY not configured.")
        return "ERROR: TAVILY_API_KEY not configured."

    # Using the client with a timeout, though tavily-python timeout support may vary.
    # We pass it just in case, or handle it via a wrapper if needed.
    client = TavilyClient(api_key=api_key)

    query = f"""
    best hotels in {city}
    hotel name
    nightly room rate
    hotel rating
    address
    """

    logger.info(f"[TOOL CALL] Running search_hotels for: {city}")
    try:

        response = client.search(
            query=query,
            max_results=5,
            search_depth="advanced",
            include_images=True,
            timeout=10
        )

        results = response.get("results", [])
        images = response.get("images", [])

        if not results:
            return f"No hotels found for {city}"

        output = "HOTEL SEARCH RESULTS\n\n"

        for idx, item in enumerate(results[:5], start=1):
            img_str = f"Image: {images[idx-1]}\n" if (idx-1) < len(images) else ""
            output += (
                f"{idx}. {item.get('title','Unknown')}\n"
                f"URL: {item.get('url', 'N/A')}\n"
                f"{img_str}"
                f"{item.get('content','')[:250]}\n\n"
            )

        return output

    except Exception as e:
        logger.error(f"Error fetching hotel data: {e}", exc_info=True)
        return f"Error fetching hotel data: {e}"