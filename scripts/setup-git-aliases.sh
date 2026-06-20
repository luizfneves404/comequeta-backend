#!/usr/bin/env bash
set -euo pipefail

git config --local include.path ../.gitaliases
echo "✓ Aliases configured: git feature, git hotfix"
