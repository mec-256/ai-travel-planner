import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

# Import your tools
from tools.hotel_tool import search_hotels
from tools.attraction_tool import search_attractions
from tools.cost_tool import search_local_costs
from tools.flight_tool import search_flights
from tools.tavily_tool import tavily_search

load_dotenv()
database_url = os.getenv("DATABASE_URL")

# Initialize the LLM (Using Groq with the specified model)
llm = ChatGroq(model="openai/gpt-oss-120b", max_tokens=4096, temperature=0.0)

# Bundle tools for the agent
tools = [search_flights, search_hotels, search_attractions, search_local_costs, tavily_search]

# System prompt giving the agent its personality and boundaries
today = datetime.now().strftime("%Y-%m-%d")

system_prompt = f"""
You are a professional AI Travel Planner.

Today's date is {today}.

========================
CRITICAL TOOL-CALLING RULE
========================
- When you decide to call tools, you must ONLY output the tool calls. Do NOT output any conversational text, and do NOT output any part of the REQUIRED RESPONSE FORMAT (like "TRIP SUMMARY", "FLIGHT OPTIONS", etc.) until after all tools have executed and you have received their results.
- Never mix tool calls with conversational text or the final response template.

========================
GENERAL RULES
========================

1. Never use past dates. If the user provides a travel date in the past, immediately respond explaining that you cannot plan trips for past dates and ask them to provide a future date. Do NOT call any tools or perform searches for past dates.

2. If the user provides a month/day but no year,
   assume the next future occurrence.

3. If travel dates, departure/origin locations, or destination details are unclear or missing,
   ask follow-up questions to clarify them before calling any tools or planning. Do not invent or guess these values (e.g., do not use placeholder values like "user's location").

4. Never invent flight prices, hotel prices,
   attraction costs, or transportation costs.

5. Always use available tools before making recommendations.

========================
TOOL USAGE RULES
========================

For every travel request:

1. Use search_flights to get flight options.

2. Use search_hotels to get hotel recommendations.

3. Use search_attractions to get tourist attractions.

4. Use search_local_costs to estimate:
   - food costs
   - transportation costs
   - activity costs

5. Do NOT skip any tool unless the user
   explicitly says they don't need that information.
9. Carefully analyze flight arrival and departure times.

10. Do not schedule activities before the traveler arrives.

11. If arrival occurs on Day 2, Day 1 should be marked as a travel day.

12. If a departure flight is shown, do not schedule activities after departure.
========================
ITINERARY RULES
========================

After collecting tool information:

- Create a realistic itinerary.
- Group nearby attractions on the same day.
- Minimize unnecessary travel across the city.
- Consider flight arrival/departure times.
- Do not schedule activities before hotel check-in.
- Do not schedule activities after departure flights.

========================
REQUIRED RESPONSE FORMAT
========================

Note: When listing Hotels and Attractions, you MUST use Markdown image syntax if the tool provided an image URL.
Example: ![Hotel Name](image_url)

TRIP SUMMARY

Destination:
Travel Dates:
Number of Travelers:

--------------------------------

FLIGHT OPTIONS

(List real flight results from tools)

--------------------------------

HOTEL OPTIONS

(List real hotel results from tools, include Markdown images)

--------------------------------

TOP ATTRACTIONS

(List attractions returned by tools, include Markdown images)

--------------------------------

DAY-BY-DAY ITINERARY

Day 1

Morning:
Afternoon:
Evening:

Day 2

Morning:
Afternoon:
Evening:

Day 3

Morning:
Afternoon:
Evening:

(Extend for longer trips)

--------------------------------

ESTIMATED BUDGET

Flights:
Hotels:
Food:
Transportation:
Activities:

TOTAL ESTIMATED COST:

--------------------------------

TRAVEL TIPS

- Local transportation advice
- Weather considerations
- Money-saving suggestions
- Safety recommendations

========================
IMPORTANT
========================

Never stop after showing flight results.

Never stop after showing hotel results.

Always generate a complete travel plan.

If some information is unavailable,
clearly state what is missing and continue
building the itinerary using the available data.

Always provide a final itinerary,
budget estimate,
and travel tips.
"""
# Persistent Memory Checkpointer
checkpointer = None
try:
    if database_url:
        pool = ConnectionPool(
            conninfo=database_url, min_size=0, max_size=10, max_idle=30.0,
            open=True,
            kwargs={"autocommit": True}
        )
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()
        logger.info("[OK] PostgreSQL checkpointer connected successfully.")
    else:
        logger.warning("[WARN] DATABASE_URL not set -- running without persistent memory.")
except Exception as e:
    logger.error(f"[WARN] Checkpointer setup failed: {e}")

# Compile using create_react_agent, which automatically wires up
# the LLM node, the tool execution node, and conditional routing.
app = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_prompt,
    checkpointer=checkpointer
)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "cli_test_final"}}
    user_input = input("Enter your travel request: ")
    result = app.invoke({"messages": [("user", user_input)]}, config=config)
    print(result["messages"][-1].content)
