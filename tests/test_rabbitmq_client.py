import pytest
import aio_pika
from services.rabbitmq_client import RabbitMQClient

@pytest.mark.asyncio
async def test_connect_and_publish(monkeypatch):
    # Mock aio_pika.connect_robust
    class DummyConnection:
        @property
        def is_closed(self):
            return False
            
        async def channel(self):
            return DummyChannel()
            
        async def close(self):
            pass

    class DummyExchange:
        async def publish(self, message, routing_key):
            return True
            
        def __await__(self):
            return iter([])

    class DummyChannel:
        async def declare_exchange(self, name, type, durable):
            return DummyExchange()

    async def mock_connect_robust(url, reconnect_interval=5):
        return DummyConnection()

    monkeypatch.setattr(aio_pika, "connect_robust", mock_connect_robust)

    mq = RabbitMQClient("localhost", "test_exchange")
    await mq.connect()

    await mq.publish('{"alert": "test"}', "alert.info")
    await mq.close()