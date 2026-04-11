#!/bin/bash
cd /root/.openclaw/workspace
mkdir -p logs

while true; do
    /usr/bin/python3 scripts/scheduler.py >> logs/scheduler.log 2>&1
    sleep 60
done
