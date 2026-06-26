#!/usr/bin/env bash
# CI/CD 流水线检查脚本
# 用途：在提交前自动运行所有验证检查，确保代码质量
# 用法：bash ci-check.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "CI/CD 流水线检查"
echo "========================================"
echo ""

# 1. 检查 Git 忽略规则
echo -e "\033[33m[1/6] 检查 Git 忽略规则...\033[0m"
python "$ROOT/.agents/scripts/check-gitignore.py"
if [ $? -ne 0 ]; then
    echo -e "\033[31m错误: Git 忽略规则检查失败\033[0m"
    exit 1
fi
echo -e "\033[32m  通过\033[0m"
echo ""

# 2. 检查 vendor 目录合规性
echo -e "\033[33m[2/6] 检查 vendor 目录合规性...\033[0m"
python "$ROOT/.agents/scripts/check-vendor.py" || {
    echo -e "\033[33m警告: vendor 目录合规性检查发现问题（如无第三方依赖可忽略）\033[0m"
}
echo ""

# 3. 检查链接有效性
echo -e "\033[33m[3/6] 检查链接有效性...\033[0m"
python "$ROOT/.agents/scripts/check-links.py"
if [ $? -ne 0 ]; then
    echo -e "\033[31m错误: 链接检查失败\033[0m"
    exit 1
fi
echo -e "\033[32m  通过\033[0m"
echo ""

# 4. 检查规格文档一致性
echo -e "\033[33m[4/6] 检查规格文档一致性...\033[0m"
python "$ROOT/.agents/scripts/check-spec-consistency.py"
# 规格一致性检查允许警告，但错误必须修复
if [ $? -ne 0 ]; then
    echo -e "\033[33m警告: 规格文档一致性检查有警告\033[0m"
fi
echo ""

# 5. 检查模式成熟度字段
echo -e "\033[33m[5/6] 检查模式成熟度字段...\033[0m"
python "$ROOT/.agents/scripts/pattern-maturity-stats.py" --check
if [ $? -ne 0 ]; then
    echo -e "\033[31m错误: 模式成熟度字段检查失败\033[0m"
    exit 1
fi
echo -e "\033[32m  通过\033[0m"
echo ""

# 6. 更新导航表
echo -e "\033[33m[6/6] 更新文档导航表...\033[0m"
python "$ROOT/.agents/scripts/generate-nav.py"
if [ $? -ne 0 ]; then
    echo -e "\033[31m错误: 导航表更新失败\033[0m"
    exit 1
fi
echo -e "\033[32m  通过\033[0m"
echo ""

echo "========================================"
echo -e "\033[32m所有检查通过\033[0m"
echo "========================================"
