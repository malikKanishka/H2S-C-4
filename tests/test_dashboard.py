def test_dashboard_summary(client, monkeypatch):
    login_resp = client.post('/api/auth/login', json={"username": "volunteer_demo", "password": "volpass123"})
    token = login_resp.get_json()["access_token"]
    
    def mock_generate(*args, **kwargs):
        return "- Watch Zone A\n- Check Gate 2\n- All good elsewhere"
    monkeypatch.setattr("modules.dashboard.service.generateGroundedReply", mock_generate)
    
    response = client.get('/api/dashboard/summary', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert "zones" in data
    assert "alerts" in data
    assert "insights" in data
    assert len(data["insights"]) == 3

def test_dashboard_summary_fan_forbidden(client):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.get('/api/dashboard/summary', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_dashboard_ui(client):
    login_resp = client.post('/api/auth/login', json={"username": "organizer_demo", "password": "orgpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.get(f'/dashboard?token={token}')
    assert response.status_code == 200
    assert b"FanPulse Operations Dashboard" in response.data
