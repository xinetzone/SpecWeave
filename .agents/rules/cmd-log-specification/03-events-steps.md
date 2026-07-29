---
id: "cmd-log-events-steps"
title: "通用事件、步骤编号与命令集特有事件"
source: "cmd-log-specification.md#03-events-steps"
x-toml-ref: "../../../.meta/toml/.agents/rules/cmd-log-specification/03-events-steps.toml"
---
# 通用事件、步骤编号与命令集特有事件

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


## 8. 强制日志纪律（不可跳过）

> **背景**：基于2026-07-28对抗审查wiki同步任务复盘发现，执行命令集/Skill门面时跳过S0 CMD_START首条日志，导致执行链路断裂、事后复盘无法追踪完整过程。此问题属于流程执行偏差，违反规范设计初衷，特此制定强制纪律条款。

### 8.1 首条日志铁律

**触发场景**：调用任何已注册CMD-LOG的命令集Skill门面（retrospective/insight/export-report/atomization/atomic-commit/mermaid/pattern-extraction）时。

| 条款 | 内容 | 级别 |
|------|------|------|
| **铁律一** | **S0 CMD_START 必须是命令集执行后的第一条输出**。在CMD_START日志行输出之前，禁止执行任何实质性操作（文件读写、代码修改、工具调用、网络请求、脚本执行），也禁止输出任何非CMD-LOG格式的内容。 | 🔴 强制 |
| **铁律二** | CMD_START 必须包含完整的 `ctx` 字段，记录本次执行的关键参数（命令类型、作用范围、触发来源、目标文件/目录等），确保仅通过S0日志即可理解本次命令"要做什么"。 | 🔴 强制 |
| **铁律三** | 步骤连续性：步骤之间必须成对出现 `STEP_ENTER` → 业务执行 → `STEP_COMPLETE`，禁止跳过STEP_ENTER直接执行步骤内容（轻量DEBUG日志除外）。 | 🟡 强烈建议 |
| **铁律四** | CMD_COMPLETE / CMD_ERROR 必须是命令集执行的最后一条输出，且必须与开头的CMD_START具有相同的 `session` ID，形成闭环。 | 🔴 强制 |
| **铁律五** | 如果命令执行过程中因异常中断或流程违规而未输出CMD_COMPLETE/CMD_ERROR，必须在后续任务复盘中手动补全CMD-LOG链路（参见§8.4事后补全规范）。 | 🟡 强烈建议 |

### 8.2 违规判定标准

出现以下任一情况即判定为日志断裂违规：

1. ❌ 命令集被调用后，第一条输出不是 `[CMD-LOG] | level=INFO | cmd=<name> | step=S0 | event=CMD_START | ...`
2. ❌ 执行过程中出现实质性工具调用（Edit/Write/Shell/Read等），但此前未输出对应步骤的STEP_ENTER
3. ❌ 命令执行结束（提交完成/报告生成/文件输出）但未输出CMD_COMPLETE
4. ❌ 输出了STEP_ENTER但对应步骤未输出STEP_COMPLETE就直接进入下一步骤（异常中断除外，但异常时须输出CMD_ERROR）
5. ❌ session ID在执行过程中发生变化（同一命令调用内session必须唯一且不变）

### 8.3 正确示例 vs 错误示例

**✅ 正确**：
```
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S0 | event=CMD_START | session=cmt-20260728-abc123 | msg=开始原子提交：修复wiki链接错误 | ctx={"files":"docs/wiki.md","type":"fix","dry_run":false}
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S1 | event=STEP_ENTER | session=cmt-20260728-abc123 | msg=进入步骤S1：三查暂存验证
...（执行git status检查）
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S1 | event=STEP_COMPLETE | session=cmt-20260728-abc123 | msg=步骤S1完成：暂存区2个文件，范围清晰
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S4 | event=COMMIT_EXECUTED | session=cmt-20260728-abc123 | msg=提交执行成功：commit a1b2c3d
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S5 | event=CMD_COMPLETE | session=cmt-20260728-abc123 | msg=原子提交完成：commit a1b2c3d，2文件变更 | ctx={"commit":"a1b2c3d","result":"success"}
```

**❌ 错误（首条日志缺失）**：
```
（直接开始执行git status/Edit等操作，没有任何CMD_START输出）
$ git status
On branch main...
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S4 | event=COMMIT_EXECUTED | ...
（缺少S0-S3的日志链，无法追溯执行过程）
```

### 8.4 事后补全规范

若因流程违规导致日志断裂（如本次事件），必须：

1. 创建任务复盘目录（`retrospective-<topic>-<date>/execution-retrospective.md`）
2. 在复盘中按时间线补全完整的CMD-LOG链路（使用反引号包裹，标注 `[事后补全]`）
3. 在"根因分析"章节明确标注"日志断裂违规"及根因
4. 在"预防措施"章节引用本节规范，承诺后续遵守
5. 提交补全文件本身也必须遵守CMD-LOG规范

---

## 相关模式

- - [阶段守卫规范](../stage-guardrails.md)
- - [PDR前置文档读取协议](../../protocols/pre-document-reading.md)
- - [结构化轻量日志格式](../../docs/retrospective/patterns/code-patterns/structured-lightweight-logging.md)

← 上一章: [日志格式与级别约定](02-format-levels.md) | **[返回索引](../cmd-log-specification.md)** | 下一章 → [输出要求、日志解析与过滤分析](04-output-parsing.md)
