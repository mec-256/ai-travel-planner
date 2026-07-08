import os
import pytest

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """
    Automatically mock environment variables for all tests.
    This prevents accidentally hitting real APIs and consuming credits.
    """
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("TAVILY_API_KEY", "test_tavily_key")
    monkeypatch.setenv("SERP_API_KEY", "test_serp_key")
    # Do not set DATABASE_URL so tests run using in-memory state by default,
    # unless a specific test needs to test the PostgresSaver.
    monkeypatch.delenv("DATABASE_URL", raising=False)
