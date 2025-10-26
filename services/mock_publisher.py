from services.publisher_base import AlertPublisher
from logger import logger

class MockPublisher(AlertPublisher):
    async def connect(self):
        logger.info("MockPublisher: connected")

    async def publish(self, message: str, routing_key: str):
        logger.info("MockPublisher: pretend published %s -> %s", routing_key, message)

    async def close(self):
        logger.info("MockPublisher: closed")