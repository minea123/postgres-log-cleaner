#!/bin/bash
#In case you want to clean the file daily basis and your project is located in /App
# type command
# crontab -e
# 0 0 * * * /usr/bin/python3 /App/con_clean_pg_log.sh >> /App/con_clean_pg_log.log 2>&1
# Get the directory of the current script
# assume read base directory from config.properties
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
cd $SCRIPT_DIR
python3 main.py
echo "done"
