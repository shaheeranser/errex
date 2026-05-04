#!/usr/bin/env bash
set -e

if ! command -v pipx >/dev/null 2>&1; then
  echo "pipx is required but not installed."
  echo "Install pipx: https://pipx.pypa.io/stable/installation/"
  exit 1
fi

if ! pipx list | grep -q "^package errex "; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  pipx install "$SCRIPT_DIR"
fi

errex "$@"
