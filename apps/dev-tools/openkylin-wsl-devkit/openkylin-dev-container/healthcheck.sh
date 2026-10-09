#!/usr/bin/env bash
# healthcheck.sh — probe core services (sshd + jupyter) for HEALTHCHECK.
# Exit 0 when both are alive, 1 otherwise.
set -uo pipefail

SSHD_ALIVE=0
JUPYTER_ALIVE=0

if pgrep -x sshd >/dev/null 2>&1; then
    SSHD_ALIVE=1
fi

if pgrep -f "jupyter" >/dev/null 2>&1; then
    JUPYTER_ALIVE=1
fi

# fallback: check listening ports when procps is unavailable
if [ "${SSHD_ALIVE}" = 0 ] && command -v ss >/dev/null 2>&1; then
    ss -ltn 2>/dev/null | grep -q ":22 " && SSHD_ALIVE=1
fi
if [ "${JUPYTER_ALIVE}" = 0 ] && command -v ss >/dev/null 2>&1; then
    ss -ltn 2>/dev/null | grep -q ":8888 " && JUPYTER_ALIVE=1
fi

[ "${SSHD_ALIVE}" = 1 ] && [ "${JUPYTER_ALIVE}" = 1 ]
