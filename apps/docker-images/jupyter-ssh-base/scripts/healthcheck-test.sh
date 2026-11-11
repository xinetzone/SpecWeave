#!/bin/bash
set -euo pipefail

CONTAINER_NAME="jupyter-ssh-test"
IMAGE_NAME="${IMAGE_NAME:-jupyter-ssh-base}"
IMAGE_TAG="${IMAGE_TAG:-1.1}"
IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "============================================"
echo " 启动容器并进行健康检查"
echo "============================================"
echo ""

# Cleanup old container
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

# Start container
echo "--- 启动容器 ---"
docker run -d \
  --name "$CONTAINER_NAME" \
  -p 2223:22 \
  -p 8889:8888 \
  -e USER_PASSWORD=testpass123 \
  -e JUPYTER_TOKEN=testtoken456 \
  -e GRANT_SUDO=no \
  "$IMAGE"

# Wait for SSH service
echo "--- 等待 SSH 服务就绪 ---"
for i in $(seq 1 20); do
  if docker exec "$CONTAINER_NAME" pgrep -x sshd >/dev/null 2>&1; then
    echo "  SSH 服务已就绪 (等待 ${i}s)"
    break
  fi
  sleep 1
done

# Wait for Jupyter: 进程存在不等于 HTTP 就绪，须轮询 API 直到可响应
echo "--- 等待 Jupyter HTTP 就绪 ---"
JUPYTER_READY=false
HTTP_CODE="000"
for i in $(seq 1 60); do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8889/api" 2>/dev/null || echo "000")
  case "$HTTP_CODE" in
    200|302|401|403)
      echo "  Jupyter HTTP 已就绪 (HTTP ${HTTP_CODE}, 等待 ${i}s)"
      JUPYTER_READY=true
      break
      ;;
  esac
  sleep 1
done
if [ "$JUPYTER_READY" = false ]; then
  echo "  [FAIL] Jupyter HTTP 60s 内未就绪 (最后 HTTP ${HTTP_CODE})"
  docker logs "$CONTAINER_NAME" --tail 50 2>&1 || true
  exit 1
fi

echo ""
echo "============================================"
echo " 1. supervisorctl 服务状态"
echo "============================================"
docker exec "$CONTAINER_NAME" supervisorctl status

echo ""
echo "============================================"
echo " 2. 容器内 healthcheck.sh"
echo "============================================"
set +e
docker exec "$CONTAINER_NAME" /usr/local/bin/healthcheck.sh
HC_EXIT=$?
set -e
echo "  Exit code: $HC_EXIT"
if [ "$HC_EXIT" -ne 0 ]; then
  echo "  [FAIL] 容器内健康检查未通过"
  exit 1
fi

echo ""
echo "============================================"
echo " 3. Docker HEALTHCHECK 状态"
echo "============================================"
sleep 10
HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "starting")
echo "  状态: $HEALTH"
if [ "$HEALTH" != "healthy" ]; then
  echo "  等待健康检查完成..."
  sleep 20
  HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")
  echo "  状态: $HEALTH"
fi

echo ""
echo "============================================"
echo " 4. Jupyter HTTP API 响应"
echo "============================================"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8889/api" 2>/dev/null || echo "FAIL")
echo "  HTTP $HTTP_CODE"

echo ""
echo "============================================"
echo " 5. SSH 非交互 PATH 验证"
echo "============================================"
echo "  --- which jupyter ---"
sshpass -p testpass123 ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -p 2223 jupyteruser@127.0.0.1 'which jupyter' 2>/dev/null || echo "  (sshpass not available, skipping)"

echo "  --- which python3 ---"
sshpass -p testpass123 ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -p 2223 jupyteruser@127.0.0.1 'which python3' 2>/dev/null || echo "  (sshpass not available, skipping)"

echo ""
echo "============================================"
echo " 6. 容器日志 (最后 20 行)"
echo "============================================"
docker logs "$CONTAINER_NAME" --tail 20 2>&1

echo ""
echo "============================================"
echo " 检查完成"
echo "============================================"
echo ""
echo "容器名: $CONTAINER_NAME"
echo "清理命令: docker rm -f $CONTAINER_NAME"