#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

nohup python main.py > "$LOG_DIR/main.out" 2>&1 &
echo "Started. PID: $!"
