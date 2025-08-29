#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$PROJECT_DIR")"

cd "$PROJECT_DIR" || exit

python manage.py delete_inactive

#save exit status
retVal=$?

#Add error handling
if [ $retVal -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup completed successfully" >> /tmp/customer_cleanup_log.txt
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup failed" >> /tmp/customer_cleanup_log.txt
    exit 1
fi




