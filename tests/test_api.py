import pytest
from fastapi.testclient import TestClient
from api.api import app, publisher
from schemes.request import AlertPayload

def test_root():
    """Test the root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Alert Bridge!"}


@pytest.mark.asyncio
async def test_receive_alert(monkeypatch):
    """Test posting alerts and publishing them to RabbitMQ."""

    # Mock connect, publish, and close to avoid real RabbitMQ calls
    async def mock_connect():
        return True

    async def mock_publish(message, routing_key, timeout=10.0):
        return True

    async def mock_close():
        return True

    monkeypatch.setattr(publisher, "connect", mock_connect)
    monkeypatch.setattr(publisher, "publish", mock_publish)
    monkeypatch.setattr(publisher, "close", mock_close)

    # Create a sample payload
    payload = {
        "alerts": [
            {
                "labels": {
                    "alertname": "TestAlert",
                    "severity": "critical"
                },
                "annotations": {"description": "CPU usage high"},
                "status": "firing"
            }
        ]
    }

    client = TestClient(app)
    response = client.post("/alerts", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["alerts_received"] == 1
    assert data["alerts_published"] == 1
