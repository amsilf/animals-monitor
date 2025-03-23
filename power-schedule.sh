#!/bin/bash

# Set log file path in the same directory as the script
LOG_FILE="$(dirname "$0")/power-schedule.log"

# Check if this is a suspend or wake operation
if [ "$1" = "suspend" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Initiating system suspend" >> "$LOG_FILE"
    systemctl suspend
elif [ "$1" = "wake" ]; then
    # Calculate wake time for next day at 8:00 AM
    WAKE_TIME=$(date -d "today 21:30:00" '+%s')
    
    # Suspend until calculated time
    sudo rtcwake -m mem -t "$WAKE_TIME"
    
    # Check if the system is awake and log the result
    if [ $? -eq 0 ]; then
        echo "System is awake"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - System woke up successfully" >> "$LOG_FILE"
    else
        echo "Failed to wake up the system"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - System failed to wake up" >> "$LOG_FILE"
    fi
else
    echo "Usage: $0 [suspend|wake]"
    exit 1
fi