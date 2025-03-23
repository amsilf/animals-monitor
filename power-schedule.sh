#!/bin/bash

# Calculate wake time for next day at 8:00 AM (adjust time as needed)
WAKE_TIME=$(date -d "today 21:30:00" '+%s')

# Suspend until calculated time
sudo rtcwake -m mem -t "$WAKE_TIME"

# Set log file path in the same directory as the script
LOG_FILE="$(dirname "$0")/power-schedule.log"

# Check if the system is awake and log the result
if [ $? -eq 0 ]; then
    echo "System is awake"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - System woke up successfully" >> "$LOG_FILE"
else
    echo "Failed to wake up the system"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - System failed to wake up" >> "$LOG_FILE"
fi