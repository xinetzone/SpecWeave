# TRAE 论坛自动编辑与发布功能探索与集成 - The Implementation Plan

> **注意**：经实际验证，原定方案（agent-browser CLI）因Windows沙箱限制无法访问Chrome Profile，最终采用 **Trae IDE集成浏览器（integrated_browser MCP）** 完成核心验证。@discourse/mcp 调研确认为长期最优方案。

## [x] Task 1: 技术方案对比与可行性验证
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 对比四种技术方案：integrated_browser MCP、agent-browser CLI、Discourse REST API、@discourse/mcp
  - 实际验证各方案可用性
  - 结论：integrated_browser MCP零配置立即可用；@discourse/mcp为长期首选；agent-browser CLI因沙箱限制受阻
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgment` TR-1.1: 四方案对比矩阵完整，各方案适用场景明确
  - `human-judgment` TR-1.2: 结论有实际验证证据支持
- **Status**: 已完成

## [x] Task 2: 核心操作全流程验证
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 通过 integrated_browser MCP 完成以下操作验证：
    - ✅ 导航到帖子页面（browser_navigate）
    - ✅ 定位并点击编辑按钮（.post-action-menu__edit）
    - ✅ 修改正文内容（textarea.d-editor-input，设置value）
    - ✅ 保存编辑（button.btn-primary text="保存"）
    - ✅ 发布回复（打开回复框→填写内容→button.btn-primary.create text="回复"）
    - ✅ 验证结果（刷新页面/snapshot确认内容变更）
    - ✅ 删除草稿（.remove-draft按钮+确认对话框）
  - 记录精确的DOM选择器和操作序列
  - 记录关键教训（标题残留、非标准选择器、提交按钮区分、草稿清理）
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: 编辑操作成功（Demo帖更新日期改为10:28并验证）
  - `programmatic` TR-2.2: 回复操作成功（回复数104→105，内容完整呈现）
  - `programmatic` TR-2.3: 草稿清理成功（2个草稿全部删除）
  - `human-judgment` TR-2.4: 选择器映射表完整，操作序列可复现
- **Status**: 已完成

## [x] Task 3: 备选方案调研（REST API & @discourse/mcp）
- **Priority**: medium
- **Depends On**: None (可并行)
- **Description**:
  - 调研Discourse REST API核心端点（创建/编辑/回复/读取/上传）
  - 调研认证方式（Admin API Key vs User API Key）
  - 分析forum.trae.cn是否支持User API Key（版本2026.3.0-latest支持）
  - 调研@discourse/mcp v0.2.4（18个工具、默认只读、OAuth授权）
  - 输出调研报告到 docs/knowledge/operations/discourse-api-research.md
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgment` TR-3.1: REST API端点列表完整（方法、路径、参数、认证）
  - `human-judgment` TR-3.2: @discourse/mcp工具列表和配置说明完整
  - `human-judgment` TR-3.3: 三方案（MCP/API/浏览器）适用场景对比明确
- **Status**: 已完成

## [ ] Task 4: 知识库文档沉淀
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 将探索成果沉淀为 docs/knowledge/FORUM-AUTOMATION.md 知识库文档
  - 文档包含以下章节：
    1. 方案概述（四种方案对比和选型建议）
    2. 快速开始：使用integrated_browser MCP操作论坛的步骤
    3. DOM选择器参考表（已验证的精确选择器）
    4. 操作序列模板（编辑帖子/发布回复/删除草稿的完整步骤）
    5. JavaScript代码片段（可用于browser_evaluate的复用函数）
    6. @discourse/mcp接入指南（长期方案的配置步骤）
    7. 常见问题与故障排查
    8. 安全注意事项
  - 文档遵循项目知识库规范，链接可跳转
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7
- **Test Requirements**:
  - `human-judgment` TR-4.1: 文档包含上述8个章节，结构清晰
  - `human-judgment` TR-4.2: 操作序列模板可直接复现
  - `programmatic` TR-4.3: 文档中所有内部链接有效
  - `human-judgment` TR-4.4: 故障排查覆盖至少6种场景
- **Notes**: 使用中文撰写；参考 docs/knowledge/ 目录下已有文档风格

## [ ] Task 5: Skill封装可行性评估与实施
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 评估是否值得将论坛操作封装为项目Skill
  - 如果封装，Skill应包含：
    - 触发条件（用户提到"发帖"、"编辑帖子"、"更新论坛"、"回复帖子"等）
    - 工作流描述（通过integrated_browser MCP执行操作的完整流程）
    - DOM选择器和操作序列（从知识库引用）
    - 安全检查（dry-run确认、操作间隔、内容预览）
    - 错误处理指南
  - 如果评估认为值得封装，创建 .agents/skills/forum-posting/SKILL.md（或对应skill目录）
  - 如果认为暂不需要封装，输出评估结论和理由
- **Acceptance Criteria Addressed**: AC-7（部分）
- **Test Requirements**:
  - `human-judgment` TR-5.1: 评估报告包含利弊分析，结论明确
  - `human-judgment` TR-5.2: 如封装Skill，SKILL.md结构完整，触发条件明确
- **Notes**: 考虑到当前方案依赖Trae IDE的integrated_browser MCP，Skill封装价值在于将操作知识固化为AI可自动执行的流程

## [ ] Task 6: 更新主题看板与索引
- **Priority**: low
- **Depends On**: Task 4, Task 5
- **Description**:
  - 更新 .trae/specs/standards-tools/README.md，登记本spec状态为已完成
  - 更新 .trae/specs/README.md 全局看板统计
  - 确保新增的知识库文档在docs导航中可查
  - 将调研报告从.temp/移动到合适的归档位置（如docs/knowledge/references/）
- **Acceptance Criteria Addressed**: (流程性任务)
- **Test Requirements**:
  - `programmatic` TR-6.1: standards-tools/README.md 中包含本spec条目且状态正确
  - `programmatic` TR-6.2: 全局看板统计数字正确
  - `programmatic` TR-6.3: 所有文档链接有效（可运行check-links.py验证）
