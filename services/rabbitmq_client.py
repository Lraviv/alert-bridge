# services/rabbitmq_client.py
import asyncio
import aio_pika
from logger import logger
from services.publisher_base import AlertPublisher


class RabbitMQClient(AlertPublisher):
    def __init__(self, host: str, exchange_name: str):
        self.host = host
        self.exchange_name = exchange_name
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        """Connect to RabbitMQ with automatic reconnection."""
        self.connection = await aio_pika.connect_robust(
            f"amqp://guest:guest@{self.host}/",
            reconnect_interval=5
        )
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name, 
            aio_pika.ExchangeType.TOPIC, 
            durable=True
        )
        logger.info("Connected to RabbitMQ exchange '%s' on host '%s'", self.exchange_name, self.host)

    async def publish(self, message: str, routing_key: str, timeout: float = 10.0):
        """
        Publish a message to RabbitMQ with timeout.
        
        Args:
            message: The message body to publish
            routing_key: The routing key for the message
            timeout: Maximum time to wait for publish operation
            
        Raises:
            TimeoutError: If the publish operation times out
            Exception: If the connection is not established
        """
        if not self.connection or self.connection.is_closed:
            raise ConnectionError("RabbitMQ connection is not established")
        
        msg = aio_pika.Message(
            body=message.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        try:
            await asyncio.wait_for(
                self.exchange.publish(msg, routing_key=routing_key),
                timeout=timeout
            )
            logger.info("Published to '%s': %s", routing_key, message[:100])
        except asyncio.TimeoutError:
            logger.error("Publish operation timed out after %s seconds", timeout)
            raise

    async def close(self):
        """Close the RabbitMQ connection."""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed.")

    def is_connected(self) -> bool:
        """Check if the connection is established and open."""
        return self.connection is not None and not self.connection.is_closed