import pytest
from app import app  # ודא שזה שם ה-app אצלך (או מ-app.py/backend)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_add_todo(client):
    response = client.post('/add', json={"title": "Buy groceries"})
    assert response.status_code in [200, 201]