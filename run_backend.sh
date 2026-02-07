#!/bin/bash
# Install additional dependencies
pip install sqlalchemy joblib torch > /dev/null

# Make sure we are in the root
cd /Users/rezaal/Documents/coding/ORCA_PURAPURANINJA

# Run the backend
cd backend
python3 -m uvicorn main:app --reload --port 8000
