from __future__ import annotations

import asyncio
import json
import os
from typing import Optional

from groq import Groq
from dotenv import load_dotenv

from .models import Action, LogEntry

_SYSTEM_PROMPT = (
    "You are a debugging assistant. Given an error log, explain what went wrong concisely, "
    "then suggest up to 3 actionable fixes. Return JSON only in this shape: "
    "{ explanation: string, actions: [ { label: string, command: string } ] }"
)

load_dotenv()


async def explain_error(entry: LogEntry) -> LogEntry:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        entry.explanation = "Missing GROQ_API_KEY environment variable."
        entry.actions = []
        return entry

    client = Groq(api_key=api_key)
    prompt = entry.raw

    def _call() -> str:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    content = await asyncio.to_thread(_call)
    explanation, actions = _parse_response(content)
    entry.explanation = explanation
    entry.actions = actions
    return entry


def _parse_response(content: str) -> tuple[str, list[Action]]:
    try:
        payload = json.loads(content)
        explanation = str(payload.get("explanation") or "")
        actions_raw = payload.get("actions") or []
        actions: list[Action] = []
        for item in actions_raw[:3]:
            label = str(item.get("label") or "")
            command = str(item.get("command") or "")
            if label and command:
                actions.append(Action(label=label, command=command))
        return explanation or "No explanation provided.", actions
    except json.JSONDecodeError:
        return "LLM response was not valid JSON.", []
