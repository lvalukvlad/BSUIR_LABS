#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/seed_logs.py
python3 scripts/analyze.py
