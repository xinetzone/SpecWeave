---
name: export-report-cmd
version: 1.3.0
description: "当用户提到'导出报告'、'export'、'生成报告'、'导出文档'、'输出报告'、'正式报告'、'归档'、'导出为'时，必须使用此技能。提供结构化报告导出能力：验证源报告→准备内容→格式转换→输出归档。支持复盘报告、洞察报告、总结报告等多种类型。不要手动拼接报告输出——本Skill封装了报告格式规范和frontmatter要求。"
argument-hint: "<报告类型：retrospective/insight/summary/custom> <源文件路径>"
user-invocable: true
paths:
  - ".agents/commands/export-report.md"
  - "docs/retrospective/reports/"
  - "rules/cmd-log-specification.md"
---

# Export-Report 导出报告命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/export-report.md](../../commands/export-report.md)（完整流程）+ [cmd-log-specification.md](../../rules/cmd-log-specification.md)（日志规范）

## 1. Skill ID
`export-report-cmd`

## 2. 功能描述

提供结构化报告导出能力，完成"验证→转换→输出→归档"流程：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **Markdown导出** | ⭐ 默认导出格式 | 原生格式、版本控制友好、可继续编辑 |
| **结构化导出** | ⭐ 需要机器处理/数据分析 | JSON格式提取结构化数据 |
| **多格式导出** | 需要对外分享/正式发布 | 支持PDF/DOCX等（当前MD优先） |

核心功能：验证源报告完整性→提取元数据和内容→格式转换→生成目录索引→输出到指定目录。

> **为什么用本Skill而非手动输出？** 手动导出容易遗漏frontmatter、忘记更新索引、格式不符合归档规范；本Skill封装了报告验证、格式规范和目录更新流程，确保输出的报告符合项目标准。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "导出报告"、"导出"、"export"、"导出文档"
- "生成报告"、"输出报告"、"正式报告"
- "归档"、"存档"、"保存报告"
- "导出为..."、"转成..."（格式转换）
- 复盘/洞察/分析完成后需要正式输出

> **关于触发**：通常在 retrospective-cmd 或 insight-cmd 执行完成后使用，作为知识沉淀的最后一步。不是所有分析都需要正式导出——快速对话中的分析结论可以直接回复，只有需要归档沉淀时才使用本Skill。

## 4. 方案选择决策树

```
需要导出报告？
├─ 报告用于项目内归档/版本控制？ → Markdown导出（默认，.md格式）
├─ 需要提取结构化数据做分析？ → JSON格式导出
├─ 需要对外分享/打印？ → 多格式导出（PDF/DOCX，需额外工具支持）
├─ 复盘报告导出？ → 放在 docs/retrospective/reports/ 对应分类目录
├─ 洞察/分析报告？ → 放在对应分类目录，更新索引README
└─ 不确定放哪里？ → 参考 docs/retrospective/reports/ 现有目录结构分类
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `exp-YYYYMMDD-<topic>`）：
```
[CMD-LOG] | level=INFO | cmd=export-report | step=S0 | event=CMD_START | session=exp-... | msg=开始报告导出：<简述> | ctx={"source":"...","report_type":"retrospective/insight/summary"}
```

> **为什么决策前必须记录日志？** 报告导出涉及格式转换，导出类型错误会产生格式不正确的文档，CMD_START记录源和类型便于回溯。

**与其他Skill的关系**：
- 通常在 `retrospective-cmd` 或 `insight-cmd` 完成后调用
- 报告过大需要拆分时，先使用 `atomization-cmd` 原子化

## 5. 核心步骤（快速开始）

```
步骤1：读取 [commands/export-report.md](../../commands/export-report.md) 了解完整流程
步骤2：验证源报告：
   - 源文件存在且内容完整
   - frontmatter包含必要字段（id、date、type、source）
   - 报告结构符合规范（标题层级、章节完整）
步骤3：准备导出内容：
   - 提取元数据（标题、日期、类型）
   - 整理正文内容
   - 收集关联附件/图表
   - 生成目录索引
步骤4：格式转换与输出：
   - Markdown：直接复制到目标目录，确保路径引用正确
   - JSON：提取结构化数据输出
步骤5：更新对应目录的README索引
步骤6：导出完成后运行 check-links.py 验证链接有效性
```

> 完整RACI矩阵、输入参数规范、约束条件见L2文档 [commands/export-report.md](../../commands/export-report.md)。

> **为什么导出后必须运行链接检查？** 报告导出时文件路径会发生变化（源位置→归档目录），相对路径的层级深度随之改变，即使原始报告中所有链接都有效，位置迁移后也可能产生断链。断链在归档后很难被发现（浏览归档报告的人不会主动测试每个链接），而在导出步骤立即运行check-links.py可以在问题产生的第一时间修复，成本最低。

## 6. 安全检查清单（导出质量门）

- [ ] 源报告已验证（文件存在、frontmatter完整、结构正确）
- [ ] 报告分类目录正确（参考 docs/retrospective/reports/ 下的现有分类）
- [ ] 报告文件命名符合规范（英文小写、连字符分隔、含日期）
- [ ] 内部链接在目标位置仍然有效（路径相对深度正确）
- [ ] frontmatter的source字段正确指向源文件/事件
- [ ] 对应目录的README索引已更新（新增报告已加入列表）
- [ ] 导出后运行了链接检查，无断链

> **为什么frontmatter必须包含source溯源字段？** 归档报告是知识沉淀的最终形态，如果没有source字段记录报告来源（如哪次复盘、哪个对话、哪个事件），几个月后回看报告时无法追溯产生背景，也就无法验证结论在当前上下文是否仍然适用。source是报告的"出生证明"，确保知识可追溯、可验证、可更新。

## 7. 执行日志（CMD-LOG）

执行导出报告命令集时，必须按 [CMD-LOG规范](../../rules/cmd-log-specification.md) 输出结构化日志：
- `cmd=export-report`，session前缀 `exprt-YYYYMMDD-<topic>`
- 步骤编号 S0-S6（启动→验证源报告→准备内容→格式转换→生成文件→归档索引→链接验证）
- 9个特有事件：`SOURCE_INVALID`、`SOURCE_VALID`、`METADATA_EXTRACTED`、`FORMAT_CONVERT`、`CONVERT_FAILED`、`FILE_WRITTEN`、`INDEX_UPDATED`、`LINKS_CHECKED`、`BROKEN_LINKS`

> 完整字段说明、事件表格、日志示例见L2文档 [cmd-log-specification.md §7.3](../../rules/cmd-log-specification.md)。

## 8. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **导出后必须运行check-links验证链接**：文件从工作位置移动到归档目录后，相对路径的层级深度发生改变（例如从`.agents/skills/xxx/`到`docs/retrospective/reports/yyy/`），原来有效的`../`链接会全部失效。导出步骤完成后第一时间运行链接检查，此时修复成本最低。
- **frontmatter的source字段是必填项**：source是归档报告的"出生证明"，记录报告来源（哪次复盘、哪个对话、哪个事件）。几个月后回看报告时，如果没有source字段就无法追溯产生背景，也就无法验证结论在当前上下文是否仍然适用。
- **报告分类目录参考现有结构**：不要随意创建新的分类目录，先查看`docs/retrospective/reports/`下已有的目录结构。新增分类会破坏索引一致性，导致后续归档和检索混乱。确需新分类时先在团队内达成共识。
- **Markdown是默认导出格式**：PDF/DOCX等格式需要额外工具支持（如Pandoc），且版本控制不友好（二进制文件无法diff）。当前阶段优先导出Markdown格式，确保报告可编辑、可追溯、可版本对比。
- **导出路径变化会破坏相对链接**：导出到不同目录深度时，相对链接中的`../`层数必须相应调整。例如源文件在根目录使用`docs/xxx.md`，导出到`docs/reports/`后需要改为`../xxx.md`。这也是导出后必须运行链接检查的核心原因。

## 9. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整命令文档（RACI/参数/约束） | L2 | [commands/export-report.md](../../commands/export-report.md) | 每次使用必读 |
| CMD-LOG日志规范 | L2 | [cmd-log-specification.md](../../rules/cmd-log-specification.md) | 日志格式、事件定义、解析方法 |
| 报告目录分类 | L2 | [docs/retrospective/reports/README.md](../../../docs/retrospective/reports/README.md) | 确定输出位置和分类 |
| 导出四通道渐进模式 | L2 | [export-four-channel-progressive.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/export-four-channel-progressive.md) | 理解导出策略 |
| 链接验证脚本 | L1工具 | [check-links.py](../../scripts/check-links.py) | 导出后验证 |

## 10. Changelog

- **v1.3.0** (2026-07-01): 在§4决策树后添加S0 CMD_START强制日志规范，记录触发时的输入参数（source/report_type）便于回溯导出类型决策；补充第3个Why解释（frontmatter source溯源字段的必要性）。
- **v1.2.1** (2026-06-30): 补充Why设计意图解释（导出后链接检查必要性），通过质量检查why.explanations≥2要求。
- **v1.2.0** (2026-06-30): 按渐进式披露三层架构重构，将CMD-LOG详细事件表迁移至L2规范文档，报告目录分类引用L2 README，SKILL.md精简为L1门面。
- **v1.1.0** (2026-06-29): 添加CMD-LOG结构化日志规范，定义19个关键日志事件。
- **v1.0.0** (2026-06-29): 初始版本（Skill门面），基于export-report命令集封装。
