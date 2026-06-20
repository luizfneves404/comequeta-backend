#!/usr/bin/env bash
set -euo pipefail

BASE_BRANCH="main"
PREFIX="hotfix"

usage() {
  cat <<EOF
Usage: $(basename "$0") <branch-name>

Creates a hotfix branch from ${BASE_BRANCH}.

Examples:
  $(basename "$0") fix-login-crash
  $(basename "$0") v1.2.1

Result: ${PREFIX}/fix-login-crash
EOF
  exit 1
}

[[ $# -eq 1 ]] || usage

BRANCH_NAME="$1"
HOTFIX_BRANCH="${PREFIX}/${BRANCH_NAME}"

if [[ ! "$BRANCH_NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9._/-]*$ ]]; then
  echo "Error: invalid branch name: '$BRANCH_NAME'" >&2
  exit 1
fi

if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "Error: not inside a Git repository." >&2
  exit 1
fi

echo "→ Fetching latest changes from origin/${BASE_BRANCH}..."
git fetch origin "${BASE_BRANCH}"

echo "→ Checking out ${BASE_BRANCH}..."
git checkout "${BASE_BRANCH}"

echo "→ Updating ${BASE_BRANCH}..."
git pull --ff-only origin "${BASE_BRANCH}"

if git show-ref --verify --quiet "refs/heads/${HOTFIX_BRANCH}"; then
  echo "Error: branch '${HOTFIX_BRANCH}' already exists locally." >&2
  exit 1
fi

echo "→ Creating branch '${HOTFIX_BRANCH}'..."
git checkout -b "${HOTFIX_BRANCH}"

echo ""
echo "✓ Branch '${HOTFIX_BRANCH}' created from '${BASE_BRANCH}'."
echo "  When done: git push -u origin ${HOTFIX_BRANCH}"
