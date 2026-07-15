---
name: forum-posting
version: 1.2.0
description: "Discourse论坛（forum.trae.cn）自动化操作。当用户需要发帖、编辑帖子、更新帖子、回复帖子、跟帖、发布论坛内容、清理草稿、读取帖子、操作forum.trae.cn、使用forum-bot脚本时，必须使用此技能。支持双方案：forum-bot.py（Playwright脚本，本地/CI首选，支持dry-run预览、幂等检查、登录持久化）和integrated_browser MCP（IDE内即时操作，零配置）。覆盖读取、编辑替换、开头追加（如日期标记）、回复、清理草稿全流程。不要手动拼接浏览器操作——本Skill封装了双方案选择逻辑和安全防线。"
argument-hint: "<操作类型> [帖子URL/ID]"
user-invocable: true
paths:
  - ".agents/scripts/forum-bot.py"
  - "docs/knowledge/operations/forum-automation.md"
  - ".agents/commands/forum-posting.md"
title: "论坛发帖与维护 (Forum Posting)"
x-toml-ref: "../../../.meta/toml/.agents/skills/forum-posting/SKILL.toml"
---
# 论坛发帖与维护 (Forum Posting)

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<200行，触发词+决策树+核心步骤+安全清单）
> - L2：[forum-automation.md](../../docs/knowledge/operations/forum-automation.md)（DOM选择器+JS函数+完整MCP步骤+故障排查）

## 1. Skill ID
`forum-posting`

## 2. 功能描述

操作 forum.trae.cn（Discourse 论坛）的技能，提供**双方案支持**，由技能根据场景自动选择，也可由用户指定：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **forum-bot.py** | ⭐ 独立运行/命令行/CI，需要 dry-run 预览 | 登录持久化、幂等检查、自动重试、完善日志 |
| **integrated_browser MCP** | ⭐ Trae IDE 内即时操作 | 零配置、复用浏览器已登录状态、可交互调试 |

核心功能：读取帖子、编辑正文（完整替换）、开头追加（如更新日期标记）、发布回复、清理草稿。

> **为什么双方案？** forum-bot.py 适合可重复、可验证的操作（推荐写操作先用它 dry-run）；MCP 适合 IDE 内快速交互式操作。两者覆盖不同使用场景，不冲突。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "发帖"、"发布"、"更新论坛"、"更新帖子"、"编辑帖子"、"修改帖子"
- "回复帖子"、"跟帖"、"发布回复"、"清理草稿"、"删除草稿"
- "读取帖子"、"查看帖子"、"forum-bot"、"Playwright脚本"
- 任何涉及 forum.trae.cn 的操作请求

> **关于触发**：即使没有明确说"用 skill"，只要涉及论坛操作就应该使用本技能，不要自己手动拼接浏览器操作。

## 4. 方案选择决策树

```
需要操作论坛？
├─ 在 Trae IDE 内临时操作、浏览器已登录？ → MCP方案（第5节核心步骤）
├─ 需要独立运行/命令行/CI/dry-run预览？ → forum-bot.py方案（第6节命令速查）
└─ 首次使用未登录？ → 先 forum-bot.py login 保存状态
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `forum-YYYYMMDD-<topic>`）：
```
[CMD-LOG] | level=INFO | cmd=forum-posting | step=S0 | event=CMD_START | session=forum-... | msg=开始论坛操作：<操作类型> <topic_id/URL> | ctx={"operation":"...","topic_id":"...","method":"auto/script/mcp","dry_run":true/false}
```

> **为什么决策前必须记录日志？** 论坛帖子一旦发布对外可见，双方案选择（script vs MCP）和dry-run决策直接影响安全性。CMD_START记录原始参数，操作失误后可回溯"当时选了什么方案、有没有开dry-run"。

**写操作（编辑/回复）原则**：优先使用 forum-bot.py 的 `--dry-run` 预览内容，确认无误再正式执行。

> **为什么 dry-run 是最重要的安全防线？** 论坛帖子一旦发布就对外可见，错误的编辑或回复无法"悄悄撤销"——修改会被记录为编辑历史，删除也会留下痕迹。dry-run 在完全不提交的情况下展示完整内容，是成本最低的防误操作手段。MCP 方案无内置 dry-run，必须先向用户展示 diff 并获得明确确认。

## 5. 核心步骤（快速开始）

```
步骤1：读取L2知识库 docs/knowledge/operations/forum-automation.md（DOM选择器可能随Discourse更新）
步骤2：通过决策树选择方案（script/mcp/auto）
步骤3：确认登录状态
步骤4：写操作必须先dry-run/展示diff → 获得用户明确确认
步骤5：执行操作（脚本参数或MCP步骤序列）
步骤6：验证结果（刷新/snapshot确认内容生效）
步骤7：清理草稿（编辑/回复后自动执行）
```

> 完整MCP操作步骤（JavaScript工具函数、DOM选择器、9.1-9.6详细序列）见L2知识库第4-6章。

## 6. 常用命令速查（forum-bot.py）

脚本路径：[forum-bot.py](../../scripts/forum-bot.py)

```bash
cd d:\spaces\SpecWeave

# 首次登录（浏览器打开后手动登录，回终端按Enter）
python .agents/scripts/forum-bot.py login

# 读取帖子
python .agents/scripts/forum-bot.py read 44601

# 编辑帖子（先dry-run预览！）
python .agents/scripts/forum-bot.py edit 44601 --file new-content.md --dry-run
python .agents/scripts/forum-bot.py edit 44601 --file new-content.md

# 开头追加（如更新日期标记，内置幂等检查防重复）
python .agents/scripts/forum-bot.py edit 44601 --prepend "📅 最新更新：2026年7月1日"

# 发布回复（先dry-run！）
python .agents/scripts/forum-bot.py reply 44601 --content "回复内容" --dry-run
python .agents/scripts/forum-bot.py reply 44601 --file reply.md

# 清理草稿
python .agents/scripts/forum-bot.py clean-drafts
```

> 完整参数表、脚本内置安全机制（幂等检查/自动重试/内容校验）见L2知识库第2-3章。

## 7. 安全检查清单（逐项确认）

- [ ] 已读知识库 [forum-automation.md](../../docs/knowledge/operations/forum-automation.md)（选择器可能更新）
- [ ] 登录状态已确认（多信号检测：Discourse全局变量+meta标签+头像链接）
- [ ] **写操作已 dry-run 预览**（脚本：`--dry-run`；MCP：先展示diff并获得确认）
- [ ] **幂等性检查已执行**（prepend 操作确认内容不存在；编辑操作确认不会意外覆盖）
- [ ] 内容已向用户展示并获得**明确确认**
- [ ] 操作间隔≥3秒（避免429频率限制）
- [ ] 保存/回复按钮已正确区分（保存无`.create`，回复有`.create`）
- [ ] MCP方案设置textarea后触发了input/change事件（否则Discourse不认）
- [ ] 操作完成后验证了结果（刷新/snapshot确认内容生效）
- [ ] 操作完成后检查并清理了草稿

## 8. 执行日志（CMD-LOG）

执行论坛操作时按CMD-LOG规范输出：
- `cmd=forum-posting`，session前缀 `forum-YYYYMMDD-<topic_id>`
- 步骤编号 S0-S7（启动→方案选择→登录→dry-run→执行→验证→清草稿→完成）
- 7个特有事件：`SCHEME_SELECTED`、`LOGIN_REQUIRED`、`DRY_RUN_OK`、`BUTTON_CONFUSION_RISK`、`IDEMPOTENT_SKIP`、`VERIFY_PASS`、`DRAFTS_CLEANED`

> 完整字段说明、事件表格、MCP方案特殊注意事项（:has-text()不可用、按钮区分等）见L2知识库；日志格式规范见 [cmd-log-specification.md](../../rules/cmd-log-specification.md)。

## 9. 常见错误处理

| 错误码 | 场景 | 处理方式 |
|--------|------|---------|
| FORUM_001 | 登录丢失 | 脚本：重新login；MCP：提示在浏览器中手动登录 |
| FORUM_002 | 找不到编辑按钮 | wait延长到3秒，滚动到帖子可见区域；脚本有多选择器兜底 |
| FORUM_003 | 保存按钮无效 | 检查：文本精确"保存"且排除`.create`类 |
| FORUM_006 | 429频率限制 | 间隔增加到5秒，等待Retry-After |
| FORUM_007 | JS语法错误（MCP） | 只用标准DOM API，不用`:has-text()` |
| FORUM_010 | prepend被跳过 | 内容已存在，正常现象无需操作 |

> 完整错误码表（FORUM_001~FORUM_010）见L2知识库第8章。

## 10. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **forum-bot.py优先于integrated_browser**：本地脚本方案内置dry-run预览、幂等检查、自动重试和完善的日志记录，写操作（编辑/回复）应优先选择forum-bot.py。MCP方案适合IDE内快速只读操作或临时交互调试。
- **登录态持久化在.browser_data/目录**：首次login成功后，Playwright会将浏览器状态（cookies/localStorage）保存在`.browser_data/`目录下。不要删除此目录，否则需要重新手动登录；此目录已加入.gitignore，不要提交到仓库。
- **内容替换使用唯一old_string**：使用Edit工具进行内容替换时，old_string必须在帖子正文中唯一匹配。如果有多处相同文本，替换会失败。遇到重复内容时，应扩大上下文范围使old_string唯一。
- **发帖前必须dry-run预览**：Playwright支持无头模式（headless）dry-run，会打开浏览器渲染完整内容但不会实际点击提交按钮。正式发帖前务必先用dry-run确认内容格式、换行、链接都正确。
- **日期标记追加在帖子开头**：使用prepend功能追加日期标记时，内容会被插入到帖子最开头（在标题之后、正文之前）。脚本内置幂等检查，如果标记已存在会自动跳过，不用担心重复追加。

## 11. 已管理帖子

| 名称 | URL | topic_id |
|------|-----|----------|
| SpecWeave Demo帖 | https://forum.trae.cn/t/topic/44601 | 44601 |
| SpecWeave报名帖 | https://forum.trae.cn/t/topic/44402 | 44402 |

## 12. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 论坛自动化知识库（DOM/JS/步骤） | L2 | [forum-automation.md](../../docs/knowledge/operations/forum-automation.md) | 每次MCP操作必读，选择器更新时查阅 |
| CMD-LOG日志规范 | L2 | [cmd-log-specification.md](../../rules/cmd-log-specification.md) | 日志格式、事件定义 |
| forum-bot.py 脚本 | 工具 | [forum-bot.py](../../scripts/forum-bot.py) | 脚本参数、debug模式 |

## 13. Changelog

- **v1.2.0** (2026-07-01): 遵循markdown-as-interface v2.0六要素标准+L1门面模式重构：删除废弃字段disable-model-invocation；添加L0/L1/L2三层架构引用块；决策前添加CMD_START强制日志；添加CMD-LOG执行日志章节（7个特有事件，L2引用模式）；将174行详细MCP步骤/JS工具函数/DOM选择器表迁移到L2知识库，SKILL.md从312行精简到~170行；核心步骤采用5步快速开始格式；添加关键参考索引表；常见错误精简为6个高频错误（完整错误码见L2）。
- **v1.1.1** (2026-06-29): 合规修复：绝对路径改为相对路径；统一Why解释格式；安全检查清单增加幂等性显式项。
- **v1.1.0** (2026-06-29): 新增forum-bot.py双方案支持；补充方案选型决策树；整合可复用JS工具函数；增加已管理帖子索引。
- **v1.0.0** (2026-06-29): 初始版本，支持编辑/回复/清理草稿（MCP方案）。
