#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "Dev env ready. Run: uvicorn backend.app:app --reload"
