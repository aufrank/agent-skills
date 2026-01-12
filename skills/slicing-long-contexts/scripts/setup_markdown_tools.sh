#!/usr/bin/env bash
set -euo pipefail

# Install markdown parsing helpers for improved slicing.
# Uses uvx to avoid polluting the current env.

uvx --python 3.11 pip install --quiet --upgrade markdown markdown-it-py

echo "Installed markdown and markdown-it-py into uvx runner. You can now invoke via 'uvx python -m markdown' or import in scripts."
