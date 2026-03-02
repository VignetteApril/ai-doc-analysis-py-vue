#!/bin/bash

# AI Document Analysis System - Run Backend Tests in Docker (Linux/macOS)
# This script runs all backend tests inside the Docker container

echo "Running AI Document Analysis System Backend Tests in Docker"
echo "========================================================="

# Check if in project root directory
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: Please run this script from the project root directory"
    exit 1
fi

# Check if Docker Compose services are running
echo "Checking if Docker services are running..."
if ! docker-compose ps -q backend >/dev/null 2>&1; then
    echo "Starting Docker services..."
    docker-compose up -d
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to start Docker services"
        exit 1
    fi
    echo "Waiting for services to be ready..."
    sleep 10
fi

# Run tests inside the Docker container
echo "Running tests inside Docker container..."
docker-compose exec backend python -m pytest tests/ -v

if [ $? -ne 0 ]; then
    echo "ERROR: Tests failed"
    exit 1
fi

echo "Tests completed successfully!"