import pytest
from unittest.mock import patch, MagicMock
from tools.hotel_tool import search_hotels
from tools.flight_tool import search_flights

def test_hotel_tool_success():
    """Test that the hotel tool formats output correctly when Tavily returns data."""
    mock_response = {
        "results": [
            {"title": "Mock Hotel 1", "url": "http://mock1.com", "content": "A great mock hotel."},
            {"title": "Mock Hotel 2", "url": "http://mock2.com", "content": "Another mock hotel."}
        ],
        "images": [
            "http://mock1.com/img.jpg",
            "http://mock2.com/img.jpg"
        ]
    }
    
    with patch("tools.hotel_tool.TavilyClient") as MockClient:
        # Configure the mock instance
        mock_instance = MockClient.return_value
        mock_instance.search.return_value = mock_response
        
        # Execute the tool
        result = search_hotels.invoke({"city": "Paris"})
        
        # Verify the mock was called
        mock_instance.search.assert_called_once()
        
        # Verify the formatting
        assert "HOTEL SEARCH RESULTS" in result
        assert "1. Mock Hotel 1" in result
        assert "Image: http://mock1.com/img.jpg" in result

def test_flight_tool_success():
    """Test that the flight tool formats output correctly when SerpAPI returns data."""
    mock_response = {
        "best_flights": [
            {
                "flights": [
                    {
                        "flight_number": "MOCK123",
                        "airline": "MockAir",
                        "departure_airport": {"name": "JFK", "time": "2026-08-10 10:00"},
                        "arrival_airport": {"name": "LHR", "time": "2026-08-10 22:00"},
                        "duration": 420
                    }
                ],
                "price": 500
            }
        ]
    }
    
    with patch("tools.flight_tool.GoogleSearch") as MockGoogleSearch:
        # Configure the mock instance
        mock_instance = MockGoogleSearch.return_value
        mock_instance.get_dict.return_value = mock_response
        
        # Set SERPAPI_MODE to 'old' to ensure we hit GoogleSearch
        with patch("tools.flight_tool.SERPAPI_MODE", "old"):
            result = search_flights.invoke({"origin": "NYC", "destination": "London", "departure_date": "2026-08-10"})
            
            # Verify the formatting
            assert "REAL-TIME FLIGHT OPTIONS" in result
            assert "MockAir" in result
            assert "$500" in result
