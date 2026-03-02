#!/bin/bash

# AI Document Analysis System - Run Backend Tests (Linux/macOS)
# This script runs all backend tests using pytest

echo "Running AI Document Analysis System Backend Tests"
echo "==============================================="

# Check if in project root directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "ERROR: Please run this script from the project root directory"
    exit 1
fi

# Change to backend directory
cd backend

# Install dependencies if needed
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Run tests
echo "Running tests..."
python -m pytest tests/ -v

# Return to original directory
cd ..

echo "Tests completed!"