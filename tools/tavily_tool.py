import os
import logging
from langchain_core.tools import tool
from tavily import TavilyClient

logger = logging.getLogger(__name__)


@tool
def tavily_search(query: str) -> str:
    """
    Search the web for hotels, attractions, restaurants, transportation,
    and travel-related information.

    Returns structured search results for the LLM.
    """

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.error("[TOOL ERROR] TAVILY_API_KEY missing")
        return "Error: TAVILY_API_KEY not configured. Cannot perform search."

    try:
        client = TavilyClient(api_key=api_key)

        response = client.search(
            query=query,
            max_results=3,
            search_depth="advanced",
            include_answer=True,
            timeout=10
        )
        results = response.get("results", [])

        if not results:
            return "No travel information found."

        output = f"SEARCH RESULTS FOR: {query}\n\n"

        for idx, result in enumerate(results[:5], start=1):

            title = result.get("title", "Unknown")
            url = result.get("url", "")
            content = result.get("content", "")

            # Keep content reasonably sized
            content = content[:300]

            output += (
                f"{idx}. {title}\n"
                f"URL: {url}\n"
                f"INFO: {content}\n\n"
            )

        return output

    except Exception as e:
        logger.error(f"Error executing tavily_search: {e}", exc_info=True)
        return f"Error executing search: {str(e)}"