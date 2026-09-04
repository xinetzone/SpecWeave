# Tasks: mermaid-wiki 裸 URL 包裹规范统一

> 按七概念方法论 I→A→C 轻量链路组织；每个文档的修改为独立可验证的小任务，最终统一验证后提交。

## 修改任务

- [x] Task 1: 包裹 `01-introduction-quickstart.md` 正文裸 URL
  - [x] 1.1 第 57 行 `（https://mermaid.live/）` → `（<https://mermaid.live/>）`
  - [x] 1.2 第 61 行 `打开 https://mermaid.live/，` → `打开 <https://mermaid.live/>，`
  - [x] 1.3 确认 frontmatter `source:` 与代码块内 URL（第 97、111 行）保持原样

- [x] Task 2: 包裹 `02-flowchart.md` 正文裸 URL
  - [x] 2.1 第 16 行 `（https://mermaid.js.org/）` → `（<https://mermaid.js.org/>）`

- [x] Task 3: 包裹 `03-sequence-diagram.md` 正文裸 URL
  - [x] 3.1 第 16 行 `（https://mermaid.js.org/）` → `（<https://mermaid.js.org/>）`

- [x] Task 4: 包裹 `04-class-state-er.md` 正文裸 URL
  - [x] 4.1 第 20 行 `（https://mermaid.js.org/）` → `（<https://mermaid.js.org/>）`

- [x] Task 5: 包裹 `05-aggregate-diagrams.md` 正文裸 URL
  - [x] 5.1 第 23 行 `（https://mermaid.js.org/）` → `（<https://mermaid.js.org/>）`

- [x] Task 6: 包裹 `06-advanced-diagrams.md` 正文裸 URL
  - [x] 6.1 第 23 行 `（https://mermaid.js.org/）` → `（<https://mermaid.js.org/>）`

- [x] Task 7: 包裹 `07-configuration-theming.md` 正文裸 URL
  - [x] 7.1 第 14 行 `（https://mermaid.js.org/）` → `（<https://mermaid.js.org/>）`

- [x] Task 8: 包裹 `08-integrations-ecosystem.md` 正文裸 URL
  - [x] 8.1 第 14 行 `（https://mermaid.js.org/）` → `（<https://mermaid.js.org/>）`
  - [x] 8.2 第 72 行 `- **地址**：https://mermaid.live/` → `- **地址**：<https://mermaid.live/>`
  - [x] 8.3 确认代码块内 CDN URL（第 96 行）与反引号包裹 URL（第 22 行）保持原样

- [x] Task 9: 包裹 `09-faq-best-practices.md` 正文裸 URL
  - [x] 9.1 第 14 行 `（https://mermaid.js.org/）` → `（<https://mermaid.js.org/>）`
  - [x] 9.2 第 228 行 `在 https://mermaid.live/ 左侧` → `在 <https://mermaid.live/> 左侧`

- [x] Task 10: 包裹 `10-cheatsheet.md` 正文裸 URL
  - [x] 10.1 第 14 行 `（https://mermaid.js.org/）` → `（<https://mermaid.js.org/>）`
  - [x] 10.2 第 333 行 `**地址**：https://mermaid.live/ ｜` → `**地址**：<https://mermaid.live/> ｜`

## 验证任务

- [x] Task 11: 全目录复核
  - [x] 11.1 重新 Grep `https?://` 确认正文中不再存在遗漏的裸 URL（frontmatter、代码块、反引号、占位符模板除外）
  - [x] 11.2 确认 `00-overview.md`（已合规）与 `README.md` 无需改动

## Task Dependencies

- Task 1-10 相互独立，可并行执行
- Task 11 依赖 Task 1-10（所有修改完成后统一复核）