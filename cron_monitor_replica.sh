#!/bin/bash
#In case you want to clean the file daily basis and your project is located in /App
# type command
# crontab -e
# 0 0 * * * /usr/bin/python3 /App/cron_monitor_pg_statement.sh >> /App/cron_monitor_pg_statement.log 2>&1
#  Run this script carefully
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
cd $SCRIPT_DIR
python3 monitor_replica.py