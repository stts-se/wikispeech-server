#!/bin/bash

hostname="127.0.0.1"

python2 ahotts-httpserver.py $hostname 1200 1201 &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start ahotts-httpserver.py: $status"
  exit $status
fi

bin/tts_server -IP=$hostname -Port=1201 &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start tts_server: $status"
  exit $status
fi

while sleep 60; do
  ps aux | grep "ahotts-httpserver.py" | grep -q -v grep
  PROCESS_1_STATUS=$?
  ps aux | grep "tts_server" | grep -q -v grep
  PROCESS_2_STATUS=$?
  # If the greps above find anything, they exit with 0 status
  # If they are not both 0, then something is wrong
  if [ $PROCESS_1_STATUS -ne 0 -o $PROCESS_2_STATUS -ne 0 ]; then
    echo "One of the processes has already exited."
    exit 1
  fi
done

