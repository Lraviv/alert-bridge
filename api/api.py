import asyncio
import json
import os
import sys
from fastapi import FastAPI, HTTPException
from utilities.json_helpers import retry_failed_alerts, store_failed_alert
from schemes.request import AlertPayload
from consts import RABBITMQ_HOST, EXCHANGE_NAME
from services.rabbitmq_client import RabbitMQClient
from services.publisher_base import AlertPublisher
from logger import logger

app = FastAPI(title="Alert Bridge", version="1.0")
publisher: AlertPublisher = RabbitMQClient(RABBITMQ_HOST, EXCHANGE_NAME)

@app.get("/")
async def root():
    return {"message": "Hello from Alert Bridge!"}


@app.on_event("startup")
async def startup_event():
    try:
        await publisher.connect()
        # Start retry background task
        asyncio.create_task(retry_failed_alerts(publisher))
    except Exception as e:
        logger.exception("Failed to connect to RabbitMQ: %s", e)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    await publisher.close()

@app.post("/alerts")
async def receive_alert(payload: AlertPayload):
    """
    Receives alerts from Alertmanager webhook, validates them,
    and publishes each alert to RabbitMQ by severity.
    """
    published = 0
    
    for alert in payload.alerts:
        severity = alert.labels.severity
        routing_key = f"alert.{severity}"
        message_json = alert.model_dump_json()

        try:
            await publisher.publish(message_json, routing_key=routing_key)
            published += 1
        except Exception as e:
            logger.exception("Failed to publish alert: %s", e)
            await store_failed_alert(alert.dict())

    logger.info("Processed %d alerts successfully.", published)
    return {"status": "ok", "alerts_received": len(payload.alerts), "alerts_published": published}