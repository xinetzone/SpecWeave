---
name: export-report-cmd
version: 1.1.0
description: "当用户提到'导出报告'、'export'、'生成报告'、'导出文档'、'输出报告'、'正式报告'、'归档'、'导出为'时，必须使用此技能。提供结构化报告导出能力：验证源报告→准备内容→格式转换→输出归档。支持复盘报告、洞察报告、总结报告等多种类型。不要手动拼接报告输出——本Skill封装了报告格式规范和frontmatter要求。"
argument-hint: "<报告类型：retrospective/insight/summary/custom> <源文件路径>"
user-invocable: true
paths:
  - ".agents/commands/export-report.md"
  - "docs/retrospective/reports/"
---

# Export-Report 导出报告命令 Skill

> ⚠️ **本Skill是命令入口门面**，详细步骤见 [.agents/commands/export-report.md](../../commands/export-report.md)。
> 门面只做发现和路由，不重复完整流程定义。

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

**与其他Skill的关系**：
- 通常在 `retrospective-cmd` 或 `insight-cmd` 完成后调用
- 报告过大需要拆分时，先使用 `atomization-cmd` 原子化

## 5. 快速开始

```
步骤1：读取 [.agents/commands/export-report.md](../../commands/export-report.md) 了解完整流程
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

## 6. 安全检查清单（导出质量门）

- [ ] 源报告已验证（文件存在、frontmatter完整、结构正确）
- [ ] 报告分类目录正确（参考 docs/retrospective/reports/ 下的现有分类）
- [ ] 报告文件命名符合规范（英文小写、连字符分隔、含日期）
- [ ] 内部链接在目标位置仍然有效（路径相对深度正确）
- [ ] frontmatter的source字段正确指向源文件/事件
- [ ] 对应目录的README索引已更新（新增报告已加入列表）
- [ ] 导出后运行了链接检查，无断链

## 7. 执行日志规范（CMD-LOG）

执行导出报告命令集时，必须在关键节点输出结构化日志：

```
[CMD-LOG] | level=<LEVEL> | cmd=export-report | step=<STEP_ID> | event=<EVENT> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
```

**字段说明**：
- `level`：日志级别（INFO/WARN/ERROR/DEBUG）
- `cmd`：固定为 `export-report`
- `step`：当前步骤（S0=启动/S1=验证源报告/S2=准备内容/S3=格式转换/S4=生成文件/S5=归档索引/S6=链接验证）
- `event`：事件类型
- `session`：会话ID（格式：`exprt-YYYYMMDD-<topic>`）
- `msg`：人类可读描述
- `ctx`：JSON格式上下文（不含换行）

**必须记录的事件**：

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 命令开始 | INFO | CMD_START | 开始导出报告：<report_type>，源文件：<source>，格式：<formats> | report_type, source_path, formats, target_dir |
| 进入步骤1 | INFO | STEP_ENTER | 进入步骤1：验证源报告 | source_path |
| 源报告验证失败 | ERROR | SOURCE_INVALID | 源报告验证失败：<失败原因> | validation_errors, source_path, impact |
| 源报告验证通过 | INFO | SOURCE_VALID | 源报告验证通过：frontmatter完整，内容长度：<chars>字符 | frontmatter_fields, content_size, structure_ok |
| 步骤1完成 | INFO | STEP_COMPLETE | 步骤1完成：源报告验证通过 | validation_result |
| 进入步骤2 | INFO | STEP_ENTER | 进入步骤2：准备导出内容 | metadata_fields |
| 元数据提取 | DEBUG | METADATA_EXTRACTED | 提取元数据：标题=<title>，日期=<date>，类型=<type> | title, date, report_type |
| 步骤2完成 | INFO | STEP_COMPLETE | 步骤2完成：内容准备完毕，正文<N>字符，附件<M>个 | content_size, attachment_count |
| 进入步骤3 | INFO | STEP_ENTER | 进入步骤3：格式转换，目标格式：<formats> | target_formats |
| 格式转换 | INFO | FORMAT_CONVERT | 格式转换完成：<from>→<to>，耗时：<duration> | from_format, to_format, duration |
| 格式转换失败 | ERROR | CONVERT_FAILED | 格式转换失败：<格式>，错误：<原因> | format, error_detail, fallback_action |
| 进入步骤4 | INFO | STEP_ENTER | 进入步骤4：生成导出文件 | output_path |
| 文件生成 | INFO | FILE_WRITTEN | 导出文件已写入：<文件路径>，大小：<size> | file_path, file_size, format |
| 进入步骤5 | INFO | STEP_ENTER | 进入步骤5：归档与索引更新 | index_path |
| 索引更新 | INFO | INDEX_UPDATED | 目录索引已更新：<README路径>，新增<N>条记录 | index_path, added_entries |
| 进入步骤6 | INFO | STEP_ENTER | 进入步骤6：链接有效性验证 | verify_path |
| 链接验证结果 | INFO | LINKS_CHECKED | 链接验证完成：检查<N>个链接，<M>个断链 | total_links, broken_count, broken_files（如有） |
| 发现断链 | WARN | BROKEN_LINKS | 导出后发现<N>个断链，需要修复 | broken_count, broken_details |
| 命令完成 | INFO | CMD_COMPLETE | 报告导出完成：<输出路径>，格式：<formats>，总耗时：<duration> | output_dir, formats, duration, link_status |
| 导出错误 | ERROR | CMD_ERROR | 导出执行错误：<错误描述> | error_type, error_detail, failed_step, recovery_hint |

**日志示例**：

```
[CMD-LOG] | level=INFO | cmd=export-report | step=S0 | event=CMD_START | session=exprt-20260629-firecrawl-report | msg=开始导出报告：retrospective，源文件：insight-extraction.md，格式：md | ctx={"report_type":"retrospective","source_path":"docs/retrospective/reports/.../README.md","formats":["md"],"target_dir":"docs/retrospective/reports/insight-extraction/"}
[CMD-LOG] | level=INFO | cmd=export-report | step=S1 | event=SOURCE_VALID | session=exprt-20260629-firecrawl-report | msg=源报告验证通过：frontmatter完整，内容长度：12500字符 | ctx={"frontmatter_fields":["id","date","type","source"],"content_size":12500,"structure_ok":true}
[CMD-LOG] | level=INFO | cmd=export-report | step=S4 | event=FILE_WRITTEN | session=exprt-20260629-firecrawl-report | msg=导出文件已写入：docs/retrospective/reports/.../README.md，大小：15KB | ctx={"file_path":"docs/retrospective/reports/.../README.md","file_size":"15KB","format":"md"}
[CMD-LOG] | level=WARN | cmd=export-report | step=S6 | event=BROKEN_LINKS | session=exprt-20260629-firecrawl-report | msg=导出后发现2个断链，需要修复 | ctx={"broken_count":2,"broken_details":["insight-extraction.md:14->insights/insight-1.md"]}
[CMD-LOG] | level=INFO | cmd=export-report | step=S6 | event=CMD_COMPLETE | session=exprt-20260629-firecrawl-report | msg=报告导出完成：docs/retrospective/reports/...，格式：md，总耗时：约10分钟 | ctx={"output_dir":"docs/retrospective/reports/...","formats":["md"],"duration":"~10min","link_status":"fixed"}
```

> **为什么需要日志？** 报告导出涉及文件写入、路径转换和索引更新，是"出了问题最难排查"的环节——文件已经复制了但路径引用错了、索引更新了但链接是断的。日志记录了每一步的输入输出和验证结果，可以快速定位是源文件问题、格式转换问题还是路径问题。

## 8. 报告目录分类参考

| 报告类型 | 存放目录 |
|---------|---------|
| 外部产品/技术学习复盘 | docs/retrospective/reports/competitive-analysis/ |
| 原子化执行复盘 | docs/retrospective/reports/atomization/ |
| 治理/规范/规则复盘 | docs/retrospective/reports/governance/ |
| 架构评估/重构复盘 | docs/retrospective/reports/insight-extraction/ |

完整目录结构见 [docs/retrospective/reports/README.md](../../../docs/retrospective/reports/README.md)。

## 9. 关键参考

| 参考 | 路径 | 何时查阅 |
|------|------|---------|
| 完整命令文档 | [.agents/commands/export-report.md](../../commands/export-report.md) | 每次使用必读 |
| CMD-LOG日志规范 | [cmd-log-specification.md](../../../docs/standards/cmd-log-specification.md) | 日志格式、事件定义、解析方法 |
| 复盘报告目录 | [docs/retrospective/reports/](../../../docs/retrospective/reports/) | 确定输出位置 |
| 报告分类规范 | [docs/retrospective/reports/README.md](../../../docs/retrospective/reports/README.md) | 分类存放时 |
| 导出四通道渐进模式 | [export-four-channel-progressive.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/export-four-channel-progressive.md) | 理解导出策略 |
| 链接验证脚本 | [check-links.py](../../scripts/check-links.py) | 导出后验证 |

## 10. Changelog

- **v1.1.0** (2026-06-29): 添加CMD-LOG结构化日志规范，定义19个关键日志事件。
- **v1.0.0** (2026-06-29): 初始版本（Skill门面），基于export-report命令集封装。
