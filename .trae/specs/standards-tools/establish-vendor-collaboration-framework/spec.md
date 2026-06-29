---
version: 1.0
---

# Vendor 外部项目协同框架 - Product Requirement Document

## Overview

- **Summary**: 为 `vendor/flexloop`（AgentForge 项目，已通过 git submodule 引入）与 SpecWeave 主项目之间建立一套完整的协同工作框架，涵盖接口规范、版本控制策略、自动化集成流程、独立测试环境、更新同步机制和边界划分原则，确保两个独立代码库在高效协同的同时保持文件结构独立、无代码冲突、无依赖混乱。
- **Purpose**: 当前 flexloop 已作为 git 子模块存在于 vendor/ 目录下，但缺乏明确的集成规范和自动化机制，存在以下风险：跨边界代码修改、版本不同步、依赖关系混乱、测试环境污染、子模块更新破坏主项目稳定性。需要建立一套可复用的 vendor 子模块协同框架，不仅解决 flexloop 集成问题，也为未来引入其他 vendor 依赖提供标准范式。
- **Target Users**: SpecWeave 项目的 AI 智能体（orchestrator、developer、reviewer、tester）以及人类维护者。

## Goals

- 定义 SpecWeave 与 vendor/flexloop 之间清晰的接口规范和交互模式
- 建立基于 git submodule 的版本控制策略，锁定版本与可控更新
- 实现自动化集成验证流程，确保子模块更新不破坏主项目
- 建立隔离的测试环境，防止两个项目的依赖和测试互相污染
- 制定子模块更新与双向同步机制（规范模式的萃取与回流）
- 明确代码边界划分原则，禁止跨边界直接修改
- 完善 vendor/ 元数据文档，确保依赖信息可追溯
- 提供可复用的 vendor 协同标准，为未来引入其他外部项目提供模板

## Non-Goals (Out of Scope)

- 不将 flexloop/AgentForge 的源码合并进 SpecWeave 主仓库（保持 git submodule 方式）
- 不修改 flexloop/AgentForge 上游代码（所有定制化通过外部适配层实现）
- 不让 flexloop 反向依赖 SpecWeave（依赖方向严格单向：SpecWeave → flexloop）
- 不将 flexloop 作为 Python 包安装到主项目的运行时依赖中（仅作为规范参考和脚本复用来源）
- 不重构 flexloop/AgentForge 的内部架构或代码风格
- 不为 flexloop 建立独立的 CI/CD 流水线（使用其上游已有的 CI）
- 不同步两个项目的 `.agents/` 规则体系（各自维护独立的规则集，通过萃取机制参考）

## Background & Context

- **现有状态**: `vendor/flexloop` 已通过 `git submodule add` 引入，指向 `git@gitcode.com:flexloop/flexloop.git`；`.gitignore` 已正确配置白名单；`vendor/README.md` 和 `vendor/VERSION.md` 已创建但元数据不完整（缺少版本号、引入日期、许可证、具体用途等详细信息）。
- **flexloop 本质**: 即 AgentForge 项目（原 tao/taolib），是一个完整的 AI Agent 协作基础设施，拥有自己的 AGENTS.md 全局契约、`.agents/` 规范体系（25+ 验证脚本、双角色体系、world CLI）、Python 包（taolib）、独立 CI/CD 流水线和文档体系。
- **当前引用关系**: SpecWeave 仅在文档层面引用 flexloop——作为规范体系的"落地案例"展示（见 [agentforge-adoption.md](file:///d:/spaces/SpecWeave/.agents/cases/agentforge-adoption.md)），尚无代码层面的导入或脚本调用。
- **两个项目的关系**: SpecWeave 是元规范框架（定义 AGENTS.md 标准和协作协议），flexloop/AgentForge 是该框架的完整落地实现和超集扩展（拥有更多角色、脚本、工具）。两者是"规范-实现"关系，而非"父子"或"主从"关系。
- **技术约束**: 两个项目均使用 Python；SpecWeave 使用标准 venv/PDM 风格，flexloop 使用 `uv`；SpecWeave 脚本在 `.agents/scripts/`，flexloop 脚本在 `apps/chaos/.agents/scripts/`；两者都有自己的 `.gitignore`、`pyproject.toml` 等配置。
- **vendor 管理现状**: 项目已有 [dependency-management.md](file:///d:/spaces/SpecWeave/.agents/protocols/dependency-management.md) 定义 vendor 基础规范，已有 `check-vendor.py`（实际为 `repo-check.py vendor` 的包装）做基础合规检查，但缺少针对 git submodule 类型依赖的深度集成规范。

## Functional Requirements

- **FR-1**: 定义边界划分原则文档，明确哪些目录/文件属于 SpecWeave 主权范围、哪些属于 flexloop 主权范围、哪些是交互接口层
- **FR-2**: 定义交互接口规范，包括：文档引用格式、脚本复用方式、模式萃取流程、禁止的交互模式
- **FR-3**: 完善 vendor/flexloop 的元数据文档（README.md），包含版本号、来源地址、引入日期、用途说明、许可证、集成方式、更新记录
- **FR-4**: 更新 vendor/VERSION.md，记录 flexloop 的当前 submodule commit、版本标签、更新时间
- **FR-5**: 建立版本控制策略文档，定义：submodule 锁定策略（固定 commit vs 跟踪分支）、版本升级流程、回滚机制、版本兼容性要求
- **FR-6**: 实现集成验证脚本 `check-vendor-integration.py`，自动化检查：submodule 状态、边界违规（跨边界修改检测）、引用完整性、元数据完整性
- **FR-7**: 定义独立测试环境规范，确保两个项目的测试运行互不干扰，包括：测试路径隔离、依赖环境隔离、测试数据隔离
- **FR-8**: 建立子模块更新流程文档和辅助脚本，包括：更新前检查、更新执行、更新后验证、提交规范
- **FR-9**: 定义双向同步机制——从 flexloop 萃取优秀模式/脚本到 SpecWeave 的规范流程，以及 SpecWeave 规范更新向 flexloop 反馈的建议路径
- **FR-10**: 更新 [dependency-management.md](file:///d:/spaces/SpecWeave/.agents/protocols/dependency-management.md) 协议，补充 git submodule 类型依赖的管理规范章节
- **FR-11**: 更新 .agents/scripts/repo-check.py（或其 vendor 子模块），增强对 git submodule 的检查能力（未初始化检查、commit 固定检查、脏工作树检测）
- **FR-12**: 编写 VENDOR-INTEGRATION.md 协同指南，作为人类维护者和 AI 智能体的操作手册

## Non-Functional Requirements

- **NFR-1**: 集成验证脚本单次运行时间不超过 10 秒
- **NFR-2**: 所有自动化检查可通过 CI 流水线执行，无需人工干预
- **NFR-3**: 边界规则必须可程序化检测，不能仅靠文档约定
- **NFR-4**: 框架设计必须具备可扩展性，未来新增其他 vendor 子模块时可复用同一套机制
- **NFR-5**: 所有文档和脚本使用中文编写，与项目现有语言风格一致
- **NFR-6**: 子模块更新流程必须具备原子性——要么全部验证通过后提交，要么回滚到更新前状态
- **NFR-7**: 集成框架不应增加 SpecWeave 主项目的运行时依赖（不安装 flexloop 的 taolib 包到主环境）

## Constraints

- **Technical**:
  - 必须使用 git submodule 机制（不切换为 npm/pip 包或其他方式）
  - Python 环境隔离：SpecWeave 使用项目根目录的 `.venv`，flexloop 使用 `apps/chaos/` 下自己的 uv 环境
  - 脚本语言以 Python 为主，PowerShell 辅助（Windows 环境）
  - 必须兼容现有的 `repo-check.py` 验证框架
- **Business**:
  - flexloop 的上游仓库在 gitcode.com，可能存在网络访问限制
  - 两个项目独立发展，不能假设上游会同步采纳 SpecWeave 的变更
- **Dependencies**:
  - Git 命令行工具（submodule 操作）
  - Python 3.x（脚本运行）
  - 现有的 `.agents/scripts/lib/` 共享工具库

## Assumptions

- flexloop 上游仓库保持可访问性（通过 SSH 或 HTTPS）
- 不需要在 SpecWeave 中直接 import taolib 模块（仅在需要独立运行 flexloop 脚本时使用其自有环境）
- 两个项目之间的交互主要是"参考"和"复用"关系，而非运行时调用关系
- vendor/flexloop 目录中不会有 SpecWeave 侧的未提交本地修改（所有修改应提交到上游或通过外部适配层实现）
- 未来可能引入更多 vendor 子模块，框架需要具备通用性

## Acceptance Criteria

### AC-1: 边界划分原则明确
- **Given**: 两个独立代码库（SpecWeave 根目录和 vendor/flexloop/）
- **When**: AI 智能体或人类开发者执行涉及 vendor 目录的任务
- **Then**: 有明确的边界文档说明哪些区域属于各自主权范围、哪些是接口层，且边界规则可被自动化脚本检测
- **Verification**: `programmatic`
- **Notes**: 边界文档应包含目录树标注和违规检测规则

### AC-2: 元数据完整
- **Given**: vendor/flexloop 作为 git submodule 存在
- **When**: 运行 vendor 合规检查
- **Then**: vendor/flexloop/README.md 包含所有必需字段（名称、版本、来源、引入日期、用途、许可证、集成方式），vendor/VERSION.md 记录当前 commit 哈希
- **Verification**: `programmatic`

### AC-3: 版本控制策略文档化
- **Given**: 需要更新或检查 flexloop 版本
- **When**: 开发者执行子模块更新操作
- **Then**: 有清晰的版本策略文档说明锁定方式、升级流程、兼容性要求、回滚步骤，且有辅助脚本支持安全更新
- **Verification**: `human-judgment`

### AC-4: 集成验证脚本可运行
- **Given**: 项目已配置 vendor/flexloop 子模块
- **When**: 运行 `python .agents/scripts/check-vendor-integration.py`
- **Then**: 脚本检测 submodule 初始化状态、工作树清洁度、元数据完整性、边界违规情况，输出结构化报告，无报错
- **Verification**: `programmatic`

### AC-5: 跨边界修改被阻止
- **Given**: 自动化检查已配置
- **When**: 有人（或 AI）在 vendor/flexloop/ 目录内创建/修改文件并尝试提交到 SpecWeave 仓库
- **Then**: 检查脚本识别到 vendor/ 内的非 submodule 变更是违规的（除元数据文件外），CI 检查失败
- **Verification**: `programmatic`

### AC-6: 测试环境隔离
- **Given**: 两个项目都有测试套件
- **When**: 在 SpecWeave 根目录运行测试
- **Then**: 测试不会执行 vendor/flexloop 内的测试用例，不会引用 vendor 内的 Python 包，不会污染 flexloop 的测试环境
- **Verification**: `programmatic`

### AC-7: 子模块更新流程可操作
- **Given**: flexloop 上游有新版本
- **When**: 维护者决定更新 submodule
- **Then**: 按照文档化流程执行更新，包含更新前检查、更新、集成验证、提交四个步骤，每步有明确的命令和验证点
- **Verification**: `human-judgment`

### AC-8: 模式萃取流程文档化
- **Given**: flexloop 中有值得 SpecWeave 借鉴的优秀模式/脚本/规则
- **When**: 开发者需要萃取这些模式到 SpecWeave
- **Then**: 有标准化的萃取流程文档指导操作，确保萃取后的内容适配 SpecWeave 规范并标注来源
- **Verification**: `human-judgment`

### AC-9: 协同指南完整
- **Given**: 新开发者或 AI 智能体需要理解如何与 vendor/flexloop 协同
- **When**: 查阅 VENDOR-INTEGRATION.md
- **Then**: 文档包含快速入门、常见操作、禁忌事项、故障排查，可独立引导用户完成基本协同操作
- **Verification**: `human-judgment`

### AC-10: dependency-management 协议补充完善
- **Given**: 现有 dependency-management.md 协议
- **When**: 查阅 vendor 管理规范
- **Then**: 协议包含 git submodule 类型依赖的专门章节，与现有手动管理依赖的规范形成互补
- **Verification**: `human-judgment`

## Open Questions

- [ ] flexloop 的版本同步策略：是固定在某个稳定 commit 上，还是定期（如每周）跟踪上游 main 分支？
- [ ] 是否需要在 SpecWeave 的 CI 中加入 flexloop submodule 的完整性检查（防止 submodule 未初始化导致构建失败）？
- [ ] 模式萃取的方向：是双向的（SpecWeave ↔ flexloop）还是仅单向（flexloop → SpecWeave）？考虑到 flexloop 是超集实现，可能以单向萃取为主。
- [ ] 未来是否可能有更多 vendor 子模块？如果有，框架需要抽象到何种程度？
- [ ] 是否需要一个 vendor 状态看板（类似 .trae/specs/ 的执行看板）来追踪所有 vendor 依赖的版本状态和健康状况？
