#!/bin/bash

source .venv/bin/activate

python3 barman.py &
BARMAN_PID=$!

sleep 1

python3 app.py &
APP_PID=$!

cleanup() {
    echo "Arresto Sbronzolo..."
    kill $BARMAN_PID $APP_PID 2>/dev/null
    wait $BARMAN_PID $APP_PID 2>/dev/null
}

trap cleanup SIGINT SIGTERM EXIT

wait