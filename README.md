# errex

Explain error logs in an interactive terminal UI. Pipe in a log or point it at a file, pick an entry, and errex asks an LLM (via Groq) to explain what went wrong and suggest runnable fixes.

## Features

- Interactive TUI (Textual) listing parsed log entries, colour-coded by level
- Reads from a pipe or a file (`--file`)
- Parser handles plain-text levels (ERROR/WARN/INFO/DEBUG/CRITICAL), multi-line Python tracebacks, and JSON log lines
- Press `Enter` on an entry to send it to Groq (`llama-3.3-70b-versatile`) for a concise explanation plus up to 3 suggested fixes
- Suggested fixes appear as buttons; pressing one runs the command and shows its output

## Requirements

- Python 3.10+
- A Groq API key

## Install

```bash
pipx install .        # global
# or
pip install -e .      # editable
```

## Usage

```bash
python buggy.py 2>&1 | errex
errex --file error.log
```

Set your key in a `.env` file (loaded automatically) or the environment:

```
GROQ_API_KEY=...
```

Helper scripts: `errex.sh` (installs via pipx if needed, then runs) and `errex-pipe.sh`.

## How it works

- `parser.py` splits the input into `LogEntry` records
- `app.py` renders them in a Textual `ListView` and drives selection and actions
- `llm.py` calls Groq and parses the JSON response into an explanation and actions
- Suggested commands are executed via `subprocess` — review them before running

## Project structure

```
src/errex/
  main.py    Typer CLI entry point
  app.py     Textual TUI
  parser.py  Log parsing
  llm.py     Groq integration
  models.py  LogEntry / Action dataclasses
```
