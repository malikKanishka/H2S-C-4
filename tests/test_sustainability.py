def test_log_sustainability(client, monkeypatch):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    def mock_generate(*args, **kwargs):
        return "Great job taking public transit!"
    monkeypatch.setattr("modules.sustainability.service.generateGroundedReply", mock_generate)
    
    response = client.post('/api/sustainability/log', 
        json={"action_type": "public_transit"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "points_total" in data
    assert "tip" in data
    assert data["tip"] == "Great job taking public transit!"

def test_log_sustainability_validation_error(client):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/sustainability/log', 
        json={}, # Missing action_type
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_log_sustainability_auth_error(client):
    login_resp = client.post('/api/auth/login', json={"username": "volunteer_demo", "password": "volpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/sustainability/log', 
        json={"action_type": "public_transit"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
