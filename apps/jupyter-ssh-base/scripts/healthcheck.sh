#!/bin/bash

SSH_PORT="${SSH_PORT:-22}"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
FAIL=0

if ! pgrep -x sshd >/dev/null 2>&1; then
    echo "[HEALTHCHECK] sshd process not running"
    FAIL=1
else
    if timeout 2 bash -c "echo >/dev/tcp/127.0.0.1/${SSH_PORT}" 2>/dev/null; then
        echo "[HEALTHCHECK] sshd port ${SSH_PORT}: OK"
    else
        echo "[HEALTHCHECK] sshd port ${SSH_PORT}: FAILED"
        FAIL=1
    fi
fi

if pgrep -f "jupyter" >/dev/null 2>&1; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${JUPYTER_PORT}/api" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo "[HEALTHCHECK] jupyter port ${JUPYTER_PORT}: OK (HTTP ${HTTP_CODE})"
    else
        echo "[HEALTHCHECK] jupyter port ${JUPYTER_PORT}: FAILED (HTTP ${HTTP_CODE})"
        FAIL=1
    fi
else
    echo "[HEALTHCHECK] jupyter process not running"
    FAIL=1
fi

if [ "$FAIL" -eq 1 ]; then
    echo "[HEALTHCHECK] STATUS: UNHEALTHY"
    exit 1
fi

echo "[HEALTHCHECK] STATUS: HEALTHY"
exit 0
