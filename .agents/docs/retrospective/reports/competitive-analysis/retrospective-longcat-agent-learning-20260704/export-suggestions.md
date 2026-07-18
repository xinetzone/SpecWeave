---
id: "export-longcat-wiki-20260704"
title: "导出建议"
source: "task-execution"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/competitive-analysis/retrospective-longcat-agent-learning-20260704/export-suggestions.toml"
---
# 导出建议

## 一、可沉淀为模式库资产

### 建议一：新建模式 `format-reference-over-memory.md`

- **领域**：方法论
- **层级**：L1（实验性，validation_count=1）
- **内容**：创建新文件前，必须先读取同目录 1-2 个现有文件确认实际格式，以现有文档做法为权威标准，而非依赖 project_memory 或模板描述
- **验证案例**：
  1. TEXT-to-CAD Wiki：子代理凭 project_memory 使用 TOML frontmatter（`+++`），实际应使用 YAML（`---`）→ 事后修复
  2. MopMonk Wiki：同样出现 TOML→YAML 格式错误 → 事后修复
  3. LongCat Wiki：创建前先读取现有文件确认格式 → 一次正确，0 修复
- **绑定**：关联到本复盘报告（source: `retrospective-longcat-agent-learning-20260704`）

### 建议二：升级模式 `document-content-funnel.md`（L2→L3）

- **当前状态**：L2（已验证，validation_count≥2），定义四层漏斗模型（L1 原始网页→L2 干净文本→L3 结构化大纲→L4 wiki 成品）
- **建议升级理由**：本次任务在 L3 层增加了"原子化决策检查点"（4 项量化判断标准），经实战验证有效（0 返工）
- **升级内容**：在 L3 结构化大纲层增加"原子化决策"步骤，包含 4 项判断标准表格
- **reuse_count**：本次为第 3+ 次使用（MopMonk、TEXT-to-CAD、LongCat 等），满足 L3 升级条件

### 建议三：升级模式 `commit-quality-gate-staging-inspection.md`（L3）

- **当前状态**：L3（可复用，reuse_count≥1），定义三查暂存法
- **建议升级理由**：本次任务中 x-toml-ref 自动化验证（fix-x-toml-ref.py）在提交前消除了所有路径错误，应纳入三查清单
- **升级内容**：在三查中增加"x-toml-ref 自动化验证"检查项

## 二、可更新为模板改进

### 建议四：更新 `wiki-spec-template.md`

1. **L1 层增加微信文章提取指引**：在 L1 内容提取层增加"微信公众号文章特殊处理"小节，说明 WebFetch 不可用时的备选方案（defuddle CLI、kimi-webbridge）
2. **DoD 表增加自动化验证行**：在标准完成定义表中增加"自动化验证通过"行，包含 fix-x-toml-ref.py、check-links.py、check-filename-convention.py 三重验证
3. **L3 层增加原子化决策检查点**：在 L3 结构化大纲层增加"原子化决策"为强制步骤

## 三、可创建为知识库资源

### 建议五：无需额外操作

本次 Wiki 教程本身已作为知识库资源完成归档（`docs/knowledge/learning/longcat-agent-learning-wiki.md`），知识库索引已更新。无需额外导出操作。

## 四、导出优先级

| 优先级 | 建议 | 类型 | 预计工作量 |
|--------|------|------|-----------|
| 高 | 建议四：更新 wiki-spec-template.md | 模板改进 | 10 分钟 |
| 中 | 建议一：新建模式文件 | 模式库 | 10 分钟 |
| 中 | 建议二：升级 document-content-funnel.md | 模式升级 | 5 分钟 |
| 低 | 建议三：升级 commit-quality-gate 模式 | 模式升级 | 5 分钟 |