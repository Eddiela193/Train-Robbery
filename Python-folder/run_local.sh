#!/usr/bin/env bash
# run_local.sh -- helper to run server on privileged port 100 (ONLY if you own the machine)

PORT=100
echo "[run_local] Starting server on port $PORT (you will be prompted for sudo if needed)..."
sudo python3 server.py --port $PORT