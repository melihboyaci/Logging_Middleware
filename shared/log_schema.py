from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogType(str, Enum):
    LOG = "LOG"
    ERROR = "ERROR"
    TRANSACTION = "TRANSACTION"
    ACCESS = "ACCESS"


class UserRole(str, Enum):
    sysadmin = "sysadmin"
    developer = "developer"
    security = "security"


class LogRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: LogLevel
    type: LogType
    role: UserRole
    source: str
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
