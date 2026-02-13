#!/bin/bash

# Installs a cron job to run the email summariser daily at 9am local time
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
CRON_CMD="0 9 * * * cd ${PROJECT_DIR} && ${PYTHON_PATH} main.py >> ${PROJECT_DIR}/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "email-summariser"; then
  echo "Cron job already exists. Skipping."
  exit 0
fi

# Append to existing crontab
(crontab -l 2>/dev/null; echo "# email-summariser daily digest"; echo "${CRON_CMD}") | crontab -

echo "Cron job installed: runs daily at 9:00 AM"
echo "Logs will be written to ${PROJECT_DIR}/cron.log"
