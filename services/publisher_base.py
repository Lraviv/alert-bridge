# services/publisher_base.py
from abc import ABC, abstractmethod

class AlertPublisher(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def publish(self, message: str, routing_key: str):
        pass

    @abstractmethod
    async def close(self):
        pass
