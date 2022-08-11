#!/bin/sh

BASEDIR=$(dirname "$0")

DATE=${1:-$(date +%Y-%m-%d)}

cd $BASEDIR
.venv/bin/python3 unifi_stock_checker.py $DATE
