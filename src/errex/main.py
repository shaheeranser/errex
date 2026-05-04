from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import typer

from .app import ErrexApp

app = typer.Typer(help="Explain error logs with an interactive TUI.")


@app.command()
def main(file: Optional[Path] = typer.Option(None, "--file", "-f")) -> None:
    if sys.stdin.isatty():
        if not file:
            raise typer.BadParameter("Provide --file or pipe input into errex.")
        raw_log = file.read_text(encoding="utf-8", errors="replace")
    else:
        raw_log = sys.stdin.read()

    if not sys.stdin.isatty():
        fd = os.open("/dev/tty", os.O_RDWR)
        os.dup2(fd, sys.stdin.fileno())

    os.environ.setdefault("TEXTUAL_DRIVER", "linux")

    app_instance = ErrexApp(log_data=raw_log)
    if not app_instance.entries:
        raise typer.BadParameter("No log entries found.")

    app_instance.run()


if __name__ == "__main__":
    app()
