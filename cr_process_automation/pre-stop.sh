#!/bin/bash

# Perform any cleanup or final actions here
echo "Performing pre-stop actions..."

# Example: Remove temporary files or log files
rm -rf /app/temp
rm -rf /app/logs
# Exit with a success status code
exit 0