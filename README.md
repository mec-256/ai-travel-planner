<div align="center">
  <h1>🌍 Sealine AI Travel Agent</h1>
  <p>An autonomous, multi-agent travel planning system built with LangGraph and Streamlit.</p>
  
  ![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
  ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
  ![LangChain](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)
  ![Groq](https://img.shields.io/badge/Groq-Fast_AI-f55036?style=flat)
</div>

---

## 📖 Overview
Sealine AI is a production-ready, autonomous travel agent that plans complex, end-to-end itineraries. Instead of simply generating static text like standard LLMs, this system utilizes a **ReAct Agent architecture** via LangGraph to actively browse the internet, fetch live flight prices, search for real-time hotel availability, and calculate estimated costs. 

## ✨ Key Features
- **Autonomous Multi-Agent Workflow:** The agent independently decides which APIs to call based on the user's prompt (e.g., calling the Flight Tool, then the Hotel Tool, then synthesizing the data).
- **Persistent Memory:** Utilizes a PostgreSQL checkpointer to maintain conversational state across sessions.
- **Real-Time Data Integration:** 
  - ✈️ **Flights:** Live flight scraping via SerpAPI / AviationStack.
  - 🏨 **Hotels:** Live accommodation data via Google Search results.
  - 📸 **Attractions:** Real-time web scraping via Tavily with image support.
- **Modern UI/UX:** Built with Streamlit, featuring a glassmorphism design, real-time "Thinking" execution expanders, and session management.

## 📸 Evidences & Screenshots
> **Note to Recruiter/Viewer:** See the system in action below!

*(Replace the links below with your actual screenshots after uploading them)*
- [Insert Screenshot of the Welcome Screen]
- [Insert Screenshot of the Agent's "Thinking" Expander]
- [Insert Screenshot of a final generated itinerary]

## 🏗️ Architecture
The backend is powered by `create_react_agent` from LangGraph. The LLM acts as the central router, accessing a suite of specialized Python tools:
1. `search_flights`: Validates origin/destination airports and fetches actual flight routes.
2. `search_hotels`: Finds live pricing for accommodations in the target city.
3. `search_attractions`: Uses Tavily to scrape the web for top-rated activities and images.
4. `search_local_costs`: Estimates daily budgets for food and transport.

## 🚀 Live Demo
You can try the live application here: **[Insert Streamlit Cloud URL]**

## 💻 Local Setup
To run this project locally on your machine:
```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-travel-planner.git

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API Keys
# Create a .env file in the root directory and add:
GROQ_API_KEY="your_key"
TAVILY_API_KEY="your_key"
SERP_API_KEY="your_key"

# 4. Run the app
streamlit run frontend2.py
```
