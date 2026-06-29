---
name: forum-posting
version: 1.0.0
description: "Discourse论坛（forum.trae.cn）自动化操作技能，支持编辑帖子、发布回复、清理草稿等操作，基于Trae IDE集成浏览器MCP"
argument-hint: "&lt;操作类型&gt; [帖子URL]"
disable-model-invocation: false
user-invocable: true
paths: []
---

# 论坛发帖与维护 (Forum Posting)

## 1. 技能唯一标识 (Skill ID)
`forum-posting`

## 2. 功能描述 (Description)

基于Trae IDE集成浏览器（integrated_browser MCP）操作forum.trae.cn论坛的技能，提供：
- 编辑已有帖子正文（支持完整内容替换和追加更新）
- 发布回复到指定帖子
- 清理自动保存的草稿
- 标准化操作流程和安全检查清单
- 故障快速排查指引

**触发条件**：当用户提到以下关键词时触发本技能：
- "发帖"、"发布"、"更新论坛"、"更新帖子"
- "编辑帖子"、"修改帖子"、"编辑主贴"
- "回复帖子"、"跟帖"、"发布回复"
- "清理草稿"、"删除草稿"
- "forum.trae.cn"相关操作

## 3. 输入输出参数定义 (I/O Parameters)

### 3.1 输入参数 (Input)
| 参数名称 | 类型 | 是否必填 | 默认值 | 说明 |
|----------|------|----------|--------|------|
| operation | string | 是 | 无 | 操作类型：edit_post（编辑帖子）/ create_reply（发布回复）/ clean_drafts（清理草稿） |
| topic_url | string | 否 | 无 | 目标帖子URL，edit_post和create_reply必填 |
| content | string | 否 | 无 | 帖子/回复内容（Markdown格式），可从源文件读取或用户提供 |
| username | string | 否 | 当前登录用户 | 清理草稿时的用户名 |

### 3.2 输出参数 (Output)
```json
{
  "status": "success|failed",
  "operation": "edit_post|create_reply|clean_drafts",
  "topic_url": "https://forum.trae.cn/t/topic/xxx",
  "drafts_cleaned": 0,
  "message": "操作结果描述",
  "verification_screenshot": "可选，验证截图"
}
```

## 4. 依赖项说明 (Dependencies)

- **Trae IDE集成浏览器MCP**：需要`integrated_browser` MCP服务可用，提供browser_navigate、browser_evaluate、browser_snapshot、browser_wait_for等工具
- **登录状态**：Trae IDE内置浏览器必须已登录forum.trae.cn（打开论坛页面确认显示用户名）
- **知识库文档**：必须先读取 `docs/knowledge/operations/forum-automation.md` 获取最新的DOM选择器和操作步骤（**重要**：选择器可能随Discourse版本更新，始终以知识库文档为准）

## 5. 部署要求 (Deployment)

1. 确认Trae IDE浏览器已登录forum.trae.cn
2. 首次使用前读取知识库文档：`docs/knowledge/operations/forum-automation.md`
3. 所有写操作必须遵循安全检查清单（见第8节）
4. 操作间隔≥3秒，避免触发频率限制

## 6. 执行流程 (Execution Flow)

### 6.1 通用前置步骤（所有操作必须执行）

```
步骤1: [PDR-LOG] 读取知识库文档 docs/knowledge/operations/forum-automation.md 获取最新操作指南
步骤2: 检查登录状态（通过browser_evaluate执行checkLoginStatus函数）
步骤3: 如果未登录，提示用户在Trae IDE浏览器中手动登录forum.trae.cn
步骤4: 准备操作内容，向用户展示预览并获得明确确认
步骤5: 确认安全检查清单全部完成
```

### 6.2 编辑帖子 (edit_post)

```
步骤1: 执行通用前置步骤
步骤2: browser_navigate → 目标帖子URL
步骤3: browser_wait_for time=2（等待页面加载）
步骤4: browser_evaluate 读取当前帖子内容用于diff对比
步骤5: 向用户展示内容diff预览，获得确认
步骤6: browser_evaluate 点击编辑按钮:
  const editBtn = document.querySelector('.post-action-menu__edit');
  if(editBtn) editBtn.click();
步骤7: browser_wait_for time=2（等待编辑器加载）
步骤8: browser_evaluate 设置正文内容（**重要**：先清空再设置，不要append，避免标题残留问题）:
  const ta = document.querySelector('textarea.d-editor-input');
  ta.value = '完整的Markdown内容';
  ta.dispatchEvent(new Event('input',{bubbles:true}));
  ta.dispatchEvent(new Event('change',{bubbles:true}));
步骤9: browser_wait_for time=1
步骤10: browser_evaluate 点击保存（注意：精确匹配"保存"文本，不要点到回复按钮）:
  const saveBtn = Array.from(document.querySelectorAll('button.btn-primary'))
    .find(b =&gt; b.textContent.trim() === '保存' &amp;&amp; !b.classList.contains('create'));
  if(saveBtn) saveBtn.click();
步骤11: browser_wait_for time=3（等待保存完成）
步骤12: browser_snapshot 验证编辑结果
步骤13: 执行清理草稿流程（见6.4）
```

### 6.3 发布回复 (create_reply)

```
步骤1: 执行通用前置步骤
步骤2: browser_navigate → 目标帖子URL
步骤3: browser_wait_for time=2
步骤4: browser_scroll deltaY=5000（滚动到底部）
步骤5: browser_wait_for time=1
步骤6: browser_evaluate 点击回复按钮:
  const replyBtn = Array.from(document.querySelectorAll('button'))
    .find(b =&gt; b.textContent.trim() === '回复' &amp;&amp; !b.classList.contains('create'));
  if(replyBtn) replyBtn.click();
步骤7: browser_wait_for time=2（等待回复编辑器加载）
步骤8: 向用户展示回复内容预览，获得确认
步骤9: browser_evaluate 设置回复内容:
  const ta = document.querySelector('textarea.d-editor-input');
  ta.value = '回复内容';
  ta.dispatchEvent(new Event('input',{bubbles:true}));
步骤10: browser_wait_for time=1
步骤11: browser_evaluate 点击回复提交（注意：使用.btn-primary.create选择器）:
  const submitBtn = document.querySelector('button.btn-primary.create');
  if(submitBtn) submitBtn.click();
步骤12: browser_wait_for time=3（等待提交完成）
步骤13: browser_navigate → 帖子URL/last（跳转到最后一页）
步骤14: browser_wait_for time=2
步骤15: browser_snapshot 验证回复出现
步骤16: 执行清理草稿流程（见6.4）
```

### 6.4 清理草稿 (clean_drafts)

```
步骤1: browser_navigate → https://forum.trae.cn/u/{username}/activity/drafts
步骤2: browser_wait_for time=2
步骤3: browser_evaluate 检查是否有草稿:
  const removeBtn = document.querySelector('.remove-draft');
  return {hasDrafts: !!removeBtn};
步骤4: 如果有草稿:
  步骤4a: browser_evaluate 点击移除按钮
  步骤4b: browser_wait_for time=1
  步骤4c: browser_snapshot 检查确认对话框
  步骤4d: browser_evaluate 点击确认删除:
    const confirmBtn = Array.from(document.querySelectorAll('button'))
      .find(b =&gt; b.textContent.trim() === '删除');
    if(confirmBtn) confirmBtn.click();
  步骤4e: browser_wait_for time=2
  步骤4f: 重复步骤3-4e直到所有草稿删除
步骤5: browser_evaluate location.reload() 刷新验证
步骤6: browser_wait_for time=2
步骤7: browser_snapshot 确认显示空状态
```

## 7. 错误处理规范 (Error Handling)

| 错误码 | 异常场景 | 应对策略 |
|--------|----------|----------|
| FORUM_001 | 登录状态丢失 | 提示用户在Trae IDE浏览器中手动重新登录forum.trae.cn |
| FORUM_002 | 编辑按钮找不到 | 增加wait时间到3秒，滚动到帖子可见区域，确认页面完全加载 |
| FORUM_003 | 保存按钮点击无效 | 检查按钮选择器：确保使用`textContent.trim() === '保存'`且排除`.create`类 |
| FORUM_004 | 内容未更新 | 确认设置value后触发了input和change事件：`dispatchEvent(new Event('input',{bubbles:true}))` |
| FORUM_005 | 标题残留前缀问题 | 编辑前先清空`ta.value = ''`，再设置完整内容，不要使用append |
| FORUM_006 | 429频率限制 | 操作间隔增加到5秒，等待Retry-After头指定时间后重试 |
| FORUM_007 | JavaScript语法错误 | 只使用标准DOM API，避免`:has-text()`等Playwright非标准选择器 |
| FORUM_008 | 草稿残留 | 按6.4流程执行清理草稿，操作中断后也应检查草稿 |

**遇到问题时**：查阅知识库文档第7章（docs/knowledge/operations/forum-automation.md）获取完整故障排查表。

## 8. 安全检查清单（必须逐项确认）

- [ ] 已读取最新知识库文档 `docs/knowledge/operations/forum-automation.md`
- [ ] 已确认浏览器登录状态正常
- [ ] 操作内容已向用户展示并获得**明确确认**
- [ ] 操作间隔≥3秒
- [ ] 测试内容已标记为"[自动化验证]"
- [ ] 编辑操作：先读取当前内容并展示diff
- [ ] 保存按钮选择器已验证（`textContent === '保存'`，排除`.create`）
- [ ] 设置textarea内容后已触发input和change事件
- [ ] 操作完成后已验证结果（snapshot或刷新页面）
- [ ] 操作完成后已检查并清理草稿

## 9. 关键DOM选择器速查（以知识库文档为准）

| 操作目标 | CSS选择器 | 注意事项 |
|---------|----------|---------|
| 编辑帖子按钮 | `.post-action-menu__edit` | 帖子右下角铅笔图标 |
| 正文编辑器 | `textarea.d-editor-input` | **必须触发input/change事件** |
| 保存编辑按钮 | `button.btn-primary`文本="保存"，排除`.create` | 不要和回复按钮混淆 |
| 回复提交按钮 | `button.btn-primary.create`文本="回复" | 注意有`.create`类 |
| 删除草稿按钮 | `.remove-draft` | 需要二次确认删除 |
| 帖子正文区域 | `.cooked` | 渲染后的HTML内容 |

## 10. 长期方案说明

@discourse/mcp是Discourse官方MCP服务器，长期来看是更稳定可靠的方案：
- 优点：官方支持、稳定性高、内置速率限制、专为AI Agent设计
- 配置步骤见知识库文档第6章
- **当前限制**：需要Node.js &gt;= 24，且`discourse_update_topic`目前只更新主题元数据，**不支持编辑已有帖子正文**，因此编辑帖子仍需浏览器自动化
- 本技能可在@discourse/mcp支持编辑帖子后平滑迁移

## 11. 版本记录 (Changelog)

- **v1.0.0** (2026-06-29): 初始版本发布，支持编辑帖子、发布回复、清理草稿三大核心操作，包含完整安全检查清单和故障排查指引。
