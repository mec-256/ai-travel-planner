import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from main import app

def test_agent_configuration():
    """
    Verify the agent is configured correctly with our tools and prompt.
    """
    assert app is not None
    assert app.name == "LangGraph"
    
    # Verify tools are attached to the agent
    assert hasattr(app, "builder")
    nodes = app.builder.nodes
    
    # create_react_agent creates two nodes: 'agent' and 'tools'
    assert "agent" in nodes
    assert "tools" in nodes
