---
name: atomization-cmd
version: 1.1.0
description: "当用户提到'原子化'、'拆分文件'、'atomize'、'拆分大文档'、'文件拆分'、'拆分成多个文件'、'单一职责'、'文档重构'、'拆分文档'时，必须使用此技能。提供文档与代码的原子化拆分能力：分析源文件→制定拆分方案→执行拆分→修复链接→收尾验证。不要手动拆分文件——本Skill封装了链接修复、索引更新、一致性检查等必要步骤。"
argument-hint: "<目标类型：document/code/config> <源文件路径>"
user-invocable: true
paths:
  - ".agents/commands/atomization.md"
  - ".agents/scripts/finalize-atomization.py"
  - ".agents/scripts/check-atomization-coverage.py"
---

# Atomization 原子化命令 Skill

> ⚠️ **本Skill是命令入口门面**，详细步骤见 [.agents/commands/atomization.md](../../commands/atomization.md)。
> 门面只做发现和路由，不重复完整流程定义。

## 1. Skill ID
`atomization-cmd`

## 2. 功能描述

提供文档与代码的原子化拆分能力，确保拆分后的文件遵循单一职责原则：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **文档原子化** | ⭐ 大文档拆分（如复盘报告、长规范） | 单一主题、易维护、可独立引用 |
| **原子化+收尾** | ⭐ 拆分完成后的一键收尾 | 自动修复断链+更新导航+刷新看板 |
| **原子化预检** | 创建新模式前的覆盖度检查 | 避免重复创建已有模式 |

核心功能：分析源文件结构→制定拆分策略→创建原子文件→迁移内容→更新交叉引用→一键收尾。

> **为什么用本Skill而非手动拆分？** 手动拆分最大的陷阱是链接断裂——文件移动后相对路径错误导致大量断链，修复成本非线性增长（跳过5分钟的规范可能导致30分钟返工）。本Skill配合finalize-atomization.py自动处理链接修复、导航更新、看板刷新。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "原子化"、"拆分"、"atomize"、"拆分文件"
- "拆分大文档"、"拆分大文件"、"文件拆分"、"拆分成多个文件"
- "单一职责"、"文档重构"、"文档拆分"
- "把这个文件拆一下"、"内容太多拆分一下"
- 文档内容超过500行、职责不单一、多个主题混在一起
- 复盘报告需要拆分insights/actions等子模块

> **关于触发**：原子化是高风险操作（涉及文件创建/移动/链接修改），必须使用本Skill确保流程规范。拆分前先用check-atomization-coverage.py预检，拆分后必须用finalize-atomization.py收尾。

## 4. 方案选择决策树

```
需要进行原子化拆分？
├─ 拆分前预检（检查是否已有模式覆盖）？ → 先运行 check-atomization-coverage.py
├─ 拆分文档（Markdown报告/规范等）？ → 文档原子化流程
├─ 拆分完成需要收尾？ → finalize-atomization.py 一键执行
├─ 原子化后需要检查一致性？ → check-atomization-duplication.py 检查残留内容
└─ Git提交原子化结果？ → 拆分完成后使用 atomic-commit-cmd
```

## 5. 快速开始

```
步骤1：读取 [.agents/commands/atomization.md](../../commands/atomization.md) 了解完整流程
步骤2：预检阶段：
   - 运行 check-atomization-coverage.py 确认新内容未被已有模式覆盖
   - 分析源文件的核心主题和结构
   - 确定拆分策略（按主题/功能/模块/组件）
步骤3：制定拆分方案：
   - 规划新文件的命名和目录结构
   - 设计文件间的引用关系
   - 将源文件转为索引页
步骤4：执行拆分：
   - 创建新的原子文件（每个文件单一主题）
   - 添加正确的frontmatter（含source溯源字段）
   - 迁移内容到对应文件
步骤5：收尾阶段（关键！）：
   - 运行 finalize-atomization.py 自动修复断链+更新导航+刷新看板
   - 运行 check-links.py 验证所有链接有效
   - 运行 check-atomization-duplication.py 检查源文件无残留深度内容
```

## 6. 安全检查清单（原子化质量门）

- [ ] 拆分前已做coverage预检，确认没有重复创建已有模式
- [ ] 每个新文件遵循单一职责原则（一个文件一个主题）
- [ ] 新文件frontmatter包含source字段（溯源到原始文档）
- [ ] 源文件转为索引页，包含子模块导航链接
- [ ] 文件命名符合规范（英文小写、连字符分隔）
- [ ] **已运行 finalize-atomization.py 收尾**（这是最重要的步骤）
- [ ] 链接验证通过（check-links.py无断链）
- [ ] 无内容残留（源文件不保留已拆分到子文件的深度内容）
- [ ] 相关README/索引已更新（新增文件出现在目录列表中）

> **为什么finalize-atomization.py是强制步骤？** 原子化最常见的问题就是相对路径错误导致断链。finalize-atomization.py自动处理：断链检测与修复、导航表更新、Spec看板刷新，避免手动修复的遗漏和错误。

## 7. 执行日志规范（CMD-LOG）

执行原子化命令集时，必须在关键节点输出结构化日志：

```
[CMD-LOG] | level=<LEVEL> | cmd=atomization | step=<STEP_ID> | event=<EVENT> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
```

**字段说明**：
- `level`：日志级别（INFO/WARN/ERROR/DEBUG）
- `cmd`：固定为 `atomization`
- `step`：当前步骤（S0=启动/S1=源文件分析/S2=制定方案/S3=执行拆分/S4=更新引用/S5=收尾验证/S6=索引更新）
- `event`：事件类型
- `session`：会话ID（格式：`atom-YYYYMMDD-<filename>`）
- `msg`：人类可读描述
- `ctx`：JSON格式上下文（不含换行）

**必须记录的事件**：

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 命令开始 | INFO | CMD_START | 开始原子化：<target_type>，源文件：<source>，策略：<strategy> | target_type, source_path, split_strategy, max_size |
| 进入步骤1 | INFO | STEP_ENTER | 进入步骤1：源文件分析 | source_path, source_size |
| 预检结果 | INFO | PRECHECK_RESULT | 预检结果：<覆盖/未覆盖>，已存在模式：<N>个 | coverage_result, existing_patterns |
| 预检发现重复 | WARN | DUPLICATE_FOUND | 预检发现重复：已有模式<名称>覆盖此内容，建议更新而非新建 | duplicate_pattern, recommendation |
| 源文件分析完成 | INFO | STEP_COMPLETE | 步骤1完成：识别<N>个可拆分单元，建议拆为<M>个文件 | unit_count, suggested_file_count, structure_type |
| 进入步骤2 | INFO | STEP_ENTER | 进入步骤2：制定拆分方案 | planned_files |
| 方案制定 | INFO | SPLIT_PLAN | 拆分方案：源文件→索引页，新建<N>个文件：<文件列表> | index_file, new_files, link_update_count |
| 过度拆分警告 | WARN | OVER_SPLIT_WARN | 拆分粒度警告：<文件>大小<chars>字符低于min_size阈值 | file_name, char_count, threshold, action |
| 步骤2完成 | INFO | STEP_COMPLETE | 步骤2完成：拆分方案已制定，含<N>个新文件 | total_new_files, total_links_to_update |
| 进入步骤3 | INFO | STEP_ENTER | 进入步骤3：执行拆分 | files_to_create |
| 新文件创建 | INFO | FILE_CREATED | 创建原子文件：<文件路径>，大小：<size>字符 | file_path, file_size, topic |
| 内容迁移 | DEBUG | CONTENT_MOVED | 内容迁移：<源位置>→<目标文件>，<chars>字符 | source_ref, target_file, char_count |
| frontmatter添加 | DEBUG | FRONTMATTER_ADDED | 添加frontmatter：source=<source> | file_path, source_trace |
| 步骤3完成 | INFO | STEP_COMPLETE | 步骤3完成：创建<N>个文件，迁移<M>字符内容 | files_created, total_chars_migrated |
| 进入步骤4 | INFO | STEP_ENTER | 进入步骤4：更新引用 | links_to_fix |
| 链接修复 | INFO | LINK_FIXED | 修复链接：<旧路径>→<新路径>，影响<N>个文件 | old_path, new_path, affected_files |
| 进入步骤5 | INFO | STEP_ENTER | 进入步骤5：收尾验证 | scripts_to_run |
| 收尾脚本执行 | INFO | FINALIZE_RUN | 执行finalize-atomization.py | script_args, exit_code |
| 链接验证结果 | INFO | LINKS_CHECKED | 链接验证：检查<N>个链接，<M>个断链（修复<fixed>个） | total_links, broken_before, fixed_count, remaining_broken |
| 发现断链 | WARN | BROKEN_LINKS_FOUND | 链接验证发现<N>个断链，需要修复 | broken_count, broken_details, auto_fix |
| 残留内容检测 | WARN | RESIDUAL_FOUND | 检测到源文件残留内容：<描述>，建议清理 | residual_desc, file_path, recommendation |
| 步骤5完成 | INFO | STEP_COMPLETE | 步骤5完成：收尾验证通过，链接<M>个有效，无残留 | valid_links, residual_status |
| 命令完成 | INFO | CMD_COMPLETE | 原子化完成：<source>→<N>个原子文件，总耗时：<duration> | source_file, output_files, duration, link_status |
| 拆分错误 | ERROR | CMD_ERROR | 原子化执行错误：<错误描述> | error_type, error_detail, failed_step, recovery_hint |

**日志示例**：

```
[CMD-LOG] | level=INFO | cmd=atomization | step=S0 | event=CMD_START | session=atom-20260629-insight-export | msg=开始原子化：document，源文件：insight-extraction.md，策略：topic | ctx={"target_type":"document","source_path":"docs/retrospective/reports/.../insight-extraction.md","split_strategy":"topic","max_size":5000}
[CMD-LOG] | level=INFO | cmd=atomization | step=S2 | event=SPLIT_PLAN | session=atom-20260629-insight-export | msg=拆分方案：源文件→索引页，新建8个insight文件+6个action文件 | ctx={"index_file":"insight-extraction.md","new_files":["insights/insight-1.md",...,"actions/action-1.md",...],"link_update_count":25}
[CMD-LOG] | level=INFO | cmd=atomization | step=S4 | event=LINK_FIXED | session=atom-20260629-insight-export | msg=修复链接：../insights/→insights/，影响14个文件 | ctx={"old_path":"../insights/","new_path":"insights/","affected_files":14}
[CMD-LOG] | level=WARN | cmd=atomization | step=S5 | event=BROKEN_LINKS_FOUND | session=atom-20260629-insight-export | msg=链接验证：发现25个断链（相对路径层级错误），正在修复 | ctx={"total_links":45,"broken_before":25,"fixing":true}
[CMD-LOG] | level=INFO | cmd=atomization | step=S6 | event=CMD_COMPLETE | session=atom-20260629-insight-export | msg=原子化完成：insight-extraction.md→14个原子文件，总耗时：约30分钟 | ctx={"source_file":"insight-extraction.md","output_files":14,"duration":"~30min","link_status":"all valid"}
```

> **为什么需要日志？** 原子化是最高风险的文件操作（创建/移动/修改大量文件），断链问题具有非线性返工成本。日志记录了每个文件的创建、每处链接的修复，当出现"为什么这个链接断了"或"为什么这个内容被移走了"时，可以精确回溯是哪个步骤、哪个操作导致的。

## 8. 关键脚本速查

| 脚本 | 用途 | 何时使用 |
|------|------|---------|
| check-atomization-coverage.py | 预检：检查模式库是否已有覆盖 | 拆分前必运行 |
| finalize-atomization.py | 一键收尾：修链接+更新导航+刷看板 | 拆分完成后必运行 |
| check-atomization-duplication.py | 检查：源文件残留内容 | 收尾后验证 |
| check-links.py | 链接有效性验证 | 收尾后验证 |

## 9. 关键参考

| 参考 | 路径 | 何时查阅 |
|------|------|---------|
| 完整命令文档 | [.agents/commands/atomization.md](../../commands/atomization.md) | 每次使用必读 |
| CMD-LOG日志规范 | [cmd-log-specification.md](../../../docs/standards/cmd-log-specification.md) | 日志格式、事件定义、解析方法 |
| 原子化三标准测试 | [atomization-three-criteria-test.md](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/atomization-three-criteria-test.md) | 判断是否需要拆分 |
| 原子化三层分类 | [atomization-three-tier-classification.md](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/atomization-three-tier-classification.md) | 确定拆分粒度 |
| 收尾脚本 | [finalize-atomization.py](../../scripts/finalize-atomization.py) | 拆分后必执行 |
| 覆盖度预检脚本 | [check-atomization-coverage.py](../../scripts/check-atomization-coverage.py) | 拆分前必执行 |

## 10. Changelog

- **v1.1.0** (2026-06-29): 添加CMD-LOG结构化日志规范，定义21个关键日志事件。
- **v1.0.0** (2026-06-29): 初始版本（Skill门面），基于atomization命令集封装。
