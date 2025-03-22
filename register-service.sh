#!/bin/bash

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Service name
SERVICE_NAME="animals-detector"

echo "Installing $SERVICE_NAME service..."

# Copy service file
cp $SERVICE_NAME.service /etc/systemd/system/

# Set proper permissions
chmod 644 /etc/systemd/system/$SERVICE_NAME.service

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable $SERVICE_NAME.service

# Start service
systemctl start $SERVICE_NAME.service

# Check status
systemctl status $SERVICE_NAME.service

echo "Service has been created and started!"
echo "Use the following commands to manage the service:"
echo "  Check status: sudo systemctl status $SERVICE_NAME"
echo "  Start service: sudo systemctl start $SERVICE_NAME"
echo "  Stop service: sudo systemctl stop $SERVICE_NAME"
echo "  View logs: sudo journalctl -u $SERVICE_NAME" 