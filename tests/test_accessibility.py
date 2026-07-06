def test_plan_accessibility(client, monkeypatch):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    def mock_generate(*args, **kwargs):
        return "Here is your accessible route to Zone A."
    monkeypatch.setattr("modules.accessibility.service.generateGroundedReply", mock_generate)
    
    response = client.post('/api/accessibility/plan', 
        json={"needs": ["wheelchair"], "destination_zone": "zone-a"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "plan" in data
    assert "facilities_used" in data
    assert data["plan"] == "Here is your accessible route to Zone A."

def test_plan_accessibility_validation_error(client):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/accessibility/plan', 
        json={"needs": ["wheelchair"]}, # Missing destination_zone
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_plan_accessibility_auth_error(client):
    login_resp = client.post('/api/auth/login', json={"username": "organizer_demo", "password": "orgpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/accessibility/plan', 
        json={"needs": ["wheelchair"], "destination_zone": "zone-a"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
