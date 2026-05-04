# errex

Explain error logs with a rich terminal UI.

## Install

### Pipx (global, no venv activation)

```bash
pipx install .
```

This makes `errex` available globally without activating a virtualenv.

### Manual (editable install)

```bash
pip install -e .
```

## Usage

```bash
python buggy.py 2>&1 | errex
```

```bash
errex --file error.log
```
