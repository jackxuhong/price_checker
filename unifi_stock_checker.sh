#!/bin/sh

BASEDIR=$(dirname "$0")

cd $BASEDIR
.venv/bin/python3 unifi_stock_checker.py $@
