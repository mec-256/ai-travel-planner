import os
import logging
from datetime import datetime
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Support both old serpapi (GoogleSearch) and new serpapi (Client)
try:
    from serpapi import GoogleSearch
    SERPAPI_MODE = "old"
except ImportError:
    import serpapi
    SERPAPI_MODE = "new"


AIRPORT_MAP = {
    "NYC": "JFK",
    "NEW YORK": "JFK",
    "LONDON": "LHR",
    "PARIS": "CDG",
    "DUBAI": "DXB",
    "HYDERABAD": "HYD",
    "MUMBAI": "BOM",
    "DELHI": "DEL",
    "BANGALORE": "BLR",
    "CHENNAI": "MAA",
}


@tool
def search_flights(origin: str, destination: str, departure_date: str) -> str:
    """
    Searches for live flights between an origin and destination.

    Args:
        origin: Airport code or city (e.g. JFK)
        destination: Airport code or city (e.g. LHR)
        departure_date: YYYY-MM-DD

    Returns:
        Flight information from SerpAPI.
    """

    logger.info(
        f"[TOOL CALL] Running search_flights "
        f"with: origin={origin}, destination={destination}, date={departure_date}"
    )

    api_key = os.getenv("SERP_API_KEY")

    if not api_key:
        logger.error("[TOOL ERROR] SERP_API_KEY missing")
        return "Error: SERP_API_KEY not configured."

    # Convert city names to airport codes
    origin = AIRPORT_MAP.get(origin.upper(), origin)
    destination = AIRPORT_MAP.get(destination.upper(), destination)

    # Date validation
    try:
        travel_date = datetime.strptime(
            departure_date,
            "%Y-%m-%d"
        ).date()

        today = datetime.now().date()

        if travel_date < today:
            return (
                f"ERROR: Travel date {departure_date} "
                f"is in the past."
            )

    except ValueError:
        return (
            f"ERROR: Invalid date format "
            f"'{departure_date}'. Use YYYY-MM-DD."
        )

    try:
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": departure_date,
            "currency": "USD",
            "hl": "en",
            "type": "2",
        }

        if SERPAPI_MODE == "old":
            # Set timeout if supported, else rely on requests internally or pass timeout=10
            results = GoogleSearch(
                {**params, "api_key": api_key}
            ).get_dict()
        else:
            # For serpapi client, it might not accept timeout natively, 
            # but we can try to pass it if the API supports it
            client = serpapi.Client(api_key=api_key)
            results = client.search(params)

        if "error" in results:
            logger.warning(f"Flight search returned error: {results['error']}")
            return f"Flight search failed: {results['error']}"

        best_flights = results.get("best_flights", [])

        if not best_flights:
            return (
                f"No flights found from "
                f"{origin} to {destination} "
                f"on {departure_date}."
            )

        output = (
            f"REAL-TIME FLIGHT OPTIONS\n"
            f"Route: {origin} → {destination}\n"
            f"Date: {departure_date}\n\n"
        )

        for idx, flight in enumerate(best_flights[:3], start=1):

            segment = flight.get("flights", [{}])[0]

            airline = segment.get(
                "airline",
                "Unknown Airline"
            )

            dep_time = (
                segment.get(
                    "departure_airport",
                    {}
                ).get("time", "?")
            )

            arr_time = (
                segment.get(
                    "arrival_airport",
                    {}
                ).get("time", "?")
            )

            price = flight.get("price", "N/A")

            output += (
                f"{idx}. {airline}\n"
                f"   Price: ${price}\n"
                f"   Departure: {dep_time}\n"
                f"   Arrival: {arr_time}\n\n"
            )

        return output

    except Exception as e:
        logger.error(f"Error fetching flight data: {str(e)[:200]}", exc_info=True)
        return f"Error fetching flight data: {str(e)[:200]}"