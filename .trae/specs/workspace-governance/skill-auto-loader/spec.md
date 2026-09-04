# Skill Auto Loader - 技能自动装载器 - Product Requirement Document

## Overview
- **Summary**: 创建一个技能自动装载器（`load-flexloop-skills`），能够扫描指定技能文件夹（默认 `vendor/flexloop/apps/chaos/.agents/skills/` 和 `.agents/skills/`），自动识别、解析、验证技能文件（SKILL.md），生成技能注册表（JSON + Markdown 报告），支持错误隔离与增量扫描。
- **Purpose**: 解决当前技能索引需要手动维护在 `vendor/AGENTS.md` 中的问题，实现技能自动发现、格式验证、冲突检测，新增技能无需手动更新索引表。
- **Target Users**: AI 智能体（启动时自动加载技能清单）、项目开发者（添加/修改技能后快速验证格式）、项目维护者（技能资产盘点）。

## Goals
- 自动扫描一个或多个技能目录，递归发现所有 SKILL.md 文件
- 解析 SKILL.md 的 YAML frontmatter，提取技能元数据（name, description, version, paths 等）
- 双模式验证（strict/relaxed）：检查必填字段缺失、格式错误、重复名称冲突
- 错误隔离：单个技能解析失败不中断整体流程，记录详细错误信息
- 生成两种输出：机器可读 JSON 注册表 + 人类可读 Markdown 汇总报告
- 增量扫描缓存：基于文件 mtime 避免重复解析未变更文件
- 只读操作：绝不写入 vendor 目录，所有输出放在主权区 `.agents/skills/load-flexloop-skills/` 或 `.temp/`
- 复用现有基础设施：`lib/frontmatter.py` 做 frontmatter 解析，`lib/check_skill_quality/` 做质量检查

## Non-Goals (Out of Scope)
- **不做 IDE 运行时动态装载**：Trae IDE 的 Skill 工具是内置机制，本技能不修改 IDE 行为，只生成注册表供 AI 参考
- **不复制 vendor 技能本体**：遵循跨边界调用规范，保持 vendor 内技能的单一可信源
- **不自动修复错误**：只报告错误，不自动修改 SKILL.md（修复留给开发者或其他 Skill）
- **不执行技能脚本**：只扫描和解析元数据，不运行技能的 scripts/ 内容
- **不处理 evals/benchmark**：不运行技能测试用例，只做静态扫描

## Background & Context
- 当前 flexloop vendor 子模块下有 9 个技能（archive-folder, asset-redundancy-analyzer, pdf-to-markdown, skill-creator, task-execution-summary, zhihu-* 等），需要手动在 `vendor/AGENTS.md` 维护索引表
- SpecWeave 主权区 `.agents/skills/` 下已有 ~20 个命令门面技能，没有统一的自动发现机制
- 项目已有成熟的基础设施：
  - `lib/frontmatter.py`：统一 YAML/TOML frontmatter 解析，支持 x-toml-ref 外部引用
  - `lib/check_skill_quality/`：技能质量检查框架（discovery, frontmatter checks, scoring）
  - `lib/cli.py`：公共 CLI 参数（typer + dataclass 风格）
- 用户偏好：Python 3.14+、typer + dataclass、YAML 配置、中文交流

## Functional Requirements
- **FR-1**: 支持多目录扫描，默认扫描两个目录：`vendor/flexloop/apps/chaos/.agents/skills/` 和 `.agents/skills/`，允许通过参数追加/覆盖
- **FR-2**: 递归发现所有子目录中的 SKILL.md 文件，排除 SKILL-TEMPLATE.md 和 .validate-skip 中列出的技能
- **FR-3**: 使用现有 `parse_frontmatter_unified()` 解析每个 SKILL.md 的 frontmatter，自动处理 YAML/TOML 格式和 x-toml-ref 外部引用
- **FR-4**: 双模式验证：
  - `strict` 模式：检查 name、description 必填，检查推荐章节存在性（I/O, Dependencies, Deployment, Error Handling, Changelog）
  - `relaxed` 模式：仅检查 name、description 必填（对齐 agentskills.io 标准）
- **FR-5**: 错误隔离与详细报告：捕获单个文件解析异常，记录错误类型、文件路径、错误消息、建议修复方式，继续处理其他文件
- **FR-6**: 冲突检测：检测重复的技能 name（跨目录同名冲突）、检测无效路径引用（paths 字段指向不存在的文件）
- **FR-7**: 增量扫描：缓存文件 mtime 和解析结果到 `.agents/cache/skill-registry-cache.json`，未变更文件跳过重新解析，支持 `--force` 全量重扫
- **FR-8**: 输出 JSON 注册表：包含扫描时间、扫描目录列表、成功加载的技能清单（含元数据、路径、状态）、失败清单、统计摘要
- **FR-9**: 输出 Markdown 报告：人类可读的技能汇总表（名称、描述、版本、状态、源目录）、错误清单、冲突警告
- **FR-10**: CLI 接口：使用 typer 构建命令行，支持 `--path`（追加扫描目录）、`--mode`（strict/relaxed）、`--force`（全量重扫）、`--output`（输出路径）、`--json-only`/`--md-only`（只输出一种格式）、`--verbose`（详细日志）
- **FR-11**: SKILL.md 门面：创建标准的 Skill 文档，包含触发词、使用示例、参数说明、输出格式说明

## Non-Functional Requirements
- **NFR-1**: 性能：当前约 30 个技能的全量扫描应在 1 秒内完成（不含磁盘 IO 等待）
- **NFR-2**: 可靠性：单个 SKILL.md 损坏（YAML 语法错误、编码错误、权限问题）不能导致整个扫描崩溃
- **NFR-3**: 安全性：只读扫描，绝不修改或删除任何被扫描目录中的文件（特别是 vendor/ 只读区）
- **NFR-4**: 兼容性：支持 Python 3.10+（与项目现有脚本一致，虽然用户偏好 py314，但共享库要求 py310 兼容）
- **NFR-5**: 可维护性：遵循项目现有代码风格（typer + dataclass），复用 lib/ 下现有工具，不重复造轮子
- **NFR-6**: 可测试性：核心逻辑（解析、验证、报告生成）模块化，支持单元测试；提供 tests/ 目录

## Constraints
- **Technical**:
  - 必须使用 Python，遵循项目现有代码风格（typer + dataclass）
  - 必须复用现有 `lib/frontmatter.py` 做 frontmatter 解析，不得重写 YAML 解析
  - 必须复用现有 `lib/check_skill_quality/discovery.py` 的文件发现逻辑（或在此基础上扩展）
  - 输出必须是 UTF-8 编码
- **Business**:
  - vendor/ 目录是 git submodule 只读区，绝对禁止写入
  - 新技能必须放在 `.agents/skills/load-flexloop-skills/`（SpecWeave 主权区）
- **Dependencies**:
  - Python 3.10+（共享库要求）
  - 项目现有 `lib/` 共享库（frontmatter, cli, cache 等）
  - typer（CLI 框架，项目已使用）

## Assumptions
- 所有 SKILL.md 都遵循 YAML frontmatter（---）格式，少数遗留 TOML（+++）frontmatter 已被 frontmatter.py 兼容处理
- 技能目录结构遵循规范：每个技能一个子目录，内含 SKILL.md，可选 scripts/、references/、tests/、evals/ 等
- 用户在项目根目录运行命令，相对路径都是相对于项目根
- 不需要网络访问（纯本地文件扫描）

## Acceptance Criteria

### AC-1: 多目录扫描发现所有技能
- **Given**: 默认配置（不指定额外路径）
- **When**: 运行技能扫描器
- **Then**: 能发现 vendor/flexloop 和 .agents/skills/ 下所有 SKILL.md 文件（排除 SKILL-TEMPLATE.md），数量与实际一致（当前约 29 个：9 vendor + 20 主权区）
- **Verification**: `programmatic`
- **Notes**: 使用 find 命令或 LS 工具实际计数对比

### AC-2: Frontmatter 解析正确
- **Given**: 有效的 SKILL.md（含 YAML frontmatter）
- **When**: 解析该文件
- **Then**: 正确提取 name、description、version、paths、argument-hint 等字段，支持 x-toml-ref 外部引用合并
- **Verification**: `programmatic`
- **Notes**: 对现有 9 个 vendor 技能做抽样验证

### AC-3: 错误隔离 - 损坏文件不中断流程
- **Given**: 目录中存在一个故意损坏的 SKILL.md（如 YAML 语法错误、无 frontmatter、编码错误）
- **When**: 运行扫描
- **Then**: 扫描继续完成，损坏文件在错误清单中记录（文件名、错误类型、消息），其他正常技能仍成功加载
- **Verification**: `programmatic`
- **Notes**: 创建临时测试文件验证

### AC-4: 重复名称冲突检测
- **Given**: 两个不同目录下存在同名技能（name 字段相同）
- **When**: 运行扫描
- **Then**: 在报告中输出警告，标记冲突技能及路径
- **Verification**: `programmatic`

### AC-5: Strict/Relaxed 双模式验证
- **Given**: 一个缺少推荐章节（如 Changelog）但有 name/description 的 SKILL.md
- **When**: 用 relaxed 模式扫描 → 通过；用 strict 模式扫描 → 标记警告（但不阻断）
- **Then**: 两种模式结果符合预期
- **Verification**: `programmatic`

### AC-6: JSON 注册表输出格式正确
- **Given**: 扫描完成
- **When**: 生成 JSON 输出
- **Then**: JSON 包含 scan_time、scan_dirs、skills（数组，含 name/description/path/source/status 等字段）、errors、stats 顶层字段；可被 json.load 正常解析
- **Verification**: `programmatic`

### AC-7: Markdown 报告人类可读
- **Given**: 扫描完成
- **When**: 生成 Markdown 报告
- **Then**: 包含技能汇总表格（Markdown table 格式）、错误清单、统计摘要；人类可读，格式清晰
- **Verification**: `human-judgment`

### AC-8: 增量扫描缓存生效
- **Given**: 第一次全量扫描完成，缓存已生成
- **When**: 第二次运行（无文件变更）
- **Then**: 使用缓存结果，扫描速度显著加快（或日志指示"using cache"）；修改某个 SKILL.md 后再次运行，该文件被重新解析
- **Verification**: `programmatic`

### AC-9: 只读安全保证
- **Given**: 任意扫描参数
- **When**: 运行扫描
- **Then**: vendor/ 目录下文件的 mtime/ctime 不变；不创建任何新文件在 vendor/ 下；输出文件只在指定的主权区路径
- **Verification**: `programmatic`（git status 验证 vendor/ 无变更）

### AC-10: SKILL.md 门面完整可用
- **Given**: 技能创建完成
- **When**: 用户阅读 SKILL.md
- **Then**: 包含清晰的触发词（"装载技能"、"扫描技能"、"加载flexloop技能"、"skill auto loader"等）、快速开始示例、参数说明、输出格式说明；遵循项目技能规范（strict 模式验证通过）
- **Verification**: `human-judgment`

### AC-11: CLI 帮助信息完整
- **Given**: 安装完成
- **When**: 运行 `python scripts/load_skills.py --help`
- **Then**: 输出完整帮助信息，列出所有参数及说明
- **Verification**: `programmatic`

## Open Questions
- [ ] JSON 注册表的输出默认路径应该放在哪里？候选：`.agents/cache/skill-registry.json` 或 `.temp/skill-registry.json`
- [ ] Markdown 报告默认输出路径？候选：`.agents/skills/load-flexloop-skills/REGISTRY.md` 或 `.temp/`
- [ ] 是否需要支持 `--check-paths` 参数来验证技能的 paths 字段引用的文件是否真实存在？（初步实现中可作为可选功能）
