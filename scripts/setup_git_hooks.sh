#!/usr/bin/env bash
# Configure git hooks to run from .githooks/
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "Configuring git hooks path to .githooks..."
git config core.hooksPath .githooks
chmod +x .githooks/*

echo "Git hooks configured successfully! Pre-commit checks will now verify type stubs."
