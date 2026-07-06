def test_get_zones(client):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.get('/api/crowd/zones', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "zones" in response.get_json()

def test_get_recommendation(client, monkeypatch):
    login_resp = client.post('/api/auth/login', json={"username": "volunteer_demo", "password": "volpass123"})
    token = login_resp.get_json()["access_token"]
    
    def mock_generate(*args, **kwargs):
        return "Divert to Zone B"
    monkeypatch.setattr("modules.crowd.service.generateGroundedReply", mock_generate)
    
    response = client.get('/api/crowd/recommendation/zone-a', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "recommendation" in response.get_json()
    assert response.get_json()["recommendation"] == "Divert to Zone B"

def test_get_recommendation_fan_forbidden(client):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.get('/api/crowd/recommendation/zone-a', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_create_alert(client):
    login_resp = client.post('/api/auth/login', json={"username": "organizer_demo", "password": "orgpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/crowd/alert', 
        json={"zone_id": "zone-a", "message": "Test alert"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "alert_id" in response.get_json()

def test_create_alert_volunteer_forbidden(client):
    login_resp = client.post('/api/auth/login', json={"username": "volunteer_demo", "password": "volpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/crowd/alert', 
        json={"zone_id": "zone-a", "message": "Test alert"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    
def test_create_alert_validation_error(client):
    login_resp = client.post('/api/auth/login', json={"username": "organizer_demo", "password": "orgpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/crowd/alert', 
        json={"message": "Test alert"}, # Missing zone_id
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
