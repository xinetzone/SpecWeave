---
name: forum-posting
version: 1.1.0
description: "Discourse论坛（forum.trae.cn）自动化操作。当用户需要发帖、编辑帖子、更新帖子、回复帖子、跟帖、发布论坛内容、清理草稿、读取帖子、操作forum.trae.cn、使用forum-bot脚本时，必须使用此技能。支持双方案：forum-bot.py（Playwright脚本，本地/CI首选，支持dry-run预览、幂等检查、登录持久化）和integrated_browser MCP（IDE内即时操作，零配置）。覆盖读取、编辑替换、开头追加（如日期标记）、回复、清理草稿全流程。"
argument-hint: "<操作类型> [帖子URL/ID]"
disable-model-invocation: false
user-invocable: true
paths:
  - docs/knowledge/operations/forum-automation.md
  - .agents/scripts/forum-bot.py
---

# 论坛发帖与维护 (Forum Posting)

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

## 4. 方案选择决策

```
需要操作论坛？
├─ 在 Trae IDE 内临时操作、浏览器已登录？ → MCP方案（第7节）
├─ 需要独立运行/命令行/CI/dry-run预览？ → forum-bot.py方案（第6节）
└─ 首次使用未登录？ → 先 forum-bot.py login 保存状态
```

**写操作（编辑/回复）原则**：优先使用 forum-bot.py 的 `--dry-run` 预览内容，确认无误再正式执行。

> **为什么 dry-run 是最重要的安全防线？** 论坛帖子一旦发布就对外可见，错误的编辑或回复无法"悄悄撤销"——修改会被记录为编辑历史，删除也会留下痕迹。dry-run 在完全不提交的情况下展示完整内容，是成本最低的防误操作手段。脚本方案内置 `--dry-run` 标志；MCP 方案无内置 dry-run，必须先向用户展示 diff 并获得明确确认。

## 5. 输入参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| operation | string | 是 | - | `read_post`/`edit_post`/`prepend_update`/`create_reply`/`clean_drafts`/`login` |
| topic_url | string | 否 | - | 帖子URL（edit/reply/read/prepend 必填） |
| topic_id | number | 否 | - | 帖子ID（如44601），与URL二选一 |
| content | string | 否 | - | 帖子/回复内容（Markdown） |
| content_file | string | 否 | - | 从Markdown文件读取内容（脚本方案） |
| prepend_text | string | 否 | - | prepend模式追加到开头的文本 |
| dry_run | boolean | 否 | false | 试运行不提交（**写操作强烈建议先开**） |
| method | string | 否 | auto | `auto`/`script`/`mcp` |

## 6. 已管理帖子

| 名称 | URL | topic_id |
|------|-----|----------|
| SpecWeave Demo帖 | https://forum.trae.cn/t/topic/44601 | 44601 |
| SpecWeave报名帖 | https://forum.trae.cn/t/topic/44402 | 44402 |

## 7. 依赖与前置准备

- **必读知识库**：[forum-automation.md](../../../docs/knowledge/operations/forum-automation.md)（DOM选择器可能随Discourse更新，始终以此为准）
- **forum-bot.py 依赖**：Python 3.8+，`pip install playwright && playwright install chromium`，首次运行 `python .agents/scripts/forum-bot.py login` 保存登录状态
- **MCP 依赖**：Trae IDE 内置浏览器已登录 forum.trae.cn，integrated_browser MCP 可用
- **操作间隔**：≥3秒，避免触发429频率限制（脚本内置此延迟，MCP操作需手动wait）

> **为什么操作间隔≥3秒？** Discourse有频率限制机制，短时间大量请求会返回429并可能临时封禁IP。脚本内置了延迟，但MCP操作需要Agent自行控制节奏。

## 8. 方案一：forum-bot.py（推荐写操作使用）

脚本路径：[forum-bot.py](../../scripts/forum-bot.py)

### 8.1 常用命令速查

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
python .agents/scripts/forum-bot.py edit 44601 --prepend "📅 最新更新：2026年6月29日"

# 发布回复（先dry-run！）
python .agents/scripts/forum-bot.py reply 44601 --content "回复内容" --dry-run
python .agents/scripts/forum-bot.py reply 44601 --file reply.md

# 清理草稿
python .agents/scripts/forum-bot.py clean-drafts

# 调试模式（详细日志）
python .agents/scripts/forum-bot.py --debug read 44601
```

### 8.2 脚本内置安全机制

- **dry-run**：所有写操作支持 `--dry-run`，展示内容但不提交——这是防止误操作的最重要防线
- **幂等检查**：`--prepend` 自动检测内容是否已存在，避免重复添加相同的日期标记
- **自动重试**：点击失败时自动重试（最多2次），含滚动到视图和JS click兜底
- **内容校验**：填写textarea后验证长度匹配，避免内容丢失
- **自动草稿清理**：编辑/回复后自动清理Discourse自动保存的草稿
- **日志记录**：控制台彩色输出 + 文件日志（`.agents/scripts/logs/`），便于排障

> 完整参数表和更多用法见知识库文档第2章。

## 9. 方案二：integrated_browser MCP（IDE内操作）

> **为什么不能用 :has-text()？** :has-text() 是 Playwright 的非标准选择器扩展，不是标准 DOM API。MCP 的 browser_evaluate 直接在浏览器页面上下文中执行原生 JavaScript，不经过 Playwright 选择器引擎，因此 :has-text()、:visible 等 Playwright 扩展选择器均不可用，必须使用 querySelector/querySelectorAll + 标准 CSS 选择器 + 文本过滤。

### 9.1 通用前置步骤（所有MCP操作必须执行）

```
步骤1: 读取知识库 docs/knowledge/operations/forum-automation.md
步骤2: browser_navigate → https://forum.trae.cn，wait 2秒
步骤3: browser_evaluate 执行 checkLoginStatus() 检查登录
步骤4: 未登录则提示用户在IDE浏览器中手动登录
步骤5: 准备操作内容，向用户展示预览并获得明确确认
```

### 9.2 读取帖子 (read_post)

```
browser_navigate → 帖子URL → wait 2s
browser_evaluate 获取标题和正文:
  (() => {
    const title = document.title.split(' - ')[0];
    const cooked = document.querySelector('.cooked');
    return {title, preview: cooked ? cooked.textContent.trim().slice(0, 500) : ''};
  })()
```

### 9.3 编辑帖子 (edit_post)

> **为什么要先读当前内容再编辑？** 直接覆盖写入有"误覆"风险——Agent可能误解用户意图或内容获取不完整，导致丢失原文重要信息。先读取当前内容、向用户展示diff（新内容vs旧内容），获得明确确认后再提交，是防止意外覆盖的关键步骤。

```
navigate → URL → wait 2s
evaluate 点击编辑: document.querySelector('.post-action-menu__edit')?.click()
wait 2s
evaluate 读取当前内容前300字符用于diff预览
向用户展示diff，获得明确确认
evaluate 使用 setTextareaContent() 设置完整内容
wait 1s
evaluate 点击保存（关键：精确匹配"保存"文本，排除.create类，别点成回复！）:
  Array.from(document.querySelectorAll('button.btn-primary'))
    .find(b => b.textContent.trim() === '保存' && !b.classList.contains('create'))?.click()
wait 3s
navigate → URL（刷新验证）→ wait 2s → snapshot 验证
执行清理草稿（9.6）
```

### 9.4 开头追加 (prepend_update)

适用于更新日期标记等场景，幂等检查避免重复添加。

```
前置步骤同上
evaluate 使用 prependToPost('📅 最新更新：2026年6月29日')
如果返回 skipped=true → 内容已存在，无需继续，告知用户即可
展示预览 → 用户确认 → 保存 → 验证 → 清理草稿（同9.3）
```

### 9.5 发布回复 (create_reply)

```
navigate → URL → wait 2s
scroll deltaY=5000（滚到底部）→ wait 1s
evaluate 点击打开回复编辑器（注意：不是提交按钮！排除.create类）:
  Array.from(document.querySelectorAll('button'))
    .find(b => b.textContent.trim() === '回复' && !b.classList.contains('create'))?.click()
wait 2s
展示回复内容预览 → 获得确认
evaluate 使用 setTextareaContent() 设置内容
wait 1s
evaluate 点击提交（注意：这里有.create类！）:
  document.querySelector('button.btn-primary.create')?.click()
wait 3s
navigate → URL/last（最后一页）→ wait 2s → snapshot 验证
执行清理草稿（9.6）
```

### 9.6 清理草稿 (clean_drafts)

用户名无需手动提供，使用 getCurrentUsername() 自动获取（见第10节工具函数）。

```
navigate → https://forum.trae.cn → wait 2s
evaluate getCurrentUsername() 获取用户名
如果失败，提示用户手动提供
navigate → /u/{username}/activity/drafts → wait 2s
循环：找到.remove-draft按钮 → 点击 → wait 1s → 点击"删除"确认 → wait 1.5s → 重复直到无草稿（最多20个安全上限）
evaluate location.reload() → wait 2s → snapshot 确认空状态
```

## 10. MCP 方案 JavaScript 工具函数

在 browser_evaluate 中使用这些函数（可以内联或组合到IIFE中）。它们封装了常见操作和多信号检测，减少出错概率。

```javascript
// 设置textarea内容（必须触发input/change让Discourse感知变更，否则保存无效）
function setTextareaContent(selector, content) {
  const ta = document.querySelector(selector);
  if (!ta) return {success: false, error: 'textarea not found'};
  ta.focus();
  ta.value = content;
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  ta.dispatchEvent(new Event('change', {bubbles: true}));
  return {success: true, length: content.length};
}

// 开头追加（幂等检查：前缀匹配则跳过，避免重复添加日期标记）
function prependToPost(contentToPrepend) {
  const ta = document.querySelector('textarea.d-editor-input');
  if (!ta) return {success: false, error: 'editor not found'};
  const prefix = contentToPrepend.trim().substring(0, 20);
  if (ta.value.startsWith(prefix)) return {success: true, skipped: true};
  ta.value = contentToPrepend + '\n\n' + ta.value;
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  ta.dispatchEvent(new Event('change', {bubbles: true}));
  return {success: true, skipped: false};
}

// 多信号组合检测登录状态（Discourse全局变量+meta标签+头像链接+登录按钮检测）
function checkLoginStatus() {
  const u = (window.Discourse?.User?.current?.())?.username;
  const m = document.querySelector('meta[name="discourse-current-username"]')?.content;
  const a = document.querySelector('a[href^="/u/"]')?.getAttribute('href')?.match(/\/u\/([^\/\?#]+)/)?.[1];
  const hasLogin = !!Array.from(document.querySelectorAll('a,button'))
    .find(el => (el.textContent||'').includes('登录'));
  const username = u || m || a;
  return {isLoggedIn: !!username && !hasLogin, username};
}

function getCurrentUsername() { return checkLoginStatus().username; }
```

> **为什么需要多信号检测？** Discourse 页面结构可能因版本/主题/插件而异，单一选择器容易失效。多信号组合大幅提高检测鲁棒性。

## 11. 安全检查清单（逐项确认）

- [ ] 已读知识库 [forum-automation.md](../../../docs/knowledge/operations/forum-automation.md)（选择器可能更新）
- [ ] 登录状态已确认（checkLoginStatus 多信号检测）
- [ ] **写操作已 dry-run 预览**（脚本：`--dry-run`；MCP：先展示diff并获得确认）
- [ ] **幂等性检查已执行**（prepend 操作确认内容不存在；编辑操作确认不会意外覆盖）
- [ ] 内容已向用户展示并获得**明确确认**
- [ ] 操作间隔≥3秒
- [ ] 测试内容标记了"[自动化验证]"
- [ ] 保存/回复按钮已正确区分（保存无`.create`，回复有`.create`）
- [ ] 设置textarea后触发了input/change事件（MCP方案，否则Discourse不认）
- [ ] 操作完成后验证了结果（刷新/snapshot确认内容生效）
- [ ] 操作完成后检查并清理了草稿

## 12. 常见错误处理

| 错误码 | 场景 | 处理方式 |
|--------|------|---------|
| FORUM_001 | 登录丢失 | 脚本：重新login；MCP：提示在浏览器中手动登录 |
| FORUM_002 | 找不到编辑按钮 | wait延长到3秒，滚动到帖子可见区域；脚本有多选择器兜底 |
| FORUM_003 | 保存按钮无效 | 检查：文本精确"保存"且排除`.create`类 |
| FORUM_004 | 内容未更新 | 确认触发了input/change事件；脚本有长度校验 |
| FORUM_005 | 标题残留前缀 | 不要append，先用完整内容替换 |
| FORUM_006 | 429频率限制 | 间隔增加到5秒，等待Retry-After |
| FORUM_007 | JS语法错误（MCP） | 只用标准DOM API，不用`:has-text()` |
| FORUM_008 | 草稿残留 | 执行clean-drafts；脚本自动清理 |
| FORUM_009 | Playwright未安装 | `pip install playwright && playwright install chromium` |
| FORUM_010 | prepend被跳过 | 内容已存在，正常现象无需操作 |

> 完整故障排查见知识库第8章；脚本方案加 `--debug` 获取详细日志。

## 13. 关键DOM选择器速查

| 目标 | 选择器 | 注意事项 |
|------|--------|---------|
| 编辑按钮 | `.post-action-menu__edit` | 帖子右下角铅笔图标 |
| 编辑器 | `textarea.d-editor-input` | **必须触发input/change** |
| 保存按钮 | `button.btn-primary` 文本="保存"，无`.create` | 别和回复混淆 |
| 打开回复 | `button` 文本="回复"，无`.create` | 页面底部 |
| 提交回复 | `button.btn-primary.create` 文本="回复" | 有`.create`类 |
| 删草稿 | `.remove-draft` | 需二次确认 |
| 帖子正文 | `.cooked` | 渲染后的HTML |
| 当前用户 | `meta[name="discourse-current-username"]` 或 `Discourse.User.current()` | 多信号检测 |

## 14. 长期方案

@discourse/mcp（Discourse官方MCP）是长期方向，但当前 `discourse_update_topic` 不支持编辑已有帖子正文，仅支持创建主题和回复。待其支持编辑正文后可平滑迁移。配置步骤见知识库第7章。

## 15. Changelog

- **v1.1.1** (2026-06-29): 合规修复：绝对路径改为相对路径（符合skill-development.md规范）；统一Why解释格式为`> **为什么？**`引用块；安全检查清单增加幂等性显式项；补充操作间隔和:has-text()的Why解释；知识库链接统一使用相对路径。
- **v1.1.0** (2026-06-29): 遵循skill-creator最佳实践重构：新增forum-bot.py双方案支持；补充方案选型决策树；增加read_post/prepend_update操作；整合可复用JS工具函数（多信号登录检测、幂等追加）；增加已管理帖子索引；完善dry-run机制；paths字段补全；description优化触发关键词（避免undertrigger）；解释"为什么"而非仅列规则；精简内容控制在合理长度。
- **v1.0.0** (2026-06-29): 初始版本，支持编辑/回复/清理草稿（MCP方案）。
