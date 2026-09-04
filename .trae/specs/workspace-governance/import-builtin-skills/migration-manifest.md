---
source: ".trae/specs/workspace-governance/import-builtin-skills/spec.md；实测命令 external/dao/xinzo/.trae-cn/builtin（2026-09-03 两次独立盘点交叉验证）"
date: "2026-09-03"
type: "manifest"
title: "import-builtin-skills 迁移清单（冻结）"
---

# import-builtin-skills 迁移清单

## 盘点结论

- 五源目录全部 SKILL.md 按键名聚合：**唯一技能名 = 24**
- 跳过既有同名 3 个：`TRAE-plan-mode`、`TRAE-spec-mode`（项目中文五要素适配版，git 已跟踪）、`trae-computer-use-ptc`（磁盘既有的小写中文适配版，**git 未跟踪**，含 paths/x-toml-ref、无 source；Windows 大小写不敏感 FS 下早期 LS 显示为大写，属同一物理目录）
- **本次新增导入 = 21 个技能目录**，合计约 **750 文件 / 17.9MB**
- 源目录 `external/dao/xinzo/.trae-cn/builtin/` **只读**，本次仅复制不搬移
- **基线修正（Task 7 实测）**：导入前磁盘含 SKILL.md 目录 32（30 已跟踪 + 小写 trae-computer-use-ptc 未跟踪 + 被忽略 alipay-aipay）；导入 21 后为 **53**，无 manifest 之外的多余新增。被跳过的 computer-use-ptc 一律保持现状，未纳入暂存与提交

## 选择规则（确定性）

对每个技能名，跨五目录与全部 profile 收集候选，按 **总字节 ↓ → 文件数 ↓ → 源路径字典序 asc** 取唯一入选版本。

## 冻结映射（21）

### work 办公/文档家族（8）

| 技能名 | 入选源（仓库根相对） | 目标目录 | 文件数 | 大小KB |
|---|---|---|---|---|
| doc-writing-guide | external/dao/xinzo/.trae-cn/builtin/work/default/skills/doc-writing-guide | .agents/skills/doc-writing-guide | 3 | 65 |
| docx | external/dao/xinzo/.trae-cn/builtin/work/iphigenia/skills/docx | .agents/skills/docx | 65 | 1186 |
| html-deck | external/dao/xinzo/.trae-cn/builtin/work/default/skills/html-deck | .agents/skills/html-deck | 189 | 1904 |
| html-report | external/dao/xinzo/.trae-cn/builtin/work/default/skills/html-report | .agents/skills/html-report | 108 | 9078 |
| pdf | external/dao/xinzo/.trae-cn/builtin/work/iphigenia/skills/pdf | .agents/skills/pdf | 14 | 117 |
| pptx | external/dao/xinzo/.trae-cn/builtin/work/default/skills/pptx | .agents/skills/pptx | 85 | 1889 |
| research-guide | external/dao/xinzo/.trae-cn/builtin/work/default/skills/research-guide | .agents/skills/research-guide | 3 | 35 |
| xlsx | external/dao/xinzo/.trae-cn/builtin/work/iphigenia/skills/xlsx | .agents/skills/xlsx | 53 | 1120 |

### global 通用家族（6）

| 技能名 | 入选源 | 目标目录 | 文件数 | 大小KB |
|---|---|---|---|---|
| TRAE-browseruse | external/dao/xinzo/.trae-cn/builtin/global/skills/TRAE-browseruse | .agents/skills/TRAE-browseruse | 1 | 28 |
| TRAE-browseruse-external | external/dao/xinzo/.trae-cn/builtin/global/skills/TRAE-browseruse-external | .agents/skills/TRAE-browseruse-external | 1 | 29 |
| TRAE-code-mode-orchestrator | external/dao/xinzo/.trae-cn/builtin/global/skills/TRAE-code-mode-orchestrator | .agents/skills/TRAE-code-mode-orchestrator | 3 | 26 |
| TRAE-computer-use | external/dao/xinzo/.trae-cn/builtin/global/skills/TRAE-computer-use | .agents/skills/TRAE-computer-use | 1 | 6 |
| digital-avatar-creator | external/dao/xinzo/.trae-cn/builtin/global/skills/digital-avatar-creator | .agents/skills/digital-avatar-creator | 1 | 17 |
| dynamic-ui | external/dao/xinzo/.trae-cn/builtin/global/skills/dynamic-ui | .agents/skills/dynamic-ui | 57 | 567 |

### design 设计家族（4）

| 技能名 | 入选源 | 目标目录 | 文件数 | 大小KB |
|---|---|---|---|---|
| design-library-creator | external/dao/xinzo/.trae-cn/builtin/design/default/skills/design-library-creator | .agents/skills/design-library-creator | 47 | 812 |
| solo-design | external/dao/xinzo/.trae-cn/builtin/design/default/skills/solo-design | .agents/skills/solo-design | 108 | 1335 |
| solo-graphic-generation | external/dao/xinzo/.trae-cn/builtin/design/default/skills/solo-graphic-generation | .agents/skills/solo-graphic-generation | 4 | 29 |
| solo-image-edit | external/dao/xinzo/.trae-cn/builtin/design/default/skills/solo-image-edit | .agents/skills/solo-image-edit | 4 | 22 |

### code 基建家族（3，跨族去重后统一复制一份）

| 技能名 | 入选源 | 目标目录 | 文件数 | 大小KB |
|---|---|---|---|---|
| feedback | external/dao/xinzo/.trae-cn/builtin/code/default/skills/feedback | .agents/skills/feedback | 1 | 30 |
| skill-creator | external/dao/xinzo/.trae-cn/builtin/code/default/skills/skill-creator | .agents/skills/skill-creator | 1 | 3 |
| TRAE-product-knowledge | external/dao/xinzo/.trae-cn/builtin/code/default/skills/TRAE-product-knowledge | .agents/skills/TRAE-product-knowledge | 1 | 5 |

## 合计核对

- 文件数：8 家族 520 + global 64 + design 163 + infra 3 = **750**
- 体积：15394 + 673 + 2198 + 38 = **18303KB ≈ 17.9MB**
