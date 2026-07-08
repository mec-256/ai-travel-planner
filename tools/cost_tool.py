# tools/cost_tool.py

import os
import logging
from langchain_core.tools import tool
from tavily import TavilyClient

logger = logging.getLogger(__name__)


@tool
def search_local_costs(city: str) -> str:
    """
    Search for average food, transport and tourist costs.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        logger.error("[TOOL ERROR] TAVILY_API_KEY not configured.")
        return "ERROR: TAVILY_API_KEY not configured."

    client = TavilyClient(api_key=api_key)

    query = f"""
    average tourist daily budget in {city}
    food cost
    public transport cost
    attraction ticket prices
    """
    logger.info(f"[TOOL CALL] Running search_local_costs for: {city}")

    try:

        response = client.search(
            query=query,
            max_results=5,
            search_depth="advanced",
            timeout=10
        )

        results = response.get("results", [])

        if not results:
            return f"No cost information found for {city}"

        output = "LOCAL COST INFORMATION\n\n"

        for idx, item in enumerate(results[:5], start=1):

            output += (
                f"{idx}. {item.get('title','Unknown')}\n"
                f"{item.get('content','')[:250]}\n\n"
            )

        return output

    except Exception as e:
        logger.error(f"Error fetching cost data: {e}", exc_info=True)
        return f"Cost search failed: {str(e)}"