#!/bin/bash

# Exit immediately if a command exits with a non-zero status (optional safety)
set -e

echo "Removing exited containers (if any)..."
docker ps --filter status=exited -q | xargs -r docker rm

echo "Building Docker image 'slice_api'..."
docker build -t slice_api .

echo "Running container on port 8080..."
docker run -p 8085:8080 slice_api # Change port from 8080 if needed
