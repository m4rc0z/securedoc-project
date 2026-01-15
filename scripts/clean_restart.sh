#!/bin/bash

# clean_restart.sh
# Forcefully restarts the SecureDoc stack to ensure fresh connections.

echo "🛑 Stopping all services..."
# Kill by port
lsof -ti:4200 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8081 | xargs kill -9 2>/dev/null
lsof -ti:11434 | xargs kill -9 2>/dev/null

echo "✅ Ports Cleared."
sleep 2

# 1. Start Ollama
echo "🚀 Starting Ollama..."
nohup ollama serve > ollama.log 2>&1 &
echo "   PID: $!"
sleep 5

# 2. Start Python Backend
echo "🚀 Starting Python Backend..."
cd backend-python
# Enforce IPv4 for Ollama
export OLLAMA_BASE_URL="http://127.0.0.1:11434"
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend-python.log 2>&1 &
echo "   PID: $!"
cd ..
sleep 5

# 3. Start Java Backend
echo "🚀 Starting Java Backend..."
cd backend-java
nohup mvn spring-boot:run > ../backend-java.log 2>&1 &
echo "   PID: $!"
cd ..
sleep 15

# 4. Start Frontend
echo "🚀 Starting Frontend..."
cd frontend
# Ensure dependencies are installed for 'marked'
if [ ! -d "node_modules/marked" ]; then
    echo "Installing missing dependencies..."
    npm install
fi
nohup npm start -- --host 0.0.0.0 --proxy-config proxy.conf.json > ../frontend.log 2>&1 &
echo "   PID: $!"
cd ..

echo "⏳ Waiting for Frontend to become ready..."
sleep 10
echo "🌍 System Restarted. Access at http://localhost:4200"
