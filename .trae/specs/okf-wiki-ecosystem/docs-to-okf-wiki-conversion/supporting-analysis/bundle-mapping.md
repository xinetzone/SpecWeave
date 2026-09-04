# Bundle 映射方案：docs/ 全量 280 文件 → OKF v0.2 Bundle

- 创建日期：2026-08-22
- 映射范围：`d:\AI\docs\` 下全部 280 个 Markdown 文件
- Bundle 总数：31 个独立 Bundle + 5 个根级导航文件
- OKF 版本：v0.2
- 类型集合：Tutorial / Concept / Reference / Pattern / Report / Example

---

## 一、Open Questions 决策记录

### Q1：`knowledge/learning/` 根目录散文件归属

**涉及文件（5 个）**：
- `F-095` ai-engineering-four-milestones-wiki.md
- `F-096` anthropic-financial-services-wiki.md
- `F-097` octo-platform-wiki.md
- `F-098` okf-topic-index.md
- `F-099` three-ai-tools-wiki.md

**决策**：

| 文件 | 归属 | 理由 |
|------|------|------|
| F-095 | Bundle 7（ai-engineering-milestones-wiki） | 该文件包含指向 `ai-engineering-four-milestones-wiki/` 目录下 8 个文件的链接，是该 Wiki 的聚合入口页，归入 `references/` |
| F-096 | Bundle 22（ai-engineering） | Anthropic 金融服务 Wiki 属于 AI 工程化领域知识沉淀，该 Bundle 当前仅 3 文件，有容量容纳；归入 `concepts/` |
| F-097 | Bundle 22（ai-engineering） | Octo 平台 Wiki 属于 AI 平台工程化案例，与 Bundle 22 主题一致；归入 `concepts/` |
| F-098 | 根级导航文件（不移动） | OKF 主题索引是知识库板块级导航，保留原位 `knowledge/learning/okf-topic-index.md`，更新 frontmatter 但不归属任何 Bundle |
| F-099 | Bundle 21（three-ai-tools） | 该文件对应 `three-ai-tools-learning-wiki/` 目录，是该主题的 Wiki 主文档；归入 `concepts/` |

**决策理由**：遵循 Assumption A5（散文件归入最近相关 Bundle），不新增 Bundle（保持 31 个），F-098 作为板块级索引导航保留原位。

---

### Q2：`retrospective/reports/` 嵌套子目录归属

**涉及目录**：
- `adversarial-review/`（2 文件）
- `competitive-analysis/analyze-wechat-article-3dnk-20260706/`（1 文件）
- `competitive-analysis/analyze-wechat-article-dy98-20260706/`（1 文件）
- `competitive-analysis/retrospective-headroom-wiki-20260803/`（4 文件）
- `knowledge/`（3 文件）
- `milestone/`（16 文件）
- `milestone/retrospective-agency-deep-learning-20260706/`（1 文件）

**决策**：全部 28 个文件统一归入 Bundle 30（retrospective-reports），在 `concepts/` 下按原始报告类别建立子目录分组：

```
concepts/
  adversarial-review/
  competitive-analysis/
  knowledge/
  milestone/
```

各子目录中的 `README.md`/`index.md` 转为子目录导航索引（移除 frontmatter），其余文件保留原始文件名（过长文件名可适当缩写但保持语义完整）。

**决策理由**：
1. 复盘报告虽有子分类，但共享同一套方法论框架和 frontmatter 模式
2. 统一 Bundle 便于交叉引用和模式索引
3. 子目录分组保持原始分类语义，不丢失结构信息
4. 避免创建 7 个细碎 Bundle（每个仅 1-4 文件），符合 OKF Bundle 的内聚原则

---

### Q3：`codewhale/` 嵌套结构处理

**涉及目录**：
- `codewhale/`（根：2 文件）
- `codewhale/general/domain/`（1 文件）
- `codewhale/tech/`（5 文件）
- `codewhale/topics/`（1 文件）

**决策**：在 Bundle 20（codewhale）的 `concepts/` 下保留原始子目录结构：

```
concepts/
  general/domain/     # F-151 domain 知识索引
  tech/               # F-152~F-156 技术文档
  topics/             # F-157 主题索引
  comparison.md       # F-149 平台对比
```

各子目录中的 `index.md` 转为子目录导航文件（移除 frontmatter，因为 OKF 规范要求子目录 index.md 不含 frontmatter）。

**决策理由**：
1. codewhale 已有清晰的三层分类（general/tech/topics），展平会丢失语义结构
2. OKF 允许 Bundle 内 concepts/ 下有任意深度子目录
3. 保留原始结构最小化链接修改范围

---

### Q4：Sphinx toctree 路径更新

**决策**：本次转换**不更新** Sphinx `toctree` 指令中的路径，作为后续任务处理。

**处理方式**：
1. 文件中所有 `{toctree}` 指令保持原样
2. 在每个 Bundle 的 `log.md` 中记录已知影响：`Sphinx toctree paths may be stale after OKF restructuring`
3. 转换完成后如需维持 Sphinx 构建，需单独执行 `conf.py` 和 toctree 路径同步任务

**决策理由**：
1. spec.md Non-Goals 明确不修改 Sphinx/Jupyter Book 构建配置
2. toctree 路径更新涉及构建配置，超出文档格式转换范围
3. OKF 消费者容忍未知指令，不影响 OKF 合规性

---

### Q5：非教程文件（seven-concepts-report / RETROSPECTIVE）归属

**涉及文件类型**：
- `seven-concepts-report.md`（出现在 Bundle 2、4、13、14、15、16、18、21 中）
- `RETROSPECTIVE.md`（出现在 Bundle 10 中）
- 其他非编号教程文件（analysis-report、article-content、insight-extraction-report 等）

**决策**：

| 文件类型 | OKF type | 目标子目录 | 理由 |
|----------|----------|------------|------|
| `seven-concepts-report.md` | Report | `references/` | 七概念分析报告是方法论产出，非教程章节，作为参考资料 |
| `RETROSPECTIVE.md` | Report | `references/` | 复盘记录是项目历史参考，非教学内容 |
| `article-content.md` | Reference | `references/` | 原始文章内容是信源材料 |
| `analysis-report.md`（微信分析） | Report | 根 `index.md` 或 `concepts/` | 作为 Bundle 总览时转 index.md，否则为概念报告 |
| `insight-extraction-report.md` | Report | `concepts/` | 洞察提取是核心分析产出 |
| `NN-topic.md`（编号教程） | Tutorial/Concept | `concepts/` | 教程章节归入概念目录 |
| `usage-examples.md` | Example | `examples/` | 可独立运行的示例归入示例目录 |

**决策理由**：
1. 遵循 OKF 的类型语义：教程在 concepts/，信源和历史文档在 references/
2. 七概念报告是 seven-concepts-cmd 工作流的元层产出，与教程章节处于不同抽象层
3. RETROSPECTIVE 是复盘记录，属于参考资料而非教学材料

---

## 二、类型映射规则总览

### 基于文件名和内容的 type 判定规则

| 文件特征 | OKF type | 目标目录 |
|----------|----------|----------|
| `00-overview.md` / `README.md`（Bundle 根） | —（index） | 根 `index.md` |
| `NN-*.md`（编号教程章节） | Tutorial / Concept | `concepts/` |
| 文件名含 `installation`/`setup`/`quickstart`/`usage`/`guide`/`deploy`/`build`/`migration` | Tutorial | `concepts/` |
| 文件名含 `architecture`/`core`/`model`/`format`/`design`/`philosophy`/`principle`/`mechanism`/`lifecycle`/`state`/`protocol`/`feature` | Concept | `concepts/` |
| 文件名含 `reference`/`cli`/`api`/`cheatsheet`/`config`/`changelog`/`contributing`/`faq`/`troubleshooting`/`summary`/`resources`/`roadmap`/`catalog`/`performance`/`limitation` | Reference | `concepts/` 或 `references/` |
| 文件名含 `pattern`/`best-practices`/`playbooks`/`insights` | Pattern | `concepts/` |
| 文件名含 `examples`/`practical-examples`/`demo` | Example | `examples/` |
| 文件名含 `report`/`analysis`/`review`/`retrospective`/`insight-extraction` | Report | `concepts/` 或 `references/` |
| `seven-concepts-report.md` | Report | `references/` |
| `RETROSPECTIVE.md` | Report | `references/` |
| `article-content.md` | Reference | `references/` |
| tech/ 下 `intro`/`quickstart`/`features` | Tutorial | `concepts/` |
| tech/ 下 `changelog`/`contributing`/`release-*` | Reference | `references/` |
| tech/ 下 `four-layer-logging-pattern` | Pattern | `concepts/` |
| methodology-patterns/ 下所有文件 | Pattern | `concepts/` |

### 特殊目录处理

- **concepts/**：教程章节、架构概念、模式文档、核心分析报告
- **references/**：FAQ、故障排除、总结资源、信源材料、变更日志、贡献指南、七概念报告、复盘记录、性能数据、限制说明
- **examples/**：使用示例、实践示例、演示指南
- **根 index.md**：Bundle 总览（00-overview 或等效文件转换）

---

## 三、文件映射表（280 文件全量）

### 根级导航文件（5 文件，不归属任何 Bundle）

| F-ID | 源路径 | OKF type | 目标路径 | 说明 |
|------|--------|----------|----------|------|
| F-003 | `index.md` | —（root index） | `index.md`（原位） | 全站根索引，添加 `okf_version: "0.2"` |
| F-004 | `README.md` | —（nav） | `README.md`（原位） | 项目 README，同步导航 |
| F-012 | `knowledge/index.md` | —（section index） | `knowledge/index.md`（原位） | 知识库板块索引 |
| F-080 | `knowledge/learning/03-agent-platforms-tools/README.md` | —（section index） | `knowledge/learning/03-agent-platforms-tools/README.md`（原位） | Wiki 组索引 |
| F-098 | `knowledge/learning/okf-topic-index.md` | Reference | `knowledge/learning/okf-topic-index.md`（原位） | OKF 主题索引，补全 type |

---

### Bundle 1：agency-agents-wiki（12 文件）

**源目录**：`knowledge/learning/03-agent-platforms-tools/agency-agents-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-013 | 00-overview.md | —（index） | `index.md` |
| F-014 | 01-architecture.md | Concept | `concepts/01-architecture.md` |
| F-015 | 02-agent-format.md | Concept | `concepts/02-agent-format.md` |
| F-016 | 03-roster-divisions.md | Concept | `concepts/03-roster-divisions.md` |
| F-017 | 04-scripts-tooling.md | Reference | `concepts/04-scripts-tooling.md` |
| F-018 | 05-integrations.md | Reference | `concepts/05-integrations.md` |
| F-019 | 06-usage-examples.md | Example | `examples/06-usage-examples.md` |
| F-020 | 07-strategy-playbooks.md | Pattern | `concepts/07-strategy-playbooks.md` |
| F-021 | 08-faq-troubleshooting.md | Reference | `references/08-faq-troubleshooting.md` |
| F-022 | 09-best-practices.md | Pattern | `concepts/09-best-practices.md` |
| F-023 | 10-summary-resources.md | Reference | `references/10-summary-resources.md` |
| F-024 | quickstart-demo-guide.md | Tutorial | `concepts/quickstart-demo-guide.md` |

---

### Bundle 2：cordis-wiki（14 文件）

**源目录**：`knowledge/learning/03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-025 | 00-overview.md | —（index） | `index.md` |
| F-026 | 01-background-paper.md | Reference | `references/01-background-paper.md` |
| F-027 | 02-repo-structure.md | Reference | `concepts/02-repo-structure.md` |
| F-028 | 03-core-architecture.md | Concept | `concepts/03-core-architecture.md` |
| F-029 | 04-effects-coeffects.md | Concept | `concepts/04-effects-coeffects.md` |
| F-030 | 05-plugin-system.md | Concept | `concepts/05-plugin-system.md` |
| F-031 | 06-lifecycle.md | Concept | `concepts/06-lifecycle.md` |
| F-032 | 07-loader-config.md | Reference | `concepts/07-loader-config.md` |
| F-033 | 08-hmr.md | Concept | `concepts/08-hmr.md` |
| F-034 | 09-aux-packages.md | Reference | `references/09-aux-packages.md` |
| F-035 | 10-usage-examples.md | Example | `examples/10-usage-examples.md` |
| F-036 | 11-faq-notes.md | Reference | `references/11-faq-notes.md` |
| F-037 | 12-summary-resources.md | Reference | `references/12-summary-resources.md` |
| F-038 | seven-concepts-report.md | Report | `references/seven-concepts-report.md` |

---

### Bundle 3：deepseek-harness-wiki（17 文件）

**源目录**：`knowledge/learning/03-agent-platforms-tools/deepseek-harness-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-039 | 00-overview.md | —（index） | `index.md` |
| F-040 | 01-introduction-background.md | Concept | `concepts/01-introduction-background.md` |
| F-041 | 02-installation-setup.md | Tutorial | `concepts/02-installation-setup.md` |
| F-042 | 03-quickstart-first-task.md | Tutorial | `concepts/03-quickstart-first-task.md` |
| F-043 | 04-four-modes.md | Concept | `concepts/04-four-modes.md` |
| F-044 | 05-architecture-everything-plugin.md | Concept | `concepts/05-architecture-everything-plugin.md` |
| F-045 | 06-agent-loop-events.md | Concept | `concepts/06-agent-loop-events.md` |
| F-046 | 07-session-log-observability.md | Reference | `concepts/07-session-log-observability.md` |
| F-047 | 08-model-configuration.md | Reference | `concepts/08-model-configuration.md` |
| F-048 | 09-tools-capability-seam.md | Concept | `concepts/09-tools-capability-seam.md` |
| F-049 | 10-plugin-development.md | Tutorial | `concepts/10-plugin-development.md` |
| F-050 | 11-ecosystem-interop.md | Reference | `concepts/11-ecosystem-interop.md` |
| F-051 | 12-headless-sdk.md | Reference | `concepts/12-headless-sdk.md` |
| F-052 | 13-faq-troubleshooting.md | Reference | `references/13-faq-troubleshooting.md` |
| F-053 | 14-use-cases-limitations.md | Reference | `concepts/14-use-cases-limitations.md` |
| F-054 | 15-ecosystem-resources.md | Reference | `references/15-ecosystem-resources.md` |
| F-055 | 16-appendix-core-services.md | Reference | `references/16-appendix-core-services.md` |

---

### Bundle 4：okf-kit-wiki（13 文件）

**源目录**：`knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-056 | 00-overview.md | —（index） | `index.md` |
| F-057 | 01-installation.md | Tutorial | `concepts/01-installation.md` |
| F-058 | 02-cli-reference.md | Reference | `references/02-cli-reference.md` |
| F-059 | 03-okf-format.md | Concept | `concepts/03-okf-format.md` |
| F-060 | 04-core-architecture.md | Concept | `concepts/04-core-architecture.md` |
| F-061 | 05-sync-mechanism.md | Concept | `concepts/05-sync-mechanism.md` |
| F-062 | 06-chat-system.md | Concept | `concepts/06-chat-system.md` |
| F-063 | 07-mcp-serve.md | Reference | `concepts/07-mcp-serve.md` |
| F-064 | 08-registry-visualize.md | Reference | `concepts/08-registry-visualize.md` |
| F-065 | 09-extension-development.md | Tutorial | `concepts/09-extension-development.md` |
| F-066 | 10-faq-troubleshooting.md | Reference | `references/10-faq-troubleshooting.md` |
| F-067 | 11-summary-resources.md | Reference | `references/11-summary-resources.md` |
| F-068 | seven-concepts-report.md | Report | `references/seven-concepts-report.md` |

---

### Bundle 5：open-code-review-wiki（11 文件）

**源目录**：`knowledge/learning/03-agent-platforms-tools/open-code-review-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-069 | 00-overview.md | —（index） | `index.md` |
| F-070 | 01-installation.md | Tutorial | `concepts/01-installation.md` |
| F-071 | 02-cli-reference.md | Reference | `references/02-cli-reference.md` |
| F-072 | 03-architecture.md | Concept | `concepts/03-architecture.md` |
| F-073 | 04-llm-providers.md | Reference | `concepts/04-llm-providers.md` |
| F-074 | 05-tools-mcp.md | Reference | `concepts/05-tools-mcp.md` |
| F-075 | 06-review-rules.md | Reference | `concepts/06-review-rules.md` |
| F-076 | 07-session-telemetry.md | Reference | `concepts/07-session-telemetry.md` |
| F-077 | 08-integrations.md | Reference | `concepts/08-integrations.md` |
| F-078 | 09-faq-troubleshooting.md | Reference | `references/09-faq-troubleshooting.md` |
| F-079 | 10-summary-resources.md | Reference | `references/10-summary-resources.md` |

---

### Bundle 6：agent-runtime-protocol-wiki（14 文件）

**源目录**：`knowledge/learning/agent-runtime-protocol-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-081 | 00-overview.md | —（index） | `index.md` |
| F-082 | 01-protocol-boundary-lifecycle.md | Concept | `concepts/01-protocol-boundary-lifecycle.md` |
| F-083 | 02-execution-model.md | Concept | `concepts/02-execution-model.md` |
| F-084 | 03-state-management.md | Concept | `concepts/03-state-management.md` |
| F-085 | 04-interrupt-error-recovery.md | Concept | `concepts/04-interrupt-error-recovery.md` |
| F-086 | 05-tools-streaming.md | Concept | `concepts/05-tools-streaming.md` |
| F-087 | 06-multi-agent.md | Concept | `concepts/06-multi-agent.md` |
| F-088 | 07-observability-evaluation.md | Reference | `concepts/07-observability-evaluation.md` |
| F-089 | 08-protocol-design-principles.md | Concept | `concepts/08-protocol-design-principles.md` |
| F-090 | 09-cross-dimensional-analysis.md | Reference | `concepts/09-cross-dimensional-analysis.md` |
| F-091 | 09-framework-comparison.md | Reference | `concepts/09-framework-comparison.md` |
| F-092 | 10-content-evaluation.md | Reference | `concepts/10-content-evaluation.md` |
| F-093 | 10-enterprise-selection-guide.md | Reference | `concepts/10-enterprise-selection-guide.md` |
| F-094 | 11-summary-faq-resources.md | Reference | `references/11-summary-faq-resources.md` |

---

### Bundle 7：ai-engineering-milestones-wiki（9 文件）

**源目录**：`knowledge/learning/ai-engineering-four-milestones-wiki/` + 1 散文件

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-095 | `knowledge/learning/ai-engineering-four-milestones-wiki.md` | Reference | `references/ai-engineering-four-milestones-wiki.md` |
| F-100 | 00-overview.md | —（index） | `index.md` |
| F-101 | 01-bottleneck-migration.md | Concept | `concepts/01-bottleneck-migration.md` |
| F-102 | 02-prompt-engineering.md | Concept | `concepts/02-prompt-engineering.md` |
| F-103 | 03-context-engineering.md | Concept | `concepts/03-context-engineering.md` |
| F-104 | 04-harness-engineering.md | Concept | `concepts/04-harness-engineering.md` |
| F-105 | 05-loop-engineering.md | Concept | `concepts/05-loop-engineering.md` |
| F-106 | 06-insights-patterns.md | Pattern | `concepts/06-insights-patterns.md` |
| F-107 | 07-summary-faq-resources.md | Reference | `references/07-summary-faq-resources.md` |

---

### Bundle 8：baidu-ocr-wiki（9 文件）

**源目录**：`knowledge/learning/baidu-unlimited-ocr-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-130 | 00-overview.md | —（index） | `index.md` |
| F-131 | 01-core-architecture.md | Concept | `concepts/01-core-architecture.md` |
| F-132 | 02-performance-data.md | Reference | `references/02-performance-data.md` |
| F-133 | 03-quick-start.md | Tutorial | `concepts/03-quick-start.md` |
| F-134 | 04-limitations-risks.md | Reference | `references/04-limitations-risks.md` |
| F-135 | 05-architecture-insights.md | Concept | `concepts/05-architecture-insights.md` |
| F-136 | 06-transferable-patterns.md | Pattern | `concepts/06-transferable-patterns.md` |
| F-137 | 07-specweave-implications.md | Reference | `concepts/07-specweave-implications.md` |
| F-138 | 08-summary-faq.md | Reference | `references/08-summary-faq.md` |

---

### Bundle 9：book-to-skill-wiki（10 文件）

**源目录**：`knowledge/learning/book-to-skill-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-139 | 00-overview.md | —（index） | `index.md` |
| F-140 | 01-core-architecture.md | Concept | `concepts/01-core-architecture.md` |
| F-141 | 02-extractor-deep-dive.md | Concept | `concepts/02-extractor-deep-dive.md` |
| F-142 | 03-skill-md-spec.md | Reference | `concepts/03-skill-md-spec.md` |
| F-143 | 04-token-economics.md | Concept | `concepts/04-token-economics.md` |
| F-144 | 05-security-model.md | Concept | `concepts/05-security-model.md` |
| F-145 | 06-installation-usage.md | Tutorial | `concepts/06-installation-usage.md` |
| F-146 | 07-extending-development.md | Tutorial | `concepts/07-extending-development.md` |
| F-147 | 08-transferable-patterns.md | Pattern | `concepts/08-transferable-patterns.md` |
| F-148 | 09-summary-faq.md | Reference | `references/09-summary-faq.md` |

---

### Bundle 10：github-cli-wiki（9 文件）

**源目录**：`knowledge/learning/github-cli-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-158 | 00-overview.md | —（index） | `index.md` |
| F-159 | 01-installation.md | Tutorial | `concepts/01-installation.md` |
| F-160 | 02-basic-commands.md | Tutorial | `concepts/02-basic-commands.md` |
| F-161 | 03-pr-workflow.md | Tutorial | `concepts/03-pr-workflow.md` |
| F-162 | 04-actions-cicd.md | Tutorial | `concepts/04-actions-cicd.md` |
| F-163 | 05-advanced-usage.md | Tutorial | `concepts/05-advanced-usage.md` |
| F-164 | 06-faq-troubleshooting.md | Reference | `references/06-faq-troubleshooting.md` |
| F-165 | 07-cheatsheet.md | Reference | `references/07-cheatsheet.md` |
| F-166 | RETROSPECTIVE.md | Report | `references/RETROSPECTIVE.md` |

---

### Bundle 11：headroom-wiki（11 文件）

**源目录**：`knowledge/learning/headroom-context-compression-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-167 | 00-overview.md | —（index） | `index.md` |
| F-168 | 01-core-architecture.md | Concept | `concepts/01-core-architecture.md` |
| F-169 | 02-compression-algorithms.md | Concept | `concepts/02-compression-algorithms.md` |
| F-170 | 03-ccr-mechanism.md | Concept | `concepts/03-ccr-mechanism.md` |
| F-171 | 04-integration-methods.md | Tutorial | `concepts/04-integration-methods.md` |
| F-172 | 05-performance-data.md | Reference | `references/05-performance-data.md` |
| F-173 | 06-advanced-features.md | Concept | `concepts/06-advanced-features.md` |
| F-174 | 07-quick-start.md | Tutorial | `concepts/07-quick-start.md` |
| F-175 | 08-insights-patterns.md | Pattern | `concepts/08-insights-patterns.md` |
| F-176 | 09-faq-resources.md | Reference | `references/09-faq-resources.md` |
| F-177 | 10-summary.md | Reference | `references/10-summary.md` |

---

### Bundle 12：minit2i-wiki（8 文件）

**源目录**：`knowledge/learning/minit2i-minimalist-t2i-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-178 | 00-overview.md | —（index） | `index.md` |
| F-179 | 01-design-philosophy.md | Concept | `concepts/01-design-philosophy.md` |
| F-180 | 02-three-subtractions.md | Concept | `concepts/02-three-subtractions.md` |
| F-181 | 03-mm-jit-architecture.md | Concept | `concepts/03-mm-jit-architecture.md` |
| F-182 | 04-experiments-performance.md | Reference | `references/04-experiments-performance.md` |
| F-183 | 05-limitations-open-problems.md | Reference | `references/05-limitations-open-problems.md` |
| F-184 | 06-paradigm-shift-insights.md | Concept | `concepts/06-paradigm-shift-insights.md` |
| F-185 | 07-summary-faq-resources.md | Reference | `references/07-summary-faq-resources.md` |

---

### Bundle 13：python314-cpython-wiki（17 文件）

**源目录**：`knowledge/learning/python314-cpython-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-186 | 00-overview.md | —（index） | `index.md` |
| F-187 | 01-language-features.md | Concept | `concepts/01-language-features.md` |
| F-188 | 02-free-threading.md | Concept | `concepts/02-free-threading.md` |
| F-189 | 03-jit-interpreter.md | Concept | `concepts/03-jit-interpreter.md` |
| F-190 | 04-new-modules.md | Reference | `concepts/04-new-modules.md` |
| F-191 | 05-stdlib-improvements.md | Reference | `concepts/05-stdlib-improvements.md` |
| F-192 | 06-cpython-architecture.md | Concept | `concepts/06-cpython-architecture.md` |
| F-193 | 07-c-api-changes.md | Reference | `references/07-c-api-changes.md` |
| F-194 | 08-build-platform.md | Tutorial | `concepts/08-build-platform.md` |
| F-195 | 09-migration-guide.md | Tutorial | `concepts/09-migration-guide.md` |
| F-196 | 10-practical-examples.md | Example | `examples/10-practical-examples.md` |
| F-197 | 11-faq-troubleshooting.md | Reference | `references/11-faq-troubleshooting.md` |
| F-198 | 12-summary-resources.md | Reference | `references/12-summary-resources.md` |
| F-199 | 13-official-docs-roadmap.md | Reference | `references/13-official-docs-roadmap.md` |
| F-200 | learning-path.md | Tutorial | `concepts/learning-path.md` |
| F-201 | Python314-Learning-Path.md | Reference | `references/Python314-Learning-Path.md` |
| F-202 | seven-concepts-report.md | Report | `references/seven-concepts-report.md` |

---

### Bundle 14：python314-stdlib-wiki（18 文件）

**源目录**：`knowledge/learning/python314-stdlib-wiki/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-203 | 00-overview.md | —（index） | `index.md` |
| F-204 | 01-version-prerequisites.md | Reference | `concepts/01-version-prerequisites.md` |
| F-205 | 02-contextlib.md | Reference | `concepts/02-contextlib.md` |
| F-206 | 03-contextvars.md | Reference | `concepts/03-contextvars.md` |
| F-207 | 04-sys-monitoring.md | Reference | `concepts/04-sys-monitoring.md` |
| F-208 | 05-annotationlib.md | Reference | `concepts/05-annotationlib.md` |
| F-209 | 06-dataclasses.md | Reference | `concepts/06-dataclasses.md` |
| F-210 | 07-traceback.md | Reference | `concepts/07-traceback.md` |
| F-211 | 08-cross-module-analysis.md | Concept | `concepts/08-cross-module-analysis.md` |
| F-212 | 09-usage-examples.md | Example | `examples/09-usage-examples.md` |
| F-213 | 10-faq-troubleshooting.md | Reference | `references/10-faq-troubleshooting.md` |
| F-214 | 11-summary-resources.md | Reference | `references/11-summary-resources.md` |
| F-215 | 12-okf-optimization-mapping.md | Reference | `concepts/12-okf-optimization-mapping.md` |
| F-216 | 13-okf-optimization-report.md | Report | `references/13-okf-optimization-report.md` |
| F-217 | 14-mystx-optimization-mapping.md | Reference | `concepts/14-mystx-optimization-mapping.md` |
| F-218 | 15-mystx-optimization-report.md | Report | `references/15-mystx-optimization-report.md` |
| F-219 | 16-mystx-tests-catalog.md | Reference | `references/16-mystx-tests-catalog.md` |
| F-220 | seven-concepts-report.md | Report | `references/seven-concepts-report.md` |

---

### Bundle 15：wechat-ai-switch-governance（4 文件）

**源目录**：`knowledge/learning/analyze-wechat-article-ai-switch-governance/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-108 | analysis-report.md | —（index） | `index.md` |
| F-109 | article-content.md | Reference | `references/article-content.md` |
| F-110 | insight-extraction-report.md | Report | `concepts/insight-extraction-report.md` |
| F-111 | seven-concepts-report.md | Report | `references/seven-concepts-report.md` |

---

### Bundle 16：wechat-causal-ai（3 文件）

**源目录**：`knowledge/learning/analyze-wechat-article-causal-ai/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-112 | analysis-report.md | —（index） | `index.md` |
| F-113 | article-content.md | Reference | `references/article-content.md` |
| F-114 | seven-concepts-report.md | Report | `references/seven-concepts-report.md` |

---

### Bundle 17：wechat-mainecoon（11 文件）

**源目录**：`knowledge/learning/analyze-wechat-article-mainecoon/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-115 | 00-article-overview.md | —（index） | `index.md` |
| F-116 | 01-argument-structure-analysis.md | Report | `concepts/01-argument-structure-analysis.md` |
| F-117 | 02-content-value-and-knowledge.md | Report | `concepts/02-content-value-and-knowledge.md` |
| F-118 | 03-technical-breakthrough-analysis.md | Report | `concepts/03-technical-breakthrough-analysis.md` |
| F-119 | 04-insights-and-reliability.md | Report | `concepts/04-insights-and-reliability.md` |
| F-120 | 05-critique-and-methodology.md | Report | `concepts/05-critique-and-methodology.md` |
| F-121 | analysis-report.md | Report | `references/analysis-report.md` |
| F-122 | archive-content-value-assessment.md | Reference | `references/archive-content-value-assessment.md` |
| F-123 | critical-review-draft.md | Report | `references/critical-review-draft.md` |
| F-124 | decision-summary.md | Reference | `references/decision-summary.md` |
| F-125 | mainecoon-social-world-model-wiki.md | Concept | `concepts/mainecoon-social-world-model-wiki.md` |

---

### Bundle 18：wechat-quantdinger（3 文件）

**源目录**：`knowledge/learning/analyze-wechat-article-quantdinger/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-126 | analysis-report.md | —（index） | `index.md` |
| F-127 | article-content.md | Reference | `references/article-content.md` |
| F-128 | seven-concepts-report.md | Report | `references/seven-concepts-report.md` |

---

### Bundle 19：wechat-rqndd（1 文件）

**源目录**：`knowledge/learning/analyze-wechat-article-rqndd/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-129 | analysis-report.md | —（index） | `index.md` |

> 注：单文件 Bundle，analysis-report.md 直接转为根 index.md，添加 `okf_version` frontmatter。

---

### Bundle 20：codewhale（9 文件）

**源目录**：`knowledge/learning/codewhale/`（保留嵌套子目录结构）

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-149 | comparison.md | Reference | `concepts/comparison.md` |
| F-150 | index.md | —（index） | `index.md` |
| F-151 | general/domain/index.md | —（sub-index） | `concepts/general/domain/index.md` |
| F-152 | tech/changelog.md | Reference | `concepts/tech/changelog.md` |
| F-153 | tech/deploy.md | Tutorial | `concepts/tech/deploy.md` |
| F-154 | tech/features.md | Tutorial | `concepts/tech/features.md` |
| F-155 | tech/intro.md | Tutorial | `concepts/tech/intro.md` |
| F-156 | tech/quickstart.md | Tutorial | `concepts/tech/quickstart.md` |
| F-157 | topics/index.md | —（sub-index） | `concepts/topics/index.md` |

> 注：F-151 和 F-157 为子目录索引，转换时移除 frontmatter（OKF 子目录 index.md 不含 frontmatter）。tech/ 下文件按用户要求分配 type：intro/quickstart/features 为 Tutorial，changelog 为 Reference，deploy 为 Tutorial。

---

### Bundle 21：three-ai-tools（3 文件）

**源目录**：`knowledge/learning/three-ai-tools-learning-wiki/` + 1 散文件

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-099 | `knowledge/learning/three-ai-tools-wiki.md` | Concept | `concepts/three-ai-tools-wiki.md` |
| F-221 | article-content.md | Reference | `references/article-content.md` |
| F-222 | seven-concepts-report.md | Report | `references/seven-concepts-report.md` |

> 注：无 00-overview 文件，新建 index.md 作为 Bundle 导航（基于 F-099 内容摘要生成链接列表）。

---

### Bundle 22：ai-engineering（5 文件）

**源目录**：`knowledge/ai-engineering/` + 2 散文件

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-005 | karpathy-llm-wiki-analysis-20260707.md | Report | `concepts/karpathy-llm-wiki-analysis.md` |
| F-006 | loop-engineering-knowledge-base.md | Reference | `concepts/loop-engineering-knowledge-base.md` |
| F-007 | README.md | —（index） | `index.md` |
| F-096 | `knowledge/learning/anthropic-financial-services-wiki.md` | Reference | `concepts/anthropic-financial-services-wiki.md` |
| F-097 | `knowledge/learning/octo-platform-wiki.md` | Reference | `concepts/octo-platform-wiki.md` |

---

### Bundle 23：atomic-emergence（1 文件）

**源目录**：`knowledge/algorithmic-art/atomic-emergence/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-008 | philosophy.md | Concept | `concepts/philosophy.md` |

> 注：无 00-overview 文件，新建 index.md 作为 Bundle 导航。

---

### Bundle 24：deep-learning-atomic-design（3 文件）

**源目录**：`knowledge/engineering/deep-learning-atomic-design/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-009 | ai-agent-atomic-design-analysis.md | Report | `concepts/ai-agent-atomic-design-analysis.md` |
| F-010 | deep-learning-atomic-components.md | Reference | `concepts/deep-learning-atomic-components.md` |
| F-011 | deep-learning-atomic-design-guide.md | —（index） | `index.md` |

> 注：F-011 为最大文件（1064 行）且为指南性质，转为根 index.md，保留其 frontmatter 并添加 `okf_version`。

---

### Bundle 25：specweave-tech-docs（10 文件）

**源目录**：`tech/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-269 | changelog.md | Reference | `references/changelog.md` |
| F-270 | contributing.md | Reference | `references/contributing.md` |
| F-271 | features.md | Tutorial | `concepts/features.md` |
| F-272 | four-layer-logging-pattern.md | Pattern | `concepts/four-layer-logging-pattern.md` |
| F-273 | index.md | —（index） | `index.md` |
| F-274 | intro.md | Tutorial | `concepts/intro.md` |
| F-275 | quickstart.md | Tutorial | `concepts/quickstart.md` |
| F-276 | README.md | Reference | `references/README.md` |
| F-277 | release-onnx-pytorch-v1-1.md | Reference | `references/release-onnx-pytorch-v1-1.md` |
| F-278 | release-onnx-quantized-v2.md | Reference | `references/release-onnx-quantized-v2.md` |

> type 分配规则：intro/quickstart/features → Tutorial；changelog/contributing → Reference；four-layer-logging-pattern → Pattern；release-* → Reference。

---

### Bundle 26：general-knowledge（2 文件）

**源目录**：`general/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-001 | index.md | —（index） | `index.md` |
| F-002 | README.md | Reference | `references/README.md` |

---

### Bundle 27：design-topics（2 文件）

**源目录**：`topics/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-279 | index.md | —（index） | `index.md` |
| F-280 | README.md | Reference | `references/README.md` |

---

### Bundle 28：refactor-notes（1 文件）

**源目录**：`refactor/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-223 | refactor-concurrent-safety-checker-20260812.md | Report | `concepts/refactor-concurrent-safety-checker.md` |

> 注：无 00-overview 文件，新建 index.md 作为 Bundle 导航。

---

### Bundle 29：methodology-patterns（16 文件）

**源目录**：`retrospective/patterns/methodology-patterns/`

> 所有文件 type 统一为 **Pattern**，归入 `concepts/`。

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-225 | content-funnel-analysis.md | Pattern | `concepts/content-funnel-analysis.md` |
| F-226 | cross-framework-atomic-analysis.md | Pattern | `concepts/cross-framework-atomic-analysis.md` |
| F-227 | dual-engine-uncertainty-certainty.md | Pattern | `concepts/dual-engine-uncertainty-certainty.md` |
| F-228 | dual-layer-analysis-report.md | Pattern | `concepts/dual-layer-analysis-report.md` |
| F-229 | error-blacklist-monotonic-evolution.md | Pattern | `concepts/error-blacklist-monotonic-evolution.md` |
| F-230 | evaluation-driven-self-evolution.md | Pattern | `concepts/evaluation-driven-self-evolution.md` |
| F-231 | integration-over-invention.md | Pattern | `concepts/integration-over-invention.md` |
| F-232 | knowledge-compilation.md | Pattern | `concepts/knowledge-compilation.md` |
| F-233 | layered-chained-spec.md | Pattern | `concepts/layered-chained-spec.md` |
| F-234 | lowering-barriers-creates-markets.md | Pattern | `concepts/lowering-barriers-creates-markets.md` |
| F-235 | offline-first-architecture.md | Pattern | `concepts/offline-first-architecture.md` |
| F-236 | README.md | —（index） | `index.md` |
| F-237 | responsibility-transfer-governance.md | Pattern | `concepts/responsibility-transfer-governance.md` |
| F-238 | subagent-standardized-instruction.md | Pattern | `concepts/subagent-standardized-instruction.md` |
| F-239 | tech-article-to-wiki-batch-generation.md | Pattern | `concepts/tech-article-to-wiki-batch-generation.md` |
| F-240 | three-layer-repair-closure.md | Pattern | `concepts/three-layer-repair-closure.md` |

---

### Bundle 30：retrospective-reports（28 文件）

**源目录**：`retrospective/reports/`（递归，concepts/ 下保留子目录分组）

#### concepts/adversarial-review/（2 文件）

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-241 | adversarial-review/adversarial-review-analyze-wechat-article-3dnk-20260803.md | Report | `concepts/adversarial-review/adversarial-review-3dnk.md` |
| F-242 | adversarial-review/adversarial-review-analyze-wechat-article-dy98-20260706.md | Report | `concepts/adversarial-review/adversarial-review-dy98.md` |

#### concepts/competitive-analysis/（5 文件）

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-243 | competitive-analysis/analyze-wechat-article-3dnk-20260706/analysis-report.md | Report | `concepts/competitive-analysis/3dnk-analysis.md` |
| F-244 | competitive-analysis/analyze-wechat-article-dy98-20260706/analysis-report.md | Report | `concepts/competitive-analysis/dy98-analysis.md` |
| F-245 | competitive-analysis/retrospective-headroom-wiki-20260803/execution-retrospective.md | Report | `concepts/competitive-analysis/headroom-execution-retrospective.md` |
| F-246 | competitive-analysis/retrospective-headroom-wiki-20260803/export-suggestions.md | Reference | `concepts/competitive-analysis/headroom-export-suggestions.md` |
| F-247 | competitive-analysis/retrospective-headroom-wiki-20260803/insight-extraction.md | Report | `concepts/competitive-analysis/headroom-insight-extraction.md` |
| F-248 | competitive-analysis/retrospective-headroom-wiki-20260803/README.md | —（sub-index） | `concepts/competitive-analysis/headroom-index.md` |

#### concepts/knowledge/（3 文件）

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-249 | knowledge/kicrd-seven-concepts-analysis-20260704.md | Report | `concepts/knowledge/kicrd-seven-concepts-analysis.md` |
| F-250 | knowledge/libtv-wiki-knowledge-precipitation-20260704.md | Report | `concepts/knowledge/libtv-wiki-knowledge-precipitation.md` |
| F-251 | knowledge/README.md | —（sub-index） | `concepts/knowledge/index.md` |

#### concepts/milestone/（18 文件）

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-252 | milestone/analyze-wechat-article-eeb14-retrospective-20260704.md | Report | `concepts/milestone/eeb14-retrospective.md` |
| F-253 | milestone/four-engineering-concepts-wiki-retrospective-20260704.md | Report | `concepts/milestone/four-engineering-concepts-retrospective.md` |
| F-254 | milestone/harness-engineering-wiki-retrospective-20260803.md | Report | `concepts/milestone/harness-engineering-retrospective.md` |
| F-255 | milestone/karpathy-llm-wiki-analysis-retrospective-20260707.md | Report | `concepts/milestone/karpathy-llm-retrospective.md` |
| F-256 | milestone/libtv-wiki-retrospective-20260704.md | Report | `concepts/milestone/libtv-retrospective.md` |
| F-257 | milestone/loop-engineering-milestone-acceptance-20260801.md | Report | `concepts/milestone/loop-engineering-acceptance.md` |
| F-258 | milestone/loop-engineering-patterns-20260801.md | Pattern | `concepts/milestone/loop-engineering-patterns.md` |
| F-259 | milestone/octo-platform-wiki-retrospective-20260704.md | Report | `concepts/milestone/octo-platform-retrospective.md` |
| F-260 | milestone/okf-ecosystem-milestone-retrospective-20260819.md | Report | `concepts/milestone/okf-ecosystem-retrospective.md` |
| F-261 | milestone/okf-python314-stdlib-optimization-retrospective-20260818.md | Report | `concepts/milestone/okf-python314-stdlib-optimization-retrospective.md` |
| F-262 | milestone/README.md | —（sub-index） | `concepts/milestone/index.md` |
| F-263 | milestone/retrospective-hermes-specweave-integration-20260812.md | Report | `concepts/milestone/hermes-specweave-integration-retrospective.md` |
| F-264 | milestone/session-atomic-commit-insight-extraction-20260706.md | Report | `concepts/milestone/session-atomic-commit-insight.md` |
| F-265 | milestone/specweave-knowledge-scaling-milestone-20260801.md | Report | `concepts/milestone/specweave-knowledge-scaling.md` |
| F-266 | milestone/torch-dev-mirror-build-retrospective-20260820.md | Report | `concepts/milestone/torch-dev-mirror-build-retrospective.md` |
| F-267 | milestone/web-content-learning-notes-patterns-20260801.md | Pattern | `concepts/milestone/web-content-learning-patterns.md` |
| F-268 | milestone/retrospective-agency-deep-learning-20260706/report.md | Report | `concepts/milestone/agency-deep-learning-report.md` |

> 注：Bundle 30 无 00-overview，新建根 index.md 作为导航，链接到四个子分类索引。子目录 README/index 文件转为导航索引并移除 frontmatter。

---

### Bundle 31：retrospective-root（1 文件）

**源目录**：`retrospective/`

| F-ID | 源文件 | OKF type | 目标路径 |
|------|--------|----------|----------|
| F-224 | index.md | —（index） | `index.md` |

> 注：retrospective 板块根索引，添加 `okf_version: "0.2"` frontmatter。

---

### 文件计数校验

| 类别 | Bundle 数 | 文件数 |
|------|:---------:|:------:|
| 第一批：现有 Wiki 教程（B1-B14） | 14 | 172 |
| 第二批：微信文章分析（B15-B19） | 5 | 22 |
| 第三批：其他知识主题（B20-B24） | 5 | 21 |
| 第四批：项目文档（B25-B28） | 4 | 15 |
| 第五批：复盘内容（B29-B31） | 3 | 45 |
| 根级导航文件 | — | 5 |
| **合计** | **31** | **280** |

> **散文件归入校验**：4 个 `knowledge/learning/` 根目录散文件已全部归入 Bundle——F-095 → B7（references/），F-096/F-097 → B22（concepts/），F-099 → B21（concepts/）。Bundle 内文件总计 275 + 5 根级导航 = 280，无未分配文件。F-001~F-280 全部 280 个 F-ID 均已覆盖，无遗漏、无重复。

---

## 四、链接转换规则

### 4.1 链接分类与处理策略

| 链接类型 | 正则/特征 | 处理方式 | 示例 |
|----------|-----------|----------|------|
| Bundle 内部相对链接 | `[text](NN-topic.md)` 或 `[text](./file.md)` | 转换为 Bundle 绝对路径 | `02-contextlib.md` → `/concepts/02-contextlib.md` |
| Bundle 内部子目录链接 | `[text](subdir/file.md)` | 转换为 Bundle 绝对路径 | `tech/intro.md` → `/concepts/tech/intro.md` |
| references 目录链接 | 指向 seven-concepts-report、RETROSPECTIVE、FAQ 等 | 添加 `/references/` 前缀 | `seven-concepts-report.md` → `/references/seven-concepts-report.md` |
| examples 目录链接 | 指向 usage-examples、practical-examples | 添加 `/examples/` 前缀 | `10-usage-examples.md` → `/examples/10-usage-examples.md` |
| 跨 Bundle 链接 | 包含 `../` 跳出当前 Bundle 目录 | 保持原样（相对路径） | `../../python314-stdlib-wiki/02-contextlib.md` 不转换 |
| 外部绝对 URL | `http://` 或 `https://` 开头 | 保持原样 | `https://example.com` 不转换 |
| 图片/静态资源 | `_static/`、`.png`、`.jpg`、`.svg` 等 | 保持原样 | `_static/diagram.png` 不转换 |
| Sphinx ref 角色 | `{ref}\`target\`` | 保持原样 | `{ref}\`my-label\`` 不转换 |
| Sphinx toctree 指令 | ` ````{toctree}`` ` 块 | 保持原样（Q4 决策） | 不转换 |
| 锚点链接 | `file.md#section` | 路径部分转换，锚点保留 | `02-contextlib.md#usage` → `/concepts/02-contextlib.md#usage` |
| index.md 自引用 | 链接到 `00-overview.md` 或 `index.md` | 转为 `/`（Bundle 根） | `00-overview.md` → `/` |

### 4.2 Bundle 绝对路径格式

```
/<concepts|references|examples>/<filename>.md
```

- 路径以 `/` 开头，表示 Bundle 根目录
- Markdown 链接内统一使用 `/` 分隔符（Windows 兼容）
- 子目录结构保留时：`/concepts/tech/intro.md`
- Bundle 根 index 引用：`/` 或 `/index.md`

### 4.3 链接转换映射表（按源文件目标位置）

#### 教程章节文件（移入 concepts/）

文件从 Bundle 根移入 `concepts/` 后：

| 原始链接模式 | 转换后链接 |
|-------------|-----------|
| `[text](01-architecture.md)` | `[text](/concepts/01-architecture.md)` |
| `[text](./02-installation.md)` | `[text](/concepts/02-installation.md)` |
| `[text](03-quickstart.md#section)` | `[text](/concepts/03-quickstart.md#section)` |
| `[text](seven-concepts-report.md)` | `[text](/references/seven-concepts-report.md)` |
| `[text](10-usage-examples.md)` | `[text](/examples/10-usage-examples.md)` |
| `[text](00-overview.md)` | `[text](/)` |
| `[text](../other-bundle/file.md)` | 保持原样 |

#### references 文件（移入 references/）

文件从 Bundle 根移入 `references/` 后：

| 原始链接模式 | 转换后链接 |
|-------------|-----------|
| `[text](01-architecture.md)` | `[text](/concepts/01-architecture.md)` |
| `[text](./02-installation.md)` | `[text](/concepts/02-installation.md)` |
| `[text](seven-concepts-report.md)` | `[text](/references/seven-concepts-report.md)` |
| `[text](00-overview.md)` | `[text](/)` |

#### 嵌套子目录文件（codewhale/retrospective-reports）

文件保留子目录结构后：

| 原始链接模式 | 转换后链接 |
|-------------|-----------|
| `[text](changelog.md)`（tech/ 内互链） | `[text](/concepts/tech/changelog.md)` |
| `[text](../topics/index.md)` | `[text](/concepts/topics/index.md)` |
| `[text](../../index.md)` | `[text](/)` |

### 4.4 不需要转换的内容

以下内容在链接转换时**保持原样**：

1. **Sphinx/MyST 指令**：`{note}`、`{warning}`、`{tip}`、`{toctree}`、`{ref}`、`{eval-rst}` 等
2. **代码块内的路径**：围栏代码块（```` ``` ````）中的文件路径和 URL
3. **行内代码中的路径**：`` `path/to/file.md` `` 格式的代码引用
4. **HTML 标签**：`<a href="...">` 等原生 HTML（如存在）
5. **图片引用**：`![alt](_static/image.png)` 等静态资源
6. **frontmatter 中的 source 字段**：YAML frontmatter 内的路径引用不修改
7. **外部 URL**：所有 `http://`、`https://`、`mailto:` 链接

### 4.5 链接完整性验证规则

转换完成后需验证：

1. **Bundle 内部链接**：所有以 `/` 开头的链接目标文件必须存在于 Bundle 内
2. **锚点验证**：`#section` 锚点对应的标题在目标文件中存在（可选验证）
3. **跨 Bundle 链接**：记录但不验证（消费者容忍断链）
4. **外部链接**：不验证可达性
5. **孤立文件检查**：Bundle 内每个 Concept 文件应至少被 index.md 引用一次

---

## 五、附录：Bundle 目录结构模板

### 标准 Bundle 结构

```
<bundle-name>/
  index.md              # Bundle 根索引（含 okf_version frontmatter）
  log.md                # 变更日志
  concepts/
    index.md            # 概念目录导航（无 frontmatter）
    NN-topic.md         # 教程/概念章节
    ...
  references/
    index.md            # 参考资料目录导航（无 frontmatter）
    faq.md
    seven-concepts-report.md
    ...
  examples/             # 仅在有示例文件时创建
    index.md
    usage-examples.md
```

### 含嵌套子目录的 Bundle 结构（codewhale）

```
codewhale/
  index.md
  log.md
  concepts/
    index.md
    comparison.md
    general/
      domain/
        index.md        # 子目录导航
    tech/
      index.md          # 需新建
      changelog.md
      deploy.md
      features.md
      intro.md
      quickstart.md
    topics/
      index.md
  references/
    index.md
```

### 复盘报告 Bundle 结构（retrospective-reports）

```
retrospective-reports/
  index.md
  log.md
  concepts/
    index.md
    adversarial-review/
      index.md
      *.md
    competitive-analysis/
      index.md
      *.md
    knowledge/
      index.md
      *.md
    milestone/
      index.md
      *.md
  references/
    index.md
```

---

## 六、转换批次建议

遵循 NFR-5（每批不超过 7 个 Bundle），建议批次划分：

| 批次 | Bundle | 数量 | 说明 |
|------|--------|:----:|------|
| Batch 1 | B1-B5 | 5 | 第一批 Wiki 教程（agency/cordis/deepseek/okf-kit/open-code-review） |
| Batch 2 | B6-B10 | 5 | 第二批 Wiki 教程（agent-runtime/milestones/baidu/book/github-cli） |
| Batch 3 | B11-B14 | 4 | 第三批 Wiki 教程（headroom/minit2i/cpython/stdlib） |
| Batch 4 | B15-B19 | 5 | 微信文章分析报告 |
| Batch 5 | B20-B24 | 5 | 其他知识主题（codewhale/three-ai-tools/ai-engineering/atomic-emergence/deep-learning） |
| Batch 6 | B25-B28 | 4 | 项目文档（tech/general/topics/refactor） |
| Batch 7 | B29-B31 | 3 | 复盘内容（methodology-patterns/retrospective-reports/retrospective-root） |
| Batch 8 | 根级导航 | 5 | 根级 index/README 更新和散文件处理 |

每个 Batch 完成后执行验证：文件计数、frontmatter 合规性、Bundle 内部链接完整性。
