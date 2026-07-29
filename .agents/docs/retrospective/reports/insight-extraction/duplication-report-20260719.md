---
title: "insight-extraction Markdown 重复度扫描报告"
source: "check-markdown-duplication.py"
generated_at: "2026-07-19"
type: "duplication-analysis"
scan_dir: ".agents/docs/retrospective/reports/insight-extraction"
threshold: 15
window: 3
json_data: "duplication-report-20260719.json"
---
# insight-extraction Markdown 重复度扫描报告

> **扫描日期**：2026-07-19
> **工具**：[check_markdown_duplication.py](../../../../scripts/check_markdown_duplication.py)（N=3，阈值=15行）
> **范围**：`insight-extraction/` 下全部 Markdown 报告（排除 README.md 索引文件）

## 一、扫描概况

| 指标 | 值 |
|------|---|
| 扫描目录 | external-learning/ + iot-ecosystem/ |
| 重复组数 | **46 组** |
| 累计重复行数 | 约 **4,116 行** |
| 受影响文件 | **48 个** |
| 阈值 | 15 行（低于此值不报告） |
| N元语法窗口 | 3 行 |

## 二、重复类型分类

### 类型 A：模板化文件跨复现复制（高优先级处理）

| 文件名 | 出现组数 | 性质 | 建议 |
|--------|---------|------|------|
| `execution-retrospective.md` | 41 组 | **复盘执行模板**，每个复盘目录都复制一份，内容高度雷同 | 提取为共享模板（`.agents/templates/execution-retrospective-template.md`），各复盘通过引用或符号链接使用 |
| `export-suggestions.md` | 13 组 | **导出建议模板**，结构固定（模式提取/知识路径/行动项等章节） | 同上，提取为共享模板 |
| `insight-action-backlog.md` | 7 组 | **行动项积压模板**，结构高度相似 | 同上，提取为共享模板 |
| `insight-extraction.md` | 8 组 | **洞察提取模板**，各复盘使用相同提取框架 | 同上，提取为共享模板 |

**类型 A 预估可消除重复行数**：约 3,000+ 行（占总重复的 ~73%）

### 类型 B：同目录内文件内容重叠（需人工审核）

| 目录 | 重复行数 | 涉及文件 | 说明 |
|------|---------|---------|------|
| `retrospective-md2card-indie-dev-20260707/` | 104+82+75+73+64+28 = 426L | analysis-report.md ↔ success-factors.md, core-insights.md, practical-recommendations.md, methodologies.md | 同一篇分析被拆分到多个文件，内容高度重叠 |
| `retrospective-tuyaopen-analysis-20260630/` | 102+51+42+38+31+27+27 = 318L | action-plan/*.md ↔ architecture-insight.md | 行动项与架构洞察内容重叠 |
| `retrospective-tuya-home-assistant-learning-20260630/` ↔ tuyaopen | 42+31+26 = 99L | core-pattern-details.md 之间 | 两个tuya系列复盘的core-pattern-details存在跨目录复制 |

**类型 B 预估可消除重复行数**：约 800+ 行（占总重复的 ~20%）

### 类型 C：跨同主题复盘的模板性内容

| 重复组 | 涉及目录 | 行数 | 说明 |
|--------|---------|------|------|
| volcengine 系列4个复盘 | vibe-coding-prompts, volcengine-cua, volcengine-mobile-use, volcengine-mua-skill-api-guide | 86+76+58+47+44+44+30+28 = 413L | 火山引擎系列4个复盘共用相同的执行模板和导出建议模板（类型A的具体实例） |
| agency-deep-learning ↔ skills-article | 36L | 两篇学习复盘的execution-retrospective高度相似（类型A实例） |

**类型 C**：本质上也是类型 A 的具体表现，模板提取后自动消除。

## 三、归并建议表

### 3.1 模板提取（优先级：高）

| 主保留文件 | 建议归并文件 | 策略 | 预估减少行数 |
|-----------|-------------|------|------------|
| `.agents/templates/execution-retrospective-template.md`（新建） | 所有 `*/execution-retrospective.md`（约20+份） | 提取为共享模板，各复盘只保留差异化内容 | ~2,000 行 |
| `.agents/templates/export-suggestions-template.md`（新建） | 所有 `*/export-suggestions.md`（约10+份） | 提取为共享模板 | ~500 行 |
| `.agents/templates/insight-extraction-template.md`（新建） | 所有 `*/insight-extraction.md`（约8份） | 提取为共享模板 | ~400 行 |
| `.agents/templates/insight-action-backlog-template.md`（新建） | 所有 `*/insight-action-backlog.md`（约7份） | 提取为共享模板 | ~300 行 |

### 3.2 同目录内容合并（优先级：中，需人工审核内容）

| 主保留文件 | 建议归并文件 | 策略 |
|-----------|-------------|------|
| `retrospective-md2card-indie-dev-20260707/analysis-report.md` | core-insights.md, success-factors.md, practical-recommendations.md | 分析报告与各专题文件高度重叠，建议合并为单文件或明确文件边界 |
| `retrospective-tuyaopen-analysis-20260630/architecture-insight.md` | action-plan/*.md | 架构洞察与行动项内容重叠，行动项应引用架构洞察而非重复描述 |
| `retrospective-tuya-home-assistant-learning/core-pattern-details.md` | tuyaopen 的对应文件 | 两个tuya复盘的模式描述有重叠，考虑提取为共享模式文档 |

### 3.3 误报排除

以下内容不视为真正重复，无需处理：
- **frontmatter 模板段落**：YAML frontmatter 中的通用字段（source/type/tags 等）格式统一但内容各异
- **章节标题**：如"## 执行摘要"、"## 核心发现"等结构性标题
- **引用段落**：对AGENTS.md或规范文件的标准化引用语句
- **导航/索引内容**：README.md 中的目录索引（已在扫描中排除）

## 四、重复组详情（Top 15）

| # | 行数 | 文件数 | 涉及位置 | 类型 |
|---|------|--------|---------|------|
| 1 | 104L | 2 | md2card-indie-dev: analysis-report.md ↔ success-factors.md | B |
| 2 | 102L | 2 | tuyaopen: action-plan/action-long-term.md ↔ action-medium-term.md | B |
| 3 | 86L | 4 | volcengine系列4个复盘: execution-retrospective.md | A/C |
| 4 | 82L | 2 | md2card-indie-dev: analysis-report.md ↔ core-insights.md | B |
| 5 | 76L | 4 | volcengine系列4个复盘: execution-retrospective.md | A/C |
| 6 | 75L | 2 | md2card-indie-dev: analysis-report.md ↔ methodologies.md | B |
| 7 | 73L | 2 | md2card-indie-dev: success-factors.md ↔ practical-recommendations.md | B |
| 8 | 64L | 2 | md2card-indie-dev: core-insights.md ↔ critical-analysis.md | B |
| 9 | 58L | 4 | volcengine系列4个复盘: execution-retrospective.md | A/C |
| 10 | 51L | 2 | tuyaopen: action-short-term.md ↔ action-medium-term.md | B |
| 11 | 47L | 4 | volcengine系列4个复盘: export-suggestions.md | A/C |
| 12 | 44L | 2 | volcengine-cua ↔ volcengine-mua-skill-api-guide | A/C |
| 13 | 44L | 2 | volcengine-cua ↔ volcengine-mua-skill-api-guide | A/C |
| 14 | 42L | 2 | tuya-home-assistant ↔ tuyaopen: core-pattern-details.md | B |
| 15 | 42L | 2 | tuyaopen: architecture-insight.md ↔ action-long-term.md | B |

完整46组数据见 [duplication-report-20260719.json](duplication-report-20260719.json)。

## 五、注意事项

1. **本报告只输出扫描结果和归并建议，实际文件合并/删除在后续独立任务执行**，避免本次大规模内容变更
2. **类型 A（模板提取）收益最大**：提取4个共享模板可消除 ~73% 的重复行，改动风险低
3. **类型 B（同目录合并）需谨慎**：涉及内容判断，建议每个目录单独评估，避免丢失有价值的差异化分析
4. **模板提取后**：各复盘的 execution-retrospective.md 等文件应改为引用模板路径，或使用生成器自动填充
5. **后续可将 check-markdown-duplication.py 纳入 CI**：设置合理阈值，在新增复盘报告时检测意外的内容复制粘贴

## 六、后续行动项

| # | 行动 | 优先级 | 依赖 |
|---|------|--------|------|
| 1 | 提取 execution-retrospective-template.md 并批量替换各复盘引用 | 高 | 本报告 |
| 2 | 提取 export-suggestions-template.md / insight-extraction-template.md / insight-action-backlog-template.md | 高 | 行动1 |
| 3 | 审核 md2card-indie-dev 目录，合并重叠文件 | 中 | 模板提取完成后 |
| 4 | 审核 tuyaopen / tuya-home-assistant 目录，处理跨复盘重复 | 中 | 模板提取完成后 |
| 5 | 将 check-markdown-duplication.py 纳入 CI（warn-only） | 低 | 类型A处理完成后 |
