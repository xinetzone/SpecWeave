# 火山引擎Agent Plan Wiki后续改进 - 任务清单

> **来源**：volcengine-agent-plan-wiki里程碑复盘（seven-concepts R→I→E→C，2026-07-31）
> **创建日期**：2026-07-31
> **状态**：进行中（2/4已完成）

## 行动项总览

| ID | 行动项 | 优先级 | 状态 | 完成日期 |
|----|--------|--------|------|---------|
| ACT-01 | 飞书云文档DOM提取模式沉淀到patterns库 | 中 | ✅ 已完成 | 2026-07-31 |
| ACT-02 | 后续飞书文档提取任务中验证`.ace-line`选择器稳定性 | 中 | ⏳ 待验证 | - |
| ACT-03 | 批量生成wiki后增加"元数据一致性检查"步骤到工作流 | 低 | ✅ 已完成 | 2026-07-31 |
| ACT-04 | Wiki扩展分析章节增加"💡知识拓展"标记区分原文与衍生分析 | 低 | ✅ 已完成 | 2026-07-31 |

---

## [x] ACT-01: 飞书云文档DOM提取模式沉淀

- **Priority**: medium
- **Depends On**: None
- **Description**: 将飞书DOM提取模式沉淀到`.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/`
- **完成情况**:
  - ✅ 创建模式文档 [feishu-doc-dom-extraction.md](../../../../../.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/feishu-doc-dom-extraction.md)
  - ✅ 包含3套代码片段：browser_evaluate(JS)、Playwright(Python)、Puppeteer(Node.js)
  - ✅ 包含关键DOM选择器表（`.bear-web-x-container` + `.ace-line`）
  - ✅ 包含7个反模式和正确做法对照
  - ✅ 包含企业SaaS文档通用降级策略（defuddle→WebFetch→DOM提取三级）
  - ✅ 包含其他平台探测提示（钉钉/企微/Notion/Confluence）
  - ✅ 包含通用滚动容器探测脚本
  - ✅ 明确与defuddle-web-extraction-preferred模式的降级关系
- **Acceptance Criteria**: 模式文档完整，含触发场景/核心步骤/代码片段/反模式/验证清单/迁移验证

## [ ] ACT-02: 验证`.ace-line`选择器在多场景下的稳定性

- **Priority**: medium
- **Depends On**: 未来遇到飞书文档提取任务时触发
- **Description**: 在后续飞书文档提取任务中验证飞书DOM选择器的稳定性
- **验证场景**（至少覆盖2个不同类型文档后可升级到L2）：
  - [ ] 飞书docx类型文档（非wiki页面）
  - [ ] 飞书多维表格/知识库空间页面
  - [ ] 含复杂表格的飞书文档
  - [ ] 含图片/附件的飞书文档
  - [ ] 飞书更新DOM结构后的兼容性验证
- **验证方法**：
  1. 打开目标飞书文档
  2. 在DevTools Console执行 `document.querySelector('.bear-web-x-container')` 检查滚动容器
  3. 执行 `document.querySelectorAll('.ace-line')` 检查文本行提取
  4. 如果选择器失效，使用模式文档中的"通用探测方法"重新定位
  5. 更新模式文档的验证记录和成熟度级别
- **Acceptance Criteria**: 至少2个不同飞书文档验证选择器有效，更新validation_count和maturity级别
- **备注**：此为被动验证项，在下次处理飞书文档时顺便执行，无需主动安排

## [x] ACT-03: 批量wiki生成后元数据一致性检查

- **Priority**: low
- **Depends On**: None
- **Description**: 在wiki创建工作流中增加元数据一致性检查步骤
- **完成情况**:
  - ✅ 在[tech-wiki-tutorial-creation.md](../../../../../.agents/docs/retrospective/patterns/documentation-patterns/tech-wiki-tutorial-creation.md)新增"步骤6：批量生成后元数据一致性检查（必做）"
  - ✅ 包含7项检查清单：source/date/category/tags/id/交叉链接/跨wiki链接
  - ✅ 在反模式表中新增"批量生成后不检查元数据"条目
- **Acceptance Criteria**: 元数据检查步骤已纳入wiki创建模式文档，后续wiki生成任务可参照执行

## [x] ACT-04: 扩展分析章节增加💡知识拓展标记

- **Priority**: low
- **Depends On**: None
- **Description**: 在Wiki的衍生分析章节增加明确标记，区分原文事实与知识库关联分析
- **完成情况**:
  - ✅ 在[06-crossmodal-paradigm.md](../../../../../.agents/docs/knowledge/learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/06-crossmodal-paradigm.md)章节开头添加📌内容说明
  - ✅ 在"一、范式演进"前添加💡知识拓展标记
  - ✅ 在"二、典型链路"前添加💡知识拓展标记
  - ✅ 在"三、Harness关联"前添加💡知识拓展标记（含跨wiki链接）
  - ✅ 在"四、实践建议"前添加💡知识拓展标记
  - ✅ 修复了重复标题问题
- **Acceptance Criteria**: 所有衍生分析章节有明确标记，读者可清晰区分原文内容与拓展分析

---

## 产出物清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `patterns/methodology-patterns/tools-automation/feishu-doc-dom-extraction.md` | 新增 | 飞书DOM提取模式（3套代码片段） |
| `patterns/documentation-patterns/tech-wiki-tutorial-creation.md` | 更新 | 新增步骤6元数据一致性检查 |
| `volcengine-agent-plan-wiki/06-crossmodal-paradigm.md` | 更新 | 添加💡知识拓展标记 |
