---
status: "draft"
id: archive-okf-spec-bundle
title: OKF 规范知识包归档（bundles/okf-spec → awesome-okf-xs）
type: Spec
timestamp: 2026-08-21
method: seven-concepts（场景3 迁移归档，链路 I→A→V→C）
source: "SpecWeave 主权区 bundles/okf-spec/"
---

# OKF 规范知识包归档 Spec

## Why

SpecWeave 主权区 `bundles/okf-spec/` 中已完成的 OKF v0.2 中文转译知识包，其正确归属是 OKF 文档库子项目 `projects/awesome-okf-xs/`（玄境项目"道"面的知识仓库）。归档使其知识资产各归其位，建立单一可信源，并保持 awesome-okf-xs 作为 OKF 文档库的完整性。

## What Changes

- 将 `bundles/okf-spec/`（24 个 .md 文件）整体迁移到 `projects/awesome-okf-xs/bundles/okf-spec/`（目标子项目 `bundles/` 目录当前不存在，需新建）。
- 将 19 个概念/示例/信源文档 frontmatter 的 `resource: ../../../vendor/knowledge-catalog/okf/SPEC.md`（相对路径，指向 SpecWeave vendored 子模块）调整为 GitHub 权威源 `https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md`。vendor 子模块即用户克隆的 `GoogleCloudPlatform/knowledge-catalog` 项目（HEAD 8e38923 @ main）。
- 更新活跃 spec `okf-100ep-anime` 中对 `bundles/okf-spec/` 的路径引用为新位置。
- 更新 awesome-okf-xs README，登记新收录的 okf-spec bundle。
- 从 SpecWeave 主权区移除源 bundle（git rm），并在两个仓库分别原子提交（awesome-okf-xs 子模块 + SpecWeave 主仓库 gitlink）。

**约束说明**：`references/okf-spec.md` 中脚注式文字描述（"见 vendor/knowledge-catalog/okf/SPEC.md"）为信息性说明，非可导航链接，保持原样不修改（仅 frontmatter `resource` 字段改为 GitHub 源）。

## Impact

- Affected specs: `okf-100ep-anime`（活跃，更新引用路径）；`okf-spec-to-bundle`（历史完成，保持原样作为档案）
- Affected code: 无代码变更，纯 Markdown 文档迁移
- Affected repos: SpecWeave 主仓库（git rm 源 + gitlink 更新）+ `projects/awesome-okf-xs` 子模块（新增 bundle）

## ADDED Requirements

### Requirement: bundle 完整归档到子项目
系统 SHALL 将 `bundles/okf-spec/` 下全部 24 个 .md 文件完整迁移到 `projects/awesome-okf-xs/bundles/okf-spec/`，保持目录结构与文件内容逐字一致。

#### Scenario: 归档成功
- **WHEN** 执行迁移
- **THEN** 目标路径 `projects/awesome-okf-xs/bundles/okf-spec/` 存在 24 个 .md 文件，与源文件内容完全一致，目录层级（concepts/examples/references/index/log）保持不变

### Requirement: resource 指向 GitHub 权威源
系统 SHALL 将归档后 19 个概念/示例/信源文档 frontmatter 的 `resource` 字段由相对路径 `../../../vendor/knowledge-catalog/okf/SPEC.md` 调整为 GitHub 权威源 URL `https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md`。

#### Scenario: resource 指向 GitHub 源
- **WHEN** 从 `projects/awesome-okf-xs/bundles/okf-spec/concepts/<x>.md` 读取 `resource` 字段
- **THEN** 该字段为 GitHub URL `https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md`，指向权威 OKF 规范源（用户克隆的 knowledge-catalog 项目 main 分支）

### Requirement: 源 bundle 移除与引用更新
系统 SHALL 从 SpecWeave 主权区删除 `bundles/okf-spec/`，并更新活跃 spec `okf-100ep-anime` 中对旧路径的引用。

#### Scenario: 无残留旧路径
- **WHEN** 归档完成后扫描 SpecWeave 工作区 `bundles/okf-spec`
- **THEN** 该路径已不存在；`okf-100ep-anime` 的 spec.md/tasks.md/checklist.md 中相关引用已指向新位置

## MODIFIED Requirements

### Requirement: okf-100ep-anime 引用路径更新
原引用 `bundles/okf-spec/`（SpecWeave 主权区）→ 新引用 `projects/awesome-okf-xs/bundles/okf-spec/`（子项目）。

#### Scenario: 活跃 spec 引用一致
- **WHEN** 阅读 `okf-100ep-anime` 的 spec.md/tasks.md/checklist.md
- **THEN** 其中指向 okf-spec 知识包的路径均为新位置，无指向已删除的旧路径

## REMOVED Requirements

### Requirement: 主权区 bundles/okf-spec/ 长期驻留
**Reason**: 已完成的知识资产应归档到其正确归属的 OKF 文档库子项目，主权区仅保留迁移档案。
**Migration**: 内容整体迁移至 `projects/awesome-okf-xs/bundles/okf-spec/`；历史创建记录保留在 `okf-spec-to-bundle` spec 中。
