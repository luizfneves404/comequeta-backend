#!/usr/bin/env bash
set -euo pipefail

MSG_FILE="${1:?commit message file required}"

HEADER=""
if ! IFS= read -r HEADER < "$MSG_FILE"; then
  echo "Error: could not read commit message file" >&2
  exit 1
fi
HEADER="${HEADER//$'\r'/}"
HEADER="${HEADER//$'\ufeff'/}"

HEADER_PATTERN='^(feat|fix|chore|docs|style|refactor|test|ci|build|perf|revert): [a-z0-9].*$'

if ! echo "$HEADER" | grep -Eq "$HEADER_PATTERN"; then
  echo "Error: header must match \"<type>: <subject>\" with a single space after the colon" >&2
  echo "Got: '$HEADER'" >&2
  exit 1
fi

if echo "$HEADER" | grep -Eq ' {2,}'; then
  echo "Error: commit header must not contain consecutive spaces" >&2
  exit 1
fi

SUBJECT="${HEADER#*: }"

if echo "$SUBJECT" | grep -Eq '[A-Z]'; then
  echo "Error: subject must be lower-case" >&2
  exit 1
fi

if [[ "$SUBJECT" == *. ]]; then
  echo "Error: subject must not end with a period" >&2
  exit 1
fi
