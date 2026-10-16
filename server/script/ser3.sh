
#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage:"
    echo "  ./ser3.sh http://FRONTEND_PUBLIC_IP"
    exit 1
fi

FRONTEND_URL="$1"

echo "======================================"
echo " Updating FRONTEND_URL"
echo "======================================"

cd "$(dirname "$0")/.."

echo "New FRONTEND_URL:"
echo "$FRONTEND_URL"

# Back up the current configuration.
cp config.py config.py.bak

# Update the frontend origin.
sed -i "s|^FRONTEND_URL = .*|FRONTEND_URL = \"$FRONTEND_URL\"|" config.py

echo ""
echo "Updated config.py:"
grep FRONTEND_URL config.py

echo ""
echo "Restarting FastAPI..."

pkill -f "[u]vicorn main:app" 2>/dev/null || true

nohup python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    > app.log 2>&1 &

echo ""
echo "FastAPI restarted."
echo "Check logs with:"
echo "    tail -f app.log"
