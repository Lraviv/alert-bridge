import os
from pathlib import Path


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "alert_exchange")

ALLOWED_SEVERITIES = {"critical", "warning", "info"}

FAILED_ALERTS_FILE = Path("./failed_alerts/failed_alerts.json")
