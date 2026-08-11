import pytest
from backend.app import create_app

@pytest.fixture
def client():
    app = create_app("dev")
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "ok"}

def test_add_todo(client):
    response = client.post('/api/todos', json={"title": "Buy groceries"})
    assert response.status_code in [200, 201]