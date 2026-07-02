---
id: "forum-automation"
title: "Discourse论坛（forum.trae.cn）自动化操作指南"
x-toml-ref: "../../../.meta/toml/docs/knowledge/operations/forum-automation.toml"
category: "operations"
tags: [discourse, 论坛, 自动化, browser, mcp, playwright, 发布]
date: "2026-06-30"
status: "stable"
author: "SpecWeave AI"
summary: "基于Trae IDE集成浏览器（integrated_browser MCP）和Playwright Python脚本操作forum.trae.cn论坛的完整指南，包含DOM选择器参考、Ember框架感知操作方法、操作序列模板、JavaScript代码片段、独立Python脚本使用、故障排查和长期方案（@discourse/mcp）接入指南。v2.1更新：精确化DOM选择器、新增diagnoseButtons诊断函数、补充MCP参数陷阱警告、补全误操作恢复方法、新增MCP vs Playwright操作区别对照表。"
---
## 1. 方案概述

五种技术方案对比表：

| 方案 | 验证结果 | 可用性 | 适用场景 |
|------|---------|--------|---------|
| **forum-bot.py（Playwright脚本）** | ✅ 完全验证通过 | ⭐⭐⭐⭐⭐ 本地首选 | 独立运行、命令行操作、CI集成 |
| integrated_browser MCP | ✅ 完全验证通过 | ⭐⭐⭐⭐⭐ IDE首选 | Trae IDE内操作，零配置，已登录 |
| @discourse/mcp | 📋 调研完成待配置 | ⭐⭐⭐⭐ 长期首选 | AI Agent集成，需OAuth授权 |
| Discourse REST API | 📋 调研完成 | ⭐⭐⭐ 高性能场景 | 需API Key，适合后端服务 |
| agent-browser CLI | ❌ 沙箱限制受阻 | ⭐⭐ 备选 | 独立脚本场景（已被Playwright脚本替代） |

**forum-bot.py（Playwright脚本）**（本地首选）：基于Playwright Python实现的独立命令行工具，支持登录状态持久化（cookie保存到JSON文件）、读取帖子、编辑正文、发布回复、清理草稿等功能，支持`--dry-run`试运行模式。优点是完全独立于IDE运行、可在CI/CD中使用、支持命令行参数化、有完善的错误处理；缺点是首次需要手动登录、需要安装Playwright依赖。

**integrated_browser MCP**（IDE首选）：核心原理是通过Trae IDE内置的浏览器MCP服务直接控制已打开的浏览器实例，复用用户已有的登录状态，无需额外配置认证信息。优点是零配置立即可用、无需处理OAuth/API Key、可以操作任何DOM元素；缺点是操作速度受页面渲染影响、需要等待元素加载、不适合高并发批量操作。

**@discourse/mcp**（长期首选）：核心原理是Discourse官方推出的MCP服务器，通过User API Key与论坛交互，使用标准的Discourse API协议。优点是官方支持、稳定性高、内置速率限制和重试、专为AI Agent设计；缺点是需要Node.js >= 24环境、需要OAuth授权流程、目前不支持编辑已有帖子（仅支持创建主题和回复）。

**Discourse REST API**：核心原理是直接调用论坛的HTTP REST接口，使用API Key认证。优点是性能最高、适合后端服务集成、功能完整；缺点是需要申请API Key、需要处理签名和认证、不适合在IDE中临时使用。

**agent-browser CLI**：核心原理是通过独立的Playwright浏览器自动化脚本操作论坛。优点是可独立运行、可编写复杂脚本；缺点是在Trae IDE沙箱环境中受网络和进程限制、需要单独处理登录状态。

## 2. 快速开始（Playwright Python脚本）

> 脚本路径：file:///d:/spaces/SpecWeave/.agents/scripts/forum-bot.py

### 2.1 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 2.2 首次登录

运行以下命令，浏览器会自动打开forum.trae.cn，手动登录后回到终端按Enter保存登录状态：

```bash
cd d:\spaces\SpecWeave\.agents\scripts
python forum-bot.py login
```

登录状态保存在 `.agents/scripts/config/forum-state.json`，后续操作自动复用。

### 2.3 常用命令

```bash
# 读取帖子内容
python forum-bot.py read 44601

# 编辑帖子（替换正文为文件内容）
python forum-bot.py edit 44601 --file new-content.md

# 在帖子开头追加文本（如更新日期标记）
python forum-bot.py edit 44601 --prepend "📅 最新更新：2026年6月29日"

# 直接指定新内容
python forum-bot.py edit 44601 --content "# 新标题\n\n新正文内容"

# 发布回复
python forum-bot.py reply 44601 --content "测试回复内容"

# 从文件发布回复
python forum-bot.py reply 44601 --file reply.md

# 清理所有草稿
python forum-bot.py clean-drafts

# 试运行（不实际提交写操作，仅预览内容）
python forum-bot.py edit 44601 --content "测试" --dry-run
python forum-bot.py reply 44601 --content "测试回复" --dry-run
```

### 2.4 命令参数说明

| 命令 | 参数 | 说明 |
|------|------|------|
| `login` | `--headless` | 无头模式（不推荐，登录需交互） |
| `read <topic_id>` | `--headless` | 无头模式（默认开启） |
| `edit <topic_id>` | `--content` | 直接指定新内容 |
| | `--file` | 从Markdown文件读取内容 |
| | `--prepend` | 在帖子开头追加文本 |
| | `--dry-run` | 试运行，不提交 |
| | `--headless` | 无头模式（默认关闭） |
| `reply <topic_id>` | `--content` | 回复内容 |
| | `--file` | 从文件读取回复内容 |
| | `--dry-run` | 试运行，不提交 |
| | `--headless` | 无头模式（默认关闭） |
| `clean-drafts` | `--headless` | 无头模式（默认开启） |

### 2.5 安全使用建议

1. **先dry-run**：所有写操作先加 `--dry-run` 预览内容，确认无误后再执行
2. **操作间隔**：脚本内置3秒操作间隔，遵守论坛频率限制
3. **自动清理草稿**：编辑/回复后自动清理Discourse自动保存的草稿
4. **登录状态**：cookie保存在本地JSON文件，不要分享或提交到Git

## 3. 快速开始（integrated_browser MCP）

使用Trae IDE的integrated_browser MCP操作论坛的步骤：

1. 确认浏览器已登录forum.trae.cn（打开论坛页面检查是否显示用户名）
2. 使用browser_navigate导航到目标帖子URL
3. 使用browser_snapshot获取页面交互元素
4. 按操作序列模板（见第5节）执行具体操作
5. 操作间隔≥3秒，遵守频率限制
6. 操作完成后验证结果（snapshot或截图）

> ⚠️ **MCP工具参数陷阱**：`browser_wait_for`的`time`参数单位是**秒**，不是毫秒！传`time=2`等待2秒，传`time=2000`会等待2000秒（约33分钟）。其他需要注意的参数：`browser_press_key`的`key`值使用标准键名（如`End`、`Escape`、`Enter`）。

### 已管理的帖子

- SpecWeave Demo帖: https://forum.trae.cn/t/topic/44601
- SpecWeave报名帖: https://forum.trae.cn/t/topic/44402
- 竹简悟道帖: 对应报名帖

## 4. DOM选择器参考表

已在forum.trae.cn上验证的精确选择器：

| 操作目标 | CSS选择器 | 说明 |
|---------|----------|------|
| 编辑帖子按钮 | `.post-action-menu__edit` | 帖子右下角铅笔图标按钮，title属性含"编辑" |
| 正文编辑器 | `textarea.d-editor-input` | Markdown编辑器，标准textarea，非iframe/非contenteditable |
| 标题输入框 | `input.title` | 编辑弹窗中的标题字段 |
| 保存编辑按钮 | `button.btn-primary`（文本为"保存"，不含`.create`类） | 提交编辑，需排除回复提交按钮（不含create类） |
| 回复按钮（打开composer） | `button.topic-footer-button`（文本为"回复"） | 页面底部footer栏按钮，用于打开回复编辑器 |
| 回复编辑器 | `textarea.d-editor-input`（composer区域内） | 回复用的textarea，和编辑正文是同一个class |
| 回复提交按钮 | `button.btn-primary.create`（不含`topic-footer-button`类，文本为"回复"） | 提交回复，必须排除footer打开按钮（消歧见第4节同名按钮说明） |
| 删除草稿按钮 | `.remove-draft` | 垃圾桶图标，btn-danger红色按钮 |
| 删除确认按钮 | 对话框中"删除"按钮 | 需要二次确认 |
| 帖子正文区域 | `.cooked` | 渲染后的帖子HTML内容 |
| 帖子作者信息 | `.poster-info`或`.username` | 用户名区域 |

**重要**：

- Discourse编辑器使用textarea.d-editor-input，不是contenteditable div，也不是iframe
- **Ember框架感知设值（关键！）**：Discourse基于Ember.js，直接设置`textarea.value`会绕过Ember双向绑定，导致composer认为内容为空、提交按钮无效。必须使用`nativeSetter`+事件链：
  ```javascript
  // ✅ 正确方式：Ember框架感知
  function setTextareaContent(selector, content) {
    const ta = document.querySelector(selector);
    if (!ta) return {success: false, error: 'textarea not found'};
    const nativeSetter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype, 'value'
    ).set;
    nativeSetter.call(ta, content);
    ta.focus();
    ta.dispatchEvent(new Event('input', {bubbles: true}));
    ta.dispatchEvent(new Event('change', {bubbles: true}));
    return {success: true, length: content.length, taLength: ta.value.length};
  }
  ```
  ⚠️ 简单的`ta.value = content`虽然DOM层面更新了值，但Ember内部模型不变，提交按钮无效！
- **同名按钮消歧**：Discourse页面存在多个文本为"回复"的按钮：
  - Footer栏"回复"按钮：`button.topic-footer-button`（用于打开composer）
  - Composer内提交按钮：`button.btn-primary.create`（不含`topic-footer-button`类）
  - 必须通过排除`topic-footer-button`类或检查父容器`.reply-composer`来定位正确按钮
- 不要使用`:has-text()`等Playwright非标准选择器，在browser_evaluate中不可用
- 保存和回复按钮的区别：保存是`button.btn-primary`文本"保存"，回复提交是`button.btn-primary.create`（不含topic-footer-button）文本"回复"

## 5. 操作序列模板

### 5.1 编辑帖子正文

```
步骤1: browser_navigate → https://forum.trae.cn/t/topic/{topic_id}
步骤2: browser_wait_for time=2（等待页面加载）
步骤3: browser_evaluate 点击编辑按钮:
  const editBtn = document.querySelector('.post-action-menu__edit');
  if(editBtn) editBtn.click();
步骤4: browser_wait_for time=2（等待编辑器加载）
步骤5: browser_evaluate 使用nativeSetter设置正文内容（Ember框架感知）:
  const ta = document.querySelector('textarea.d-editor-input');
  const nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype, 'value').set;
  nativeSetter.call(ta, '完整的Markdown内容');
  ta.focus();
  ta.dispatchEvent(new Event('input',{bubbles:true}));
  ta.dispatchEvent(new Event('change',{bubbles:true}));
步骤6: browser_wait_for time=1
步骤7: browser_evaluate 点击保存:
  const saveBtn = Array.from(document.querySelectorAll('button.btn-primary'))
    .find(b => b.textContent.trim() === '保存' && !b.classList.contains('create'));
  if(saveBtn) saveBtn.click();
步骤8: browser_wait_for time=4（等待保存完成）
步骤9: browser_navigate → https://forum.trae.cn/t/topic/{topic_id}/last
步骤10: browser_wait_for time=2
步骤11: browser_snapshot 验证编辑结果
```

### 5.2 发布回复

```
步骤1: browser_navigate → https://forum.trae.cn/t/topic/{topic_id}/last
步骤2: browser_wait_for time=2
步骤3: 按End键滚动到底部（browser_press_key key=End）
步骤4: browser_wait_for time=1
步骤5: browser_evaluate 点击footer回复按钮打开composer:
  const replyBtn = Array.from(document.querySelectorAll('button.topic-footer-button'))
    .find(b => b.textContent.trim() === '回复');
  if(replyBtn) replyBtn.click();
步骤6: browser_wait_for time=2（等待composer加载完成）
步骤7: browser_evaluate 使用nativeSetter设置回复内容（Ember框架感知）:
  const ta = document.querySelector('textarea.d-editor-input');
  const nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype, 'value').set;
  nativeSetter.call(ta, '回复内容');
  ta.focus();
  ta.dispatchEvent(new Event('input',{bubbles:true}));
  ta.dispatchEvent(new Event('change',{bubbles:true}));
步骤8: browser_wait_for time=1.5
步骤9: browser_evaluate 点击composer内的提交按钮（排除topic-footer-button!）:
  const submitBtn = Array.from(document.querySelectorAll('button.btn-primary.create'))
    .find(b => !b.classList.contains('topic-footer-button'));
  if(submitBtn) submitBtn.click();
步骤10: browser_wait_for time=4（等待POST完成+页面重定向渲染）
步骤11: 多信号验证：
  - URL是否变为/{n+1}（新帖子号）
  - body.scrollHeight是否增加
  - 页面是否显示"刚刚发布"文本
步骤12: browser_navigate → https://forum.trae.cn/t/topic/{topic_id}/last
步骤13: browser_wait_for time=2
步骤14: browser_evaluate 检查.cooked元素数量和最后一个帖子内容
```

> ⚠️ **关键陷阱**：
> - 步骤5的footer按钮和步骤9的提交按钮textContent都是"回复"，class都包含btn-primary create，必须用`!b.classList.contains('topic-footer-button')`排除footer按钮
> - 步骤7必须用nativeSetter设值，直接`ta.value=xxx`会导致Ember不感知内容、提交按钮无效
> - 步骤10必须等待≥4秒，提交后立即刷新会因POST未完成而误判为失败

### 5.3 删除草稿

```
步骤1: browser_navigate → https://forum.trae.cn/u/{username}/activity/drafts
步骤2: browser_wait_for time=2
步骤3: browser_evaluate 点击移除按钮:
  const removeBtn = document.querySelector('.remove-draft');
  if(removeBtn) removeBtn.click();
步骤4: browser_wait_for time=1
步骤5: browser_snapshot 检查确认对话框
步骤6: browser_evaluate 点击确认删除:
  const confirmBtn = Array.from(document.querySelectorAll('button'))
    .find(b => b.textContent.trim() === '删除');
  if(confirmBtn) confirmBtn.click();
步骤7: browser_wait_for time=2
步骤8: 重复步骤3-7直到所有草稿删除
步骤9: browser_evaluate location.reload() 刷新验证
步骤10: browser_wait_for time=2
步骤11: browser_snapshot 确认显示空状态
```

## 6. JavaScript代码片段（用于browser_evaluate）

### 6.1 通用等待和工具函数

```javascript
// 查找包含指定文本的按钮
function findButton(text) {
  return Array.from(document.querySelectorAll('button'))
    .find(b => b.textContent.trim() === text);
}

// 设置textarea内容并触发事件（Ember框架感知版本）
function setTextareaContent(selector, content) {
  const ta = document.querySelector(selector);
  if (!ta) return {success: false, error: 'textarea not found'};
  const nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype, 'value'
  ).set;
  nativeSetter.call(ta, content);
  ta.focus();
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  ta.dispatchEvent(new Event('change', {bubbles: true}));
  return {success: true, length: content.length, taLength: ta.value.length};
}

// 获取帖子正文内容
function getPostContent(postIndex = 0) {
  const cooked = document.querySelectorAll('.cooked');
  if (postIndex >= cooked.length) return {error: 'post not found'};
  return {text: cooked[postIndex].textContent?.trim()?.substring(0, 500)};
}
```

### 6.2 安全编辑：仅追加内容到帖子开头（如更新日期标记）

```javascript
function prependToPost(contentToPrepend) {
  const ta = document.querySelector('textarea.d-editor-input');
  if (!ta) return {success: false, error: 'editor not found'};
  const nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype, 'value'
  ).set;
  const currentContent = ta.value;
  // 避免重复添加（幂等性检查）
  if (currentContent.startsWith(contentToPrepend.trim().substring(0, 20))) {
    return {success: true, skipped: 'content already exists'};
  }
  nativeSetter.call(ta, contentToPrepend + '\n\n' + currentContent);
  ta.focus();
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  ta.dispatchEvent(new Event('change', {bubbles: true}));
  return {success: true, newLength: ta.value.length};
}
```

### 6.2.1 添加AI发布声明（幂等）

专门用于在帖子开头添加标准化AI发布声明的函数。幂等性检查：搜索全文是否已包含"本文由 AI 智能体协助撰写"关键词，无论声明在哪个位置都视为已添加。

```javascript
const AI_NOTICE = '---\n\n> 🤖 **本文由 AI 智能体协助撰写与发布** | 内容经人工审核确认，观点归属作者本人。\n\n---\n\n';

function addAINotice() {
  const ta = document.querySelector('textarea.d-editor-input');
  if (!ta) return {success: false, error: 'editor not found'};
  const nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype, 'value'
  ).set;
  let content = ta.value;
  // 幂等性检查：全文搜索关键词，避免重复添加
  if (content.includes('本文由 AI 智能体协助撰写')) {
    return {success: true, skipped: 'AI notice already exists'};
  }
  // 智能插入：如果开头有问候语（以🎉/👋/📢等emoji开头的短行），在问候语之后插入
  const greetingMatch = content.match(/^([\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}].{0,80})\n\n/su);
  if (greetingMatch) {
    content = greetingMatch[1] + '\n\n' + AI_NOTICE + content.slice(greetingMatch[0].length);
  } else {
    content = AI_NOTICE + content;
  }
  nativeSetter.call(ta, content);
  ta.focus();
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  ta.dispatchEvent(new Event('change', {bubbles: true}));
  return {success: true, newLength: content.length};
}
```

### 6.3 检查登录状态

```javascript
function checkLoginStatus() {
  const userBtn = document.querySelector('.current-user, [data-user-id], .avatar-wrapper');
  return {
    isLoggedIn: !!userBtn,
    url: location.href,
    title: document.title
  };
}
```

### 6.4 诊断：枚举页面所有按钮（排查按钮歧义）

当遇到"找不到正确按钮"或"点错按钮"时，先运行此函数枚举所有可见按钮，对比text/class/父容器定位目标：

```javascript
function diagnoseButtons() {
  const buttons = Array.from(document.querySelectorAll('button'));
  const visible = buttons.filter(b => {
    const rect = b.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 && b.offsetParent !== null;
  });
  return visible.map((b, i) => ({
    index: i,
    text: b.textContent.trim().substring(0, 30),
    classes: b.className.substring(0, 80),
    parentTag: b.parentElement?.tagName,
    parentClass: b.parentElement?.className?.substring(0, 60),
    rect: {
      top: Math.round(b.getBoundingClientRect().top),
      left: Math.round(b.getBoundingClientRect().left),
      w: Math.round(b.getBoundingClientRect().width),
      h: Math.round(b.getBoundingClientRect().height)
    }
  }));
}
```

> **使用场景**：composer打开后找不到提交按钮、误点"分享/书签/举报"按钮、多个同名"回复"按钮消歧时使用。输出包含按钮文本、class、父容器信息和坐标位置，帮助快速定位目标。

### 6.5 MCP DOM操作与Playwright脚本的关键区别

| 维度 | integrated_browser MCP (browser_evaluate) | Playwright脚本 (forum-bot.py) |
|------|------------------------------------------|-------------------------------|
| 设值方式 | 必须使用`nativeSetter`+`dispatchEvent`（见6.1），直接`ta.value=xxx`会绕过Ember绑定 | 使用`locator.fill()`，Playwright自动模拟真实输入，框架自动感知 |
| 按钮定位 | `querySelectorAll`+Array过滤，需手动消歧 | `locator().filter(has_text=...)`，内置重试和等待 |
| 等待策略 | 手动`browser_wait_for`指定秒数 | 自动等待元素可见/可交互（timeout参数） |
| 调试方式 | 运行diagnoseButtons()枚举DOM | 日志自动打印所有btn-primary按钮信息 |
| 误操作恢复 | 按`browser_press_key key=Escape`关闭弹窗 | `page.keyboard.press("Escape")`关闭弹窗 |

## 7. @discourse/mcp接入指南（长期方案）

@discourse/mcp是Discourse官方MCP服务器（v0.2.4），需要Node.js >= 24。

### 7.1 配置步骤

1. 生成User API Key：
   ```bash
   npx @discourse/mcp@latest generate-user-api-key \
     --site https://forum.trae.cn \
     --save-to ./trae-forum-profile.json
   ```
2. 浏览器自动打开后登录forum.trae.cn并点击授权
3. 编辑profile.json，添加 `"read_only": false, "allow_writes": true` 开启写入
4. 在MCP客户端配置中启动：
   ```bash
   npx -y @discourse/mcp@latest --profile ./trae-forum-profile.json
   ```

### 7.2 核心工具列表

只读工具（10个）：discourse_select_site, discourse_search, discourse_read_topic, discourse_read_post, discourse_get_user, discourse_list_user_posts, discourse_filter_topics, discourse_get_chat_messages, discourse_get_draft, discourse_list_users

写入工具（8个）：discourse_create_topic, discourse_create_post（回复）, discourse_update_topic, discourse_save_draft, discourse_delete_draft, discourse_upload_file, discourse_create_user, discourse_update_user

### 7.3 注意事项

- Node.js版本要求>=24，注意当前环境Node版本
- @discourse/mcp目前不支持编辑已有帖子（discourse_update_topic只更新主题元数据），编辑帖子仍需REST API或浏览器自动化
- 默认只读模式，写入需显式开启
- 内置~1 req/sec速率限制和自动重试

## 8. 常见问题与故障排查

| 问题 | 现象 | 原因 | 解决方案 |
|------|------|------|---------|
| 登录状态丢失 | 页面显示登录/注册按钮而非用户名 | Session/Cookie过期 | 在Trae IDE浏览器中手动重新登录forum.trae.cn |
| 编辑按钮找不到 | JS返回null，querySelector找不到.edit按钮 | 页面未完全加载或需要滚动 | 增加wait时间到3秒，确保帖子完全渲染；滚动到帖子可见区域 |
| 保存按钮点击无效 | 点击后无反应，编辑器不关闭 | 按钮选择器错误（点到了回复按钮） | 使用精确的文本过滤：find(b => b.textContent.trim() === '保存' && !b.classList.contains('create')) |
| 内容未更新 | 保存后刷新，内容仍是旧的 | 没有触发input事件，Discourse未感知内容变更 | 使用nativeSetter设置值后必须dispatchEvent input和change事件（见6.1节） |
| 回复点击后composer打开但提交无效 | 点击回复按钮后composer出现，填入内容后点提交无反应 | 1) 直接设置textarea.value绕过Ember绑定；2) 点错了footer回复按钮而非composer提交按钮 | 1) 使用nativeSetter+事件链设值；2) 提交按钮排除topic-footer-button类 |
| 提交后刷新看不到新帖子 | 提交后立即navigate刷新，仍显示旧帖子数 | 提交后立即刷新，POST请求尚未完成 | 提交后wait≥4秒，通过URL变化/body高度/"刚刚发布"文本多信号验证 |
| 误点"分享"按钮 | 点击后弹出分享对话框而非打开composer | topic-footer-button类包含多个按钮（分享/书签/举报/回复），仅按textContent查找不够精确 | 选择器加上.topic-footer-button类限定，或先枚举所有按钮检查className |
| 标题残留【标题】【标签】前缀 | 编辑后标题包含多余前缀 | 编辑时textarea包含Discourse UI注入的前缀文本 | 编辑前先清空textarea.value，再设置完整内容，不要append |
| 回复提交后编辑器未关闭 | 点击回复按钮后composer仍然打开 | 按钮选择错误或点击太快 | 使用button.btn-primary.create选择器，点击后wait 3秒 |
| 草稿残留 | 个人中心显示未预期的草稿 | 编辑中断或失败时Discourse自动保存 | 运行 `python forum-bot.py clean-drafts` 清理 |
| 429频率限制 | 操作返回频率限制错误 | 操作太快 | 操作间隔≥3秒，遇到429等待Retry-After头指定的秒数 |
| JavaScript语法错误 | browser_evaluate返回错误 | 使用了非标准选择器如:has-text() | 使用标准DOM API：querySelectorAll + Array.from().filter() |
| browser_wait_for等待时间异常长 | 等待很久没反应，似乎卡住 | 误将毫秒当秒，传了time=2000等2000秒 | time参数单位是秒，常规等待传1-5即可 |
| 误点按钮后弹出对话框 | 点击后弹出分享/书签/举报等不需要的弹窗 | 按钮选择器不精确，误触其他topic-footer-button | 按Escape键关闭弹窗（browser_press_key key=Escape），然后用diagnoseButtons()重新枚举按钮定位 |
| 页面跳转到首页 | 提交后不在帖子页面 | 回复提交后页面可能重定向 | 提交后重新导航到帖子URL/last验证 |
| Playwright脚本未登录 | 脚本提示"未登录" | forum-state.json不存在或过期 | 重新运行 `python forum-bot.py login` |
| Playwright浏览器无法启动 | 报错browserType.launch失败 | Chromium未安装 | 运行 `playwright install chromium` |
| 脚本点击按钮超时 | TimeoutError waiting for locator | 页面未完全加载或选择器变化 | 增加wait时间，检查选择器是否仍正确 |

## 9. 安全注意事项

1. **操作间隔**：所有自动化操作之间至少等待3秒，避免触发频率限制
2. **Dry-run原则**：写操作（编辑/发帖）前先通过getPostContent读取当前内容，确认修改范围，避免误操作
3. **幂等性**：编辑操作应检查目标内容是否已存在（如更新日期标记），避免重复添加
4. **内容验证**：每次写操作后必须验证结果（snapshot或刷新页面确认）
5. **草稿清理**：编辑操作可能产生自动保存草稿，操作完成后检查并清理
6. **禁止**：不发送垃圾内容、不绕过审核机制、不批量注册/灌水、不暴露认证token
7. **测试标记**：测试回复/编辑应明确标记为"[自动化测试]"或"[自动化验证]"，便于识别和后续清理
8. **AI发布声明（强制）**：所有通过智能体自动化撰写或发布的帖子，必须在正文开头添加标准化AI声明文本，清晰告知读者内容由AI参与生成，声明内容经人工审核确认。标准模板如下：

```markdown
---

> 🤖 **本文由 AI 智能体协助撰写与发布** | 内容经人工审核确认，观点归属作者本人。

---
```

   - **放置位置**：正文开头（问候语之后、正文标题之前），确保读者第一眼可见
   - **视觉区分**：使用 `---` 水平分隔线上下包裹 + `>` 引用块样式，Discourse渲染时呈现灰色背景引用框，与正文有明确视觉区隔
   - **措辞原则**：专业、简洁、透明——"协助撰写与发布"如实说明AI参与程度，"内容经人工审核确认"强调人工把关，"观点归属作者本人"避免责任混淆
   - **幂等性检查**：添加前检查是否已包含"本文由 AI 智能体协助撰写"关键词，避免重复添加
   - **适用范围**：所有自动化发布的新帖、回复、编辑操作，均须包含此声明；测试标记（第7条）与AI声明不冲突，测试帖应同时包含两者

**注意**：

- 所有JavaScript代码必须使用标准DOM API，避免Playwright特有选择器
- 内部链接使用file:///d:/spaces/SpecWeave/...格式
- 参考文档：
  - file:///d:/spaces/SpecWeave/.trae/specs/standards-tools/explore-forum-auto-posting/spec.md
  - file:///d:/spaces/SpecWeave/docs/knowledge/operations/discourse-api-research.md
