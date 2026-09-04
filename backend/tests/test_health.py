def test_health_check(client):
    """Test root health endpoint returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "cropshift-api"
    assert data["version"] == "1.0.0"

def test_v1_health_check(client):
    """Test API v1 health endpoint returns ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "cropshift-api"
    assert data["version"] == "1.0.0"
