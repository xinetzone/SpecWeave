# Anything OKF Wiki 生成 - Implementation Plan

## Phase R: 事实采集（Retrospective）

### Task 1: CLI-Anything 源码深度阅读与事实采集
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 阅读 `external/libs/ai/Anything/CLI-Anything/` 核心源码：
    - `cli-anything-plugin/cli_anything_plugin/` 目录：`skill_generator.py`、`repl_skin.py`、`preview_bundle.py`、`skill_bundle.py`、`cli.py`
    - `cli-anything-plugin/HARNESS.md`：7阶段方法论
    - `cli-hub/cli_hub/` 目录：`cli.py`、`installer.py`、`registry.py`、`matrix.py`、`matrix_skill.py`、`preview.py`、`analytics.py`、`config.py`、`preflight.py`、`upgrade.py`
    - `skill_generation/` 目录：测试辅助代码
    - 一个代表性 Harness（如 `gimp/agent-harness/` 或 `blender/agent-harness/`）作为生成产物样本
    - 平台适配层：`cursor-plugin/`、`codex-skill/`、`claude-plugin/` 目录结构与核心文件
  - 在 `projects/awesome-okf-xs/bundles/ai-agent/cli-anything/spec/` 下生成 `facts.md`
  - facts.md 包含：编号事实（F-xxx，每条带源码路径+行号）、API 表（类/方法/函数签名+定义位置+信源）、目录结构清单、依赖关系
  - 零推测原则：只记录可验证事实，不包含"用于"/"目的是"等推断性表述
- **Acceptance Criteria Addressed**: R5（API 真实性基础）
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 中每条事实包含源码路径引用
  - `rule` TR-1.2: API 表中每个类/方法/函数签名可通过源码 Grep 验证（抽检 ≥15 个）
  - `rule` TR-1.3: 无推断性表述（grep "用于\|目的是\|设计为" in facts.md 结果为 0）
- **Notes**: CLI-Hub 是独立的 Python 包（setup.py 存在），与 cli-anything-plugin 并列

### Task 2: anywidget 源码深度阅读与事实采集
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 阅读 `external/libs/ai/Anything/anywidget/` 核心源码：
    - `anywidget/` Python 包：`widget.py`、`_descriptor.py`、`_protocols.py`、`_traits.py`、`_file_contents.py`、`_util.py`、`_cellmagic.py`、`experimental.py`、`_version.py`、`_serve.py`
    - `packages/` JS 包：重点 `types/src/`（类型定义）、`anywidget/src/`（核心 JS）、`vite/`（构建集成）；react/svelte/vue/signals 仅登记信源
    - `tests/`：测试文件辅助理解 API 用法
  - 在 `projects/awesome-okf-xs/bundles/jupyter/anywidget/spec/` 下生成 `facts.md`
  - facts.md 包含：编号事实、API 表、ESM 协议细节、Trait 同步机制、HMR 实现路径
- **Acceptance Criteria Addressed**: R5（API 真实性基础）
- **Test Requirements**:
  - `rule` TR-2.1: facts.md 中每条事实包含源码路径引用
  - `rule` TR-2.2: API 表中每个类/方法/函数签名可通过源码 Grep 验证（抽检 ≥15 个）
  - `rule` TR-2.3: 无推断性表述

## Phase I: 架构洞察（Insight）

### Task 3: CLI-Anything 架构洞察与知识地图设计
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 facts.md 提炼 3-5 个核心架构洞察（陈述+证据+反常识+行动四元组）
  - 设计知识地图：确定概念文档清单（8-10 个核心概念）、示例文档清单（2-4 个实践示例）、信源文档清单
  - 概念文档覆盖方向（初步）：
    1. 整体架构与7阶段管线
    2. ReplSkin 双语言外壳机制
    3. SkillGenerator 代码生成器
    4. PreviewBundle 预览系统
    5. CLI-Hub 包管理器与注册表
    6. Matrix 技能矩阵系统
    7. 多平台插件适配层
    8. 安全策略与防护机制
  - 示例文档方向：创建自定义 Harness、CLI-Hub 命令使用
  - 在 `spec/` 下生成 `insights.md`
- **Acceptance Criteria Addressed**: B1, B3
- **Test Requirements**:
  - `rule` TR-3.1: insights.md 包含 ≥3 个洞察，每个包含陈述+证据（指向 facts.md 编号）
  - `rubric` TR-3.2: 知识地图合理性；scale 0-2；anchors 0=路径混乱/1=基本合理/2=循序渐进；threshold ≥1.5；evidence=概念编号排序与依赖关系

### Task 4: anywidget 架构洞察与知识地图设计
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 基于 facts.md 提炼 3-5 个核心架构洞察
  - 设计知识地图：确定概念文档清单（6-8 个核心概念）、示例文档清单（2-3 个实践示例）、信源文档清单
  - 概念文档覆盖方向（初步）：
    1. 整体架构与 ESM 协议
    2. Widget 基类与生命周期
    3. Trait 同步与双向绑定
    4. 前端通信协议（custom messages）
    5. HMR 热更新机制
    6. 多前端框架桥接（React/Svelte/Vue）
  - 示例文档方向：创建 Counter Widget、双向绑定示例
  - 在 `spec/` 下生成 `insights.md`
- **Acceptance Criteria Addressed**: B1, B3
- **Test Requirements**:
  - `rule` TR-4.1: insights.md 包含 ≥3 个洞察
  - `rubric` TR-4.2: 知识地图合理性；threshold ≥1.5

## Phase E: 批量生成（Extraction）

### Task 5: CLI-Anything Bundle 目录与 references 信源生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建目录结构：`bundles/ai-agent/cli-anything/{concepts,examples,references,spec}`
  - 按 insights.md 的信源清单分批生成 references/ 文档（≤7 文件/批）：
    - repl-skin.md: ReplSkin 类源码级文档
    - skill-generator.md: SkillGenerator 类源码级文档
    - preview-bundle.md: PreviewBundle 预览机制
    - cli-hub.md: CLI-Hub 包管理器（installer/registry/matrix/analytics）
    - harness-methodology.md: 7阶段方法论（HARNESS.md 提炼）
    - plugin-adapters.md: 多平台插件适配
  - 每个 reference 文档包含源码级 API 文档（Grep 验证）
  - 生成 references/index.md（无 frontmatter，保留文件）
- **Acceptance Criteria Addressed**: R1, R3, R4
- **Test Requirements**:
  - `rule` TR-5.1: 目录结构符合 OKF v0.2
  - `rule` TR-5.2: 每个 reference .md 含有效 frontmatter（type: reference + title + sources）
  - `rule` TR-5.3: references/index.md 无 frontmatter

### Task 6: CLI-Anything concepts/ 分批生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 按 insights.md 知识地图分批生成 concepts/ 文档（≤7 文件/批）
  - 每个概念文档：编号命名（00-xxx.md, 01-xxx.md, ...），包含 YAML frontmatter（type: concept），含知识来源引用、代码示例、交叉链接
  - 概念覆盖：整体架构、ReplSkin、SkillGenerator、PreviewBundle、CLI-Hub、Matrix系统、插件适配、安全策略
  - 生成 concepts/index.md（无 frontmatter）
- **Acceptance Criteria Addressed**: R1, R3, R4, B1, B2, B4
- **Test Requirements**:
  - `rule` TR-6.1: 每个概念文档含 type: concept frontmatter + sources 指向 references/
  - `rule` TR-6.2: 代码块标注语言标识
  - `rubric` TR-6.3: 概念文档质量；scale 0-2；anchors 0=错误多/1=基本准确/2=透彻；threshold ≥1.5
  - `rubric` TR-6.4: API 覆盖度；scale 0-2；anchors 0=遗漏多/1=主要覆盖/2=全面；threshold ≥1.5

### Task 7: CLI-Anything examples/ 生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 生成 examples/ 文档（2-4 个实践示例）
  - 示例方向：创建自定义软件 Harness 端到端流程、CLI-Hub 常用命令操作、Skill 生成器使用
  - 每个示例文档：YAML frontmatter（type: example），含完整代码、步骤说明、sources 引用
  - 生成 examples/index.md（无 frontmatter）
- **Acceptance Criteria Addressed**: R1, R3, R4, B1
- **Test Requirements**:
  - `rule` TR-7.1: 每个示例文档含 type: example frontmatter + sources
  - `rule` TR-7.2: 代码块标注语言标识
  - `rubric` TR-7.3: 示例可操作性；threshold ≥1.5

### Task 8: CLI-Anything index.md 与 log.md 生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 最后生成 bundle 根 `index.md`：包含 okf_version: "0.2" frontmatter、项目简介、知识地图、学习路径、信源清单、标签
  - 生成 `log.md`：记录变更日志（初始版本、日期、覆盖范围）
- **Acceptance Criteria Addressed**: R1, R6
- **Test Requirements**:
  - `rule` TR-8.1: index.md 含 okf_version: "0.2"
  - `rule` TR-8.2: 学习路径表格包含所有概念文档

### Task 9: anywidget Bundle 目录与 references 信源生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建目录结构：`bundles/jupyter/anywidget/{concepts,examples,references,spec}`
  - 分批生成 references/ 文档（≤7 文件/批）：
    - widget-base.md: AnyWidget 基类源码级文档
    - traits.md: Trait 同步与数据绑定机制
    - esm-protocol.md: ESM 前端协议与通信
    - descriptor.md: Descriptor 与文件内容管理
    - hmr.md: HMR 热更新与开发服务器
    - framework-bridges.md: 多框架桥接概览
  - 生成 references/index.md（无 frontmatter）
- **Acceptance Criteria Addressed**: R2, R3, R4
- **Test Requirements**:
  - `rule` TR-9.1: 目录结构符合 OKF v0.2
  - `rule` TR-9.2: 每个 reference .md 含有效 frontmatter
  - `rule` TR-9.3: references/index.md 无 frontmatter

### Task 10: anywidget concepts/ 分批生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 按知识地图分批生成 concepts/ 文档（≤7 文件/批）
  - 概念覆盖：整体架构、Widget 基类、Trait 同步、ESM 协议、HMR、框架桥接
  - 生成 concepts/index.md（无 frontmatter）
- **Acceptance Criteria Addressed**: R2, R3, R4, B1, B2, B4
- **Test Requirements**:
  - `rule` TR-10.1: 每个概念文档含 type: concept frontmatter + sources
  - `rule` TR-10.2: 代码块标注语言标识
  - `rubric` TR-10.3: 概念文档质量；threshold ≥1.5
  - `rubric` TR-10.4: API 覆盖度；threshold ≥1.5

### Task 11: anywidget examples/ 生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 生成 examples/ 文档（2-3 个实践示例）
  - 示例方向：Counter Widget 入门、双向绑定高级用法、Vite 集成开发
  - 每个示例文档：YAML frontmatter（type: example）
  - 生成 examples/index.md（无 frontmatter）
- **Acceptance Criteria Addressed**: R2, R3, R4, B1
- **Test Requirements**:
  - `rule` TR-11.1: 每个示例文档含 type: example frontmatter + sources
  - `rubric` TR-11.2: 示例可操作性；threshold ≥1.5

### Task 12: anywidget index.md 与 log.md 生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 最后生成 bundle 根 `index.md`：okf_version: "0.2"、项目简介、知识地图、学习路径
  - 生成 `log.md`
- **Acceptance Criteria Addressed**: R2, R6
- **Test Requirements**:
  - `rule` TR-12.1: index.md 含 okf_version: "0.2"
  - `rule` TR-12.2: 学习路径表格包含所有概念文档

## Phase V: 独立验证（Verification）

### Task 13: 结构与 Frontmatter 检查
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8, Task 12
- **Description**:
  - 验证两个 bundle 的目录结构完整性（concepts/examples/references/index.md/log.md）
  - 验证所有非保留 .md 文件 YAML frontmatter 可解析且 type 非空
  - 验证子目录 index.md 无 frontmatter
  - 验证交叉引用路径格式（`/` 开头，无 `../`）
  - 验证代码块语言标识
- **Acceptance Criteria Addressed**: R1, R2, R3, R6, R7, R8, R9
- **Test Requirements**:
  - `rule` TR-13.1: 两个 bundle 目录结构完整（所有必需目录和文件存在）
  - `rule` TR-13.2: 所有 .md 文件 frontmatter 检查通过（0 错误）
  - `rule` TR-13.3: 无 `../` 交叉引用路径
  - `rule` TR-13.4: 所有代码块有语言标识

### Task 14: Grep 级 API 真实性验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8, Task 12
- **Description**:
  - 对两个 bundle 的概念和示例文档，抽检 ≥15 个 API 引用（类名/方法名/函数名）
  - 使用 Grep 在源码目录中验证每个 API 的存在性（精确匹配类定义/函数定义/方法定义）
  - 记录验证结果，标记虚构 API（必须为 0）
  - 对发现的虚构 API 立即修复文档
- **Acceptance Criteria Addressed**: R5, R12
- **Test Requirements**:
  - `rule` TR-14.1: CLI-Anything 抽检 ≥15 个 API，全部在源码中可验证
  - `rule` TR-14.2: anywidget 抽检 ≥15 个 API，全部在源码中可验证
  - `rule` TR-14.3: 虚构 API 数量为 0
  - `rule` TR-14.4: 验证报告写入 spec/verify.md

### Task 15: 链接验证与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 13, Task 14
- **Description**:
  - 验证两个 bundle 内所有交叉引用指向存在的文件
  - 验证 sources 字段中引用的 references/ 文件存在
  - 修复所有断链
- **Acceptance Criteria Addressed**: R4
- **Test Requirements**:
  - `rule` TR-15.1: 所有交叉引用指向存在文件（0 断链）
  - `rule` TR-15.2: 所有 sources 字段引用存在

## Phase C: 配置更新（Configuration）

### Task 16: 更新分组索引
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 15
- **Description**:
  - 更新 `bundles/ai-agent/index.md`：在学习路径表和详情表中添加 cli-anything 条目，更新统计数字
  - 更新 `bundles/jupyter/index.md`：在学习路径表和详情表中添加 anywidget 条目，更新统计数字
- **Acceptance Criteria Addressed**: R10
- **Test Requirements**:
  - `rule` TR-16.1: ai-agent/index.md 包含 cli-anything 条目且链接正确
  - `rule` TR-16.2: jupyter/index.md 包含 anywidget 条目且链接正确
  - `rule` TR-16.3: 统计数字（项目数/概念数/示例数）更新准确

### Task 17: 更新总索引
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 16
- **Description**:
  - 更新 `bundles/index.md`：
    - 更新统计数字（44→46 bundles，11→11 groups 等）
    - 在分组导航表中确认 ai-agent 和 jupyter 数字更新
    - 在详情表中添加 cli-anything 和 anywidget 行
    - 更新生态关系图（如有）
- **Acceptance Criteria Addressed**: R11
- **Test Requirements**:
  - `rule` TR-17.1: bundles/index.md 统计数字更新准确
  - `rule` TR-17.2: 详情表包含两个新 bundle 条目且链接正确
