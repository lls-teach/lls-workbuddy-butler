#!/bin/bash
cd /tmp/wb-cdp
for i in $(seq 1 15); do
  echo "=== run $i ==="
  node harvest2.mjs
  code=$?
  if [ $code -eq 0 ]; then break; fi
  sleep 2
done
