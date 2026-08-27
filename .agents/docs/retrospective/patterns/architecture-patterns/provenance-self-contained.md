---
id: "provenance-self-contained"
title: "溯源自包含：知识包脱离宿主仓库的可移植分发"
source: "../../../reports/project-governance/okf-spec-bundle-review-fix-retrospective-20260821.md"
maturity: "L1-draft"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "trust-first-metadata"
  - "provenance-driven-trust"
  - "verifiable-knowledge-claim"
  - "python-native-extension-self-contained-wheel"
tags:
  - provenance
  - portable-distribution
  - knowledge-bundle
  - resource-reference
  - offline-distribution
  - self-contained
---
# 溯源自包含：知识包脱离宿主仓库的可移植分发

## 模式概述

在打包/分发知识包（bundle）时，使包内所有**溯源资源引用**采用相对本包（bundle-relative）的路径，并登记唯一权威信源，从而让知识包**脱离宿主仓库仍能自洽、可分发、可离线校验**。核心反直觉洞察：溯源字段直接指向"更权威的外部 URL"看似更可信，实则破坏了打包可移植性——包一旦脱离仓库，溯源能力即失效，成为"脱链的声明"。

该模式由 okf-spec bundle 溯源自包含修复（P2）实践验证。

## 触发场景

- 当知识包需**脱离原仓库**独立分发/归档/传输时使用
- 适用于：多文件知识包/规范的打包交付、离线知识库、单包随附溯源的知识分发
- 不适用：知识始终在单一仓库内原地维护、永不外发（此时外部引用无移植成本）

## 核心做法

1. **识别外部资源引用**：扫描包内所有 `sources[].resource`、脚注、交叉链接，找出指向包外绝对路径/URL 的条目。
2. **改为包内相对引用**：将资源统一改写为指向包内信源（如 `references/okf-spec.md`）的 bundle-relative 路径。
3. **登记唯一权威信源**：在包内信源登记簿中登记一个权威信源文档，作为包内所有引用的单一事实源。
4. **校验自洽性**：检查所有引用在包内可解析，无悬空链接、无绝对外链残留。

## 反模式（不要这么做）

- ❌ **外链权威化**：为"更权威"把 `sources[].resource` 指向外部 URL——包脱离仓库后溯源断裂，无法离线自证。
- ❌ **多源冲突**：同一包内不同文档引用不同权威源，导致溯源判断分裂、无法判定唯一事实源。
- ❌ **仅改正文不改脚注**：改了 `sources[].resource` 却遗漏 `[^okf-spec]` 一类脚注，链接仍指向包外，自洽校验失败。

## 失败案例

**失败案例1：外链权威化导致"脱链的声明"（okf-spec bundle，2026-08-21）**

在 okf-spec bundle 修复前的初版中，多个文档的 `sources[].resource` 直接指向宿主仓库外的 URL/绝对路径，以图"更权威"。后果：该 bundle 一旦脱离宿主仓库单独分发，溯源引用即刻断裂，无法离线自证——信任字段成为"脱链的声明"，机器与第三方的核验能力全部失效。**失败根因**：把"溯源可信度"错误等同于"引用外部更权威源"，忽略了可移植自洽这一前提——外链权威化在打包分发场景下以可信度为名破坏可校验性。

**失败案例2：仅改正文不改脚注（同类包分发复盘）**

有 bundle 修正了正文的 `sources[].resource`，却遗漏 `[^okf-spec]` 一类脚注仍指向包外，自洽扫描时断链依旧，修复不完整造成二次返工。

## 反目标用户/场景

以下用户/场景**不适用或不适合**该模式，强制套用会造成反效果：

1. **知识永不外发、原地维护的单仓库**：若知识始终在单一仓库内原地维护、绝不打包分发，把资源改写为包内引用**对**可移植性**无效**，只增加了与外部最新源同步的维护负担。
2. **对权威性有刚性要求、且允许在线访问的实时活文档**：当引用方必须时刻锚定最新官方规范（如协议标准、法律条文）且支持在线访问时，封死为包内快照**有害**，会引入版本滞后风险。
3. **包内根本无法容纳的资源（超大二进制/流式数据）**：把超大体积或流式数据强要塞进 bundle 内相对引用**无效**且撑爆包体，应保留外部引用并另行登记可移植校验码。
4. **需要精确实时同步的协作仓库**：多端实时协同的场景下，包内相对引用作为唯一信源**不适合**，会造成多端副本漂移难以收敛。

## 检验标准

- 包内所有 `resource` 均能解析到包内文件，无 `http(s)://` 或绝对外盘路径残留。
- 存在唯一权威信源登记（references/index 或等价），且所有文档指向它。
- 将该包单独拷贝到任意空目录后，所有溯源链接仍可解析。
- 包内链接通过自洽扫描（如 check-links）零断链。

## 迁移示例

| 非当前领域场景 | 直接引用外部源的代价 | 本模式做法 |
|---------------|-------------------|-----------|
| Docker 镜像分层构建 | 镜像依赖构建宿主机的绝对路径私有依赖，无法跨机重建 | 依赖清单用镜像内相对路径 + 锁文件自含，实现可移植重建（同构：`python-native-extension-self-contained-wheel`） |
| npm/pip 包发布 | 安装脚本硬编码仓库绝对路径，包装到别的环境即失效 | 包内引用相对自身结构，`files`/`sdist` 自包含 |
| 离线文档分发（PDF/站点包） | 文档内嵌绝对站内链接，离线打开即断链 | 资源改写为包内相对路径，离线可导航 |

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [trust-first-metadata](trust-first-metadata.md) | 互补 | 信任优先元数据规定可信字段体系；本模式保证这些字段的 `sources[].resource` 在包内自洽可解析，是溯源字段的"可移植地基" |
| [provenance-driven-trust](provenance-driven-trust.md) | 基础设施互补 | 溯源驱动信任提供哈希/日志信任锚；本模式解决溯源引用的物理自洽性，二者叠合构成完整可验证溯源链 |
| [verifiable-knowledge-claim](verifiable-knowledge-claim.md) | 表示层互补 | 可验证知识声明用 `documentation` 链接引用外部文档；本模式要求这些链接在打包分发时保持自洽 |
| [python-native-extension-self-contained-wheel](../code-patterns/python-native-extension-self-contained-wheel.md) | 同构迁移 | 自包含 wheel 是"自包含可移植"在二进制分发领域的同类实践 |

---

*模式版本：v1.0 | 创建日期：2026-08-21 | maturity: L1-draft（validation_count=1：okf-spec bundle 溯源自包含修复）—— **单案例待验证**，建议在第二个知识包分发场景验证后升级至 L2*