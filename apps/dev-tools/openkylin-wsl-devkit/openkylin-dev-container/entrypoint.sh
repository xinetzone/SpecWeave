#!/usr/bin/env bash
# entrypoint.sh — one-time container initialization then hand over to supervisord.
# Runs as root inside the container. SSH host keys are generated at startup
# (never baked into the image); devuser password comes from DEV_PASSWORD or a
# random one-shot value printed to stdout.
set -euo pipefail

DEVUSER="${DEVUSER:-devuser}"
SUPERVISOR_CONF="/etc/supervisor/supervisord.conf"

echo "[entrypoint] openKylin dev container starting (devuser=${DEVUSER})"

# 1. devuser password: env var wins, otherwise generate a random one-shot password
if [ -n "${DEV_PASSWORD:-}" ]; then
    echo "${DEVUSER}:${DEV_PASSWORD}" | chpasswd
    echo "[entrypoint] devuser password set from DEV_PASSWORD"
else
    PW="$(head -c 12 /dev/urandom | base64 | tr -d '/+=' | head -c 12)"
    echo "${DEVUSER}:${PW}" | chpasswd
    echo "[entrypoint] random one-shot password for ${DEVUSER}: ${PW}"
    echo "[entrypoint] connect: ssh ${DEVUSER}@<host> -p 22"
fi

# 2. SSH host keys: generate once at startup if missing
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    echo "[entrypoint] generating SSH host keys"
    ssh-keygen -A
fi

# 3. runtime dirs required by sshd / supervisord
mkdir -p /run/sshd /var/run/sshd /run/supervisor

echo "[entrypoint] handing over to supervisord"
exec supervisord -c "${SUPERVISOR_CONF}" -n
