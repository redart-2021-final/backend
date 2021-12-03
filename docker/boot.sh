#!/bin/bash

set -e

if [ "$1" = 'update' ]; then
  aerich upgrade
  cd src
  exec python tasks.py
elif [ "$1" = 'server' ]; then
  cd src
  exec python main.py
elif [ "$1" = 'worker' ]; then
  cd src
  exec rq worker -u $BROKER_URL
elif [ "$1" = 'scheduler' ]; then
  cd src
  exec rqscheduler -u $BROKER_URL
else
  exec $@
fi
