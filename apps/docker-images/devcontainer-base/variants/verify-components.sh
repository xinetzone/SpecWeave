#!/bin/bash
echo "=== Verify conda ==="
which conda && conda --version
echo ""
echo "=== Verify conda envs ==="
conda env list
echo ""
echo "=== Verify Python (main env) ==="
python --version && which python
echo ""
echo "=== Verify Jupyter ==="
which jupyter && jupyter --version 2>&1 | head -5
echo ""
echo "=== Verify sshd ==="
which sshd && sshd -t && echo "sshd config valid"
echo ""
echo "=== Verify supervisord ==="
which supervisord && supervisord --version
echo ""
echo "=== Verify docker ==="
which docker && docker --version
echo ""
echo "=== Verify services config ==="
ls -la /etc/supervisor/conf.d/ 2>/dev/null
echo ""
echo "=== Verify build-info ==="
cat /etc/devcontainer-build-info 2>/dev/null
echo ""
echo "=== Verify pip mirrors ==="
echo "root pip config:"
pip config get global.index-url 2>/dev/null
echo ""
echo "=== Verify conda mirror ==="
echo "condarc content:"
cat /opt/conda/.condarc
