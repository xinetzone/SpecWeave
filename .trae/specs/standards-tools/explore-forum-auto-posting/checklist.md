# TRAE 论坛自动编辑与发布功能探索与集成 - Verification Checklist

## 环境准备阶段

- [ ] agent-browser 版本确认 ≥ v0.28.0，必要时已 upgrade（不适用：沙箱限制未解决，改用 integrated_browser MCP）
- [ ] Chrome 浏览器可用（agent-browser install 已执行或已有 Chrome）（不适用：改用 IDE 内置浏览器）
- [ ] 本地配置目录 `.agents/config/discourse/` 已创建（不适用：不采用 CLI 方案）
- [ ] `.gitignore` 已包含 `.agents/config/discourse/` 规则（不适用：不采用 CLI 方案）
- [ ] 域名白名单已配置（`AGENT_BROWSER_ALLOWED_DOMAINS=forum.trae.cn`）（不适用：MCP 无此配置）
- [ ] agent-browser 能正常启动（open + snapshot 无报错）（不适用：改用 integrated_browser MCP）

## 持久化会话阶段

- [ ] 使用 `--session-name trae-forum` 首次打开论坛，用户成功手动登录（不适用：改用 MCP，复用 IDE 浏览器已登录状态）
- [ ] 关闭浏览器后重新打开，自动保持登录状态（无需重新登录）（不适用：MCP 复用 IDE 会话）
- [x] snapshot 输出包含用户头像/用户名元素，确认登录有效（通过 browser_evaluate 检查登录状态）

## 命令序列探索阶段

- [x] 读取帖子标题的命令序列已验证，返回正确标题
- [x] 读取帖子正文的命令序列已验证，返回正确内容
- [x] "编辑"按钮定位方式已确定（find text 或 snapshot ref）→ `.post-action-menu__edit`
- [x] 标题输入框定位方式已确定（placeholder/label/role）→ `input.title`
- [x] 正文编辑器类型已确认（textarea / contenteditable / iframe）→ `textarea.d-editor-input`，非 iframe/非 contenteditable
- [x] 正文编辑器定位策略已确定
- [x] 填写内容的方法已确定（fill / type / keyboard inserttext）→ JS 设置 value + dispatchEvent input/change
- [x] 保存按钮定位方式已确定 → `button.btn-primary` 文本"保存"
- [x] 保存完成等待策略已确定（networkidle / URL变化 / 文本出现）→ wait 3秒
- [x] diff snapshot 验证方法已验证有效
- [x] 回复框定位和回复发布命令序列已记录
- [x] 所有关键步骤的选择器、等待时间、注意事项已文档化

## 写操作验证阶段

- [x] 编辑帖子功能已验证（安全编辑目标如更新日期）
- [x] 编辑后 diff snapshot 显示预期变化，无意外修改
- [x] 浏览器人工验证编辑结果正确
- [x] 发布跟帖功能已验证（测试回复内容明确标记）
- [x] 测试回复成功出现在帖子下方
- [x] 操作间隔 ≥3 秒的频率限制已遵守
- [x] 删除草稿功能已验证（`.remove-draft` 选择器 + 二次确认流程）

## 备选方案调研阶段

- [x] Discourse REST API 核心端点列表已整理
- [x] forum.trae.cn 是否开放 User API Key 已确认（探索用户设置页面）
- [x] @discourse/mcp 工具列表和配置要求已整理
- [x] 三种方案对比结论已明确，记录何种场景下切换备选

## 脚本封装阶段

- [ ] forum-read 脚本可正常调用，参数解析正确（不适用：改用知识库文档+Skill方式，不封装CLI脚本）
- [ ] forum-edit 脚本可正常调用，--dry-run 模式不执行写操作（不适用：改用知识库文档+Skill方式）
- [ ] forum-reply 脚本可正常调用，--dry-run 模式不执行写操作（不适用：改用知识库文档+Skill方式）
- [ ] 脚本执行后返回明确的成功/失败状态码（不适用）
- [ ] 脚本错误信息清晰，包含排查建议（不适用）
- [ ] 脚本风格与项目现有脚本一致（参考 .agents/scripts/lib/）（不适用）
- [ ] 脚本自动做 diff snapshot 验证（不适用）
- [ ] 脚本自动遵守 ≥3 秒操作间隔（不适用：操作指南中已说明）

## 文档与收尾阶段

- [x] 标准化工作流文档完成（内容准备→dry-run→确认→发布→验证）
- [x] 故障排查指南覆盖至少5种常见场景（共10种故障场景）
- [x] 每个故障场景包含：现象描述、可能原因、排查步骤、解决方案
- [x] 安全配置文档完成（域名白名单、action policy、敏感文件保护）→ 安全注意事项章节
- [x] 文档保存到 `docs/knowledge/` 目录，链接有效 → docs/knowledge/operations/forum-automation.md
- [x] standards-tools/README.md 已更新登记本 spec
- [x] 全局看板统计数字已更新
- [x] 未引入任何硬编码的敏感信息到版本控制
- [x] Skill 创建完成（通过知识库文档+操作指南方式提供能力）
- [x] 调研报告归档至 docs/knowledge/operations/
