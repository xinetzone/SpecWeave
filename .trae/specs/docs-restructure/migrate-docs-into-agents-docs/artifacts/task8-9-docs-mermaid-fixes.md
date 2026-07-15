---
source:
  - "tasks.md#Task 8"
  - "artifacts/task8-7-mermaid-batches.md"
generated_at: "2026-07-15"
task: "SubTask 8.9"
type: "docs-mermaid-fixes"
status: "completed"
---

# Task 8.9 第一批 `.agents/docs` 高价值人类文档 Mermaid 修复摘要

## 处理范围

- 仅处理 `task8-7-mermaid-batches.md` 中 `H1/H2` 批次的高价值样本，共 8 个文件：
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/00-overview.md`
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/01-core-concepts.md`
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/10-case-study.md`
  - `.agents/docs/knowledge/mdi-research/01-feasibility-analysis.md`
  - `.agents/docs/knowledge/mdi-research/02-ecosystem-comparison.md`
  - `.agents/docs/knowledge/mdi-research/03-technical-architecture.md`
  - `.agents/docs/knowledge/learning/07-vendor-product-learning/volcengine/volcengine-computer-use-agent-analysis.md`
  - `.agents/docs/knowledge/learning/07-vendor-product-learning/volcengine/volcengine-eip-analysis.md`
- 未处理纯归档或历史产出目录。
- 未修改 `AGENTS.md`、`project-governance/documentation-governance` 路径、`tasks.md`。
- 处理策略：只做 Mermaid 安全写法最小修复，不改动图表表达意图与正文结构。

## 样本选择理由

- `H1` 选择 `harness-seven-components-wiki`：属于 Agent 工程方法论文档簇，入口页、核心流程图、案例时序图都具有高复用价值。
- `H2` 选择 `mdi-research`：属于平台/架构分析类核心资料，技术架构图会被后续学习与复用反复引用。
- `H2` 选择 `volcengine` 两篇分析：都是真实产品接入/架构分析文档，且错误集中在 `subgraph` 裸中文 ID，修复收益高、改动风险低。

## 修复结果

| 文件 | 批次 | 修复动作 | 结果 |
|---|---|---|---|
| `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/00-overview.md` | H1 | 删除 Mermaid 代码块内空行 | 七组件总览图通过定向 Mermaid 校验 |
| `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/01-core-concepts.md` | H1 | 将 `subgraph` 中文 ID 改为英文 ID + 中文标题；去除空行；将边标签改为安全引号写法 | 组件协作流程图通过定向 Mermaid 校验 |
| `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/10-case-study.md` | H1 | 将两个图中的裸中文 `subgraph` ID 改为英文 ID；为中文 participant 别名补引号；清除代码块内空行 | 架构图与时序图均通过定向 Mermaid 校验 |
| `.agents/docs/knowledge/mdi-research/01-feasibility-analysis.md` | H2 | 将 `可行性维度`、`评分` 两个 `subgraph` 改为安全英文 ID | 可行性评估图通过定向 Mermaid 校验 |
| `.agents/docs/knowledge/mdi-research/02-ecosystem-comparison.md` | H2 | 将三个 `subgraph` 改为安全英文 ID；同步更新 `style` 目标，消除中文 ID 引发的 warning | 互补关系图通过定向 Mermaid 校验且无 warning |
| `.agents/docs/knowledge/mdi-research/03-technical-architecture.md` | H2 | 将五个层级 `subgraph` 改为安全英文 ID；同步更新 `style` 目标 | 模块依赖关系图通过定向 Mermaid 校验且无 warning |
| `.agents/docs/knowledge/learning/07-vendor-product-learning/volcengine/volcengine-computer-use-agent-analysis.md` | H2 | 将 3 组流程/架构图中的中文 `subgraph` ID 统一改为英文 ID + 中文标题 | 自有设备接入、整体架构、Agent 通信图均通过定向 Mermaid 校验 |
| `.agents/docs/knowledge/learning/07-vendor-product-learning/volcengine/volcengine-eip-analysis.md` | H2 | 将 2 组网络/生态图中的中文 `subgraph` ID 改为安全英文 ID + 中文标题 | 容灾架构图与生态协同图通过定向 Mermaid 校验 |

## 校验记录

### 1. 编辑器诊断

- 对 8 个已编辑文件运行诊断，结果均为 `0` 个新增问题。

### 2. Mermaid 定向校验

- 由于 `check-mermaid.py --path <file>` 当前仍以目录扫描为主，采用检查器底层 `_process_file()` 对 8 个目标文件做定向复扫。
- 执行命令：

```bash
python -X utf8 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.agents/scripts').resolve())); from lib.checks import mermaid; root = Path('.').resolve(); files = [Path(r'.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/00-overview.md'), Path(r'.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/01-core-concepts.md'), Path(r'.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/10-case-study.md'), Path(r'.agents/docs/knowledge/mdi-research/01-feasibility-analysis.md'), Path(r'.agents/docs/knowledge/mdi-research/02-ecosystem-comparison.md'), Path(r'.agents/docs/knowledge/mdi-research/03-technical-architecture.md'), Path(r'.agents/docs/knowledge/learning/07-vendor-product-learning/volcengine/volcengine-computer-use-agent-analysis.md'), Path(r'.agents/docs/knowledge/learning/07-vendor-product-learning/volcengine/volcengine-eip-analysis.md')]; total_err = total_warn = 0; bad = 0; print('[检查] 定向 Mermaid 校验');\
for f in files:\
    issues, fixes, diffs = mermaid._process_file((root / f).resolve(), root, fix=False, dry_run=False);\
    errs = [i for i in issues if i[1] == 'error']; warns = [i for i in issues if i[1] == 'warning'];\
    if issues:\
        bad += 1;\
        print(f'[文件] {f.as_posix()}');\
        [print(f'  [{lvl}] L{ln}: {msg}') for ln, lvl, msg in issues];\
    total_err += len(errs); total_warn += len(warns);\
print(f'[结果] files={len(files)} bad={bad} errors={total_err} warnings={total_warn}');\
sys.exit(1 if total_err else 0)"
```

- 校验结果：`files=8 bad=0 errors=0 warnings=0`。

## 备注

- 本轮是 `SubTask 8.9` 第一批样本修复，优先覆盖 `H1/H2` 中最有复用价值且错误形态明确的文档。
- `openai/chatgpt-codex-wiki` 当前以 `mindmap` 冒号 warning 为主，无 `error`，本批未纳入。
- `H1` 中 `seven-concepts-monkeycode-vibe-coding-wiki` 与 `seven-concepts-india-manufacturing-wiki` 已在第二批目录簇治理中完成收敛，见下文。

## 第二批处理范围

- 本批继续执行 `SubTask 8.9`，按 `task8-7-mermaid-batches.md` 的 `H1` 目录簇策略处理：
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/`
  - `.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/`
- 处理原则保持不变：只修 Mermaid 真问题，优先用检查器自动修复机械性问题，再对残留 `subgraph` 中文 ID / `end` 保留字等问题做最小手工收尾。
- 未修改 `AGENTS.md`、`project-governance/documentation-governance` 路径、`tasks.md`。

## 第二批修复结果

### 目录簇 A：`seven-concepts-monkeycode-vibe-coding-wiki`

- 扫描范围：目录内 `8` 个 Markdown 文件。
- 实际修改文件：`6` 个。
- 自动修复覆盖文件：
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/00-overview.md`
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/01-seven-concepts-framework.md`
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/02-monkeycode-deep-analysis.md`
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/03-practice-guide.md`
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/06-assessment.md`
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/07-seven-concepts-applied.md`
- 自动修复动作：
  - 删除 Mermaid 代码块空行。
  - 为中文/空格节点与边标签补双引号。
  - 将节点内 `\n` 替换为 `<br/>`。
- 手工收尾动作：
  - 将 `00-overview.md` 中的保留字节点 ID `End` 改为 `Finish`。
  - 将 `01-seven-concepts-framework.md` 中 5 个裸中文 `subgraph` ID 改为英文 ID + 中文标题。
  - 将 `02-monkeycode-deep-analysis.md` 中 5 个裸中文 `subgraph` ID 改为英文 ID + 中文标题。

### 目录簇 B：`seven-concepts-india-manufacturing-wiki`

- 扫描范围：目录内 `7` 个 Markdown 文件。
- 实际修改文件：`6` 个。
- 自动修复覆盖文件：
  - `.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/README.md`
  - `.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/01-theory-framework.md`
  - `.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/03-concepts-application.md`
  - `.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/04-learning-path.md`
  - `.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/05-faq-notes.md`
  - `.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/06-resources.md`
- 自动修复动作：
  - 删除 Mermaid 代码块空行。
  - 为中文/空格节点与 participant 别名补双引号。
  - 保持原图结构，仅做 Mermaid 安全写法规整。
- 手工收尾动作：
  - 将 `01-theory-framework.md` 中 5 个裸中文 `subgraph` ID 改为英文 ID + 中文标题。
  - 将 `03-concepts-application.md` 中 `输入`、`输出` 两个裸中文 `subgraph` ID 改为英文 ID + 中文标题。

## 第二批校验记录

### 1. 编辑器诊断

- 对 5 个手工收尾文件运行诊断，结果均为 `0` 个新增问题：
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/00-overview.md`
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/01-seven-concepts-framework.md`
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/02-monkeycode-deep-analysis.md`
  - `.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/01-theory-framework.md`
  - `.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/03-concepts-application.md`

### 2. 目录簇复扫

- 执行命令：

```bash
python .agents/scripts/check-mermaid.py --path ".agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki"
python .agents/scripts/check-mermaid.py --path ".agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki"
```

- 复扫结果：
  - `seven-concepts-monkeycode-vibe-coding-wiki`：`扫描文件: 8`，`问题文件: 0`，`错误: 0`，`警告: 0`
  - `seven-concepts-india-manufacturing-wiki`：`扫描文件: 7`，`问题文件: 0`，`错误: 0`，`警告: 0`

## 第二批备注

- 本批严格遵循“目录簇修复 → 目录簇复扫”的节奏，避免只修单文件导致同系列写法持续漂移。
- 结合 `git diff --stat`，本批共修改 `12` 个文件，整体改动集中在 Mermaid 代码块内部，未触碰禁改路径。

## 第三批处理范围

- 本批继续执行 `SubTask 8.9`，优先处理 `task8-7-mermaid-batches.md` 中 `H3` 的高价值模式/方法论文档目录簇：
  - `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/`
  - `.agents/docs/retrospective/patterns/methodology-patterns/document-architecture/`
  - `.agents/docs/retrospective/patterns/methodology-patterns/research-knowledge/`
  - `.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/`
- 处理原则保持不变：只修 Mermaid 真问题，优先用检查器自动修复空行、引号、边标签、`\n` 等机械性问题，再对残留 `subgraph` 中文 ID 与 `end` 保留字做最小手工收尾。
- 未修改 `AGENTS.md`、`project-governance/documentation-governance` 路径、`tasks.md`。

## 第三批修复结果

### 目录簇 A：`governance-strategy`

- 扫描范围：目录内 `109` 个 Markdown 文件。
- 初扫命中问题文件：`9` 个，错误 `54`、警告 `1`。
- 自动修复覆盖的机械性问题文件：
  - `dual-track-metadata-consistency.md`
  - `implement-review-harden-sop.md`
  - `tech-selection-three-checks.md`
  - `version-ripple-grep-sweep.md`
  - 以及其他仅涉及空行/引号/边标签的模式文档
- 手工收尾文件：
  - `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/command-knowledge-link.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/commit-quality-gate-staging-inspection.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/five-layer-governance-architecture.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/seven-concepts-positioning-model.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/seven-concepts-quick-reference.md`
- 手工收尾动作：
  - 将 `command-knowledge-link.md` 的 `公理层/规则层/操作层` 裸中文 `subgraph` ID 改为英文 ID，并同步连接关系。
  - 将 `commit-quality-gate-staging-inspection.md` 的保留字节点 `End` 改为 `Finish`。
  - 将 `five-layer-governance-architecture.md` 的 `组织保障层` 改为英文 `subgraph` ID，并同步 `style` 目标。
  - 将 `seven-concepts-positioning-model.md` 与 `seven-concepts-quick-reference.md` 的五层 `subgraph` 中文 ID 改为英文 ID。
- 说明：`five-layer-governance-architecture.md` 原始 warning 与中文 `style` 目标绑定，修复 `subgraph` ID 时一并改为英文引用，未额外扩展到无关样式重构。

### 目录簇 B：`document-architecture`

- 扫描范围：目录内 `48` 个 Markdown 文件。
- 初扫命中问题文件：`5` 个，错误 `29`。
- 自动修复覆盖的机械性问题文件：
  - `methodology-evolution-cross-refs.md`
  - `protocol-reference-distill-verify.md`
  - `tech-wiki-four-layer-need-structure.md`
  - 以及 `atomization-quick-reference-dual-layer.md` 中的节点/边标签安全写法规整
- 手工收尾文件：
  - `.agents/docs/retrospective/patterns/methodology-patterns/document-architecture/atomization-quick-reference-dual-layer.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/document-architecture/large-scale-duplication-elimination.md`
- 手工收尾动作：
  - 将 `atomization-quick-reference-dual-layer.md` 中 `认知负荷区/最优区间/导航成本区` 裸中文 `subgraph` ID 改为英文 ID + 中文标题。
  - 将 `large-scale-duplication-elimination.md` 的保留字节点 `END` 改为 `FINISH`。

### 目录簇 C：`research-knowledge`

- 扫描范围：目录内 `30` 个 Markdown 文件。
- 初扫命中问题文件：`6` 个，错误 `6`。
- 自动修复覆盖的机械性问题文件：
  - `essential-contradiction-three-step.md`
  - `first-principles-feature-analysis.md`
  - `source-pipeline-penetration-method.md`
- 手工收尾文件：
  - `.agents/docs/retrospective/patterns/methodology-patterns/research-knowledge/cross-cultural-reverse-hermeneutics-defense.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/research-knowledge/cross-domain-semantic-drift.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/research-knowledge/vendor-doc-info-compensation-search.md`
- 手工收尾动作：
  - 将 3 个文件中的保留字节点 `End` 改为非保留字目标：`FinalDeliverable` / `Finish`。
  - `cross-domain-semantic-drift.md` 中同步修正了两个指向终止节点的引用，保持原图语义不变。

### 目录簇 D：`ai-collaboration`

- 扫描范围：目录内 `54` 个 Markdown 文件。
- 初扫命中问题文件：`2` 个，错误 `5`。
- 自动修复覆盖的机械性问题文件：
  - `human-ai-collaboration-70-30-rule.md` 中 4 个中文边标签引号问题
- 手工收尾文件：
  - `.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/generation-validation-closed-loop.md`
- 手工收尾动作：
  - 将保留字节点 `END` 改为 `FinalOutput`，并同步更新 `style` 目标。

## 第三批校验记录

### 1. 编辑器诊断

- 对 11 个手工收尾文件运行诊断，结果均为 `0` 个新增问题。

### 2. 目录簇复扫

- 执行命令：

```bash
python .agents/scripts/check-mermaid.py --path ".agents/docs/retrospective/patterns/methodology-patterns/governance-strategy"
python .agents/scripts/check-mermaid.py --path ".agents/docs/retrospective/patterns/methodology-patterns/document-architecture"
python .agents/scripts/check-mermaid.py --path ".agents/docs/retrospective/patterns/methodology-patterns/research-knowledge"
python .agents/scripts/check-mermaid.py --path ".agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration"
```

- 复扫结果：
  - `governance-strategy`：`扫描文件: 109`，`问题文件: 0`，`错误: 0`，`警告: 0`
  - `document-architecture`：`扫描文件: 48`，`问题文件: 0`，`错误: 0`，`警告: 0`
  - `research-knowledge`：`扫描文件: 30`，`问题文件: 0`，`错误: 0`，`警告: 0`
  - `ai-collaboration`：`扫描文件: 54`，`问题文件: 0`，`错误: 0`，`警告: 0`

## 第三批备注

- 本批按 `H3` 目录簇整体治理，优先收敛高复用模式与方法论文档，收益高于继续扩散到低复用长尾笔记。
- 结合 `git diff --stat`，本批累计涉及 `31` 个文件变更，其中多数来自检查器对机械性问题的自动修复；手工改动集中在 `11` 个残留问题文件。
- 本批未触碰禁改路径，也未修改任何任务规划文件；`task8-9-docs-mermaid-fixes.md` 仅追加执行记录。

## 第四批处理范围

- 本批继续执行 `SubTask 8.9`，在 `.agents/docs` 中清理剩余高价值人类文档的 Mermaid 真问题，明确排除：
  - 纯归档/历史产出目录
  - `.agents/docs/retrospective/reports/`
  - `project-governance/documentation-governance` 路径
- 盘点后优先选择 5 组高价值目标：
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/`
  - `.agents/docs/retrospective/patterns/architecture-patterns/`
  - `.agents/docs/retrospective/patterns/code-patterns/`
  - `.agents/docs/knowledge/best-practices/mermaid-guide.md`
  - `.agents/docs/quality/mermaid-manual-fix-guide.md`
- 选择理由：
  - `harness-seven-components-wiki` 仍是高复用 Agent 工程方法论文档簇，第一批只修了入口样本，剩余核心章节继续被频繁引用。
  - `architecture-patterns` 与 `code-patterns` 都是模式库核心资产，属于高复用知识入口。
  - `mermaid-guide.md` 与 `mermaid-manual-fix-guide.md` 都直接影响后续 Mermaid 写法扩散，属于“阻止新问题继续生成”的文档。

## 第四批修复结果

### 目录簇 A：`harness-seven-components-wiki` 剩余核心章节

- 扫描范围：目录内 `15` 个 Markdown 文件。
- 自动修复覆盖文件：
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/02-model-gateway.md`
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/05-memory-system.md`
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/06-policy-engine.md`
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/07-observability.md`
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/08-configuration.md`
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/09-practice-guide.md`
- 自动修复动作：
  - 删除 Mermaid 代码块空行。
  - 为中文/空格节点和边标签补双引号。
  - 将节点内容中的 `\n` 统一替换为 `<br/>`。
- 手工收尾文件：
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/08-configuration.md`
- 手工收尾动作：
  - 将 `顶层/中层/底层` 3 个裸中文 `subgraph` ID 改为 `TOP_LAYER/MIDDLE_LAYER/BOTTOM_LAYER`，并同步更新层间连接。

### 目录簇 B：`architecture-patterns`

- 扫描范围：目录内 `35` 个 Markdown 文件。
- 自动修复覆盖文件：
  - `.agents/docs/retrospective/patterns/architecture-patterns/triple-entry-design.md`
  - `.agents/docs/retrospective/patterns/architecture-patterns/prompt-defense-in-depth.md`
- 自动修复动作：
  - 为中文节点补双引号。
  - 清除空行与旧写法残留。
- 手工收尾文件：
  - `.agents/docs/retrospective/patterns/architecture-patterns/multi-agent-closed-loop-execution.md`
- 手工收尾动作：
  - 将保留字节点 `END` 改为 `FINISH`。

### 目录簇 C：`code-patterns`

- 扫描范围：目录内 `61` 个 Markdown 文件。
- 自动修复覆盖文件：
  - `.agents/docs/retrospective/patterns/code-patterns/bulk-replace-zero-omission-verify.md`
- 手工收尾文件：
  - `.agents/docs/retrospective/patterns/code-patterns/checklist-to-assertion-conversion.md`
  - `.agents/docs/retrospective/patterns/code-patterns/example-driven-test-generation.md`
- 手工收尾动作：
  - 将两文件中的裸中文 `subgraph` ID 改为英文 ID。
  - 同步更新 `style` 目标，消除中文 ID 引发的 warning 风险。

### 文档 D：`mermaid-guide.md`

- 文件：
  - `.agents/docs/knowledge/best-practices/mermaid-guide.md`
- 修复动作：
  - 将示例图中的保留字节点 `END` 改为 `FINISH`，并同步更新 `style` 语句。
- 说明：
  - 该文件无法通过 `check-mermaid.py --path <file>` 直接校验，因此采用 `_process_file()` 做文件级判定与复扫。

### 文档 E：`mermaid-manual-fix-guide.md`

- 文件：
  - `.agents/docs/quality/mermaid-manual-fix-guide.md`
- 修复动作：
  - 将“错误写法”示例的代码块从 ` ```mermaid ` 改为普通 ` ```text ` 代码块。
- 说明：
  - 该处属于教学反例，不应要求其可渲染；改为普通代码块后，既保留错误示例的说明价值，也不再污染 Mermaid 校验。

## 第四批校验记录

### 1. 编辑器诊断

- 对 6 个手工收尾文件运行诊断，结果均为 `0` 个新增问题：
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/08-configuration.md`
  - `.agents/docs/retrospective/patterns/architecture-patterns/multi-agent-closed-loop-execution.md`
  - `.agents/docs/retrospective/patterns/code-patterns/checklist-to-assertion-conversion.md`
  - `.agents/docs/retrospective/patterns/code-patterns/example-driven-test-generation.md`
  - `.agents/docs/knowledge/best-practices/mermaid-guide.md`
  - `.agents/docs/quality/mermaid-manual-fix-guide.md`

### 2. 目录簇复扫

- 执行命令：

```bash
python .agents/scripts/check-mermaid.py --path ".agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki"
python .agents/scripts/check-mermaid.py --path ".agents/docs/retrospective/patterns/architecture-patterns"
python .agents/scripts/check-mermaid.py --path ".agents/docs/retrospective/patterns/code-patterns"
```

- 复扫结果：
  - `harness-seven-components-wiki`：`扫描文件: 15`，`问题文件: 0`，`错误: 0`，`警告: 0`
  - `architecture-patterns`：`扫描文件: 35`，`问题文件: 0`，`错误: 0`，`警告: 0`
  - `code-patterns`：`扫描文件: 61`，`问题文件: 0`，`错误: 0`，`警告: 0`

### 3. 文件级复扫

- 对无法直接通过 `--path <file>` 校验的文档，使用检查器底层 `_process_file()` 做文件级复扫。
- 复扫结果：
  - `.agents/docs/knowledge/best-practices/mermaid-guide.md`：`errors=0 warnings=0`
  - `.agents/docs/quality/mermaid-manual-fix-guide.md`：`errors=0 warnings=0`

## 第四批备注

- 本批是 `H1/H3` 之后的剩余高价值入口清理，优先选择仍会持续影响后续写法扩散的知识簇、模式库与 Mermaid 指南文档。
- 结合 `git diff --stat`，本批累计涉及 `14` 个文件变更，变更大多来自检查器对机械性问题的自动修复；手工改动集中在 `6` 个文件。
- `mermaid-manual-fix-guide.md` 的处理方式与普通文档不同：不是把“错误示例”强行修成正确 Mermaid，而是将故障示例降级为普通代码块，符合该文档的教学目的，也避免误报反复出现。

## 第五批处理范围

- 本批继续执行 `SubTask 8.9`，直接处理第四批结束后按同口径盘点出的剩余 `16` 个高价值人类文档 `error` 文件。
- 排除范围保持不变：
  - 纯归档/历史产出目录
  - `.agents/docs/retrospective/reports/`
  - `project-governance/documentation-governance` 路径
- 本批目标文件：
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/workbuddy-four-layers-seven-concepts-analysis.md`
  - `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md`
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/02-seven-concepts-mapping.md`
  - `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-loop-engineering-article-analysis.md`
  - `.agents/docs/knowledge/learning/douyin-vibecoding-guide-analysis.md`
  - `.agents/docs/patterns/pattern-comparison-implement-review-harden-vs-configurable-by-default.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/product-growth/deadline-breakpoint-first.md`
  - `.agents/docs/knowledge/learning/CATEGORIES.md`
  - `.agents/docs/knowledge/learning/first-principles/chinese-philosophy-parallels/07-cross-cultural-methodology-framework.md`
  - `.agents/docs/knowledge/myst-unified-ecosystem/01-idl.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/signal-identification-four-step.md`
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/04-selection-guide.md`
  - `.agents/docs/knowledge/learning/03-agent-platforms-tools/mobile-use-deep-learning-analysis.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/knowledge-sedimentation-workflow-sop.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/pre-check-duplication-layered-sedimentation.md`
  - `.agents/docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md`

## 第五批修复结果

### 1. 自动修复阶段

- 先对 16 个目标逐文件调用检查器底层 `_process_file(..., fix=True)`，自动处理机械性问题：
  - Mermaid 代码块空行
  - 中文/空格节点引号
  - `\n` 到 `<br/>`
  - 可自动识别的边标签安全写法
- 其中 `.agents/docs/knowledge/learning/02-agent-engineering-methodology/workbuddy-four-layers-seven-concepts-analysis.md` 在自动修复后即已通过，不再需要手工补丁。

### 2. 手工收尾阶段

#### A. `subgraph` 中文 ID → 英文 ID

- `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md`
  - 将 `应用层/语言抽象层/服务抽象层/本地二进制层/网络通信层/系统层` 改为英文 `subgraph` ID。
- `.agents/docs/knowledge/learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/02-seven-concepts-mapping.md`
  - 将 `感知层/认知层/验证层/执行层/沉淀层` 改为英文 `subgraph` ID。
- `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-loop-engineering-article-analysis.md`
  - 将两个裸中文 `subgraph` 标题改为 `META_LOOP` / `INNER_LOOP` 安全格式。
- `.agents/docs/knowledge/learning/douyin-vibecoding-guide-analysis.md`
  - 将 `根源/原理/规则` 改为 `ROOT_CAUSE_LAYER` / `PRINCIPLE_LAYER` / `RULE_LAYER`。
- `.agents/docs/knowledge/learning/CATEGORIES.md`
  - 将 `核心技术层/横向能力层` 改为英文 `subgraph` ID。
- `.agents/docs/knowledge/myst-unified-ecosystem/01-idl.md`
  - 将 `痛点/方案` 改为 `PAIN_POINTS` / `SOLUTION_SPACE`。
- `.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/signal-identification-four-step.md`
  - 将 `四步方法论/验证发布` 改为 `FOUR_STEP_METHOD` / `VALIDATION_RELEASE`。

#### B. `end/END` 保留字节点替换

- `.agents/docs/knowledge/learning/first-principles/chinese-philosophy-parallels/07-cross-cultural-methodology-framework.md`
  - 将终止节点 `End` 改为 `BeginAnalysis`，并同时去除代码块内空行。
- `.agents/docs/knowledge/learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/04-selection-guide.md`
  - 将 `End` 改为 `Finish`，同步更新三处引用。
- `.agents/docs/knowledge/learning/03-agent-platforms-tools/mobile-use-deep-learning-analysis.md`
  - 将 `END` 改为 `FINISH`。
- `.agents/docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/knowledge-sedimentation-workflow-sop.md`
  - 将 `End` 改为 `Complete`，并同步更新 `style` 目标。
- `.agents/docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/pre-check-duplication-layered-sedimentation.md`
  - 将 `End` 改为 `Complete`。
- `.agents/docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md`
  - 将 `END` 改为 `FINISH`。

#### C. 引号与边标签安全写法

- `.agents/docs/patterns/pattern-comparison-implement-review-harden-vs-configurable-by-default.md`
  - 将菱形节点 `发现问题?` 改为安全引号写法。
  - 将边标签 `是/否` 改为 `|"是"|` / `|"否"|`。
- `.agents/docs/retrospective/patterns/methodology-patterns/product-growth/deadline-breakpoint-first.md`
  - 为 `T-7天以上`、`T-3~7天`、`T-48小时以内` 三个边标签补双引号。

#### D. `style` 目标同步收尾

- `.agents/docs/knowledge/learning/douyin-vibecoding-guide-analysis.md`
  - 将 `style 根源/原理/规则` 同步改为英文 ID，消除 warning。
- `.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/signal-identification-four-step.md`
  - 将 `style 四步方法论/验证发布` 同步改为英文 ID，消除 warning。

## 第五批校验记录

### 1. 编辑器诊断

- 对本批手工收尾文件执行诊断，结果均为 `0` 个新增问题。

### 2. 第五批 16 文件定向复扫

- 执行方式：
  - 使用检查器底层 `_process_file()` 对 16 个目标逐文件复扫。
- 复扫结果：

```text
[结果] files=16 bad=0 errors=0 warnings=0
```

### 3. 全量剩余问题盘点

- 在与第四批相同的排除口径下，再次盘点 `.agents/docs` 剩余 Mermaid `error` 文件：

```text
[总计] issue_files=0
```

- 说明：
  - 表示在当前排除纯归档/历史产出与 `project-governance/documentation-governance` 后，`.agents/docs` 下剩余高价值人类文档的 Mermaid `error` 已经全部清零。

## 第五批备注

- 本批采用“自动修复打底 + 手工收尾固定模式”的方式，一次性收敛了上轮剩余的 16 个 `error` 文件。
- 结合 `git diff --stat`，本批累计涉及 `17` 个文件统计项，其中 `16` 个为目标文档，另 `1` 个为本摘要文件。
- 目标文档中改动集中在 Mermaid 代码块内部；未修改 `AGENTS.md`、`tasks.md`，也未触碰 `project-governance/documentation-governance` 路径。
