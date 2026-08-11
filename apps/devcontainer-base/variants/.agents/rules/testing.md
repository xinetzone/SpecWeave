---
id: "variants-testing"
title: "镜像变体测试规范"
source: "variants/scripts/test-conda-llvm.sh"
---
# 镜像变体测试规范

本文件定义镜像变体的单元测试脚本约定、测试分层策略和编写规范。

## 测试脚本位置与命名

- **位置**：`variants/scripts/test-<variant>.sh`
- **执行入口**：`bash variants/scripts/test-<variant>.sh [--tag TAG]`
- **默认 TAG**：`latest`
- **被构建脚本调用**：build.sh 构建成功后自动调用，独立构建脚本 `build-<variant>.sh` 末尾也调用

## 测试分层策略

测试脚本应按以下 6 个层级组织，覆盖从底层工具到上层服务的完整验证链：

### L1: 工具链可用性（Toolchain Availability）

验证变体安装的核心命令可执行并输出版本信息：
```bash
test_<tool>_version() {
    local result
    result=$(docker run --rm "$IMAGE" <tool> --version 2>&1)
    if [ $? -eq 0 ] && echo "$result" | grep -q "<version-pattern>"; then
        pass "T<N>: <Tool> version check"
    else
        fail "T<N>: <Tool> version check failed"
    fi
}
```

### L2: 功能编译/执行（Functional Compilation）

验证工具链能完成实际工作（如 C++ 编译、Python 包导入）：
```bash
test_<tool>_hello_world() {
    local result
    result=$(docker run --rm "$IMAGE" bash -c '
        echo "<test code>" > /tmp/test && \
        <tool> /tmp/test -o /tmp/out && /tmp/out
    ' 2>&1)
    if echo "$result" | grep -q "<expected output>"; then
        pass "T<N>: Hello World <function>"
    else
        fail "T<N>: Hello World <function> failed: $result"
    fi
}
```

### L3: 核心组件深度验证（Deep Component Validation）

验证变体特有组件的配置正确性（如 LLVM components 列表、conda 环境列表）：
- 库文件路径检查
- 头文件路径检查
- 配置文件内容验证
- 包管理器环境列表

### L4: 基础服务继承（Base Service Inheritance）

**必须验证**基础镜像的核心服务未被破坏：
```bash
test_ssh_exists() { docker run --rm "$IMAGE" which sshd; }
test_supervisord_exists() { docker run --rm "$IMAGE" which supervisord; }
test_docker_cli_exists() { docker run --rm "$IMAGE" which docker; }
test_jupyter_exists() { docker run --rm "$IMAGE" bash -c 'source /opt/venv/bin/activate && which jupyter'; }
test_devuser_exists() { docker run --rm "$IMAGE" id devuser; }
```

### L5: 环境隔离（Environment Isolation）

验证 PATH 优先级、环境隔离正确：
- 默认 python 指向 `/opt/venv/bin/python`
- 非 root 用户可访问新工具
- 虚拟环境完整性

### L6: 配置验证（Configuration Validation）

验证配置文件存在且内容正确：
- `.condarc` 存在且包含镜像源配置
- 激活脚本语法正确

## 测试脚本模板结构

```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"
source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="test-<variant>"

TAG="latest"
VARIANT="<variant-name>"
IMAGE="devcontainer-base:${VARIANT}-${TAG}"
PASSED=0
FAILED=0
TESTS=()

# 参数解析
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag) TAG="$2"; IMAGE="devcontainer-base:${VARIANT}-${TAG}"; shift 2;;
        -h|--help) usage; exit 0;;
        *) echo "Unknown option: $1"; exit 1;;
    esac
done

# 辅助函数
pass() { PASSED=$((PASSED+1)); TESTS+=("PASS: $1"); log_ok "$1"; }
fail() { FAILED=$((FAILED+1)); TESTS+=("FAIL: $1"); log_error "$1"); }

# ===== 测试函数定义（按L1-L6分层） =====
# L1: 工具链可用性
test_t1() { ... }
test_t2() { ... }
# L2: 功能编译
test_t7() { ... }
# ... 更多测试 ...

# 主执行流程
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       Unit Tests: ${VARIANT} variant                         "
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
log_info "Image: ${IMAGE}"
echo ""

# 检查镜像是否存在
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE}$"; then
    log_fatal "Image not found: ${IMAGE}, please build first"
fi

# 执行所有测试
log_step "Running tests..."
test_t1
test_t2
# ...
total=$((PASSED + FAILED))

# 结果汇总
echo ""
log_step "Test Summary"
echo ""
printf "%-10s %-50s\n" "RESULT" "TEST"
printf "%-10s %-50s\n" "------" "----"
for t in "${TESTS[@]}"; do
    result="${t%%:*}"
    name="${t#*: }"
    printf "%-10s %-50s\n" "$result" "$name"
done
echo ""
log_info "Total: ${total} | Passed: ${PASSED} | Failed: ${FAILED}"

if [ $FAILED -gt 0 ]; then
    log_error "Tests FAILED"
    exit 1
else
    log_ok "All tests PASSED"
fi
```

## 验证命令与测试脚本的关系

build.sh 中的 `VARIANTS` 数组定义**构建后快速验证命令**（快速冒烟测试），而 `test-<variant>.sh` 是**完整单元测试**：

| 对比项 | build.sh 验证命令 | test-<variant>.sh |
|-------|------------------|-------------------|
| 时机 | 构建后自动执行 | 手动或一键脚本调用 |
| 范围 | 核心工具版本输出（冒烟） | 6 层完整验证 |
| 数量 | 3-5 条命令 | 15-25 个测试用例 |
| 耗时 | <30秒 | 1-5分钟 |
| 失败处理 | 标记构建失败 | 输出详细错误，逐项报告 |

## 测试容器运行约定

- 使用 `--rm` 标志自动清理测试容器
- 每个测试函数独立运行 `docker run`，不共享容器状态
- 测试代码通过 `bash -c '...'` 内联传递，不依赖外部文件
- 超时控制：快速验证 60s，完整测试脚本中编译测试可放宽到 120s
- 禁止 `--privileged` 除非测试 DinD 功能（基础服务测试不需要）

## 新增变体测试检查清单

创建新变体测试脚本时，逐项确认：
- [ ] L1: 所有核心工具的 `--version` 测试
- [ ] L2: 至少 1 个 Hello World 功能测试（编译/执行）
- [ ] L3: 2+ 深度组件验证（库路径、配置、环境列表）
- [ ] L4: 5 项基础服务继承测试（ssh/supervisord/docker/jupyter/devuser）
- [ ] L5: PATH 优先级测试（`which python` = `/opt/venv/bin/python`）
- [ ] L6: 配置文件验证
- [ ] 测试结果逐项 PASS/FAIL 输出
- [ ] 最终汇总统计
- [ ] 脚本通过 `bash -n` 语法检查
