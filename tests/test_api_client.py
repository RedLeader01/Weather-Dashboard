"""
API kliens tesztelése
"""
import pytest
from unittest.mock import Mock, patch
from frontend.api_client import WeatherAPIClient

@pytest.fixture
def mock_api_client():
    """Mock API kliens létrehozása"""
    client = WeatherAPIClient("http://test.api")
    return client

def test_api_client_initialization():
    """API kliens inicializáció teszt"""
    client = WeatherAPIClient("http://localhost:8000")
    assert client.base_url == "http://localhost:8000"
    assert client.session is not None

@patch('requests.Session.get')
def test_fetch_data_success(mock_get):
    """Sikeres API hívás teszt"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response
    
    client = WeatherAPIClient("http://test.api")
    result = client.fetch_data("/test")
    
    assert result == {"data": "test"}
    mock_get.assert_called_once()

@patch('requests.Session.get')
def test_fetch_data_failure(mock_get):
    """Sikertelen API hívás teszt"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_get.return_value = mock_response
    
    client = WeatherAPIClient("http://test.api")
    result = client.fetch_data("/test")
    
    assert result is None