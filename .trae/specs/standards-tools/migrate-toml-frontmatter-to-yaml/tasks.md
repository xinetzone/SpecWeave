# TOML→YAML Frontmatter 全面迁移与 x-toml-ref 体系建立 - The Implementation Plan

## [ ] Task 1: 迁移前准备与基线建立
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建迁移专用 Git 分支（如 `feature/frontmatter-migration`）
  - 创建迁移前基线 Git tag：`pre-frontmatter-migration`
  - 运行完整测试套件和 CI 检查，记录基线状态
  - 开发文件扫描统计脚本，输出 833 个 TOML 文件的完整清单（JSON 格式），包含路径、字段列表、字段值哈希
  - 确认清单与基准统计（docs:786, .agents:45, apps:1, .trae:1）一致
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: 扫描脚本输出文件总数为 833
  - `programmatic` TR-1.2: 扫描输出包含每个文件的相对路径、字段名列表、字段值哈希
  - `programmatic` TR-1.3: 基线测试套件全部通过（282+ tests）
  - `programmatic` TR-1.4: 基线 CI 检查全部通过（8 steps）
  - `human-judgment` TR-1.5: Git tag 和分支创建正确，工作区清洁
- **Notes**: 基线清单将作为后续一致性验证的基准

## [ ] Task 2: TOML→YAML 转换规则与外部存储设计
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 明确 YAML frontmatter 保留字段最小集：`id`、`x-toml-ref`（必需）；`source`、`title` 可选保留
  - 制定 TOML 标量字段到 YAML 的转义规则（冒号、引号、# 注释、多行值处理）
  - 制定 TOML 数组（tags = ["a", "b"]）到 YAML 数组格式（tags: ["a", "b"] 或块格式）的转换规则
  - 设计外部 TOML 存储结构：`.meta/toml/<mirror-path>/<filename>.toml`
  - 定义 x-toml-ref 相对路径计算规则（从 .md 到 .toml，使用 `/` 分隔符）
  - 设计幂等性策略：重复迁移不重复创建文件、不重复修改
  - 输出转换规则文档（代码注释 + 设计文档片段）
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgment` TR-2.1: 转换规则覆盖所有字段类型（标量、数组、特殊字符）
  - `human-judgment` TR-2.2: 外部存储结构设计合理，无命名冲突
  - `programmatic` TR-2.3: 提供至少 10 个典型字段的转换示例（含边界情况）
- **Notes**: 参考 MDI Spec v1.0 中 x-toml-ref 规范定义

## [ ] Task 3: frontmatter.py 库更新（x-toml-ref 支持）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 更新 [frontmatter.py](file:///d:/spaces/SpecWeave/.agents/scripts/lib/frontmatter.py) 添加 `x-toml-ref` 支持
  - 新增函数 `parse_frontmatter_unified(file_path)` 作为统一入口：
    - 自动检测 YAML(`---`) 或 TOML(`+++`) 格式
    - 若为 YAML 且包含 `x-toml-ref`，加载外部 TOML 文件（使用 Python 3.13 tomllib）
    - 合并元数据：YAML 字段覆盖 TOML 同名字段
    - TOML 文件不存在/格式错误时 warning 而非 error
    - 解析旧 `+++` 格式时发出 DeprecationWarning
  - 新增辅助函数：`load_external_toml(toml_path, base_dir)`、`merge_metadata(yaml_meta, toml_meta)`
  - 保持现有 API（parse_toml_frontmatter、extract_frontmatter_field 等）向后兼容
  - 添加详细 logging 用于排查 x-toml-ref 加载问题
- **Acceptance Criteria Addressed**: [AC-2, AC-6]
- **Test Requirements**:
  - `programmatic` TR-3.1: 编写 ≥15 个单元测试覆盖 x-toml-ref 解析场景
  - `programmatic` TR-3.2: 测试覆盖：正常引用、路径不存在、TOML 格式错误、YAML 覆盖 TOML 字段、数组字段、相对路径解析
  - `programmatic` TR-3.3: 测试覆盖：旧 `+++` 格式解析仍正常工作（带 deprecation warning）
  - `programmatic` TR-3.4: 现有 frontmatter 相关测试全部通过（无回归）
  - `programmatic` TR-3.5: 代码覆盖率 ≥90%
  - `human-judgment` TR-3.6: 所有公共函数有 docstring 和类型注解
- **Notes**: 使用 Python 3.13 标准库 tomllib，不引入第三方依赖

## [ ] Task 4: 批量迁移脚本开发（migrate-frontmatter.py）
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 创建 `.agents/scripts/migrate-frontmatter.py` 批量转换脚本
  - 实现核心功能：
    - `scan_files()`: 扫描并识别所有 TOML frontmatter 文件
    - `convert_file(md_path, dry_run=False)`: 转换单个文件（TOML→YAML frontmatter + 外部 TOML 文件）
    - `batch_convert(paths, dry_run=False, backup=False)`: 批量转换
    - `verify_consistency(original_manifest, converted_manifest)`: 一致性验证
    - `rollback(backup_dir)`: 从备份回滚
  - 实现 CLI 参数：`--dry-run`、`--backup`、`--verify`、`--rollback`、`--path <dir>`、`--report <json>`
  - 转换流程：读取原文件 → 解析 TOML frontmatter → 生成 YAML frontmatter（含 x-toml-ref）→ 将原 TOML 写入外部 .toml 文件 → 替换原文件 frontmatter（保留正文不变）
  - Windows 兼容性：路径分隔符统一为 `/`，UTF-8 编码
  - 生成结构化 JSON 迁移报告
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-12]
- **Test Requirements**:
  - `programmatic` TR-4.1: 编写 ≥20 个单元测试覆盖迁移脚本核心逻辑
  - `programmatic` TR-4.2: 测试覆盖：单文件转换、批量转换、dry-run 模式、backup/rollback、幂等性（重复运行）、特殊字符转义、数组字段转换
  - `programmatic` TR-4.3: 测试覆盖：边界情况（空 frontmatter、仅一个字段、无正文文件）
  - `programmatic` TR-4.4: dry-run 模式不修改任何文件
  - `programmatic` TR-4.5: 批量转换 833 个文件总耗时 <30 秒
  - `programmatic` TR-4.6: 代码覆盖率 ≥90%
- **Notes**: 遵循项目现有 CLI 风格（参考 cli.py），使用 UTF-8 编码

## [ ] Task 5: 依赖脚本兼容性排查与更新
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 全局搜索所有调用 frontmatter 解析函数的脚本（使用 SearchCodebase 和 Grep）
  - 逐个排查并更新以下已知依赖脚本：
    - check-source-traceability.py
    - check-spec-consistency.py
    - check-pattern-quality.py / pattern-maturity.py / pattern-maturity-stats.py
    - docgen.py（及旧版 generate-nav.py、generate-dashboard.py）
    - check-agent-skills-compliance.py
    - check-atomization-coverage.py、check-atomization-duplication.py
    - check-report-categorization.py
    - generate_index.py（docs/knowledge/scripts/）
    - 其他依赖脚本（逐个确认）
  - 更新策略：统一使用 `parse_frontmatter_unified()` 或 `extract_frontmatter_field_from_file()` 入口
  - 确保脚本同时兼容迁移前（`+++`）和迁移后（`---` + x-toml-ref）格式
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有被识别的依赖脚本在迁移后的样本文件上运行无报错
  - `programmatic` TR-5.2: 各脚本输出结果与迁移前一致（或在预期范围内）
  - `programmatic` TR-5.3: 每个被修改的脚本对应的现有测试全部通过
  - `human-judgment` TR-5.4: 无遗漏的依赖脚本（Grep 全局搜索确认）
- **Notes**: 使用 SearchCodebase 搜索 "frontmatter"、"parse_toml"、"extract_frontmatter" 等关键词

## [ ] Task 6: 执行批量迁移与验证
- **Priority**: high
- **Depends On**: Task 4, Task 5
- **Description**:
  - 在 feature 分支上执行迁移：
    1. 运行 `python .agents/scripts/migrate-frontmatter.py --backup --verify`
    2. 检查迁移报告（成功数=833，失败数=0）
    3. 检查 `.meta/toml/` 目录结构和文件数量
    4. 检查 `.meta/backup/` 备份完整性
  - 运行一致性验证脚本（迁移后字段值与基线清单对比）
  - 运行链接检查：`python .agents/scripts/check-links.py --path . --fix`
  - 人工抽样验证 83 个文件（10%）
- **Acceptance Criteria Addressed**: [AC-1, AC-3, AC-4, AC-5, AC-9]
- **Test Requirements**:
  - `programmatic` TR-6.1: 迁移报告显示成功=833，失败=0，跳过=0
  - `programmatic` TR-6.2: `.meta/toml/` 目录下文件数=833
  - `programmatic` TR-6.3: 一致性验证脚本输出 0 个差异
  - `programmatic` TR-6.4: check-links.py 检查 x-toml-ref 路径 0 个断链
  - `human-judgment` TR-6.5: 抽样 83 个文件格式正确、内容完整、正文未修改
- **Notes**: 如果发现失败案例，修复脚本后重新执行（幂等性保证安全）

## [ ] Task 7: CI 与全量测试验证
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 运行完整 pytest 测试套件
  - 运行完整 CI 流水线：`python .agents/scripts/ci-check.ps1`（8步检查）
  - 运行 Skill 质量检查：`python .agents/scripts/check-skill-quality.py --threshold 70`
  - 运行硬编码检查：`python .agents/scripts/check-hardcode.py`
  - 运行 RACI 合规检查：`python .agents/scripts/check-raci-compliance.py`
  - 运行重复代码检测：`python .agents/scripts/check-duplication.py`
  - 对比迁移前后 CI 结果，确认无新增问题
- **Acceptance Criteria Addressed**: [AC-7, AC-8]
- **Test Requirements**:
  - `programmatic` TR-7.1: pytest 全部通过（原有 282+ 测试 + 新增 ≥35 个测试）
  - `programmatic` TR-7.2: CI 8 步检查全部通过
  - `programmatic` TR-7.3: Skill 质量检查平均分 ≥90（迁移前水平）
  - `programmatic` TR-7.4: 硬编码检查无新增误报
  - `programmatic` TR-7.5: 链接检查 0 错误
- **Notes**: 任何失败必须修复后才能进入下一阶段

## [ ] Task 8: 文档更新与规范制定
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 创建 `.meta/README.md` 说明外部元数据目录结构：
    - `.meta/toml/` - 外部 TOML 元数据文件（镜像目录结构）
    - `.meta/backup/` - 迁移备份（Git 忽略，不提交）
  - 更新 [docs/development-standards.md](file:///d:/spaces/SpecWeave/docs/development-standards.md) frontmatter 章节：
    - YAML(`---`) 为唯一标准 frontmatter 格式
    - `x-toml-ref` 字段使用规范
    - 外部 TOML 文件存储约定
    - 从旧 `+++` 格式迁移指南
  - 更新 `.gitignore` 添加 `.meta/backup/`
  - 必要时更新 [.agents/global-core-rules.md](file:///d:/spaces/SpecWeave/.agents/global-core-rules.md) 和 [.agents/capability-boundaries.md](file:///d:/spaces/SpecWeave/.agents/capability-boundaries.md) 中相关描述
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-8.1: check-links.py 验证新文档中链接 0 错误
  - `human-judgment` TR-8.2: .meta/README.md 内容清晰，说明目录用途和维护方式
  - `human-judgment` TR-8.3: development-standards.md 中规范描述准确、示例正确
  - `programmatic` TR-8.4: .gitignore 正确忽略 .meta/backup/
- **Notes**: 文档使用中文，遵循现有文档风格

## [ ] Task 9: 原子提交与版本控制
- **Priority**: high
- **Depends On**: Task 7, Task 8
- **Description**:
  - 按以下顺序分原子提交（遵循 Conventional Commits）：
    1. `feat(scripts): add x-toml-ref support to frontmatter.py`（库更新 + 测试）
    2. `feat(scripts): add migrate-frontmatter.py batch migration tool`（迁移脚本 + 测试）
    3. `fix(scripts): update dependent scripts for unified frontmatter parsing`（依赖脚本更新）
    4. `refactor(docs): migrate 833 TOML frontmatter files to YAML with x-toml-ref`（批量文件转换）
    5. `docs(meta): add .meta directory README and update frontmatter standards`（文档更新）
  - 每个提交前运行相关测试确保通过
  - 生成迁移统计报告（文件变更数、新增文件数、行数变化）
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `programmatic` TR-9.1: 每个提交通过原子提交校验（单一职责、显式 add、敏感信息检查）
  - `programmatic` TR-9.2: Git 历史清晰，每个提交可独立回滚
  - `human-judgment` TR-9.3: 提交信息符合 Conventional Commits 规范（中文描述）
- **Notes**: 使用 atomic-commit-cmd skill 执行原子提交

## [ ] Task 10: 复盘报告与模式沉淀
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 创建迁移复盘报告目录：`docs/retrospective/reports/project-governance/tools-and-automation/retrospective-frontmatter-migration-20260701/`
  - 编写 README.md、execution-retrospective.md、insight-extraction.md、export-suggestions.md
  - 记录关键数据：833 文件、迁移耗时、发现的问题、改进建议
  - 萃取可复用模式（如适用）：大规模格式迁移方法论、双格式兼容策略、x-toml-ref 引用模式
  - 更新 docs/retrospective 索引和看板
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `human-judgment` TR-10.1: 复盘报告包含完整的背景、过程、结果、洞察、建议
  - `programmatic` TR-10.2: 复盘文档的链接和索引正确（check-links 通过）
  - `human-judgment` TR-10.3: 如有可复用模式，正确注册到模式库并更新索引
- **Notes**: 遵循项目复盘体系四文件结构（README + execution + insight + export）
