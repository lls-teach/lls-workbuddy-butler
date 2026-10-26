#!/bin/bash
cd /tmp/wb-cdp
for i in $(seq 1 12); do
  echo "=== run $i ==="
  node harvest.mjs && break
  sleep 2
done
