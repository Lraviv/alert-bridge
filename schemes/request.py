from pydantic import BaseModel, Field, field_validator

class AlertLabels(BaseModel):
    alertname: str
    severity: str

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value):
        allowed = {"critical", "warning", "info"}
        value = value.lower()
        if value not in allowed:
            raise ValueError(f"Invalid severity '{value}', must be one of {allowed}")
        return value

class Alert(BaseModel):
    status: str
    labels: AlertLabels
    annotations: dict = {}

class AlertPayload(BaseModel):
    alerts: list[Alert]
