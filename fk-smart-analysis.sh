#!/bin/bash

exec 2>&1

sleep 12h

exec /usr/lib/fk-smart-analysis/fk-smart-analysis.py | /usr/bin/cosmos
