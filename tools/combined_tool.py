import os
from serpapi import GoogleSearch
from langchain_core.tools import tool
from tavily import TavilyClient

@tool
def search_travel_info(origin: str, destination: str, departure_date: str, destination_city: str) -> str:
    """
    Searches for flights, hotels, and attractions in one call.
    - origin: 3-letter airport code (e.g., 'JFK')
    - destination: 3-letter airport code (e.g., 'LHR')
    - departure_date: date in YYYY-MM-DD format
    - destination_city: city name for hotel/attraction search (e.g., 'London')
    """
    result_parts = []

    # --- FLIGHTS ---
    api_key = os.getenv("SERP_API_KEY")
    if api_key:
        try:
            params = {
                "engine": "google_flights",
                "departure_id": origin,
                "arrival_id": destination,
                "outbound_date": departure_date,
                "type": "2",
                "currency": "USD",
                "hl": "en",
                "api_key": api_key,
            }
            results = GoogleSearch(params).get_dict()
            best_flights = results.get("best_flights", [])
            if best_flights:
                flights_text = "Available flights:\n"
                for f in best_flights[:3]:
                    price = f.get("price", "?")
                    airline = f.get("flights", [{}])[0].get("airline", "?")
                    dep = f.get("flights", [{}])[0].get("departure_airport", {}).get("time", "?")
                    arr = f.get("flights", [{}])[0].get("arrival_airport", {}).get("time", "?")
                    flights_text += f"- {airline}: {dep} -> {arr} | ${price}\n"
                result_parts.append(flights_text)
        except Exception as e:
            result_parts.append(f"Flight search error: {e}")

    # --- HOTELS ---
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            client = TavilyClient(api_key=tavily_key)
            query = f"budget hotels in {destination_city} near city center double room price per night September 2026"
            hotels = client.get_search_context(query=query, max_results=3)
            result_parts.append(f"Hotel options from web search:\n{hotels}")
        except Exception as e:
            result_parts.append(f"Hotel search error: {e}")

    # --- ATTRACTIONS ---
    if tavily_key:
        try:
            client = TavilyClient(api_key=tavily_key)
            query = f"top tourist attractions in {destination_city} admission prices September 2026"
            attractions = client.get_search_context(query=query, max_results=3)
            result_parts.append(f"Attractions from web search:\n{attractions}")
        except Exception as e:
            result_parts.append(f"Attraction search error: {e}")

    return "\n\n".join(result_parts)
