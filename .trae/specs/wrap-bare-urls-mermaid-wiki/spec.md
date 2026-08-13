# mermaid-wiki 裸 URL 包裹规范统一 Spec

## Why

`mermaid-wiki` 目录下的多篇文档正文中存在**未被任何 Markdown 语法包裹的裸 URL**（如 `https://mermaid.live/`）。裸 URL 在多数渲染器中虽可自动识别，但不具备语义明确的自动链接（autolink）形态，且与同目录内已使用 `<url>` 包裹的写法（如 `00-overview.md` 中的 `<https://mermaid.js.org/>`）不一致，造成文档格式风格不统一。

本轮任务将正文中**可点击的裸 URL**统一包裹为 `<...>` 自动链接格式，以提升可读性与格式一致性。

## What Changes

- 将 `mermaid-wiki` 目录 10 个章节文档正文中的**裸 URL** 包裹为 `<url>` 自动链接格式。
- **不改动**以下类型的 URL（不属于"裸 URL"）：
  - YAML frontmatter 中的 `source:` 元数据字段（非正文渲染内容）。
  - 代码块（含 import 语句、CDN 示例）内的 URL。
  - 已使用反引号 `` `...` `` 包裹的 URL（如 `` `https://cdn.jsdelivr.net/...` ``、`` `https://github.com/mermaid-js/mermaid-cli` ``）。
  - 已使用 `<...>` 包裹的 URL（如 `00-overview.md` 中已合规的 `<https://mermaid.js.org/>`）。
  - 含 `<...>` 占位符的 URL 模板（如 `https://mermaid.js.org/syntax/<名称>.html`）。

## Impact

- Affected specs: `create-mermaid-wiki-tutorial`（mermaid-wiki 文档源）
- Affected code: `d:\AI\.agents\docs\knowledge\learning\04-docs-markup-tooling\mermaid-wiki\` 下正文含裸 URL 的章节文档

## ADDED Requirements

### Requirement: 正文裸 URL 包裹为自动链接

mermaid-wiki 各章节文档的**正文**中，凡出现可点击的裸 URL，系统 SHALL 将其包裹为 `<url>` 自动链接形式。

#### Scenario: 正文行内裸 URL

- **WHEN** 正文中存在裸 URL（如 `https://mermaid.live/` 或 `https://mermaid.js.org/`）
- **THEN** 该 URL 被包裹为 `<https://mermaid.live/>` / `<https://mermaid.js.org/>` 形式

#### Scenario: 列表项中的裸 URL

- **WHEN** 列表项中为裸 URL（如 `- **地址**：https://mermaid.live/`）
- **THEN** URL 部分被包裹为 `- **地址**：<https://mermaid.live/>`

### Requirement: 非裸 URL 保持原样

系统 SHALL 保持 frontmatter 元数据、代码块内 URL、反引号包裹 URL、已用 `<...>` 包裹 URL、含占位符 URL 模板不变。

#### Scenario: 元数据与代码块 URL 不受影响

- **WHEN** URL 位于 frontmatter `source:` 字段、代码块、反引号包裹或占位符模板中
- **THEN** 该 URL 保持原样，不做任何包裹修改