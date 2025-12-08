#!/usr/bin/env bash
set -euo pipefail

# Run pre-commit against all files using uvx to avoid managing a dedicated venv.
uvx pre-commit run --all-files
