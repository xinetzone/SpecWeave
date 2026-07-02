---
id = "cmd-log-specification"
domain = "standards"
layer = "standards"
maturity = "L2"
validation_count = 3
reuse_count = 1
documentation_level = "detailed"
source = ".agents/skills/retrospective-cmd/SKILL.md#7, .agents/skills/insight-cmd/SKILL.md#7, .agents/skills/export-report-cmd/SKILL.md#7, .agents/skills/atomization-cmd/SKILL.md#7, .agents/skills/atomic-commit-cmd/SKILL.md#7, .agents/skills/pattern-extraction-cmd/SKILL.md#9, .agents/commands/mermaid.md#CMD-LOG"

[bindings]
rules = ["stage-guardrails.md"]
references = ["../skills/", "../../docs/retrospective/patterns/code-patterns/structured-lightweight-logging.md"]
skills = ["retrospective-cmd", "insight-cmd", "export-report-cmd", "atomization-cmd", "atomic-commit-cmd", "mermaid-cmd", "pattern-extraction-cmd"]
title: "CMD-LOG 命令集执行日志规范"
---
# CMD-LOG 命令集执行日志规范

## 1. 概述

CMD-LOG 是 SpecWeave 命令集（Skill门面）的结构化执行日志规范，是项目日志体系的第三类日志（继 SG-LOG 阶段守卫日志、PDR-LOG 前置文档读取日志之后），用于追踪6大命令集执行过程中的关键节点，支持故障排查、断点续传、执行审计和事后复盘。

本规范与项目已有的 [结构化轻量日志格式](../../docs/retrospective/patterns/code-patterns/structured-lightweight-logging.md) 模式保持一致，采用统一前缀+键值对+JSON上下文的单行格式，零依赖、grep友好、机器可解析。

## 2. 适用范围

本规范适用于以下7个命令集Skill门面：

| 命令集 | cmd标识 | Session ID前缀 | 步骤数 | 特有事件数 |
|--------|---------|---------------|--------|-----------|
| 复盘（retrospective） | `retrospective` | `retr-` | 6步（S0-S5） | 17个 |
| 洞察（insight） | `insight` | `insgt-` | 7步（S0-S6） | 18个 |
| 导出报告（export-report） | `export-report` | `exprt-` | 7步（S0-S6） | 19个 |
| 原子化（atomization） | `atomization` | `atom-` | 7步（S0-S6） | 22个 |
| 原子提交（atomic-commit） | `atomic-commit` | `cmt-` | 7步（S0-S6） | 20个 |
| Mermaid图表（mermaid） | `mermaid` | `merm-` | 7步（S0-S6） | 8个 |
| 模式萃取（pattern-extraction） | `pattern-extraction` | `ptrn-` | 6步（S0-S5） | 9个 |

> **新增命令集时**：必须遵循本规范添加CMD-LOG日志章节，定义该命令集的step编号、session ID前缀和特有事件枚举。

## 3. 日志格式

### 3.1 统一格式

```
[CMD-LOG] | level=<LEVEL> | cmd=<CMD_NAME> | step=<STEP_ID> | event=<EVENT> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
```

### 3.2 字段说明

| 字段 | 必填 | 说明 | 示例 |
|------|-----|------|------|
| `[CMD-LOG]` | ✅ | 日志前缀标识，grep时一行命令即可过滤命令集日志 | `[CMD-LOG]` |
| `level` | ✅ | 日志级别：DEBUG/INFO/WARN/ERROR | `INFO` |
| `cmd` | ✅ | 命令集标识，固定值见上表 | `retrospective` |
| `step` | ✅ | 当前执行步骤编号，格式 `S<N>` | `S3` |
| `event` | ✅ | 事件类型，大写下划线风格，见各命令集事件表 | `CMD_START` |
| `session` | ✅ | 会话ID，格式：`<prefix>-YYYYMMDD-<topic>` | `retr-20260629-firecrawl` |
| `msg` | ✅ | 中文人类可读消息，不依赖工具即可理解 | `开始复盘：project...` |
| `ctx` | ❌ | 压缩JSON上下文（单行无换行），键名使用英文 | `{"scope":"project",...}` |

### 3.3 分隔符约定

使用 `|` 作为字段分隔符，原因：
- `|` 在自然语言文本中出现频率极低，不易产生歧义
- 视觉上清晰分隔各字段
- 正则匹配简单：`([^|]+?)\s*` 即可提取字段值

### 3.4 Session ID格式规范

| 命令集 | 前缀 | 完整格式 | 示例 |
|--------|------|---------|------|
| retrospective | `retr-` | `retr-YYYYMMDD-<topic>` | `retr-20260629-firecrawl` |
| insight | `insgt-` | `insgt-YYYYMMDD-<topic>` | `insgt-20260629-architecture` |
| export-report | `exprt-` | `exprt-YYYYMMDD-<topic>` | `exprt-20260629-firecrawl-report` |
| atomization | `atom-` | `atom-YYYYMMDD-<filename>` | `atom-20260629-insight-export` |
| atomic-commit | `cmt-` | `cmt-YYYYMMDD-<short-hash>` | `cmt-20260629-a3f2b1` |
| mermaid | `merm-` | `merm-YYYYMMDD-<topic>` | `merm-20260630-architecture` |
| pattern-extraction | `ptrn-` | `ptrn-YYYYMMDD-<pattern-name>` | `ptrn-20260701-markdown-as-interface` |

## 4. 日志级别约定

| 级别 | 标识 | 使用场景 | 是否入交接文档 |
|------|------|---------|-------------|
| DEBUG | 🔍 | 细粒度调试（元数据提取、内容迁移细节、单项检查通过） | 否 |
| INFO | ℹ️ | 正常流程节点（命令开始/完成、步骤进入/完成、文件创建、提交执行） | 否 |
| WARN | ⚠️ | 异常但可恢复（数据不足、断链发现、无关文件、过度拆分警告） | **是** |
| ERROR | ❌ | 严重错误（源文件无效、敏感文件检测、提交失败、验证阻塞） | **是** |

## 5. 通用事件

所有命令集必须记录以下通用生命周期事件：

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 命令开始 | INFO | `CMD_START` | 开始\<命令\>：\<关键参数\> | 命令特有参数（见各命令集定义） |
| 进入步骤N | INFO | `STEP_ENTER` | 进入步骤\<N\>：\<步骤名称\> | 步骤特有参数 |
| 步骤N完成 | INFO | `STEP_COMPLETE` | 步骤\<N\>完成：\<结果摘要\> | 步骤结果数据（计数、状态等） |
| 命令完成 | INFO | `CMD_COMPLETE` | \<命令\>完成：\<结果摘要\>，总耗时：\<duration\> | duration, 结果统计字段 |
| 执行错误 | ERROR | `CMD_ERROR` | \<命令\>执行错误：\<错误描述\> | error_type, error_detail, failed_step, recovery_hint |

## 6. 步骤编号规范

每个命令集的步骤从 S0 开始编号，S0 固定为启动阶段，最后一步固定为归档/完成阶段：

| 步骤 | retrospective | insight | export-report | atomization | atomic-commit | mermaid | pattern-extraction |
|------|--------------|---------|---------------|-------------|---------------|---------|--------------------|
| S0 | 启动 | 启动 | 启动 | 启动 | 启动 | 启动与范围确认 | 启动与参数记录 |
| S1 | 收集事实 | 数据采集 | 验证源报告 | 源文件分析 | 检查范围 | 图表设计与类型选择 | 模式识别与分类 |
| S2 | 分析过程 | 趋势分析 | 准备内容 | 制定方案 | 预提交验证 | Mermaid代码生成 | 方案决策 |
| S3 | 提炼洞察 | 根因分析 | 格式转换 | 执行拆分 | 构建信息 | 语法检查 | 文档生成/更新 |
| S4 | 生成报告 | 异常检测 | 生成文件 | 更新引用 | 执行提交 | 自动修复 | 质量验证 |
| S5 | 归档沉淀 | 建议生成 | 归档索引 | 收尾验证 | 结果验证 | 质量验证 | 索引更新与归档 |
| S6 | — | 沉淀 | 链接验证 | 索引更新 | 推送通知 | 归档交付 | — |

## 7. 各命令集特有事件定义

### 7.1 复盘（retrospective）特有事件

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 发现根因/关键问题 | WARN | `KEY_FINDING` | 关键发现：\<问题描述\> | finding_type（success/failure/bottleneck）, severity |
| 萃取到可复用模式 | INFO | `PATTERN_EXTRACTED` | 萃取到可复用模式：\<模式名称\> | pattern_name, pattern_type, maturity |
| 行动项生成 | INFO | `ACTION_ITEM` | 生成行动项：\<描述\>，优先级：\<high/med/low\> | action_id, priority, owner（可空） |
| 报告生成完成 | INFO | `REPORT_GENERATED` | 复盘报告已生成：\<文件路径\>，含\<N\>个行动项 | report_path, action_count |
| 事实数据不足 | WARN | `DATA_INSUFFICIENT` | 事实数据不足：\<缺失描述\>，将基于有限信息继续 | missing_data, risk_level, mitigation |
| 模式沉淀跳过 | DEBUG | `PATTERN_SKIPPED` | 跳过模式沉淀：\<原因\> | pattern_name, skip_reason |

**典型日志示例**：

```
[CMD-LOG] | level=INFO | cmd=retrospective | step=S0 | event=CMD_START | session=retr-20260629-firecrawl | msg=开始复盘：project（Firecrawl深度学习），重点领域：产品架构、商业模式、Agent集成 | ctx={"scope":"project","focus_areas":["产品架构","商业模式","Agent集成"],"trigger":"用户明确请求复盘"}
[CMD-LOG] | level=INFO | cmd=retrospective | step=S3 | event=PATTERN_EXTRACTED | session=retr-20260629-firecrawl | msg=萃取到可复用模式：三源验证法 | ctx={"pattern_name":"triangular-source-verification","pattern_type":"methodology","maturity":"L1"}
[CMD-LOG] | level=INFO | cmd=retrospective | step=S5 | event=CMD_COMPLETE | session=retr-20260629-firecrawl | msg=复盘完成：project（Firecrawl学习），总耗时：约2小时 | ctx={"duration":"~2h","total_insights":8,"total_actions":6,"total_patterns":2}
```

### 7.2 洞察（insight）特有事件

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 数据质量低 | WARN | `DATA_QUALITY_LOW` | 数据质量不足：\<原因\>，可能影响分析结论 | quality_issue, confidence_level, mitigation |
| 发现异常拐点 | WARN | `ANOMALY_DETECTED` | 检测到异常拐点：\<时间点\>，变化幅度：\<幅度\> | inflection_point, change_magnitude, trend_direction |
| 根因定位 | WARN | `ROOT_CAUSE_FOUND` | 根因定位：第\<N\>层Why → \<根因描述\> | why_depth, root_cause, causal_chain（因果链） |
| 因果关系不确定 | DEBUG | `CAUSALITY_UNCERTAIN` | 因果关系不确定：\<相关性描述\>≠因果，需验证 | correlation, possible_confounders, verification_needed |
| 异常分级 | INFO | `ANOMALY_CLASSIFIED` | 异常分级：\<异常描述\> → \<等级：P0/P1/P2/P3\> | anomaly_desc, severity_level, affected_systems |
| 建议生成 | INFO | `RECOMMENDATION` | 建议生成：\<描述\>，优先级：\<high/med/low\>，预期收益：\<收益\> | rec_id, priority, expected_benefit, cost_estimate |

**典型日志示例**：

```
[CMD-LOG] | level=WARN | cmd=insight | step=S3 | event=ROOT_CAUSE_FOUND | session=insgt-20260629-architecture-priority | msg=根因定位：第3层Why → 缺乏Agent自发现能力，新会话需遍历目录树定位能力 | ctx={"why_depth":3,"root_cause":"缺乏Agent可发现的能力注册中心","causal_chain":["Agent需要能力→遍历目录→效率低→遗漏"]}
[CMD-LOG] | level=INFO | cmd=insight | step=S5 | event=RECOMMENDATION | session=insgt-20260629-architecture-priority | msg=建议生成：建立L0-L3四层能力发现机制，优先级：P0，预期收益：新会话冷启动时间减少80% | ctx={"rec_id":"rec-1","priority":"high","expected_benefit":"新会话冷启动时间减少80%","cost_estimate":"约2小时实施"}
```

### 7.3 导出报告（export-report）特有事件

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 源报告验证失败 | ERROR | `SOURCE_INVALID` | 源报告验证失败：\<失败原因\> | validation_errors, source_path, impact |
| 源报告验证通过 | INFO | `SOURCE_VALID` | 源报告验证通过：frontmatter完整，内容长度：\<chars\>字符 | frontmatter_fields, content_size, structure_ok |
| 元数据提取 | DEBUG | `METADATA_EXTRACTED` | 提取元数据：标题=\<title\>，日期=\<date\>，类型=\<type\> | title, date, report_type |
| 格式转换 | INFO | `FORMAT_CONVERT` | 格式转换完成：\<from\>→\<to\>，耗时：\<duration\> | from_format, to_format, duration |
| 格式转换失败 | ERROR | `CONVERT_FAILED` | 格式转换失败：\<格式\>，错误：\<原因\> | format, error_detail, fallback_action |
| 文件生成 | INFO | `FILE_WRITTEN` | 导出文件已写入：\<文件路径\>，大小：\<size\> | file_path, file_size, format |
| 索引更新 | INFO | `INDEX_UPDATED` | 目录索引已更新：\<README路径\>，新增\<N\>条记录 | index_path, added_entries |
| 链接验证结果 | INFO | `LINKS_CHECKED` | 链接验证完成：检查\<N\>个链接，\<M\>个断链 | total_links, broken_count, broken_files（如有） |
| 发现断链 | WARN | `BROKEN_LINKS` | 导出后发现\<N\>个断链，需要修复 | broken_count, broken_details |

**典型日志示例**：

```
[CMD-LOG] | level=INFO | cmd=export-report | step=S1 | event=SOURCE_VALID | session=exprt-20260629-firecrawl-report | msg=源报告验证通过：frontmatter完整，内容长度：12500字符 | ctx={"frontmatter_fields":["id","date","type","source"],"content_size":12500,"structure_ok":true}
[CMD-LOG] | level=WARN | cmd=export-report | step=S6 | event=BROKEN_LINKS | session=exprt-20260629-firecrawl-report | msg=导出后发现2个断链，需要修复 | ctx={"broken_count":2,"broken_details":["insight-extraction.md:14->insights/insight-1.md"]}
```

### 7.4 原子化（atomization）特有事件

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 预检结果 | INFO | `PRECHECK_RESULT` | 预检结果：\<覆盖/未覆盖\>，已存在模式：\<N\>个 | coverage_result, existing_patterns |
| 预检发现重复 | WARN | `DUPLICATE_FOUND` | 预检发现重复：已有模式\<名称\>覆盖此内容，建议更新而非新建 | duplicate_pattern, recommendation |
| 方案制定 | INFO | `SPLIT_PLAN` | 拆分方案：源文件→索引页，新建\<N\>个文件：\<文件列表\> | index_file, new_files, link_update_count |
| 过度拆分警告 | WARN | `OVER_SPLIT_WARN` | 拆分粒度警告：\<文件\>大小\<chars\>字符低于min_size阈值 | file_name, char_count, threshold, action |
| 新文件创建 | INFO | `FILE_CREATED` | 创建原子文件：\<文件路径\>，大小：\<size\>字符 | file_path, file_size, topic |
| 内容迁移 | DEBUG | `CONTENT_MOVED` | 内容迁移：\<源位置\>→\<目标文件\>，\<chars\>字符 | source_ref, target_file, char_count |
| frontmatter添加 | DEBUG | `FRONTMATTER_ADDED` | 添加frontmatter：source=\<source\> | file_path, source_trace |
| 链接修复 | INFO | `LINK_FIXED` | 修复链接：\<旧路径\>→\<新路径\>，影响\<N\>个文件 | old_path, new_path, affected_files |
| 收尾脚本执行 | INFO | `FINALIZE_RUN` | 执行finalize-atomization.py | script_args, exit_code |
| 链接验证结果 | INFO | `LINKS_CHECKED` | 链接验证：检查\<N\>个链接，\<M\>个断链（修复\<fixed\>个） | total_links, broken_before, fixed_count, remaining_broken |
| 发现断链 | WARN | `BROKEN_LINKS_FOUND` | 链接验证发现\<N\>个断链，需要修复 | broken_count, broken_details, auto_fix |
| 残留内容检测 | WARN | `RESIDUAL_FOUND` | 检测到源文件残留内容：\<描述\>，建议清理 | residual_desc, file_path, recommendation |

**典型日志示例**：

```
[CMD-LOG] | level=INFO | cmd=atomization | step=S2 | event=SPLIT_PLAN | session=atom-20260629-insight-export | msg=拆分方案：源文件→索引页，新建8个insight文件+6个action文件 | ctx={"index_file":"insight-extraction.md","new_files":["insights/insight-1.md",...],"link_update_count":25}
[CMD-LOG] | level=WARN | cmd=atomization | step=S5 | event=BROKEN_LINKS_FOUND | session=atom-20260629-insight-export | msg=链接验证：发现25个断链（相对路径层级错误），正在修复 | ctx={"total_links":45,"broken_before":25,"fixing":true}
[CMD-LOG] | level=INFO | cmd=atomization | step=S6 | event=CMD_COMPLETE | session=atom-20260629-insight-export | msg=原子化完成：insight-extraction.md→14个原子文件，总耗时：约30分钟 | ctx={"source_file":"insight-extraction.md","output_files":14,"duration":"~30min","link_status":"all valid"}
```

### 7.5 原子提交（atomic-commit）特有事件

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 变更范围检查 | INFO | `SCOPE_CHECK` | 变更范围检查：\<N\>个文件，类型：\<add/modify/delete\> | changed_files, file_types, single_concern（是否单一职责） |
| 发现无关文件 | WARN | `UNRELATED_FILES` | 发现无关文件混入变更：\<文件列表\>，需排除 | unrelated_files, action |
| 敏感文件检测 | ERROR | `SENSITIVE_FILE` | 检测到敏感文件：\<文件\>，禁止提交！ | sensitive_file, risk_level |
| 临时文件检测 | WARN | `TEMP_FILE_FOUND` | 检测到临时文件：\<文件\>，应加入.gitignore | temp_file, recommendation |
| vendor目录变更 | WARN | `VENDOR_CHANGE` | 检测到vendor/目录变更，需确认是否为子模块更新 | vendor_files, is_submodule_update |
| 验证项通过 | DEBUG | `CHECK_PASS` | 验证通过：\<检查项名称\> | check_name, duration |
| 验证项失败 | WARN | `CHECK_FAIL` | 验证失败：\<检查项名称\>，错误：\<原因\> | check_name, error_detail, blocking（是否阻塞） |
| 验证失败阻塞提交 | ERROR | `VERIFICATION_BLOCKED` | 预提交验证阻塞：\<失败项\>，需要修复后继续 | failed_checks, fix_required |
| 提交信息构建 | INFO | `COMMIT_MSG_BUILT` | 提交信息构建完成：\<type\>(\<scope\>): \<subject\> | full_message, commit_type, scope, subject_length |
| 提交信息不合规 | WARN | `MSG_NONCOMPLIANT` | 提交信息不合规：\<问题描述\>，建议修正 | issue, suggested_fix |
| 执行提交 | INFO | `COMMIT_EXECUTED` | 提交执行成功：commit \<hash\>，\<N\>个文件变更 | commit_hash, files_committed, insertions, deletions |
| 提交失败 | ERROR | `COMMIT_FAILED` | 提交执行失败：\<错误信息\> | error, retry_hint |
| 提交验证通过 | INFO | `COMMIT_VERIFIED` | 提交验证通过：\<hash\>信息正确，无遗漏文件 | commit_hash, log_verified, status_clean |

**典型日志示例**：

```
[CMD-LOG] | level=WARN | cmd=atomic-commit | step=S1 | event=UNRELATED_FILES | session=cmt-20260629-a3f2b1 | msg=发现无关文件混入变更：playground.log，需排除 | ctx={"unrelated_files":["playground.log"],"action":"exclude"}
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S3 | event=COMMIT_MSG_BUILT | session=cmt-20260629-a3f2b1 | msg=提交信息构建完成：feat(skills): 新增5个命令集Skill门面增强能力发现 | ctx={"full_message":"feat(skills): 新增5个命令集Skill门面增强能力发现","commit_type":"feat","scope":"skills","subject_length":22}
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S4 | event=COMMIT_EXECUTED | session=cmt-20260629-a3f2b1 | msg=提交执行成功：commit a3f2b1c，6个文件变更 | ctx={"commit_hash":"a3f2b1c","files_committed":6,"insertions":280,"deletions":12}
```

### 7.6 Mermaid图表（mermaid）特有事件

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 图表类型确定 | INFO | `DIAGRAM_DESIGNED` | 设计完成：\<diagram_type\>，复杂度：\<complexity\>，模板：\<template\> | diagram_type, complexity, template_used |
| 代码生成完成 | INFO | `CODE_GENERATED` | Mermaid代码生成完成：\<节点数\>个节点，使用模板：\<template\> | node_count, edge_count, template_used |
| 语法检查完成 | INFO/WARN | `CHECK_COMPLETED` | 语法检查完成：发现\<N\>个错误，\<M\>个警告 | error_count, warning_count, issues |
| 自动修复应用 | INFO | `FIX_APPLIED` | 自动修复应用：修复了\<N\>个问题（空行/引号/换行符） | fixed_count, fix_types |
| 验证通过 | INFO | `VERIFY_PASSED` | 质量验证通过：渲染正确，规范合规 | validator, render_target |
| 验证失败 | WARN | `VERIFY_FAILED` | 验证失败：\<原因\>，需要返工 | failure_reason, failed_step |
| 模板推荐 | INFO | `TEMPLATE_RECOMMENDED` | 推荐模板：\<template_name\>，适用场景：\<scenario\> | template_name, scenario, alternatives |
| 团队协作触发 | INFO | `TEAM_COLLABORATION` | 触发团队协作：\<原因\>，参与角色：\<roles\> | reason, roles, complexity |

**典型日志示例**：

```
[CMD-LOG] | level=INFO | cmd=mermaid | step=S0 | event=CMD_START | session=merm-20260630-architecture | msg=开始创建Mermaid图表：架构流程图，复杂度：complex | ctx={"operation":"create","diagram_type":"flowchart","complexity":"complex","target_file":".agents/capabilities/ARCHITECTURE.md"}
[CMD-LOG] | level=INFO | cmd=mermaid | step=S4 | event=FIX_APPLIED | session=merm-20260630-architecture | msg=自动修复应用：修复了3个问题（空行2处、引号补全1处） | ctx={"fixed_count":3,"fix_types":["空行","引号"]}
[CMD-LOG] | level=INFO | cmd=mermaid | step=S6 | event=CMD_COMPLETE | session=merm-20260630-architecture | msg=Mermaid图表完成：三层架构流程图已插入文档 | ctx={"duration":"~15min","node_count":12,"subgraph_count":3,"verification":"passed"}
```

## 8. 输出要求

1. **即时输出**：事件发生时立即输出，不得延迟到步骤结束批量输出
2. **单行输出**：每条日志必须在一行内，ctx JSON压缩为单行（无换行、无额外空格）
3. **中文消息**：msg字段使用中文，ctx键名使用英文
4. **不替代交互**：日志是辅助排查工具，不替代面向用户的正式输出
5. **ctx精简**：ctx只记录对排查问题有用的关键数据，不输出大段内容
6. **错误必记**：所有ERROR级别事件必须记录，且ctx中必须包含recovery_hint

## 9. 日志解析

一条正则即可解析所有CMD-LOG日志：

```python
import re
import json

CMD_LOG_RE = re.compile(
    r'\[CMD-LOG\]\s*\|\s*'
    r'level=(\w+)\s*\|\s*'
    r'cmd=(\w+(?:-\w+)?)\s*\|\s*'
    r'step=(S\d+)\s*\|\s*'
    r'event=(\w+)\s*\|\s*'
    r'session=([^|]+?)\s*\|\s*'
    r'msg=([^|]+?)(?:\s*\|\s*ctx=(.+))?$'
)

def parse_cmd_log(line: str) -> dict | None:
    m = CMD_LOG_RE.match(line.strip())
    if not m:
        return None
    result = {
        'level': m.group(1),
        'cmd': m.group(2),
        'step': m.group(3),
        'event': m.group(4),
        'session': m.group(5),
        'msg': m.group(6),
        'ctx': {}
    }
    ctx_str = m.group(7)
    if ctx_str:
        try:
            result['ctx'] = json.loads(ctx_str)
        except json.JSONDecodeError:
            result['ctx'] = {'_raw': ctx_str}
    return result
```

ctx字段用 `json.loads()` 解析，失败时降级为raw存储。

## 10. 过滤与分析命令

常用日志分析命令：

```bash
# 过滤所有CMD-LOG日志
grep "\[CMD-LOG\]" output.log

# 过滤某个命令集的日志
grep "\[CMD-LOG\].*cmd=retrospective" output.log

# 过滤某个会话的完整执行链路
grep "session=retr-20260629-firecrawl" output.log

# 过滤所有错误事件
grep "\[CMD-LOG\].*level=ERROR" output.log

# 过滤所有警告事件
grep "\[CMD-LOG\].*level=WARN" output.log

# 统计各命令集执行次数
grep "event=CMD_START" output.log | grep -oP 'cmd=\K[^|]+' | sort | uniq -c

# 查看某个会话的耗时
grep "session=retr-20260629-firecrawl.*event=CMD_COMPLETE" output.log | grep -oP 'ctx=\{.*"duration":"[^"]+"'
```

## 11. 实施检查清单

新增命令集Skill门面时，必须完成以下检查项：

- [ ] 定义命令集的 `cmd` 标识和 `session` ID前缀
- [ ] 定义步骤编号（S0-Sn）及每个步骤的名称
- [ ] 定义通用事件（CMD_START/STEP_ENTER/STEP_COMPLETE/CMD_COMPLETE/CMD_ERROR）的消息模板和ctx字段
- [ ] 定义命令集特有事件的枚举（封闭集合）
- [ ] 提供至少3条真实日志示例（包含正常流程+WARN/ERROR场景）
- [ ] 在SKILL.md的"执行日志规范"章节中记录上述内容
- [ ] 在本规范文档中同步更新步骤表、特有事件定义和示例

## 12. 与其他日志类型的关系

SpecWeave 项目日志体系：

| 日志类型 | 前缀 | 适用场景 | 文档 |
|---------|------|---------|------|
| 阶段守卫日志 | SG-LOG | 开发流程阶段边界拦截、跳转审批 | [.agents/rules/stage-guardrails.md](stage-guardrails.md) |
| 前置文档读取日志 | PDR-LOG | 必读文档读取确认、缺失告警 | [.agents/protocols/pre-document-reading.md](../protocols/pre-document-reading.md) |
| **命令集执行日志** | **CMD-LOG** | **6大命令集Skill门面执行追踪** | **本文件** |

三类日志共享相同的格式规范（前缀+键值对+JSON ctx），但前缀、字段集合和事件枚举各自封闭，解析脚本按前缀分发。

## 13. Changelog

- **v1.2.0** (2026-06-30): 新增mermaid命令集注册，包含7步流程定义、8个特有事件、Session ID前缀`merm-`及典型日志示例，命令集总数从5个扩展为6个。
- **v1.1.0** (2026-06-30): 5个命令集SKILL全部完成三层架构重构，L1层CMD-LOG章节精简为概要+L2引用模式，retrospective/export-report（v1.1）+ insight/atomization/atomic-commit（v1.2）共减少重复内容约260行。
- **v1.0.0** (2026-06-30): 初始版本，从5个Skill门面提取并规范化CMD-LOG日志标准，包含通用格式、字段说明、级别约定、通用事件、各命令集特有事件定义、解析正则和分析命令。
