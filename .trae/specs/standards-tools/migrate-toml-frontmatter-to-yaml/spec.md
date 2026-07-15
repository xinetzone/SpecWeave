---
version: 1.0
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/migrate-toml-frontmatter-to-yaml/spec.toml"
---
# TOML→YAML Frontmatter 全面迁移与 x-toml-ref 体系建立 - Product Requirement Document

## Overview
- **Summary**: 对 SpecWeave 项目进行全面系统复盘后，将项目中 833 个 Markdown 文件的 TOML 格式 frontmatter（`+++` 包裹）统一迁移为 YAML 格式 frontmatter（`---` 包裹），同时通过 `x-toml-ref` 扩展字段将原始 TOML 元数据外部化存储到独立的 TOML 文件中，建立符合 MDI（Markdown as Interface）v1.0 规范的元数据管理体系。迁移后所有 Markdown 文件仅保留精简的 YAML frontmatter 用于核心展示字段，完整元数据通过外部 TOML 文件引用获得。
- **Purpose**: 
  1. 对齐 MDI Spec v1.0 规范：YAML(`---`) 为唯一标准 frontmatter 格式，TOML 仅通过 `x-toml-ref` 外部引用
  2. 消除双格式 frontmatter 并存导致的解析器复杂度和维护成本
  3. 为即将完成的 MDI Parser/Validator/Generator 工具链提供统一的输入格式
  4. 通过外部 TOML 文件集中管理元数据，支持程序化批量更新和类型安全访问
  5. 建立可追溯的迁移机制，确保零数据丢失和可回滚能力
- **Target Users**: AI 智能体（解析 frontmatter 的工具脚本）、项目维护者（需要读写元数据）、MDI 工具链（Parser/Validator/Generator）

## Goals
- 将 833 个 TOML frontmatter 文件 100% 迁移为 YAML frontmatter 格式，零数据丢失
- 设计外部 TOML 元数据文件的存储结构和命名规范，保持目录镜像映射
- 为每个转换后的 YAML frontmatter 正确添加 `x-toml-ref` 字段，建立相对路径引用
- 开发自动化批量转换脚本，支持 dry-run 预览、增量转换、备份回滚
- 更新 frontmatter.py 解析库支持 `x-toml-ref` 外部文件加载与合并
- 更新所有依赖 frontmatter 解析的检查脚本（check-source-traceability.py、check-spec-consistency.py、check-pattern-quality.py 等）以兼容新格式
- 进行全面功能验证和兼容性测试，确保所有 CI 检查通过
- 输出迁移复盘报告和 x-toml-ref 使用规范文档
- 建立 Git 版本控制基线，支持迁移前后对比和回滚

## Non-Goals (Out of Scope)
- 不修改 Markdown 文件正文内容，仅替换 frontmatter 部分
- 不重构现有元数据字段定义或语义，仅做格式转换
- 不迁移 `.trae/specs/` 目录下已使用 YAML frontmatter 的文件（这些文件保持原样）
- 不迁移 vendor/ 目录（git 子模块，独立管理）
- 不迁移 .temp/ 目录下的临时文件
- 不实现完整的 TOML 库或 YAML 库，使用 Python 标准库（tomllib）+ 现有正则解析
- 不引入第三方 YAML/TOML 依赖库（遵循零依赖原则）

## Background & Context
- **当前状态**：项目中存在 833 个使用 TOML frontmatter（`+++`）的 Markdown 文件，分布在 docs(786)、.agents(45)、apps(1)、.trae(1) 目录；同时 `.trae/specs/` 下有 38+ 个使用 YAML frontmatter（`---`）的 Spec 文件，形成双格式并存局面
- **MDI 规范决策**：根据 [markdown-as-interface-research](../markdown-as-interface-research/spec.md) FR-2.2，YAML(`---`) 为唯一标准 frontmatter 格式；不直接支持 TOML(`+++`)；通过 `x-toml-ref` 扩展字段引用外部 TOML 文件
- **现有工具链**：
  - [.agents/scripts/lib/frontmatter.py](../../../../.agents/scripts/lib/frontmatter.py) 现有实现同时支持 TOML 和 YAML 解析
  - 多个检查脚本依赖 frontmatter 解析：check-source-traceability.py、check-spec-consistency.py、check-pattern-quality.py、pattern-maturity.py 等
  - CI 流水线在 ci-check.ps1/ci-check.sh 中包含 frontmatter 相关检查
- **字段分布统计**：833 个文件包含约 60 种不同字段，高频字段包括 id(814)、source(759)、date(517)、type(507)、maturity(296)、layer(226)、domain(224)、validation_count(211)、reuse_count(211) 等，部分字段为数组类型（tags、rules、references、skills 等）
- **历史教训**：此前"规则文档误加 TOML frontmatter"反模式（见 insight）表明 frontmatter 格式不统一会导致混淆和返工

## Functional Requirements

- **FR-1**: 项目结构与文件扫描
  - FR-1.1: 递归扫描项目所有 Markdown 文件（排除 .git、vendor、.temp、__pycache__、node_modules、.venv）
  - FR-1.2: 识别所有包含 TOML frontmatter（`+++` 块）的文件，输出完整清单
  - FR-1.3: 按目录、字段类型、文件类型进行分类统计
  - FR-1.4: 识别已使用 YAML frontmatter（`---`）的文件（不做迁移，仅记录）

- **FR-2**: TOML→YAML 转换规则设计
  - FR-2.1: 定义 TOML 标量字段到 YAML 的映射规则（字符串、数字、布尔值）
  - FR-2.2: 定义 TOML 数组字段（tags = ["a", "b"]）到 YAML 数组的映射规则
  - FR-2.3: 定义 TOML 内联表/嵌套结构到 YAML 的映射规则
  - FR-2.4: 定义字段优先级：哪些字段保留在 YAML frontmatter（核心展示字段），哪些字段移入外部 TOML 文件（完整元数据）
  - FR-2.5: YAML frontmatter 核心字段最小集：id、title（或从文件名推断）、source（如有）、x-toml-ref（必须）
  - FR-2.6: 处理 YAML 特殊字符转义（冒号、引号、# 注释符等）

- **FR-3**: 外部 TOML 文件存储设计
  - FR-3.1: 设计外部 TOML 文件目录结构：与源 Markdown 文件保持镜像目录结构，根目录为 `.meta/toml/`
  - FR-3.2: 定义外部 TOML 文件命名规范：与源 Markdown 文件同名，扩展名为 `.toml`（如 `README.md` → `.meta/toml/.../README.toml`）
  - FR-3.3: 确保外部 TOML 文件内容是原 TOML frontmatter 的完整、无修改拷贝
  - FR-3.4: `.meta/toml/` 目录纳入 Git 版本控制
  - FR-3.5: 在 `.meta/` 目录下添加 README.md 说明结构和用途

- **FR-4**: x-toml-ref 引用关系建立
  - FR-4.1: 计算从 Markdown 文件到外部 TOML 文件的相对路径
  - FR-4.2: 在 YAML frontmatter 中添加 `x-toml-ref: "<relative-path>"` 字段
  - FR-4.3: 路径解析规则：相对于当前 .md 文件所在目录解析
  - FR-4.4: Windows/Unix 路径分隔符兼容性处理（统一使用 `/`）
  - FR-4.5: 确保 x-toml-ref 路径可通过 check-links.py 验证

- **FR-5**: 批量转换工具开发
  - FR-5.1: 开发 `.agents/scripts/migrate-frontmatter.py` 转换脚本
  - FR-5.2: 支持 `--dry-run` 模式：预览转换结果但不写入文件
  - FR-5.3: 支持 `--backup` 选项：转换前自动备份到 `.meta/backup/` 目录
  - FR-5.4: 支持 `--verify` 选项：转换后自动验证双向一致性
  - FR-5.5: 支持 `--rollback` 选项：从备份恢复原始文件
  - FR-5.6: 支持单文件转换和批量目录转换
  - FR-5.7: 生成转换报告：成功数、失败数、跳过数、警告列表
  - FR-5.8: 转换过程详细日志，便于排查问题

- **FR-6**: frontmatter.py 解析库更新
  - FR-6.1: 更新 [frontmatter.py](../../../../.agents/scripts/lib/frontmatter.py) 支持 `x-toml-ref` 字段识别
  - FR-6.2: 当解析到 `x-toml-ref` 字段时，自动加载并解析外部 TOML 文件
  - FR-6.3: 实现 YAML 字段与 TOML 字段合并逻辑：YAML 字段优先级更高，覆盖 TOML 同名字段
  - FR-6.4: TOML 文件不存在或格式错误时产生警告（非致命错误），提供详细 logging
  - FR-6.5: 保持向后兼容：仍能解析旧的 `+++` TOML frontmatter（用于迁移过渡和回滚场景），但发出 deprecation 警告
  - FR-6.6: 新增 `parse_frontmatter_unified()` 统一入口函数，自动识别格式并处理 x-toml-ref

- **FR-7**: 依赖脚本兼容性更新
  - FR-7.1: 更新 check-source-traceability.py 兼容新格式
  - FR-7.2: 更新 check-spec-consistency.py 兼容新格式
  - FR-7.3: 更新 check-pattern-quality.py / pattern-maturity.py 兼容新格式
  - FR-7.4: 更新 docgen.py（导航/看板生成）兼容新格式
  - FR-7.5: 更新 check-agent-skills-compliance.py 兼容新格式
  - FR-7.6: 更新其他依赖 frontmatter 解析的脚本（逐个排查）
  - FR-7.7: 所有脚本使用统一入口 `parse_frontmatter_unified()`，避免重复解析逻辑

- **FR-8**: 测试与验证
  - FR-8.1: 为迁移脚本编写单元测试（≥20 个测试用例）
  - FR-8.2: 为 frontmatter.py 的 x-toml-ref 功能编写单元测试（≥15 个测试用例）
  - FR-8.3: 迁移前后字段一致性验证：每个文件的字段集合和值必须完全匹配
  - FR-8.4: 链接有效性验证：所有 x-toml-ref 路径必须可达
  - FR-8.5: 运行完整 CI 流水线（ci-check.ps1），所有 8 步检查通过
  - FR-8.6: 运行现有测试套件（282+ 个测试），无回归
  - FR-8.7: 抽样人工验证（10% 文件），确认格式正确、内容完整

- **FR-9**: 文档更新
  - FR-9.1: 更新 `.agents/docs/development-standards.md` 中 frontmatter 格式规范章节
  - FR-9.2: 创建 `.meta/README.md` 说明外部 TOML 元数据目录结构和维护方式
  - FR-9.3: 创建 x-toml-ref 使用规范文档（docs/knowledge/ 或 docs/development-standards/ 下）
  - FR-9.4: 更新 .gitignore 确保备份目录不被提交（.meta/backup/）
  - FR-9.5: 输出迁移复盘报告（docs/retrospective/reports/ 下）

- **FR-10**: 版本控制与回滚
  - FR-10.1: 迁移前创建 Git tag 作为基线（如 `pre-frontmatter-migration`）
  - FR-10.2: 迁移变更分原子提交：(1)工具开发 (2)库更新 (3)依赖脚本更新 (4)批量文件转换 (5)文档更新
  - FR-10.3: 备份目录保留，支持一键回滚脚本
  - FR-10.4: 迁移后生成 diff 统计报告（变更文件数、新增文件数、删除行数、新增行数）

## Non-Functional Requirements
- **NFR-1**: 正确性：迁移后元数据字段和值 100% 与原始一致，无截断、无错转、无丢失
- **NFR-2**: 性能：批量转换 833 个文件总耗时 <30 秒（单文件平均 <36ms）
- **NFR-3**: 幂等性：重复运行迁移脚本不会产生重复变更或错误
- **NFR-4**: 可回滚性：提供一键回滚机制，恢复到迁移前状态
- **NFR-5**: 兼容性：保持对旧 TOML frontmatter 的解析能力（deprecation 警告），过渡期至少 2 周
- **NFR-6**: Windows 兼容：所有脚本和路径处理支持 Windows 环境（UTF-8 编码、`\`/`/` 路径分隔符）
- **NFR-7**: 零新增依赖：仅使用 Python 3.13 标准库（tomllib、re、pathlib、json、shutil 等）
- **NFR-8**: 可观测性：迁移过程输出详细日志（INFO/WARNING/ERROR 分级），生成结构化 JSON 报告
- **NFR-9**: 代码质量：新代码单元测试覆盖率 ≥90%，遵循现有代码风格
- **NFR-10**: 文档完整：所有公共 API 有 docstring 和类型注解

## Constraints
- **Technical**:
  - Python 3.13+，使用标准库 tomllib 解析 TOML（不使用第三方库如 pyyaml、toml）
  - YAML 生成采用手动格式化（简单 key: value 格式），不依赖 PyYAML
  - 复用现有 frontmatter.py 的正则解析能力，不重写解析逻辑
  - 遵循项目零依赖原则（见项目记忆）
  - 外部 TOML 文件路径必须使用相对路径，确保仓库可移植
- **Business**:
  - 迁移必须在一次工作会话内完成核心转换，避免长时间中间状态
  - 迁移期间不阻塞其他开发工作（通过 feature branch）
  - CI 流水线必须全程通过，不允许绕过质量门禁
- **Dependencies**:
  - 现有 .agents/scripts/lib/frontmatter.py 解析库
  - 现有 check-source-traceability.py 等检查脚本
  - Python 3.13 标准库 tomllib
  - 现有 833 个 TOML frontmatter 文件作为测试样本

## Assumptions
- TOML frontmatter 中的字段结构相对简单（标量、字符串数组、无深层嵌套表），现有正则解析已覆盖绝大多数场景
- 元数据字段值不包含需要复杂 YAML 转义的特殊字符（如未闭合引号、多行字符串），少数特殊情况可手动处理
- 所有 TOML frontmatter 文件均为 UTF-8 编码
- 外部 TOML 文件存储在 `.meta/toml/` 下不会引起命名冲突（该目录此前不存在）
- 现有检查脚本通过 frontmatter.py 访问元数据，更新该库即可使大部分脚本自动兼容
- Python 3.13 的 tomllib 可正确解析所有现有 TOML frontmatter 内容

## Acceptance Criteria

### AC-1: 文件识别完整性
- **Given**: 项目当前状态（833 个 TOML frontmatter 文件）
- **When**: 运行迁移扫描工具
- **Then**: 准确识别所有 833 个文件，无遗漏、无误报（与基准统计对比差异为 0）
- **Verification**: `programmatic`

### AC-2: 转换规则正确性（单元测试）
- **Given**: 迁移脚本和 frontmatter.py 更新完成
- **When**: 运行单元测试套件
- **Then**: 迁移脚本测试 ≥20 个用例全部通过；frontmatter.py x-toml-ref 测试 ≥15 个用例全部通过；代码覆盖率 ≥90%
- **Verification**: `programmatic`

### AC-3: 字段一致性零丢失
- **Given**: 所有文件完成迁移
- **When**: 运行一致性验证脚本，逐文件对比迁移前 TOML frontmatter 与迁移后（YAML + 外部 TOML 合并）的字段集合和值
- **Then**: 833 个文件全部通过一致性校验，字段名和字段值完全匹配（零差异）
- **Verification**: `programmatic`

### AC-4: x-toml-ref 链接有效性
- **Given**: 所有文件完成迁移
- **When**: 运行 check-links.py 检查所有 x-toml-ref 路径
- **Then**: 所有 x-toml-ref 引用路径有效，无断链（0 个错误）
- **Verification**: `programmatic`

### AC-5: 外部 TOML 文件结构正确
- **Given**: 批量转换完成
- **When**: 检查 `.meta/toml/` 目录结构
- **Then**: 目录结构与源 Markdown 文件保持镜像映射；每个源 .md 文件对应一个 .toml 文件；TOML 文件内容与原 frontmatter 完全一致
- **Verification**: `programmatic` + `human-judgment`

### AC-6: 现有脚本兼容性
- **Given**: frontmatter.py 和所有依赖脚本更新完成
- **When**: 运行所有依赖 frontmatter 的检查脚本（check-source-traceability.py、check-spec-consistency.py、check-pattern-quality.py、pattern-maturity.py、docgen.py 等）
- **Then**: 所有脚本正常运行，无报错，输出结果与迁移前一致（或在预期范围内）
- **Verification**: `programmatic`

### AC-7: CI 流水线全通过
- **Given**: 全部迁移工作完成
- **When**: 运行完整 CI 检查 `python .agents/scripts/ci-check.ps1`
- **Then**: 所有 8 步检查全部通过，0 错误，警告数量不超过迁移前基线
- **Verification**: `programmatic`

### AC-8: 现有测试套件无回归
- **Given**: 全部迁移工作完成
- **When**: 运行 pytest 完整测试套件
- **Then**: 282+ 个现有测试 + 新增测试全部通过，无失败、无错误
- **Verification**: `programmatic`

### AC-9: 人工抽样验证通过
- **Given**: 批量转换完成
- **When**: 随机抽取 83 个文件（10%）进行人工检查
- **Then**: YAML frontmatter 格式正确（`---` 包裹、YAML 语法合法）；x-toml-ref 路径正确；外部 TOML 文件内容完整；正文内容未被修改
- **Verification**: `human-judgment`

### AC-10: 回滚机制有效
- **Given**: 迁移前已创建备份和 Git tag
- **When**: 执行回滚操作
- **Then**: 所有文件恢复到迁移前状态；Git 工作区清洁；可重新执行迁移
- **Verification**: `programmatic`

### AC-11: 文档完整规范
- **Given**: 迁移完成
- **When**: 评审文档更新
- **Then**: .agents/docs/development-standards.md 更新 frontmatter 规范为 YAML+x-toml-ref；.meta/README.md 存在且说明清晰；x-toml-ref 使用规范文档存在；迁移复盘报告产出
- **Verification**: `human-judgment`

### AC-12: 性能达标
- **Given**: 迁移脚本开发完成
- **When**: 对 833 个文件执行批量转换并计时
- **Then**: 总耗时 <30 秒（不含备份和验证步骤）
- **Verification**: `programmatic`

## Open Questions
- [ ] YAML frontmatter 中应保留哪些核心字段？（建议最小集：id、x-toml-ref；可选保留 title、source）→ 默认策略：仅保留 id 和 x-toml-ref，其余全部外置
- [ ] 对于 `.trae/specs/` 下已用 YAML frontmatter 但无 x-toml-ref 的文件，是否需要补充 x-toml-ref？→ 默认策略：不主动修改，保持原样，仅迁移 TOML 文件
- [ ] `.meta/toml/` 目录命名是否合适？是否有更符合项目惯例的命名？→ 默认使用 `.meta/toml/`
- [ ] 过渡期策略：是否保留对 `+++` TOML frontmatter 的解析支持？保留多久？→ 默认保留 2 周，发出 deprecation 警告
- [ ] 外部 TOML 文件是否需要包含版本标识或迁移时间戳？→ 默认不添加，保持原始内容完全一致
