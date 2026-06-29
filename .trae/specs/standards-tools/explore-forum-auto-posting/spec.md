# TRAE 论坛自动编辑与发布功能探索与集成 - Product Requirement Document

## Overview
- **Summary**: 系统性探索 forum.trae.cn（Discourse 论坛）自动编辑与发布帖子的技术方案。经实际验证，**Trae IDE 集成浏览器（integrated_browser MCP）** 是当前立即可用的零配置方案；同时调研确认 **@discourse/mcp 官方MCP服务器** 是长期最优方案。本探索完成了核心操作（编辑帖子、发布回复、删除草稿）的全流程验证，记录了精确的DOM选择器和操作序列，为后续脚本封装和Skill开发提供依据。
- **Purpose**: 解决手动通过浏览器编辑帖子效率低、步骤多（7-10步）、易出错（如Demo帖标题残留【标题】前缀问题）、无法批量处理的问题，建立稳定可复用的论坛自动化操作能力。
- **Target Users**: SpecWeave 项目维护者，用于自动化管理 TRAE 大赛专区的三个帖子（Demo帖44601/报名帖44402/竹简悟道帖）。

## Goals
- ✅ 系统性对比四种自动化方案并实际验证可行性
- ✅ 通过 integrated_browser MCP 完成核心操作验证（编辑帖子、发布回复、删除草稿）
- ✅ 记录精确的DOM选择器、操作序列和等待策略
- ✅ 调研 Discourse REST API 与 @discourse/mcp 作为长期方案
- 🔄 开发可复用的操作脚本/工具封装
- 🔄 建立标准化工作流文档和故障排查指南
- 🔄 评估 Skill 封装可行性

## Non-Goals (Out of Scope)
- 不开发自定义爬虫或逆向工程论坛私有接口
- 不实现帖子内容自动生成（AI写作功能）
- 不实现批量注册/灌水等违反论坛规则的功能
- 不实现多账号管理或自动审核绕过
- 不对Discourse平台本身进行修改或插件开发
- 不替代人工审核内容质量的最终环节

## Background & Context

### 实际验证结果

经探索验证，**四种技术方案中 integrated_browser MCP 是当前唯一零配置可用方案**：

| 方案 | 验证结果 | 可用性 | 适用场景 |
|------|---------|--------|---------|
| **integrated_browser MCP** | ✅ 完全验证通过 | ⭐⭐⭐⭐⭐ 立即可用 | Trae IDE内操作，零配置，已登录 |
| **@discourse/mcp** | 📋 调研完成待配置 | ⭐⭐⭐⭐ 长期首选 | AI Agent集成，需OAuth授权 |
| **Discourse REST API** | 📋 调研完成 | ⭐⭐⭐ 高性能场景 | 需API Key，适合后端服务 |
| **agent-browser CLI** | ❌ 沙箱限制受阻 | ⭐⭐ 待解决 | 独立脚本场景，需解决profile权限 |

### 方案选择说明

1. **integrated_browser MCP（当前可用）**：
   - Trae IDE内置浏览器，通过MCP协议控制，**无需额外安装或配置**
   - 已保持forum.trae.cn登录状态，无需重复认证
   - 提供完整的浏览器自动化能力：导航、快照、点击、输入、滚动、JavaScript执行、截图
   - 缺点：MCP工具调用逐条执行，无法通过shell脚本批量串联；依赖Trae IDE环境

2. **@discourse/mcp（长期推荐 v0.2.4）**：
   - Discourse官方MCP服务器，提供18个工具（10只读+8写入）
   - 默认只读模式，写入需显式开启，内置速率限制和自动重试
   - 通过User API Key OAuth授权，普通用户可自助生成，无需管理员权限
   - forum.trae.cn版本2026.3.0-latest支持User API Key
   - 需要Node.js >= 24，需运行npx命令完成OAuth授权流程

3. **Discourse REST API**：
   - 核心端点：创建POST /posts.json、编辑PUT /posts/{id}.json、回复POST /posts.json（带topic_id）、读取GET /t/{id}.json、上传POST /uploads.json
   - 认证：User API Key（`User-Api-Key` header）或Admin API Key（`Api-Key`+`Api-Username` headers）
   - 适合高性能后端集成，但需要API Key管理

4. **agent-browser CLI（v0.28.0）**：
   - 功能强大但在Windows沙箱环境下无法访问用户Chrome Profile目录
   - 作为独立CLI工具在非沙箱环境下可用，支持--session-name持久化、batch批量执行、diff验证

### 已验证的DOM选择器与操作序列

通过 integrated_browser MCP 实际操作forum.trae.cn，确认以下关键信息：

**编辑器类型：textarea.d-editor-input（非iframe、非contenteditable）**

| 操作 | 选择器/方法 | 说明 |
|------|-----------|------|
| 导航到帖子 | `browser_navigate` → URL | 如 https://forum.trae.cn/t/topic/44601 |
| 编辑按钮 | `.post-action-menu__edit` 或JS查找title含"编辑"的button | 帖子右下角铅笔图标 |
| 正文编辑器 | `textarea.d-editor-input` | 标准textarea，可直接设置value |
| 标题输入框 | `input.title` 或编辑弹窗中的标题字段 | 编辑已有帖子时标题可改 |
| 保存按钮 | `button.btn-primary`，文本为"保存" | 提交编辑 |
| 回复按钮（打开） | 底部"回复"按钮 | 打开回复编辑器 |
| 回复编辑器 | `textarea.d-editor-input`（composer内） | 回复的textarea |
| 回复提交按钮 | `button.btn-primary.create`，文本为"回复" | 提交回复 |
| 删除草稿 | `.remove-draft`（btn-danger，trash图标） | 需确认对话框点击"删除" |
| 等待策略 | 固定等待2-3秒 | Discourse SPA加载和操作反馈 |

### 关键教训

1. **标题残留问题**：编辑帖子时，标题输入框可能包含"【标题】"和"【标签】"前缀（Discourse编辑器的UI残留），编辑时必须先清空textarea的value，不能仅append
2. **非标准选择器不可用**：`:has-text()` 等Playwright非标准选择器在 `browser_evaluate` 中不可用，必须用标准DOM API（`querySelectorAll` + `Array.from().filter()`）
3. **提交按钮区分**：编辑保存用 `button.btn-primary`（文本"保存"），回复提交用 `button.btn-primary.create`（文本"回复"），不可混淆
4. **草稿自动保存**：Discourse会自动保存编辑中的草稿，编辑失败/中断后需手动清理草稿
5. **回复验证**：提交回复后页面会跳转到帖子，可导航到 `/last` URL验证最后一页

### 帖子内容源
项目中已有帖子内容以Markdown文件形式管理：
- [specweave-demo-post.md](file:///d:/spaces/SpecWeave/docs/retrospective/reports/competitive-analysis/retrospective-specweave-contest-advantage-analysis-20260624/specweave-demo-post.md) — Demo帖内容
- [specweave-registration-post.md](file:///d:/spaces/SpecWeave/docs/retrospective/reports/competitive-analysis/retrospective-specweave-contest-advantage-analysis-20260624/specweave-registration-post.md) — 报名帖内容
- [报名帖_竹简悟道.md](file:///d:/spaces/SpecWeave/apps/zhujian-wudao/报名帖_竹简悟道.md) — 竹简悟道报名帖

### 调研文档
- [discourse-api-research.md](file:///d:/spaces/SpecWeave/docs/knowledge/operations/discourse-api-research.md) — REST API和@discourse/mcp详细调研

## Functional Requirements

- **FR-1**: ✅ 完成四种技术方案的对比分析和实际可行性验证
- **FR-2**: ✅ 通过 integrated_browser MCP 完成核心操作全流程验证（编辑帖子、发布回复、删除草稿）
- **FR-3**: ✅ 记录精确的DOM选择器、操作序列、等待策略和关键教训
- **FR-4**: 🔄 基于已验证的操作序列，封装可复用的操作工具（脚本或MCP工具序列模板）
- **FR-5**: 📋 完成REST API和@discourse/mcp调研，记录接入要点
- **FR-6**: 🔄 建立帖子Markdown源文件→发布的标准化工作流（含dry-run预览和确认机制）
- **FR-7**: 🔄 沉淀配置文档、使用指南、故障排查手册
- **FR-8**: 🔄 评估将论坛操作封装为项目Skill的可行性

## Non-Functional Requirements

- **NFR-1 安全性**: 任何认证信息（API Key、session文件）存储在本地安全位置，加入.gitignore；禁止明文输出敏感token
- **NFR-2 可逆性**: 所有自动化写操作必须支持dry-run模式，正式执行前展示将要发布/修改的内容供人工确认
- **NFR-3 幂等性**: 编辑操作支持幂等执行（如更新日期标记重复添加检测）
- **NFR-4 可观测性**: 操作完成后返回成功/失败状态、帖子URL、操作结果截图；关键步骤可截图保存
- **NFR-5 合规性**: 严格遵守论坛规则，操作间隔≥3秒，不发送垃圾内容，不绕过审核机制
- **NFR-6 可维护性**: 优先使用语义化定位方式，记录选择器失效时的恢复策略

## Constraints

- **Technical**: 
  - 当前验证环境为Trae IDE + integrated_browser MCP（Windows）
  - Discourse论坛UI可能更新导致选择器失效
  - forum.trae.cn为第三方平台，API访问权限不保证
  - agent-browser CLI在Windows沙箱下有profile目录访问限制
- **Business**: 
  - 所有操作以用户账号身份执行，内容审核由论坛管理员负责
  - 大赛期间帖子内容修改需谨慎，避免误操作
- **Dependencies**: 
  - Trae IDE + integrated_browser MCP（当前可用）
  - @discourse/mcp v0.2.4（长期方案，需Node.js 24+和OAuth配置）
  - forum.trae.cn用户账号（已注册且已登录）

## Assumptions

- ✅ Discourse编辑器使用textarea.d-editor-input（已验证），非iframe/非contenteditable
- ✅ "编辑"按钮可通过`.post-action-menu__edit` class定位（已验证）
- ✅ 用户拥有forum.trae.cn的正常发帖/编辑权限（已通过三个帖子审核验证）
- ✅ 已审核帖子的编辑和回复不会触发重新审核（已验证：回复立即公开）
- integrated_browser MCP的登录状态在Trae IDE重启后保持（cookie有效期取决于论坛设置）
- @discourse/mcp的User API Key OAuth流程在forum.trae.cn上可用（基于版本支持推测）

## Acceptance Criteria

### AC-1: 四种技术方案对比分析完成 ✅
- **Given**: 已调研和/或验证 integrated_browser MCP、agent-browser CLI、Discourse REST API、@discourse/mcp
- **When**: 完成技术方案对比分析
- **Then**: 输出四种方案的对比矩阵，明确各方案适用场景和推荐优先级
- **Verification**: `human-judgment`
- **Status**: 已完成（integrated_browser为当前可用方案，@discourse/mcp为长期推荐）

### AC-2: 核心操作功能验证通过 ✅
- **Given**: integrated_browser MCP已连接且forum.trae.cn已登录
- **When**: 通过MCP工具执行编辑Demo帖（更新日期标记）和发布测试回复
- **Then**: 编辑成功（更新日期改为10:28），回复成功发布（回复数从104→105，内容完整呈现）
- **Verification**: `programmatic` + `human-judgment`
- **Status**: 已完成

### AC-3: DOM选择器和操作序列文档化 ✅
- **Given**: 核心操作已验证通过
- **When**: 记录所有关键操作的DOM选择器、操作步骤、等待策略
- **Then**: 文档包含完整的选择器映射表和操作序列说明
- **Verification**: `human-judgment`
- **Status**: 已完成（见本spec的"已验证的DOM选择器与操作序列"章节）

### AC-4: 备选方案调研完成 ✅
- **Given**: 已查阅Discourse REST API和@discourse/mcp文档
- **When**: 输出备选方案分析文档
- **Then**: REST API端点列表完整，@discourse/mcp工具列表和配置要求明确，三方案对比结论清晰
- **Verification**: `human-judgment`
- **Status**: 已完成（调研报告见docs/knowledge/operations/discourse-api-research.md）

### AC-5: 可复用操作工具封装 🔄
- **Given**: 核心操作序列已验证
- **When**: 封装为可复用的工具/脚本
- **Then**: 提供操作模板：读取帖子、编辑帖子、发布回复，支持参数化（topic ID、内容）
- **Verification**: `programmatic` + `human-judgment`
- **Status**: 待实施

### AC-6: 标准化工作流文档完成 🔄
- **Given**: 操作工具封装完成
- **When**: 梳理从Markdown源文件到论坛发布的完整流程
- **Then**: 输出工作流文档：内容准备→dry-run预览→用户确认→发布执行→结果验证
- **Verification**: `human-judgment`
- **Status**: 待实施

### AC-7: 故障排查指南完成 🔄
- **Given**: 已了解常见失败场景
- **When**: 完成操作手册
- **Then**: 排查指南覆盖（session过期/选择器失效/权限不足/频率限制/保存失败/草稿残留）
- **Verification**: `human-judgment`
- **Status**: 待实施

## Open Questions

- [x] Discourse编辑器是否使用iframe？→ 否，使用textarea.d-editor-input
- [x] 编辑器是contenteditable div还是textarea？→ textarea
- [x] 编辑按钮如何定位？→ .post-action-menu__edit class
- [x] 回复提交后是否需要重新审核？→ 已审核帖子的回复无需重审，立即公开
- [ ] integrated_browser MCP登录状态在Trae IDE重启后保持多久？→ 待观察
- [ ] @discourse/mcp在forum.trae.cn上的User API Key OAuth流程是否顺利？→ 待验证
- [ ] 是否封装为Skill？→ 待评估Task 9
