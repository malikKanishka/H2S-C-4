def test_login_success(client):
    # Tests rely on the db being seeded with 'fan_demo' / 'fanpass123'
    response = client.post('/api/auth/login', json={
        "username": "fan_demo",
        "password": "fanpass123"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["role"] == "fan"

def test_login_validation_error(client):
    response = client.post('/api/auth/login', json={
        "username": "fan_demo"
        # missing password
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "validation_failed"

def test_login_invalid_credentials(client):
    response = client.post('/api/auth/login', json={
        "username": "fan_demo",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.get_json()["error"] == "invalid_credentials"
