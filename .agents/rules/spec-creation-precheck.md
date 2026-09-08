---
id: "spec-creation-precheck"
title: "Spec 创建前预检：位置与格式双重核查"
source: "AGENTS.md#规则体系"
version: "1.0"
x-toml-ref: "../../.meta/toml/.agents/rules/spec-creation-precheck.toml"
---

# Spec 创建前预检：位置与格式双重核查

> 两个高复发错误已通过此规则固化预防：spec 位置错误 + 产物格式漂移（checklist.md 等非规范文件）。
> 规则触发时机：**任何智能体准备创建 spec.md 之前**，必须严格执行以下预检流程。

---

## 一、规则定义

### RULE-SCP-001：创建 Spec 前必须读主题 README

- **触发条件**：准备创建新 spec（首次 `touch spec.md` 或 `mkdir <theme-subdir>` 之前）
- **执行步骤**：
  1. 找到目标主题子目录的 `README.md`（如 `classics-knowledge/README.md`）
  2. 阅读其中"新增 Spec 流程"或类似说明
  3. 确认本主题已有 spec 的命名规律与存放位置
  4. 严格按 README 指引创建（如"先查重 → 创建三件套 → docgen 刷新看板"）
- **禁止行为**：跳过 README 直接创建目录或文件
- **反模式**：
  - ❌ 直接 `mkdir new-spec && touch spec.md`
  - ❌ 创建后才发现位置不对再移动，导致路径引用批量更新
  - ❌ README 中已有明确指引时仍凭经验放置

---

### RULE-SCP-002：创建 Spec 前必须核对产物格式

- **触发条件**：准备创建或更新 `spec.md` / `tasks.md` / `review.md` 时
- **执行步骤**：
  1. 读取 [TRAE-spec-mode/SKILL.md](../skills/TRAE-spec-mode/SKILL.md) 第 4 节"输入与产物"，确认三件套格式要求
  2. 找一个同主题已完成 spec（如 `classics-knowledge/<已存在主题>/spec.md`）作为格式参照
  3. 新建时逐项对齐 frontmatter 字段、tasks 结构化字段
- **禁止行为**：
  - 凭记忆创建，不查规范文件
  - 创建 `checklist.md` 等非规范产物（所有检查点应写入 `tasks.md` 的 `Test Requirements`）
  - tasks.md 用纯 checkbox 列表而不加结构化字段
- **反模式**：
  - ❌ 只参考一个 spec 不参考 SKILL.md，遗漏 SKILL 中的最新要求
  - ❌ tasks.md 用 ` - [ ] xxx` 纯 checkbox 列表，缺少结构化字段（Requirement/Scenario/Test Requirements）
  - ❌ spec frontmatter 缺少 `methodology` / `content-sensitivity` 等必需字段

---

## 二、预检流程速查卡

创建新 spec 前，按顺序完成以下 2 项检查（总计约 2-3 分钟）：

```
┌─ 预检 1：位置 ──────────────────────────────────────────────┐
│ ① 读主题 README.md（如 classics-knowledge/README.md）      │
│ ② 确认 spec 应放的位置（子目录 vs 根目录）                 │
│ ③ 确认命名规律与已有 spec 一致                             │
└────────────────────────────────────────────────────────────┘
                          ↓
┌─ 预检 2：格式 ──────────────────────────────────────────────┐
│ ① 读 SKILL.md 第 4 节"输入与产物"                          │
│ ② 找同主题已完成 spec 作参照                               │
│ ③ 新建时逐项对齐 frontmatter + tasks 结构化字段            │
└────────────────────────────────────────────────────────────┘
```

---

## 三、违规后果

- 违反 RULE-SCP-001：spec 位置错误 → 需要批量更新路径引用，返工成本高
- 违反 RULE-SCP-002：产物格式漂移 → 后续工具（docgen/sphinx）无法正确解析，看板失效

两条规则均为**阻断性规则**——预检未完成前不得创建 spec 文件。

---

## 四、关联规范

- [Spec 文档编写指南](spec-writing-guide.md)：spec.md 的标准章节结构与格式要求
- [TRAE-spec-mode SKILL.md](../skills/TRAE-spec-mode/SKILL.md)：产物三件套的权威定义
- [修复即闭环](fix-prevent-close-loop.md)：本规则是 SPEC-LOCATION-ERROR 和 SPEC-FORMAT-DRIFT 两个错误的阶段 2 预防产出
