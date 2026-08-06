---
id: monorepo-ci-blindspot-detection
title: Monorepo子项目CI盲区检测
type: process
date: 2026-07-31
maturity: L1-draft
source: 2026-07-31-caffe-ffi-backward-logging-milestone-retro.md
related_patterns:
  - selective-testing-strategy
  - release-gate-automated-verification
tags:
  - ci
  - monorepo
  - testing
  - pytest
  - build-systems
  - quality-gate
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/process-patterns/monorepo-ci-blindspot-detection.toml"
---

# Monorepo子项目CI盲区检测

## 触发场景

- 当在Monorepo项目中怀疑子项目测试未被CI覆盖时
- 当主CI显示绿灯但子项目测试可能从未执行过时
- 当新增子项目/子模块后需要验证CI是否覆盖到它
- 当重构CI配置后需要确认测试发现逻辑正确
- 适用于：pytest/pnpm/cargo/gradle等任意包管理器的Monorepo项目
- 不适用于：
  - ❌ 单项目仓库（无嵌套子项目）
  - ❌ 已明确配置了递归测试发现的项目（仍建议定期审计）
  - ❌ 刻意把子项目测试排除在主CI外的项目（但应有独立CI）

## 核心做法

1. **第一步：审计根pytest/testpaths配置**
   - 检查根目录pyproject.toml/pytest.ini/tox.ini中的`testpaths`配置
   - 确认`testpaths`是否只列出了根目录下的tests，没有递归发现
   - 检查是否有`--recursive`或类似配置

2. **第二步：审计子项目独立pytest配置**
   - 检查每个子项目目录下是否有独立的pyproject.toml/pytest.ini
   - 确认子项目的`testpaths`指向自己的tests目录
   - 记录每个子项目的测试文件数量和测试用例数量

3. **第三步：用collect-only对比测试计数**
   - 在根目录运行`pytest --collect-only -q | wc -l`统计根CI能收集到的测试数
   - 在每个子项目目录分别运行`pytest --collect-only -q | wc -l`统计子项目测试数
   - 对比：子项目测试数之和是否≈根收集数？如果差距大，说明有盲区
   - （Windows PowerShell用`(pytest --collect-only -q | Measure-Object -Line).Lines`计数）

4. **第四步：检查构建命令是否含测试步骤**
   - 检查项目的构建脚本/命令（如`xs build`、`make build`、`npm run build`）
   - 确认构建命令是否自动执行测试，还是只编译不测试
   - 检查CI workflow yaml中是否有独立的test job

5. **第五步：选择修复方案**
   - **方案A：独立CI**（推荐C++/重编译项目）：为子项目配置独立GitHub Actions/GitLab CI，子项目代码变更时触发
   - **方案B：条件步骤**（推荐折中方案）：在主CI中添加路径过滤，只有子项目代码变更时才运行其测试
   - **方案C：统一递归配置**（推荐轻量Python/JS项目）：配置pytest/jest递归发现所有子项目测试
   - **方案D：统一测试命令**（如新增`xs test`）：提供统一入口，自动发现并运行所有子项目测试

## 反模式（不要这么做）

- ❌ **反模式1：假设pytest会递归**
  - 表现：认为"CI配了pytest就会自动跑所有测试"
  - 后果：pytest默认只发现根testpaths下的测试，不会递归进入子项目；103个测试可能只有3个在跑，绿灯毫无意义

- ❌ **反模式2：主CI无条件跑所有子项目测试**
  - 表现：不管改了什么代码，每次CI都跑所有子项目的全量测试
  - 后果：C++编译+测试可能耗时30分钟+，拖慢主CI反馈周期；开发者倾向于跳过CI或绕过质量门

- ❌ **反模式3：只看绿灯不看覆盖率**
  - 表现：CI显示绿灯就认为质量没问题，不深究跑了哪些测试
  - 后果：子项目测试几个月没跑，回归bug堆积到发布才发现；尤其是涉及编译的C++子项目，最容易被忽略

## 检验标准

做完之后怎么知道做对了？
- 标准1：`pytest --collect-only`在根目录收集到的测试数 = 所有子项目测试数之和（或明确知道少了哪些以及为什么）
- 标准2：CI日志中能看到子项目测试的输出（不是只有根3个测试）
- 标准3：子项目代码变更时，对应的测试确实在CI中运行了（可通过故意改坏一个子项目测试来验证）
- 标准4：构建命令和测试命令分离（build只编译，test跑测试），职责清晰
- 标准5：有文档说明CI测试覆盖策略（哪些在主CI跑，哪些有独立CI）

## 迁移示例

这个模式还能用在什么其他场景？

- **场景1：pnpm Monorepo**：前端pnpm workspace项目，根package.json的test脚本只跑根测试；用同样方法检查每个package的test脚本，对比`pnpm recursive test`和根test的测试数量
- **场景2：Cargo Workspace**：Rust Cargo workspace项目，根Cargo.toml的members是否包含所有子crate；`cargo test --workspace`是否在CI中运行
- **场景3：Gradle多模块**：Java/Kotlin Gradle多模块项目，检查根build.gradle的test任务是否包含所有子模块
- **场景4：Go多模块**：Go Monorepo多模块项目，每个模块有自己的go.mod；检查CI是否在每个模块目录下跑`go test ./...`
- **场景5：文档/示例测试**：不仅是代码测试，文档中的示例代码、配置文件示例是否也被验证？这类"非代码"测试最容易成为盲区

## 实施检查清单

检测阶段：
- [ ] 根pyproject.toml/pytest.ini的testpaths配置已审计
- [ ] 各子项目独立pytest配置已列出
- [ ] `pytest --collect-only`在根目录计数已记录
- [ ] `pytest --collect-only`在每个子项目目录计数已记录
- [ ] 对比计数差异，列出未覆盖的子项目清单
- [ ] 构建命令是否含测试已确认
- [ ] CI workflow yaml检查完成

修复阶段：
- [ ] 根据子项目特点选择修复方案（独立CI/条件步骤/统一配置/统一命令）
- [ ] CI配置修改完成
- [ ] 故意破坏一个子项目测试，验证CI能捕获到失败（红灯测试）
- [ ] 恢复破坏，验证CI恢复绿灯
- [ ] 在README/贡献指南中说明CI测试覆盖策略
- [ ] 考虑新增统一测试入口命令（如`xs test`）

## 代码审查速查

审查CI配置变更时，使用 [框架扩展与性能日志CR清单](../../../checklists/framework-extension-and-perf-logging-review.md#四monorepo-ci覆盖检查) 逐项对照。

## 实际案例（Caffe-ffi CI盲区发现）

本模式提炼自caffe-ffi子项目CI盲区发现：

- **背景**：SpecWeave是Monorepo，主CI运行`python -m pytest`；caffe-ffi是projects/下的子项目，包含C++扩展
- **发现过程**：
  1. 审计根pyproject.toml：`testpaths = ["tests"]`，只指向根tests目录
  2. 审计caffe-ffi/pyproject.toml：有独立`testpaths = ["tests/python"]`配置
  3. collect-only计数：根目录只收集到3个测试文件，caffe-ffi子项目有19个测试文件、103个测试类
  4. 构建命令检查：`xs build`只编译安装，不运行pytest
  5. 结果：主CI绿灯，但103个caffe-ffi测试从未在CI中运行过
- **修复方案选择**：caffe-ffi有C++编译耗时长，选择方案A（独立CI）或方案B（路径过滤条件步骤）
- **行动项**：为caffe-ffi添加独立GitHub Actions CI配置；考虑新增`xs test`统一命令

## 快速检测脚本（pytest版）

可直接在项目中运行此脚本快速检测盲区：

```bash
#!/bin/bash
echo "=== 根目录测试收集 ==="
ROOT_COUNT=$(cd /path/to/repo && pytest --collect-only -q 2>/dev/null | tail -1)
echo "根目录: $ROOT_COUNT"

echo ""
echo "=== 子项目测试收集 ==="
TOTAL_SUB=0
for proj in projects/*/ libs/*/ apps/*/; do
  if [ -f "$proj/pyproject.toml" ] || [ -f "$proj/pytest.ini" ]; then
    COUNT=$(cd "$proj" && pytest --collect-only -q 2>/dev/null | tail -1)
    echo "$proj: $COUNT"
    # 提取数字累加...
  fi
done

echo ""
echo "=== 对比 ==="
echo "如果子项目测试数之和远大于根目录数，说明存在CI盲区！"
```

## 与现有模式的关系

| 关联模式 | 关系 |
|---------|------|
| [selective-testing-strategy.md](../code-patterns/selective-testing-strategy.md) | 选择性测试策略是修复方案B/C的具体实现方法 |
| [release-gate-automated-verification.md](release-gate-automated-verification.md) | 发布门禁自动化验证确保所有测试在发布前必须通过 |
| [ci-integration-three-interface.md](../code-patterns/ci-integration-three-interface.md) | CI集成三接口模式可用于统一测试入口设计 |
