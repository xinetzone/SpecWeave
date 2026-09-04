---
version: 1.0
---

# seven-concepts-cmd 三层分离重构 - Product Requirement Document

## Overview
- **Summary**: 将单文件脚本 `seven-concepts-trigger.py`（377行）按照「三层分离·渐进迁移」模式重构为标准 `lib/seven_concepts/` 模块，拆分领域层（纯逻辑）、渲染层（纯格式化）、平台层（薄CLI壳），核心匹配逻辑可被Python直接import复用。
- **Purpose**: 解决当前单文件耦合导致的无法单元测试、无法被其他脚本/MCP/Skill直接调用、测试必须通过subprocess黑盒执行等问题。重构后对齐项目 lib/ 下成熟模块（如 check_hardcode、link_fixer）的组织规范。
- **Target Users**: AI Agent（通过Skill/MCP调用）、开发者（通过CLI调用）、其他自动化脚本（通过import调用）

## Goals
- 将核心匹配逻辑（match_task）与CLI/IO解耦，成为可import的纯函数
- 拆分后CLI入口脚本 < 100行，保持命令行接口100%向后兼容
- 可以编写不依赖subprocess的单元测试直接测试匹配逻辑
- 对齐项目现有 lib/ 模块目录结构规范
- 现有19个黑盒测试用例全部通过，零回归

## Non-Goals (Out of Scope)
- 不修改匹配规则本身（match_task中的关键词/置信度/工作流定义原样迁移）
- 不新增功能（JSON输出、MCP集成、文档自动生成等留待阶段2）
- 不重构项目中其他脚本或模块
- 不改变任何命令行参数的行为或输出格式（等价重构）

## Background & Context
- 当前 `seven-concepts-trigger.py` 是377行单文件脚本，常量、数据模型、匹配算法、输出格式化、argparse CLI 全部耦合在一起
- 项目已有成熟的模块组织规范：lib/check_hardcode/、lib/link_fixer/ 等均采用 models/scanner/cli 分层结构
- 本次重构基于知识沉淀的「三层分离·渐进迁移」模式：领域层（零IO纯逻辑）→ 渲染层（纯格式化）→ 平台层（薄CLI壳）
- 重构遵循项目 lib/README.md 的"新增脚本开发流程"规范

## Functional Requirements
- **FR-1**: 领域层纯函数 `match_task(text: str) -> list[MatchResult]` 可被任何Python代码import调用，无IO副作用
- **FR-2**: 数据模型 MatchResult、常量 CONCEPTS/WORKFLOWS/QUALITY_GATES 可独立导入
- **FR-3**: 格式化函数不直接调用print，返回字符串/数据结构
- **FR-4**: CLI入口脚本保留原文件名 seven-concepts-trigger.py，命令行参数/输出格式完全兼容
- **FR-5**: 提供清晰的 `__init__.py` 公开API导出

## Non-Functional Requirements
- **NFR-1**: 领域层所有模块可在纯Python环境下import，不依赖argparse/sys/IO
- **NFR-2**: CLI入口脚本行数 < 100行
- **NFR-3**: 重构后所有现有测试用例100%通过
- **NFR-4**: 不引入任何新的第三方依赖
- **NFR-5**: 新增的单元测试直接import领域层，无需subprocess，执行速度提升10倍以上

## Constraints
- **Technical**: Python标准库 + 项目现有lib.cli共享工具；遵循现有代码风格（typer+dataclass偏好）
- **Business**: 等价重构，不破坏现有调用者（test-seven-concepts-trigger.py黑盒测试必须通过）
- **Dependencies**: 依赖项目现有 lib.project、lib.cli 等共享工具

## Assumptions
- 现有 match_task() 函数逻辑是正确的，本次重构不修改匹配规则
- 项目 lib/ 下的模块结构是经过验证的最佳实践，本次重构对齐该结构
- 输出格式的细微不影响功能的差异（如末尾空行）可接受，但核心字段必须一致

## Acceptance Criteria

### AC-1: 领域层零IO可导入
- **Given**: 一个纯Python环境（无sys.argv、无stdout捕获）
- **When**: 执行 `from lib.seven_concepts import match_task, MatchResult, CONCEPTS, WORKFLOWS`
- **Then**: import成功，不产生任何stdout/stderr输出，不触发任何文件读写或网络请求
- **Verification**: `programmatic`

### AC-2: 核心匹配逻辑纯函数等价
- **Given**: 相同的任务描述文本输入
- **When**: 分别调用重构前的 match_task 和重构后的 lib.seven_concepts.match_task
- **Then**: 返回结果的 scenario/confidence/concepts/workflow/quality_gates/anti_patterns 字段完全一致
- **Verification**: `programmatic`

### AC-3: CLI向后兼容
- **Given**: 任意原有命令行调用方式（直接传任务描述、--top N、--list）
- **When**: 运行重构后的 seven-concepts-trigger.py
- **Then**: 输出格式包含原有所有核心字段（🎯场景、置信度、概念组合、参考流程、提示、质量门、反模式），exit code行为一致
- **Verification**: `programmatic`

### AC-4: 现有黑盒测试全部通过
- **Given**: 现有 test-seven-concepts-trigger.py 19个测试用例
- **When**: 运行 `python .agents/scripts/test-seven-concepts-trigger.py`
- **Then**: 准确率19/19=100%，exit code 0
- **Verification**: `programmatic`

### AC-5: 新增单元测试直接测试领域层
- **Given**: 新增 tests/test_seven_concepts_lib.py
- **When**: 运行该测试文件
- **Then**: 测试直接import lib.seven_concepts，不使用subprocess，覆盖主要场景匹配逻辑
- **Verification**: `programmatic`

### AC-6: 目录结构对齐项目规范
- **Given**: 重构后的代码布局
- **When**: 查看目录结构
- **Then**: 符合 lib/<module>/{__init__.py,constants.py,models.py,matcher.py,scenarios.py,formatters.py} + 根目录薄CLI入口的模式，对齐 lib/check_hardcode/ 等已有模块
- **Verification**: `human-judgment`

### AC-7: CLI入口脚本精简
- **Given**: 重构后的 seven-concepts-trigger.py
- **When**: 统计文件行数
- **Then**: 有效代码行数（不含空行/注释）< 100行
- **Verification**: `programmatic`

## Open Questions
- 无
