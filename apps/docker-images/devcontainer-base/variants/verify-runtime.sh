#!/bin/bash
set -e
cd /mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base

echo "=== 清理旧容器 ==="
docker rm -f test-base 2>/dev/null || true

echo "=== 启动验证容器 ==="
docker run -d --name test-base --privileged -e USER_PASSWORD=test devcontainer-base:test-aliyun
sleep 8

echo ""
echo "=== 1. root 用户验证 ==="
docker exec test-base bash -c '
    echo "--- conda 验证 ---"
    conda --version
    echo "conda envs:"
    conda info --envs
    echo ""
    echo "--- Python 验证（应是 main 环境） ---"
    which python
    python --version
    python -c "import sysconfig; print(\"SOABI:\", sysconfig.get_config_var(\"SOABI\"))"
    echo ""
    echo "--- 镜像源验证 - conda .condarc ---"
    cat /opt/conda/.condarc
    echo ""
    echo "--- pip 配置验证（root） ---"
    pip config get global.index-url
    echo ""
    echo "--- /etc/environment PATH 验证 ---"
    grep PATH /etc/environment
    echo ""
    echo "--- conda-init.sh 内容验证 ---"
    cat /etc/profile.d/conda-init.sh
'

echo ""
echo "=== 2. devuser 用户验证 ==="
docker exec test-base su - devuser -c '
    echo "--- devuser conda 验证 ---"
    conda --version
    echo ""
    echo "--- devuser Python 验证 ---"
    which python
    python --version
    echo "CONDA_DEFAULT_ENV=$CONDA_DEFAULT_ENV"
    echo ""
    echo "--- devuser pip 配置验证 ---"
    pip config get global.index-url
'

echo ""
echo "=== 3. 服务与文件验证 ==="
docker exec test-base bash -c '
    sshd -t && echo "[OK] sshd config valid"
    supervisord --version && echo "[OK] supervisord available"
    docker --version && echo "[OK] docker available"
    test ! -d /opt/venv && echo "[OK] /opt/venv does not exist"
    test -f /home/devuser/.config/pip/pip.conf && echo "[OK] devuser pip.conf exists"
    test -f /root/.config/pip/pip.conf && echo "[OK] root pip.conf exists"
    test -f /opt/conda/.condarc && echo "[OK] system .condarc exists"
'

echo ""
echo "=== 验证完成，清理容器 ==="
docker rm -f test-base
echo "=== 所有验证完成 ==="
