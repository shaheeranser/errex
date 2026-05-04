from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Action:
    label: str
    command: str


@dataclass
class LogEntry:
    level: str
    timestamp: Optional[str]
    message: str
    source: Optional[str]
    raw: str
    actions: List[Action] = field(default_factory=list)
    explanation: Optional[str] = None
