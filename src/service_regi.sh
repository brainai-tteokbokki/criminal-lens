#!/bin/bash

SERVICE_NAME="criminal-lens.service"
SERVICE_FILE="./$SERVICE_NAME"
SYSTEMD_PATH="/etc/systemd/system/$SERVICE_NAME"

if [ ! -f "$SERVICE_FILE" ]; then
    echo "Error: $SERVICE_FILE not found in the current directory."
    exit 1
fi

sudo cp "$SERVICE_FILE" "$SYSTEMD_PATH"
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy $SERVICE_FILE to $SYSTEMD_PATH."
    exit 1
fi
echo "Service file copied to $SYSTEMD_PATH."

sudo chmod 644 "$SYSTEMD_PATH"
echo "Permissions set for $SYSTEMD_PATH."

sudo systemctl daemon-reload
if [ $? -ne 0 ]; then
    echo "Error: Failed to reload systemd daemon."
    exit 1
fi
echo "Systemd daemon reloaded."

sudo systemctl enable "$SERVICE_NAME"
if [ $? -ne 0 ]; then
    echo "Error: Failed to enable $SERVICE_NAME."
    exit 1
fi
echo "Service enabled."

sudo systemctl start "$SERVICE_NAME"
if [ $? -ne 0 ]; then
    echo "Error: Failed to start $SERVICE_NAME."
    exit 1
fi
echo "Service started successfully."

sudo systemctl status "$SERVICE_NAME" --no-pager
