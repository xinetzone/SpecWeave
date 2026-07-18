---
id: "chain-pre-commit-hooks"
title: "链式pre-commit钩子架构"
source: "retrospective-concurrent-safety-checker-20260708 + retrospective-sensitive-info-hooks-20260708"
maturity: L2
validation_count: 2
reuse_count: 2
tags: ["git-hooks", "pre-commit", "architecture", "cross-platform"]
related:
  -   - "three-tier-check-tool"
  -   - "core-hookspath-distribution"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/chain-pre-commit-hooks.toml"
---
# 链式pre-commit钩子架构

## 问题

Git pre-commit钩子的组织方式面临选择：
1. **多独立钩子文件**（pre-commit框架模式）：每个检查一个独立钩子文件，通过框架调度
2. **单shell脚本堆砌**：所有检查逻辑写在一个shell脚本中，难以维护
3. **单入口多检查链**：一个Python主入口，内部串联多个独立检查模块

多独立钩子方案在跨平台场景下维护成本高（每个钩子都需要shell/cmd包装器），且检查顺序不可控。单shell脚本方案难以编写复杂逻辑和测试。

## 模式

采用"单Shell入口 + Python链式主入口 + 独立检查模块"的三层架构：

```
Git调用
  ↓
.githooks/pre-commit (Shell脚本，唯一入口)
  职责：找到Python解释器，exec调用Python主入口
  ↓ exec python
.agents/scripts/hooks/pre_commit.py (Python主入口)
  职责：链式调用各检查模块，按顺序执行，失败即终止
  │
  ├──→ _run_sensitive_check(project_root, staged_files)
  │     模块：lib/checks/sensitive_info.py
  │     特点：秒级快速检查，失败立即exit 1
  │
  ├──→ run_concurrent_check(project_root, staged_files)
  │     模块：hooks/concurrent_check.py
  │     特点：10秒级检查，失败exit 1
  │
  └──→ [未来扩展更多检查...]
        只需新增模块并在main()中注册一行
```

## 核心设计原则

1. **顺序可控**：快速/高价值检查放在前面，失败立即阻断，避免不必要的扫描耗时
2. **单一Shell包装器**：跨平台只维护一套Shell脚本，新增检查不修改Shell层
3. **检查模块独立**：每个检查模块导出统一签名 `run_xxx(project_root, staged_files) -> int`，可独立测试
4. **一致的环境变量控制**：每个检查遵循 `XXX_CHECK_SKIP` / `XXX_CHECK_WARN_ONLY` 命名约定
5. **增量扫描**：所有检查只扫描 `git diff --cached` 的暂存文件，保证pre-commit速度

## 新增检查的标准流程

```python
# 1. 创建 hooks/xxx_check.py
def run_xxx_check(project_root: Path, staged_files: list[Path]) -> int:
    """检查XXX问题，返回0通过/1阻断。"""
    ...
    return 0 if has_high_risk else 1

# 2. 在 pre_commit.py main() 中注册
def main():
    ...
    result = _run_sensitive_check(project_root, scripts_dir, staged_files)
    if result != 0:
        return result
    result = run_concurrent_check(project_root, scripts_dir, staged_files)
    if result != 0:
        return result
    result = run_xxx_check(project_root, staged_files)  # 新增
    if result != 0:
        return result
    return 0
```

## 对比

| 维度 | 多独立钩子 | 单Shell脚本 | **链式Python** |
|------|-----------|------------|--------------|
| 跨平台维护 | N套包装器 | 1套但难维护 | **1套包装器** |
| 检查顺序 | 文件名字母序 | 脚本顺序 | **显式链式控制** |
| 输出格式 | 碎片化 | 混杂 | **统一格式** |
| 早期阻断 | 不可控 | 手动处理 | **自动：失败即终止** |
| 新增检查成本 | 新增包装器+配置 | 追加shell代码 | **新增Python模块+1行注册** |
| 可测试性 | 需框架支持 | 差 | **每个模块独立单元测试** |
| Windows兼容 | 每个钩子需.cmd | 困难 | **共享一套.cmd** |

## 复用场景

- 任何需要多个pre-commit检查的项目（代码规范、安全扫描、复杂度检查等）
- 需要跨平台（Windows/macOS/Linux）支持的团队
- 希望pre-commit检查可扩展、可独立测试的项目

## 时间预算约束

pre-commit钩子总耗时应控制在5秒以内。如果某个检查耗时超过1秒，考虑：
1. 优化为增量扫描（只检查变更部分）
2. 移至pre-push钩子（30秒预算）
3. 移至CI流水线（分钟级预算）

> **关联模式**：
> - [three-tier-check-tool](three-tier-check-tool.md) — 单个检查工具内部架构（解析→检查→输出）
> - [precision-over-recall](../methodology-patterns/tools-automation/precision-over-recall.md) — 静态分析宁可漏报不可误报原则
