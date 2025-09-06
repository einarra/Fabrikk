import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)

@patch('src.main.supabase')
def test_get_random_quote(mock_supabase, client):
    # Mock the Supabase client's behavior
    mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = {'data': [{'quote': 'This is a test quote'}]}
    
    response = client.get('/quote/random')
    assert response.status_code == 200
    assert response.json() == {'quote': 'This is a test quote'}

@patch('src.main.supabase')
def test_get_random_quote_no_data(mock_supabase, client):
    # Mock the Supabase client to return no data
    mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = {'data': []}
    
    response = client.get('/quote/random')
    assert response.status_code == 200
    assert response.json() == {'message': 'No quotes found.'}