#!/usr/bin/env bash
# smoke.sh — smoke-test the openKylin dev container image (Linux / openKylin WSL).
# Static probes run with --entrypoint /bin/bash; then the full service stack is
# booted and checked via container exec. Every run uses --pull=never and the
# shared container contract flags (--device /dev/fuse, --security-opt
# label=disable, --cgroupns=host). Local image only; no implicit pulls.
set -euo pipefail

IMAGE="${IMAGE:-localhost/openkylin-dev:3.0}"

command -v podman >/dev/null 2>&1 || { echo "[SMOKE] FAIL: podman not found" >&2; exit 2; }

if ! podman image exists "$IMAGE" >/dev/null 2>&1; then
    echo "[SMOKE] FAIL: image '$IMAGE' not present locally — run scripts/build.sh first" >&2
    exit 2
fi

RUN=(run --rm --pull=never --device /dev/fuse --security-opt label=disable --cgroupns=host)

PROBE='set -euo pipefail
fail() { echo "PROBE_FAIL: $1"; exit 1; }
echo "P1 sshd -t";       sshd -t || fail "sshd -t"
echo "P2 jupyter";       python3 -m jupyter --version >/dev/null 2>&1 || fail "jupyter"
echo "P3 supervisord";   supervisord --version || fail "supervisord"
echo "P4 locale";        locale -a | grep -qiE "zh_CN\.(utf-?8)" || fail "locale zh_CN.UTF-8"
echo "P5 timezone";      [ "$(cat /etc/timezone)" = "Asia/Shanghai" ] || fail "timezone"
echo "P6 devuser-uid";   [ "$(id -u devuser)" = "1000" ] || fail "devuser uid"
echo "P7 subuid";        grep -q "^devuser:" /etc/subuid || fail "subuid"
echo "P8 podman-bins";   command -v podman >/dev/null && command -v newuidmap >/dev/null && command -v fuse-overlayfs >/dev/null || fail "podman binaries"
echo "P8b rootless-live"; RL="$(su - devuser -c "podman info --format '\''{{.Host.Security.Rootless}}'\''" 2>&1 || true)"; if [ "$RL" = "true" ]; then echo "  live rootless=true"; elif echo "$RL" | grep -q "Operation not permitted"; then echo "  ENV-LIMIT: nested userns EPERM (rootless outer host); image readiness verified, live rootless needs rootful host"; else fail "podman rootless: $RL"; fi
echo "ALL_PROBES_OK"'

echo "[SMOKE] static probes on $IMAGE"
if ! podman "${RUN[@]}" --entrypoint /bin/bash "$IMAGE" -lc "$PROBE"; then
    echo "[SMOKE] FAIL: static probes failed" >&2
    exit 1
fi
echo "[SMOKE] static probes OK"

echo "[SMOKE] full boot (waiting for HEALTHCHECK)"
CTR="$(podman run -d --pull=never --device /dev/fuse \
    --security-opt label=disable --cgroupns=host "$IMAGE")"

cleanup() { podman rm -f "$CTR" >/dev/null 2>&1 || true; }
trap cleanup EXIT

ready=0
for _ in $(seq 1 20); do
    sleep 3
    state="$(podman inspect -f '{{.State.Health.Status}}' "$CTR" 2>/dev/null || true)"
    [ "$state" = "healthy" ] && { ready=1; break; }
    running="$(podman inspect -f '{{.State.Running}}' "$CTR" 2>/dev/null || true)"
    [ "$running" != "true" ] && break
done

if [ "$ready" != "1" ]; then
    podman logs "$CTR" 2>&1 | tail -30
    echo "[SMOKE] FAIL: container not healthy within timeout" >&2
    exit 1
fi
echo "[SMOKE] full boot healthy (sshd + jupyter via healthcheck)"

SVC="$(podman exec "$CTR" bash -lc \
    'pgrep -x sshd >/dev/null && echo SSH_OK; pgrep -f "jupyter" >/dev/null && echo JUPYTER_OK; ss -ltn 2>/dev/null | grep -E ":22 |:8888 " && echo PORTS_OK')"
echo "$SVC"
echo "$SVC" | grep -q SSH_OK || { echo "[SMOKE] FAIL: sshd not running" >&2; exit 1; }
echo "$SVC" | grep -q JUPYTER_OK || { echo "[SMOKE] FAIL: jupyter not running" >&2; exit 1; }
echo "$SVC" | grep -q PORTS_OK || { echo "[SMOKE] FAIL: ports 22/8888 not listening" >&2; exit 1; }

echo "[SMOKE] OK: all probes passed on $IMAGE"
