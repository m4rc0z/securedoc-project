#!/bin/bash
echo "Pulling Ollama model: tinyllama..."
docker exec securedoc-ollama ollama pull llama3

echo "Warming up model (forcing load into memory)..."
docker exec securedoc-ollama ollama run llama3 "Hello" || true

echo "Model ready!"
