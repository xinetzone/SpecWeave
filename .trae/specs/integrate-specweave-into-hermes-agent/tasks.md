# 将 SpecWeave 工作区集成到 Hermes Agent 的技术指导文档 - 实施计划

> **方法论**：seven-concepts 知识沉淀场景（R→I→E→V→C）。本计划聚焦 E（萃取知识文档）+ C（原子提交），质量门 G3（模式可迁移）与 G4（行动项原子化）。
> **产出定位**：技术指导文档（Wiki），非源码改动。

## 任务分解

### [x] Task 1: 盘点 SpecWeave 能力体系（作为集成内容的事实基础）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 读取 AGENTS.md、.agents/capability-registry.md、skills/README.md、commands/README.md、scripts/README.md、roles/README.md
  - 盘点真实可暴露的能力：skills 门面、commands（7+）、scripts（25+）、roles（7）、knowledge 知识库、vendor 子模块技能
  - 输出一份"SpecWeave 能力清单"作为后续映射矩阵的事实基础（可放入 01 章节或单独 facts 文件）
- **Acceptance Criteria**: AC-4
- **Test Requirements**:
  - `programmatic` TR-1.1: 盘点覆盖 skills/commands/scripts/roles/AGENTS.md/knowledge/vendor
  - `human-judgement` TR-1.2: 盘点基于仓库真实目录，不虚构

### [x] Task 2: 创建 hermes-agent-integration 目录骨架与 README
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/` 下创建目录
  - 创建 README.md：YAML frontmatter + 定位说明（把 SpecWeave 接入 Hermes 的实战指导）+ 章节索引表 + 阅读路径 + 与 hermes-okf-wiki/okf-wiki 的关系 + 相关资源
  - frontmatter 使用 YAML（--- 分隔），遵循现有原子化 wiki 格式
- **Acceptance Criteria**: AC-1, AC-2, AC-10
- **Test Requirements**:
  - `programmatic` TR-2.1: 目录与 README.md 存在于正确路径
  - `programmatic` TR-2.2: frontmatter 使用 YAML 格式且包含必填字段
  - `human-judgement` TR-2.3: README 含章节索引表与阅读路径

### [x] Task 3: 编写 00-overview（集成总览与两条路径）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 集成目标：使 Hermes 正确识别、调用、执行 SpecWeave 功能
  - 两条路径总览：(1) Hermes Agent 框架插件（tools/skills/memory/context），(2) Hermes OKF 记忆层挂接
  - 章节导航表 + 阅读路径 + 前置知识（交叉引用 hermes-okf-wiki / okf-wiki）
- **Acceptance Criteria**: AC-1, AC-3, AC-10
- **Test Requirements**:
  - `human-judgement` TR-3.1: 清晰说明两条集成路径
  - `human-judgement` TR-3.2: 章节导航表完整
  - `human-judgement` TR-3.3: 前置知识交叉引用正确

### [x] Task 4: 编写 01-hermes-plugin-interface（Hermes Agent 插件接口规范）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 插件三类：通用插件（General）/ 内存插件（Memory Provider）/ 上下文插件（Context Engine）
  - 发现路径：官方内置 /plugins → ~/.hermes/plugins → ./.hermes/plugins → Pip 插件入口点（后加载覆盖）
  - 启用机制：默认禁用，plugins.enabled 允许列表
  - plugin.yaml 字段（name/version/description/manifest_version）
  - register(ctx) API（register_tool 等）与 tool schema（JSON Schema）
  - 插件目录结构（plugin.yaml + __init__.py + schemas.py + tools.py）
- **Acceptance Criteria**: AC-3
- **Test Requirements**:
  - `human-judgement` TR-4.1: 插件三类阐述清晰
  - `human-judgement` TR-4.2: 发现路径/启用机制完整
  - `human-judgement` TR-4.3: plugin.yaml / register(ctx) / tool schema 示例完整

### [x] Task 5: 编写 02-capability-mapping（SpecWeave 能力盘点与映射矩阵）
- **Priority**: high
- **Depends On**: Task 1, Task 4
- **Description**:
  - SpecWeave 能力清单（来自 Task 1）
  - 映射矩阵：skills/commands/scripts/roles/AGENTS.md → Hermes tool / skill / hook / memory provider / context engine
  - 每个映射给出理由（如 commands/insight → 工具函数；scripts/check-links.py → 工具；AGENTS.md 契约 → 系统提示/hook）
  - 说明哪些能力适合直接暴露、哪些需封装、哪些不适合（如角色仅作 prompt）
- **Acceptance Criteria**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-5.1: 映射矩阵覆盖 skills/commands/scripts/roles/AGENTS.md
  - `human-judgement` TR-5.2: 每个映射有合理理由

### [x] Task 6: 编写 03-configuration（配置文件设置）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - `~/.hermes/config.yaml`：plugins.enabled / disabled / memory.provider / context_engine
  - HERMES_HOME 环境变量
  - project 级 `./.hermes/plugins` 与权限开启
  - hermes-okf install-plugin 自动写入的字段
  - 配置示例（含注释）
- **Acceptance Criteria**: AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: 覆盖 plugins.enabled/disabled/memory.provider/context_engine/HERMES_HOME
  - `human-judgement` TR-6.2: 配置示例完整可复制

### [x] Task 7: 编写 04-data-conversion（数据格式转换方法）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - AGENTS.md 契约 → plugin.yaml + register(ctx) 的转换路径
  - 知识库 markdown → OKF concept/bundle 的转换（frontmatter 对齐 / concept / bundle 路径）
  - tool schema（JSON Schema）定义方法
  - 转换前后的结构对照示例
- **Acceptance Criteria**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-7.1: AGENTS.md → plugin 转换路径清晰
  - `human-judgement` TR-7.2: 知识库 md → OKF concept/bundle 转换清晰
  - `human-judgement` TR-7.3: tool schema 定义示例完整

### [x] Task 8: 编写 05-auth-permission（权限认证流程）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 插件 name 消毒（拒绝 / \ .. 路径穿越，路径校验在 ~/.hermes/plugins 内）
  - manifest_version 校验（过高则拒绝安装并提示更新）
  - HERMES_HOME 目录隔离
  - API key 环境变量（如 model provider、zhihu 等）
  - project 插件权限开启流程
  - security 警告（http/file scheme）
- **Acceptance Criteria**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-8.1: name 消毒/路径安全阐述
  - `human-judgement` TR-8.2: manifest_version/环境变量/权限开启流程完整

### [x] Task 9: 编写 06-usage-examples（调用方式示例）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - `hermes plugins install owner/repo [--enable]` / update / remove / list
  - `hermes plugins enable/disable`
  - hermes-okf：install-plugin / validate-config / memory setup / `hermes okf search|list|show|snapshot|restore`
  - Hermes 会话内工具调用示例
  - with_context 记忆召回示例
  - 端到端流程示例（安装插件 → 启用 → 调用工具 → 记忆持久化）
- **Acceptance Criteria**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-9.1: 覆盖 plugins install/update/remove/list/enable/disable
  - `human-judgement` TR-9.2: 覆盖 hermes okf 关键命令
  - `human-judgement` TR-9.3: 会话内工具调用与 with_context 召回示例完整

### [x] Task 10: 编写 07-troubleshooting（常见问题及解决方案）
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 插件未发现（路径/HERMES_HOME/权限）
  - 插件未启用（不在 plugins.enabled）
  - tool schema 不匹配（模型无法调用）
  - Memory Provider 单实例限制
  - Windows 路径问题
  - name 冲突（后加载覆盖）
  - 修改后未 restart 生效
  - 每个问题：现象 / 原因 / 解决方案
- **Acceptance Criteria**: AC-9
- **Test Requirements**:
  - `human-judgement` TR-10.1: 覆盖未发现/未启用/schema/provider 单实例/Windows/name 冲突/restart
  - `human-judgement` TR-10.2: 每个问题含现象/原因/解决

### [x] Task 11: 全量验证（链接 + 格式 + 命名 + AC 覆盖）
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 运行 `python .agents/scripts/check-links.py` 验证交叉链接
  - 检查所有章节 frontmatter 合规（YAML、必填字段）
  - 检查命名规范（kebab-case）
  - 核对 10 个 AC 满足情况
  - 检查与 hermes-okf-wiki / okf-wiki 的交叉引用指向存在文件
- **Acceptance Criteria**: AC-1 ~ AC-10
- **Test Requirements**:
  - `programmatic` TR-11.1: 链接检查通过（无断链）
  - `programmatic` TR-11.2: 命名规范通过
  - `human-judgement` TR-11.3: 全部 AC 满足

# Task Dependencies
- Task 1（能力盘点）无前置，可最先执行
- Task 2 依赖 Task 1；Task 3 依赖 Task 2；Task 4 依赖 Task 3；Task 5 依赖 Task 1 + Task 4
- Task 6 → Task 7 → Task 8 → Task 9 → Task 10 串行依赖
- Task 11（验证）依赖所有前序任务
- 并行优化：Task 1（盘点）与 Task 2/3 可部分并行，但为保证内容一致建议按序执行

# 质量门记录（seven-concepts G3/G4）
- **G3（模式可迁移）**：产出为可复用的"把 AGENTS.md + .agents 能力体系接入 Hermes Agent"技术指导，含触发场景、核心步骤、反模式（如"把角色误当工具暴露"）、迁移验证（可复制到其他 Agent 宿主）
- **G4（行动项原子化）**：每个章节单一职责、可独立验证、有明确验收标准；最终通过原子提交交付
