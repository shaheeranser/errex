from __future__ import annotations

import json
import re
from typing import List, Optional

from .models import LogEntry

_LEVEL_PATTERN = re.compile(r"\b(ERROR|WARN|WARNING|INFO|DEBUG|CRITICAL)\b", re.IGNORECASE)


def _detect_level(text: str) -> str:
    match = _LEVEL_PATTERN.search(text)
    if not match:
        return "INFO"
    value = match.group(1).upper()
    if value == "WARNING":
        return "WARN"
    return value


def _entry_from_text(raw: str, message: Optional[str] = None) -> LogEntry:
    text = raw.strip("\n")
    return LogEntry(
        level=_detect_level(text),
        timestamp=None,
        message=message or text.splitlines()[-1] if text else "",
        source=None,
        raw=text,
    )


def _is_traceback_start(line: str) -> bool:
    return line.startswith("Traceback (most recent call last):")


def parse_logs(content: str) -> List[LogEntry]:
    entries: List[LogEntry] = []
    lines = content.splitlines()
    buffer: List[str] = []
    in_traceback = False

    def flush_buffer() -> None:
        nonlocal buffer, in_traceback
        if not buffer:
            return
        raw = "\n".join(buffer)
        entries.append(_entry_from_text(raw))
        buffer = []
        in_traceback = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if buffer and not in_traceback:
                flush_buffer()
            else:
                buffer.append(line)
            continue

        if _is_traceback_start(line):
            flush_buffer()
            in_traceback = True
            buffer.append(line)
            continue

        if in_traceback:
            buffer.append(line)
            continue

        # Try JSON log line
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                payload = json.loads(stripped)
                message = str(payload.get("message") or payload.get("msg") or "")
                raw = json.dumps(payload, ensure_ascii=True)
                entry = LogEntry(
                    level=_detect_level(message or raw),
                    timestamp=str(payload.get("timestamp") or payload.get("time") or "") or None,
                    message=message or raw,
                    source=str(payload.get("source") or payload.get("logger") or "") or None,
                    raw=raw,
                )
                entries.append(entry)
                continue
            except json.JSONDecodeError:
                pass

        buffer.append(line)

    flush_buffer()
    return entries
