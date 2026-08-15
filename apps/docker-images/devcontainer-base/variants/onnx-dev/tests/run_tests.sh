#!/usr/bin/env bash
# =============================================================================
# Run all tests: host-side bash tests + container-side Python tests
# Usage:
#   bash tests/run_tests.sh              # Run host bash tests only (no Docker)
#   bash tests/run_tests.sh --container  # Also run Python tests inside Docker
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$VARIANT_ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

RUN_CONTAINER=false
if [[ "${1:-}" == "--container" ]]; then
    RUN_CONTAINER=true
fi

echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo -e "${CYAN}  onnx-dev 测试套件${NC}"
echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo ""

# ── Host-side tests (no Docker needed) ──
echo -e "${YELLOW}[1/2] 主机端测试（bash路径解析，无需Docker）${NC}"
echo ""
bash tests/test_resolve_script_path.sh
BASH_RC=$?

echo ""

# ── Check if pytest is available on host ──
PYTEST_HOST=false
if command -v python3 &>/dev/null && python3 -m pytest --version &>/dev/null 2>&1; then
    if python3 -c "import ft_compat_check" 2>/dev/null; then
        PYTEST_HOST=true
    fi
fi

if [[ "$PYTEST_HOST" == true ]]; then
    echo -e "${YELLOW}[2/2] 主机端Python单元测试（ft_compat_check mock测试）${NC}"
    echo ""
    python3 -m pytest tests/test_ft_compat_check.py -v
    PYTEST_RC=$?
else
    echo -e "${YELLOW}[2/2] 主机端Python测试跳过（需要pytest且无需ONNX依赖）${NC}"
    echo "  提示: pip install pytest 后可运行主机端mock测试"
    PYTEST_RC=0
fi

echo ""

# ── Container tests ──
CONTAINER_RC=0
if [[ "$RUN_CONTAINER" == true ]]; then
    echo -e "${YELLOW}[3] 容器端集成测试（需要Docker镜像）${NC}"
    echo ""
    if ! command -v docker &>/dev/null || ! docker info &>/dev/null 2>&1; then
        echo -e "${RED}Docker不可用，跳过容器测试${NC}"
    else
        IMAGE="devcontainer-base:onnx-dev-latest"
        if ! docker image inspect "$IMAGE" &>/dev/null; then
            echo -e "${RED}镜像 $IMAGE 不存在，请先构建${NC}"
            CONTAINER_RC=1
        else
            # Check if pytest is available in container
            docker run --rm \
                -e WORKSPACE_CHOWN_MODE=named-only \
                -v "$VARIANT_ROOT:/workspace" \
                -w /workspace \
                "$IMAGE" \
                bash -c "/opt/conda/envs/main/bin/pip install pytest -q 2>&1 && /opt/conda/envs/main/bin/python -m pytest tests/ -v"
            CONTAINER_RC=$?
        fi
    fi
fi

# ── Summary ──
echo ""
echo -e "${CYAN}═══════════════════════════════════════${NC}"
FAILED=0
[[ $BASH_RC -ne 0 ]] && ((FAILED++))
[[ $PYTEST_RC -ne 0 ]] && ((FAILED++))
[[ $CONTAINER_RC -ne 0 ]] && ((FAILED++))

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}  ✅ 所有测试通过！${NC}"
else
    echo -e "${RED}  ❌ $FAILED 个测试套件失败${NC}"
fi
echo -e "${CYAN}═══════════════════════════════════════${NC}"
exit $FAILED
