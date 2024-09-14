#!/bin/bash
#In case you want to clean the file daily basis and your project is located in /App
# type command
# crontab -e
# 0 0 * * * /usr/bin/python3 /App/cron_clean_old_wal.sh >> /App/cron_clean_old_wal.log 2>&1
#  Run this script carefully
WAL_DIR=/var/lib/postgresql/14/main/pg_wal
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
cd $SCRIPT_DIR
python3 main.py --d $WAL_DIR --a 30
