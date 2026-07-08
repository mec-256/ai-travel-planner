import os
import pytest
from langchain_core.messages import HumanMessage
from main import app

def test_agent_compilation():
    """Verify that the LangGraph agent compiles and the checkpointer is attached."""
    assert app is not None
    assert type(app).__name__ == "CompiledStateGraph"
    
    # We expect the checkpointer to be PostgresSaver if the URL is set
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        assert type(app.checkpointer).__name__ == "PostgresSaver"

def test_environment_variables():
    """Verify critical environment variables are available for testing."""
    assert os.getenv("GROQ_API_KEY"), "GROQ_API_KEY is missing"
    assert os.getenv("TAVILY_API_KEY"), "TAVILY_API_KEY is missing"
    assert os.getenv("SERP_API_KEY"), "SERP_API_KEY is missing"
