# 火山引擎Agent Plan Wiki后续改进 - 任务清单

> **来源**：volcengine-agent-plan-wiki里程碑复盘（seven-concepts R→I→E→C，2026-07-31）
> **创建日期**：2026-07-31
> **最后更新**：2026-07-31（二次验证+自动化脚本+SaaS适配草案完成）
> **状态**：进行中（4/4原始ACT已闭环，新增后续项跟踪中）

## 行动项总览

### 原始复盘行动项（R→I→E→C产出）

| ID | 行动项 | 优先级 | 状态 | 完成日期 |
|----|--------|--------|------|---------|
| ACT-01 | 飞书云文档DOM提取模式沉淀到patterns库 | 中 | ✅ 已完成 | 2026-07-31 |
| ACT-02 | 验证`.ace-line`选择器稳定性 | 中 | ✅ 二次验证通过 | 2026-07-31 |
| ACT-03 | 批量wiki生成后元数据一致性检查步骤 | 低 | ✅ 已完成 | 2026-07-31 |
| ACT-04 | 扩展分析章节增加💡知识拓展标记 | 低 | ✅ 已完成 | 2026-07-31 |

### 二次迭代新增行动项

| ID | 行动项 | 优先级 | 状态 | 完成日期 |
|----|--------|--------|------|---------|
| ACT-05 | 创建飞书文档提取自动化脚本（feishu-doc-extract.py） | 高 | ✅ 已完成 | 2026-07-31 |
| ACT-06 | 模式参数优化（scrollStep 600→400px, waitMs 1000→1500ms） | 中 | ✅ 已完成 | 2026-07-31 |
| ACT-07 | 多SaaS平台DOM提取适配方案草案 | 中 | ✅ 已完成 | 2026-07-31 |
| ACT-08 | 其他平台（钉钉/企微/语雀等）选择器实测验证 | 中 | ⏳ 按需触发 | - |
| ACT-09 | 统一多平台saas-doc-extract.py脚本 | 低 | ⏳ 待规划 | - |

---

## [x] ACT-01: 飞书云文档DOM提取模式沉淀

- **完成情况**:
  - ✅ 创建模式文档 [feishu-doc-dom-extraction.md](../../../../../.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/feishu-doc-dom-extraction.md)
  - ✅ V2质量门：6类反目标场景、2个失败案例、7个早期预警信号
  - ✅ 包含3套代码片段（browser_evaluate/Playwright/Puppeteer）
  - ✅ 明确企业SaaS三级降级策略
  - ✅ validation_count=2, maturity=L1
- **Acceptance Criteria**: 模式文档完整通过V2质量检查 ✅

## [x] ACT-02: 验证`.ace-line`选择器稳定性（二次验证）

- **验证结果**（2026-07-31 MCP浏览器实测）：
  - ✅ `.bear-web-x-container`选择器稳定（DIV，class含`catalogue-opened docx-in-wiki`变体）
  - ✅ `.ace-line`选择器稳定（43行完整提取，1542字符）
  - ✅ 五大方向emoji（🔬🤖🎨💻🌱）全部识别
  - ✅ 8个官方URL全部保留（subscribe+console+6个docs链接）
  - ✅ 标题提取正确
  - ⚠️ 发现虚拟滚动DOM回收行为（scrollTop≥800px时顶部DOM移除）
  - ⚠️ 发现scrollStep=600px导致长段落截断（已修复为400px）
- **剩余验证场景**（下次遇到飞书文档时执行）：
  - [ ] 飞书docx类型文档（非wiki页面）
  - [ ] 含复杂表格的飞书文档
  - [ ] 含图片/附件的飞书文档

## [x] ACT-03: 批量wiki生成后元数据一致性检查

- **完成情况**:
  - ✅ 在[tech-wiki-tutorial-creation.md](../../../../../.agents/docs/retrospective/patterns/documentation-patterns/tech-wiki-tutorial-creation.md)新增"步骤6：批量生成后元数据一致性检查（必做）"
  - ✅ 7项检查清单：source/date/category/tags/id/交叉链接/跨wiki链接
- **Acceptance Criteria**: ✅

## [x] ACT-04: 扩展分析章节增加💡知识拓展标记

- **完成情况**:
  - ✅ 在[06-crossmodal-paradigm.md](../../../../../.agents/docs/knowledge/learning/03-agent-platforms-tools/volcengine-agent-plan-wiki/06-crossmodal-paradigm.md)添加4处💡标记+章节开头📌说明
  - ✅ 修复重复标题问题
- **Acceptance Criteria**: ✅

## [x] ACT-05: 飞书文档提取自动化脚本

- **完成情况**:
  - ✅ 创建[feishu-doc-extract.py](../../../../../.agents/scripts/feishu-doc-extract.py)
  - ✅ Playwright驱动，支持有头/无头模式
  - ✅ 集成全部10项反模式/质量检查
  - ✅ 双向扫描（向下→向上→向下）
  - ✅ 自动输出元数据报告（JSON）
  - ✅ 内置平台自动检测（detect_saas_platform）
  - ✅ 内容阈值检查、链接保留验证、空行比例检测
- **Acceptance Criteria**: ✅

## [x] ACT-06: 模式参数优化

- **完成情况**:
  - ✅ scrollStep: 600px → 400px（基于实测长段落截断数据）
  - ✅ waitMs: 1000ms → 1500ms（确保虚拟滚动渲染）
  - ✅ 初始等待: 1500ms → 2000ms
  - ✅ 选择器作用域: document → container（避免UI噪音）
  - ✅ 新增实测验证结果表
  - ✅ 3套代码片段参数同步更新
- **Acceptance Criteria**: ✅

## [x] ACT-07: 多SaaS平台DOM提取适配方案草案

- **完成情况**:
  - ✅ 创建[saas-doc-extraction-adaptation-draft.md](../../../../../.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/saas-doc-extraction-adaptation-draft.md)
  - ✅ 7大平台候选选择器（钉钉/企微/语雀/石墨/WPS/Notion/Confluence）
  - ✅ 通用DOM探测脚本（自动定位滚动容器+文本行选择器）
  - ✅ 4阶段实施路线图
  - ✅ 跨平台统一10项反模式检查清单
  - ✅ 风险与注意事项（版本风险/合规/反爬/Canvas兜底/iframe）
- **Acceptance Criteria**: ✅

## [ ] ACT-08: 其他平台选择器实测验证

- **Priority**: medium
- **触发条件**: 遇到钉钉/企微/语雀/Notion等平台文档时
- **验证方法**: 运行通用探测脚本 → 验证候选选择器 → 更新适配方案表
- **Acceptance Criteria**: 每个平台验证后创建独立pattern文档

## [ ] ACT-09: 统一多平台提取脚本

- **Priority**: low
- **Depends On**: ACT-08至少完成2个平台验证
- **Description**: 将feishu-doc-extract.py扩展为支持多平台自动检测和提取

---

## 产出物清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `patterns/.../feishu-doc-dom-extraction.md` | 新增→更新 | 飞书DOM提取模式（V2质量门通过，参数优化后） |
| `patterns/.../saas-doc-extraction-adaptation-draft.md` | 新增 | 多SaaS平台适配方案草案 |
| `scripts/feishu-doc-extract.py` | 新增 | 飞书文档自动化提取脚本（10项质量检查） |
| `patterns/documentation-patterns/tech-wiki-tutorial-creation.md` | 更新 | 步骤6元数据一致性检查 |
| `volcengine-agent-plan-wiki/06-crossmodal-paradigm.md` | 更新 | 💡知识拓展标记 |
| `.trae/specs/volcengine-agent-plan-wiki-followups/tasks.md` | 更新 | 任务跟踪清单 |
