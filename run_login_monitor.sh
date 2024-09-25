#!/bin/bash
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
cd $SCRIPT_DIR
nohup python3 monitor_login_log.py > monitor_login_log.out 2>&1 &