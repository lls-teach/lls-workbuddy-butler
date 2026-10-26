#!/bin/bash
cd /tmp/wb-cdp
for i in $(seq 1 15); do
  echo "=== run $i ==="
  node harvest3.mjs
  [ $? -eq 0 ] && break
  sleep 2
done
