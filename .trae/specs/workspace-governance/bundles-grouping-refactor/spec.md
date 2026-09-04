---
title: "doc/bundles 分组重构（域层重组）Spec"
status: "draft"
---

# doc/bundles 分组重构（域层重组）Spec

## Why

`awesome-okf-xs/doc/bundles/` 现有 **28 个顶层分组**，但导航索引严重失同步、主题重叠与碎片化并存：

- 根 [bundles/index.md](../../projects/awesome-okf-xs/doc/bundles/index.md) frontmatter 声明 `total_bundles: 246 / groups: 25`，导航表实际仅列 **17 组**，且 11 组（build、coze、deepseek、fastapi、graphql、katex、laozi、myst、pocketflow、tencent、trae）完全缺失
- [doc/index.md](../../projects/awesome-okf-xs/doc/index.md) 又声称 **23 组 / 236 束**——三处数字互相矛盾
- 索引引用的部分路径与磁盘不符（sphinx 声称 10 束实为 3 束、jupyter 声称 4 束实为 ~35 束）
- 主题重叠/碎片化：构建域分散在 conda/build/cmake/tooling 四组；文档域分散在 sphinx/myst/jupyter-book/katex/jupyter 五组；AI 域分散在 9 组并列

需通过「域层重组」将 28 个扁平组归入 8-10 个技术域，恢复导航一致性。

## What Changes

- **引入 10 个一级技术域（domain）目录**，作为 `doc/bundles/` 的新顶层结构；现有 28 组按主题归入对应域下（二级），域内保留组索引
- **物理迁移**：通过 `git mv` 将组目录移入域目录，组内相对链接不受影响
- **扁平化锚点组**：单束组（meta/okf-spec、python/cpython、build/scikit-build）作为域锚点直接保留（域名复用组名，路径不变），避免 `域/组/束` 过深嵌套
- **修复全部跨组链接**：约 224 处根绝对链接 `](/group/...` → `](/domain/group/...`，约 121 处相对链接 `](../group/...` 按层级调整
- **重写根索引** [bundles/index.md](../../projects/awesome-okf-xs/doc/bundles/index.md)：域导航 + 域内分组导航，修正 `total_bundles`/`groups` 计数与实际一致
- **更新 Sphinx 入口** [doc/index.md](../../projects/awesome-okf-xs/doc/index.md) 计数；Sphinx toctree 仅引用 `bundles/index`，无需改动 conf.py
- **每批迁移一次原子提交**（Conventional Commits，中文主题）

## Impact

- **Affected specs**: OKF v0.2 bundle 组织（[frontmatter.md](../../projects/awesome-okf-xs/.agents/rules/frontmatter.md) 第 11 节交叉引用规范）
- **Affected code/文件**:
  - [doc/bundles/](../../projects/awesome-okf-xs/doc/bundles/) 全部 28 组目录迁移
  - [doc/bundles/index.md](../../projects/awesome-okf-xs/doc/bundles/index.md) 重写
  - 10 个新域 `index.md`（`type: group` 或 `domain`）
  - 各域内组 `index.md` 的交叉引用（如指向其他组的链接）
  - [doc/index.md](../../projects/awesome-okf-xs/doc/index.md) 计数
  - `doc/bundles/.gitignore`（含 `!build/`，与 `build/` 域命名相关，需验证不影响跟踪）
- **不受影响**: Sphinx conf.py（toctree 仍指向 `bundles/index`）、doc/bundles junction 机制、束内部 `index.md`/`log.md` 内容

## ADDED Requirements

### Requirement: 域层目录体系
系统 SHALL 在 `doc/bundles/` 下建立 10 个一级域目录，并将现有 28 组物理归入对应域：

| 域 | 域名 | 收录现有组 |
|---|---|---|
| 规范与格式 | `meta` | meta（锚点，okf-spec） |
| 语言核心 | `python` | python（锚点，cpython） |
| 构建与工具链 | `build` | conda、build（scikit-build，锚点）、cmake、tooling |
| 文档与交互 | `document` | sphinx、myst、jupyter-book、katex、jupyter |
| 数据与科学计算 | `data` | pydata |
| 机器学习与模型 | `ml` | onnx |
| AI 与智能体 | `ai` | agnes-ai、ai-agent、langchain-ai、datawhale、coze、deepseek、trae、tencent、pocketflow |
| 网络与通信 | `comm` | messaging、networking |
| Web 与 API | `web` | fastapi、graphql |
| 哲学与人文 | `think` | psi、laozi |

- 锚点组（meta/python/build）域名复用组名，束目录路径不变（如 `build/scikit-build/`）
- 每个域创建 `index.md`（`type: group`），含域说明与域内分组导航

#### Scenario: 域目录创建成功
- **WHEN** 执行重构任务
- **THEN** `doc/bundles/` 顶层出现 10 个域目录，每个域含 `index.md` 与已迁移的组目录

### Requirement: 跨组链接修复
系统 SHALL 修复迁移引入的全部断链：
- 根绝对链接 `](/<group>/...` → `](/<domain>/<group>/...`（约 224 处）
- 相对链接 `](../<group>/...` 按新层级调整（约 121 处）
- 组内相对链接不修改（组内容整体迁移）

#### Scenario: 迁移后无断链
- **WHEN** 全量链接检查执行
- **THEN** 无指向不存在目标的 Markdown 链接（OKF 允许容忍断链，但本任务验收以 0 断链为目标）

### Requirement: 索引一致性
系统 SHALL 重写根索引与 Sphinx 入口，使分组、束数与磁盘一致：
- [bundles/index.md](../../projects/awesome-okf-xs/doc/bundles/index.md)：域导航表 + 每组详情，`total_bundles`/`groups` 取实际盘点值
- [doc/index.md](../../projects/awesome-okf-xs/doc/index.md)：修正「N 组 / M 束」计数

#### Scenario: 索引与磁盘一致
- **WHEN** 对比根索引导航表与磁盘目录
- **THEN** 每组均出现在导航表中，无缺失/多余；frontmatter 计数与实际一致

### Requirement: 等价性验证
系统 SHALL 在重构后验证等价性（功能/内容不丢失、依赖完整）：
- 每个束的 `index.md`/`log.md` 保留原内容（仅路径变化）
- Sphinx 构建通过：`sphinx-build -b dummy -E doc _build/dummy <file>`（按 frontmatter.md §14 验证法）
- `git status` 仅含预期的移动/新增/修改，无意外删除

## MODIFIED Requirements

### Requirement: 根索引（bundles/index.md）
原 25 组/246 束的声明与 17 组导航表，修改为与实际一致的域+组两级导航结构，计数与磁盘对齐。

### Requirement: Sphinx 入口（doc/index.md）
原「236 束 / 23 组」声明，修改为实际盘点值。

### Requirement: 组索引交叉引用
各域内组 `index.md` 指向其他组的相对/根绝对链接，按新路径同步更新。

## REMOVED Requirements

### Requirement: 平铺 28 组顶层结构
**Reason**: 顶层平铺导致导航碎片化、主题重叠、索引失同步
**Migration**: 组目录物理移入 10 个域下，组内结构保持不变；链接按新路径修复；锚点组复用域名路径不变
