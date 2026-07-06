def test_ask_assistant(client, monkeypatch):
    # Authenticate
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    def mock_generate(*args, **kwargs):
        return "Mocked answer about Gate 1."
        
    monkeypatch.setattr("modules.assistant.service.generateGroundedReply", mock_generate)
    
    response = client.post('/api/assistant/ask', 
        json={"question": "Where is Gate 1?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "answer" in data
    assert "sources" in data
    assert data["answer"] == "Mocked answer about Gate 1."

def test_ask_assistant_validation_error(client):
    login_resp = client.post('/api/auth/login', json={"username": "fan_demo", "password": "fanpass123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post('/api/assistant/ask', 
        json={"language": "en"}, # missing question
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "validation_failed"

def test_ask_assistant_auth_error(client):
    response = client.post('/api/assistant/ask', json={"question": "Where?"})
    assert response.status_code == 401
