import json
from consts import FAILED_ALERTS_FILE
from logger import logger
import asyncio
import aiofiles


async def store_failed_alert(alert: dict):
    """Store a failed alert to a local JSON file asynchronously."""
    failed = []
    if FAILED_ALERTS_FILE.exists():
        try:
            async with aiofiles.open(FAILED_ALERTS_FILE, "r") as f:
                content = await f.read()
                if content.strip():
                    failed = json.loads(content)
        except json.JSONDecodeError:
            failed = []
        except FileNotFoundError:
            failed = []

    failed.append(alert)
    async with aiofiles.open(FAILED_ALERTS_FILE, "w") as f:
        await f.write(json.dumps(failed, indent=2))


async def get_failed_alerts() -> list:
    """Read failed alerts from file."""
    if not FAILED_ALERTS_FILE.exists():
        return []
    
    try:
        async with aiofiles.open(FAILED_ALERTS_FILE, "r") as f:
            content = await f.read()
            if not content.strip():
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        logger.warning("Failed to parse failed alerts file, starting fresh")
        return []
    except FileNotFoundError:
        return []


async def save_failed_alerts(failed_alerts: list):
    """Save failed alerts to file."""
    async with aiofiles.open(FAILED_ALERTS_FILE, "w") as f:
        await f.write(json.dumps(failed_alerts, indent=2))


async def retry_failed_alerts(publisher):
    """Background task to retry failed alerts every 5 minutes.
    
    Args:
        publisher: The alert publisher instance to use for retrying
    """
    await asyncio.sleep(30)  # Wait for startup to complete
    
    while True:
        try:
            failed = await get_failed_alerts()
            
            if not failed:
                await asyncio.sleep(300)
                continue

            still_failed = []
            for alert in failed:
                routing_key = f"alert.{alert['labels']['severity']}"
                try:
                    await publisher.publish(json.dumps(alert), routing_key=routing_key)
                    logger.info("Successfully retried alert: %s", alert.get('labels', {}).get('alertname', 'unknown'))
                except Exception as e:
                    logger.exception("Retry failed for alert: %s", e)
                    still_failed.append(alert)

            # Write remaining failed alerts back
            if still_failed != failed:
                await save_failed_alerts(still_failed)
                logger.info(f"Retry cycle completed. {len(still_failed)} alerts still failed, {len(failed) - len(still_failed)} succeeded")

        except Exception as e:
            logger.exception("Error in retry loop: %s", e)

        await asyncio.sleep(300)  # Retry every 5 minutes