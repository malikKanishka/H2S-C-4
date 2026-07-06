def test_recommend_transport(client, monkeypatch):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    def mock_generate(*args, **kwargs):
        return "Take the metro to avoid traffic!"
    monkeypatch.setattr("modules.transport.service.generateGroundedReply", mock_generate)
    
    response = client.post('/api/transport/recommend', 
        json={"origin_lat": 34.05, "origin_lng": -118.24, "kickoff_iso": "2026-06-11T12:00:00Z"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "options" in data
    assert "summary" in data
    assert data["summary"] == "Take the metro to avoid traffic!"

def test_recommend_transport_validation_error(client):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/transport/recommend', 
        json={"origin_lat": 34.05}, # Missing fields
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_recommend_transport_auth_error(client):
    login_resp = client.post('/api/auth/login', json={"username": "volunteer_demo", "password": "volpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/transport/recommend', 
        json={"origin_lat": 34.05, "origin_lng": -118.24, "kickoff_iso": "2026-06-11T12:00:00Z"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
