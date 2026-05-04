from __future__ import annotations

import asyncio
import subprocess
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Label, ListItem, ListView, LoadingIndicator, Static

from .llm import explain_error
from .models import LogEntry
from .parser import parse_logs


class EntrySelected(Message):
    def __init__(self, entry: LogEntry) -> None:
        super().__init__()
        self.entry = entry


class ErrexApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    .main {
        height: 1fr;
    }

    .left {
        width: 1fr;
        border: round $surface;
    }

    .right {
        width: 2fr;
        border: round $surface;
    }

    .explanation {
        height: 2fr;
        padding: 1 2;
    }

    .actions {
        height: 1fr;
        padding: 1 2;
    }

    .output {
        height: 1fr;
        padding: 1 2;
        overflow: auto;
    }

    .error {
        color: red;
    }

    .warn {
        color: yellow;
    }

    .info {
        color: gray;
    }

    .critical {
        color: red;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("enter", "explain", "Explain"),
    ]

    entries: List[LogEntry]
    current_index: reactive[Optional[int]] = reactive(None)

    def __init__(self, log_data: str) -> None:
        super().__init__()
        self.entries = parse_logs(log_data)

    def compose(self) -> ComposeResult:
        with Horizontal(classes="main"):
            with Container(classes="left"):
                yield ListView(id="entry_list")
            with Container(classes="right"):
                yield Static("Select an entry and press Enter.", id="explanation", classes="explanation")
                yield LoadingIndicator(id="loading", classes="actions")
                yield Container(id="action_buttons", classes="actions")
                yield Static("", id="action_output", classes="output")

    def on_mount(self) -> None:
        list_view = self.query_one(ListView)
        for entry in self.entries:
            label = f"{entry.level}: {entry.message}"
            item = ListItem(Label(label))
            item.add_class(self._class_for_level(entry.level))
            list_view.append(item)
        if self.entries:
            list_view.index = 0
        list_view.focus()
        self.query_one(LoadingIndicator).display = False

    def _class_for_level(self, level: str) -> str:
        value = level.upper()
        if value == "ERROR":
            return "error"
        if value == "WARN":
            return "warn"
        if value == "CRITICAL":
            return "critical"
        return "info"

    def action_explain(self) -> None:
        list_view = self.query_one(ListView)
        if list_view.index is None:
            return
        self.current_index = list_view.index
        entry = self.entries[list_view.index]
        self.post_message(EntrySelected(entry))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.index is None:
            return
        self.current_index = event.list_view.index
        entry = self.entries[event.list_view.index]
        self.post_message(EntrySelected(entry))

    async def on_entry_selected(self, message: EntrySelected) -> None:
        loading = self.query_one(LoadingIndicator)
        explanation = self.query_one("#explanation", Static)
        output = self.query_one("#action_output", Static)
        action_buttons = self.query_one("#action_buttons", Container)

        output.update("")
        action_buttons.remove_children()
        loading.display = True
        explanation.update("Explaining...")

        updated = await explain_error(message.entry)
        explanation.update(updated.explanation or "No explanation available.")
        loading.display = False

        if not updated.actions:
            action_buttons.mount(Static("No suggested actions."))
            return

        for index, action in enumerate(updated.actions):
            button = Button(action.label, id=f"action_{index}")
            button.data = action.command
            action_buttons.mount(button)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        output = self.query_one("#action_output", Static)
        command = getattr(event.button, "data", None)
        if not command:
            return

        output.update("Running...\n")

        def _run() -> str:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
            )
            text = result.stdout or ""
            if result.stderr:
                text += "\n" + result.stderr
            if not text:
                text = f"Command exited with code {result.returncode}."
            return text

        text = await asyncio.to_thread(_run)
        output.update(text)
