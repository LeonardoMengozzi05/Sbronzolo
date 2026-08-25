#!/bin/bash
source .venv/bin/activate
cd "$(dirname "$0")/.."
if [[ "$1" == "-mock" ]]; then
    echo "Avvio in modalita' mock"
    DEBUG="true" GPIOZERO_PIN_FACTORY="mock" python3 barman.py &
else
    DEBUG="false" python3 barman.py &
fi
BARMAN_PID=$!
sleep 1
python3 app-eritivo.py &
APP_PID=$!
cleanup() {
    trap - SIGINT SIGTERM EXIT
    echo -e "\nArresto Sbronzolo..."
    kill $BARMAN_PID $APP_PID 2>/dev/null
    wait $BARMAN_PID $APP_PID 2>/dev/null
}
trap cleanup SIGINT SIGTERM EXIT
wait
