#!/usr/bin/env bash
set -e

TMPFILE=$(mktemp /tmp/errex_XXXXXX.log)
cat > "$TMPFILE"
errex --file "$TMPFILE"
rm -f "$TMPFILE"
