---
title: "docs 目录 OKF Wiki 教程规范化改造 - 产品需求文档"
status: "draft"
---

# docs 目录 OKF Wiki 教程规范化改造 - 产品需求文档

## Overview

- **Summary**: 将 `d:\AI\docs` 目录从当前的"部分 OKF 化"状态，参考 `d:\AI\projects\awesome-okf-xs` 的规范实践，全面改造为符合 OKF v0.2 规范的 Wiki 教程文档库。
- **Purpose**: 消除现有文档中 frontmatter 不规范、index.md 越权携带 okf_version、toctree 不完整、质量门缺失等问题，使 docs 目录达到与 awesome-okf-xs 同等的规范水平。
- **Target Users**: SpecWeave 项目维护者、AI 智能体（读取文档时依赖 frontmatter 和结构一致性）、外部读者。

## Goals

- 所有 Markdown 文档符合 OKF v0.2 frontmatter 规范（必填 `type` 字段，推荐字段完整）
- index.md 文件层级权限正确：仅文档根 `index.md` 携带 `okf_version`，子目录 index.md 无 frontmatter
- 每个知识包（bundle）具备完整的 `index.md` + `log.md` + `concepts/` + `examples/`（如适用）+ `references/` 结构
- Sphinx 构建配置增强：引入 frontmatter 日期兼容性钩子、质量门检查脚本
- toctree 完整覆盖所有内容文档，无孤立文档、无断链
- 清理重复文件（README.md 与 index.md 内容重复问题）

## Non-Goals

- **不改变现有内容组织结构**：不将 tech/knowledge/retrospective/general/topics 五大板块重构为 awesome-okf-xs 的技术域分类（ai/build/comm 等），因为两者的内容性质不同——awesome-okf-xs 是外部开源项目教程库，docs 是 SpecWeave 项目自身文档中心
- **不重写正文内容**：仅修正元数据、链接路径和结构，不改动文档正文中的技术内容
- **不引入 awesome-okf-xs 的具体知识包内容**：仅参考其规范、工具链和结构模式
- **不处理 docs 目录之外的文件**：`.agents/docs/` 等目录不在本次范围内

## Background & Context

### 现状

`d:\AI\docs` 是 SpecWeave 的 Sphinx 文档工程，包含 200+ Markdown 文件，按五大板块组织：

| 板块 | 内容 | OKF 化程度 |
|------|------|-----------|
| `tech/` | 项目技术文档 | 已完成 bundle 转换（2026-08-22），结构规范 |
| `knowledge/` | 外部知识学习 Wiki | 大部分 Wiki 已有 concepts/examples/references 结构，但 frontmatter 不统一 |
| `retrospective/` | 复盘与模式库 | 有嵌套 concepts/ 结构，但 index.md 越权携带 okf_version |
| `general/` | 通用知识 | 基本为空壳，index.md 越权携带 okf_version |
| `topics/` | 设计洞见 | 基本为空壳，index.md 越权携带 okf_version |

### 已识别的规范差距

1. **index.md frontmatter 越权**：`knowledge/index.md`、`tech/index.md`、`retrospective/index.md`、`general/index.md`、`topics/index.md` 均携带 `okf_version: "0.2"`，违反 OKF 规范（仅 bundle 根 index.md 可携带）
2. **子目录 index.md 有 frontmatter**：部分 `concepts/index.md` 等子目录索引携带了不应有的 frontmatter
3. **frontmatter 字段不统一**：部分文档有非标准字段（`id`、`date`、`category`），`type` 值不一致（Tutorial/Reference/Pattern/Concept 等）
4. **conf.py 缺少日期兼容性钩子**：awesome-okf-xs 的 `doc/conf.py` 有 `_quote_frontmatter_dates` 钩子，docs 的 conf.py 没有
5. **缺少质量门检查脚本**：awesome-okf-xs 有 `scripts/check-toctrees.py` 和 `scripts/check-utf8.py`，docs 没有
6. **tasks.py 为单文件**：awesome-okf-xs 使用 `tasks/` 包（`__init__.py`、`docs.py`、`gates.py`），docs 只有单文件 `tasks.py`
7. **README.md 重复**：`docs/README.md` 与 `docs/index.md` 内容高度重复
8. **toctree 不完整**：部分目录的 toctree 未覆盖全部文档（如 knowledge/index.md 的 toctree 只列了两个条目）
9. **log.md 格式不统一**：部分 log.md 有详细转换记录，部分只有简单一行

### 参考项目

`d:\AI\projects\awesome-okf-xs` 是 OKF v0.2 规范的成熟参考实现，具有：
- 11 个技术域、30 个分组、263 个知识包
- 完整的 Sphinx 构建配置（含 frontmatter 日期钩子）
- Invoke 任务包（构建 + 质量门）
- CI 检查脚本（toctree 完整性、UTF-8 编码）
- 严格的 frontmatter 规范执行

## Functional Requirements

- **FR-1**: 所有非保留文件名（非 index.md/log.md）的 Markdown 文件必须包含可解析的 YAML frontmatter，且含非空 `type` 字段
- **FR-2**: 仅 `docs/index.md`（文档根）可在 frontmatter 中携带 `okf_version: "0.2"`；所有子目录 index.md 不得携带 frontmatter
- **FR-3**: 每个知识包目录必须包含 `index.md` 和 `log.md`；有概念文档的需有 `concepts/` 子目录
- **FR-4**: `conf.py` 必须包含 frontmatter 裸日期自动加引号的 `source-read` 钩子，从 awesome-okf-xs 移植
- **FR-5**: 引入 `scripts/check-toctrees.py` 和 `scripts/check-utf8.py` 质量门脚本（从 awesome-okf-xs 适配）
- **FR-6**: 将 `tasks.py` 重构为 `tasks/` 包，包含 `__init__.py`、`docs.py`（构建任务）、`gates.py`（质量门任务）
- **FR-7**: 所有含内容文档的目录，其 `index.md` 的 toctree 必须完整覆盖该目录下所有可构建文档
- **FR-8**: 清理 `docs/README.md` 重复文件，或重定向到 `index.md`
- **FR-9**: 统一 frontmatter 字段：保留标准 OKF 字段（type/title/description/resource/tags/generated/verified/status/stale_after/sources），已有非标准字段（id/date/category）作为扩展字段保留但不强制
- **FR-10**: 所有交叉引用使用相对路径，无 `file:///` 绝对路径，无断链

## Non-Functional Requirements

- **NFR-1**: 改造后 Sphinx 构建必须成功通过（`sphinx-build -b html` 无错误）
- **NFR-2**: 所有 Markdown 文件必须为 UTF-8 编码无 BOM
- **NFR-3**: 改造过程不丢失任何正文内容，仅修改 frontmatter、路径和结构
- **NFR-4**: 文件名遵循 kebab-case 纯英文命名（已有中文文件名需评估是否重命名）
- **NFR-5**: 质量门脚本可独立运行，输出清晰的通过/失败信息

## Constraints

- **Technical**: Windows 平台环境；Sphinx + myst_parser 技术栈；Python 3.10+
- **Business**: 不破坏现有文档的可读性和可访问性；改造后文档 URL 路径尽量保持稳定
- **Dependencies**: Sphinx、myst_parser、invoke（已有）；可能需要 sphinx-book-theme
- **Reference**: 必须对齐 OKF v0.2 规范（见 `projects/awesome-okf-xs/doc/bundles/meta/okf-spec/`）

## Assumptions

- docs 目录中已有的 `type` 值（Tutorial/Reference/Pattern/Concept）均为合法的 OKF 扩展类型，OKF 规范不限制 type 取值
- 现有文档正文内容质量可接受，不需要内容层面的改写
- `docs/README.md` 与 `docs/index.md` 的重复是历史遗留，README.md 可以安全删除或改为重定向
- 部分 wiki 目录（如 analyze-wechat-article-*）的结构可能不完整（缺少 examples/），这是可接受的——examples/ 不是强制的
- 保留现有 frontmatter 中的非标准扩展字段（id/date/category 等），因为 OKF 规范允许生产者添加扩展字段

## Acceptance Criteria

### AC-1: Frontmatter 合规性

- **Type**: `rule`
- **Given**: docs 目录下所有非保留 Markdown 文件
- **When**: 检查每个文件的 frontmatter
- **Then**: 每个文件都有可解析的 YAML frontmatter，包含非空 `type` 字段
- **Pass Condition**: 脚本扫描所有 .md 文件（排除 index.md/log.md），100% 通过 type 字段存在性检查
- **Evidence**: 质量门脚本输出报告

### AC-2: index.md 层级权限

- **Type**: `rule`
- **Given**: docs 目录下所有 index.md 文件
- **When**: 检查 frontmatter
- **Then**: 仅 `docs/index.md` 可有 `okf_version` 字段；其他所有 index.md 无 frontmatter
- **Pass Condition**: 除根 index.md 外，0 个子目录 index.md 含 frontmatter
- **Evidence**: 文件内容检查 + 脚本扫描

### AC-3: Sphinx 构建通过

- **Type**: `rule`
- **Given**: 改造后的 docs 目录
- **When**: 运行 `sphinx-build -b html docs _build/html`
- **Then**: 构建成功，无错误
- **Pass Condition**: 退出码 0，无 Sphinx 错误/警告（suppress_warnings 中已排除的 myst.xref_missing 除外）
- **Evidence**: 构建输出日志

### AC-4: toctree 完整性

- **Type**: `rule`
- **Given**: 所有含 toctree 指令的 index.md
- **When**: 运行 toctree 完整性检查
- **Then**: 无孤立文档（未被任何 toctree 引用的内容文档），无断链（toctree 引用不存在的文件）
- **Pass Condition**: check-toctrees.py 脚本通过
- **Evidence**: 质量门脚本输出

### AC-5: 质量门工具链可用

- **Type**: `rule`
- **Given**: tasks/ 包和 scripts/ 目录
- **When**: 运行 `invoke gates.all`
- **Then**: UTF-8 检查和 toctree 检查均通过
- **Pass Condition**: 两个检查均返回成功
- **Evidence**: 命令输出

### AC-6: 内容完整性

- **Type**: `rubric`
- **Dimension**: 改造过程中正文内容零丢失
- **Scale**: 1-5
- **Anchors**: 1 = 有正文内容丢失或被错误改写；3 = 正文完整但有少量格式偏差；5 = 正文 100% 保留，仅 frontmatter/路径/结构变更
- **Pass Threshold**: >= 4
- **Evidence**: git diff 审查，抽样对比改造前后的正文内容

### AC-7: 结构一致性

- **Type**: `rubric`
- **Dimension**: 文档结构与 awesome-okf-xs 参考规范的对齐程度
- **Scale**: 1-5
- **Anchors**: 1 = 结构混乱，与参考差距大；3 = 主要结构对齐但有细节不一致；5 = 完全对齐 OKF v0.2 结构规范
- **Pass Threshold**: >= 4
- **Evidence**: 目录结构对比审查

## Open Questions

- [ ] `docs/README.md` 是直接删除还是改为指向 index.md 的重定向？（建议删除，因为 index.md 已是主入口）
- [ ] 部分 wiki 目录中的 `seven-concepts-report.md` 应归入 references/ 还是保留原位？（建议归入 references/）
- [ ] `docs/knowledge/learning/03-agent-platforms-tools/README.md` 是该目录的索引，是否应重命名为 index.md？
- [ ] 是否需要为 general/ 和 topics/ 空壳板块创建示例内容，还是保持现状仅修复 frontmatter？
