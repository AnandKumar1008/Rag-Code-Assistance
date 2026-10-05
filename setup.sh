#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting setup on remote server..."

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual env
source venv/bin/activate

# Install requirements
if [ -f "backend/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r backend/requirements.txt
fi

# Pull Ollama models (we will use Llama 3 for LLM and nomic-embed-text for embeddings)
echo "Ensuring required Ollama models are pulled..."
# Setting CUDA_VISIBLE_DEVICES to limit Ollama to GPU 5 and 6
export CUDA_VISIBLE_DEVICES=5,6

# Check if ollama is accessible
if command -v ollama > /dev/null; then
    echo "Pulling llama3..."
    ollama pull llama3
    echo "Pulling nomic-embed-text..."
    ollama pull nomic-embed-text
else
    echo "Ollama command not found. Please ensure Ollama is installed."
fi

# Run Qdrant Vector DB via Docker if not already running
if ! docker ps | grep -q qdrant; then
    echo "Starting Qdrant Docker container..."
    docker run -d -p 6333:6333 -p 6334:6334 \
        -v $(pwd)/qdrant_storage:/qdrant/storage \
        --name qdrant \
        qdrant/qdrant || echo "Qdrant container might already exist but stopped, try starting it..."
        docker start qdrant || true
fi

echo "Setup script completed successfully!"
