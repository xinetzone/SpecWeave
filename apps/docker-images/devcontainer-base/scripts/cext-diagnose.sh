#!/bin/bash
# Diagnose why verify-cext.sh fails inside build.sh smoke test
set +e

IMG=devcontainer-base:latest
C=diag-repro

docker rm -f $C >/dev/null 2>&1

echo "=== 1. docker run -d (same as smoke test) ==="
docker run -d --name $C "$IMG" tail -f /dev/null >/dev/null 2>&1
echo "start rc=$?"
sleep 3

echo "=== 2. docker exec verify-cext.sh (non-json, exact smoke call) ==="
timeout 30 docker exec $C bash /usr/local/bin/verify-cext.sh > /tmp/diag-nonjson.txt 2>&1
echo "exec rc=$?"
echo "--- output (full, filtered) ---"
grep -v '^\[' /tmp/diag-nonjson.txt | sed 's/^/| /'
echo "--- line count: $(wc -l < /tmp/diag-nonjson.txt) ---"

echo ""
echo "=== 3. docker exec verify-cext.sh --json ==="
timeout 30 docker exec $C bash /usr/local/bin/verify-cext.sh --json > /tmp/diag-json.txt 2>&1
echo "json rc=$?"
tail -1 /tmp/diag-json.txt | sed 's/^/| /'

echo ""
echo "=== 4. env inside container ==="
docker exec $C bash -c 'echo "PATH=$PATH"; which conda python; conda --version' 2>&1 | sed 's/^/| /'

docker rm -f $C >/dev/null 2>&1
echo "=== DONE ==="
