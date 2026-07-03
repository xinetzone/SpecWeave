---
version: 3.0
id: retrospective-mdi-action-plan
title: "MDI项目复盘 - 后续行动计划"
category: retrospective
type: project-reports
source: "合并改进建议清单(07)+P1拆分计划(08)：统一的后续行动指南（功能改进+代码结构优化）"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/07-improvement-recommendations.toml"
date: 2026-07-03
---
# MDI项目复盘 - 后续行动计划

> 本文档合并了原改进建议清单和P1文件拆分计划，包含功能改进、代码结构优化、流程建设三类后续行动。基于 `module-size-bug-correlation`、`semi-structured-parsing-complexity-budget`、`mvp-unvalidated-code-debt` 三个新模式的核心规则制定。

## ✅ 阶段二战役已完成成果（2026-07-03）

单日原子化拆分战役已完成P1-High优先级全部6个核心文件拆分：

| # | 文件 | 原行数 | 拆分后结构 |
|---|------|--------|-----------|
| 1 | versioning.py | 872 | versioning/ 包（5模块） |
| 2 | validator.py | 639 | validator/ 包（9模块） |
| 3 | forum-bot.py | 1,174 | forum_bot/ 包（13模块，薄入口+延迟导入） |
| 4 | generate-sg-dashboard.py | 863 | sg_dashboard/ 包（9模块） |
| 5 | link_fixer.py | 958 | link_fixer/ 包（11模块） |
| 6 | vendor.py | 985 | vendor检查逻辑重构整合 |

额外完成：check-skill-quality、check-spec-adoption、analyze-xlsx-test-report、trae_edge_case_handler、test_mdi_fence_codeblocks、jest_gen/pytest_gen等文件拆分。战役成果：🟠橙色高风险区清零（14→0），安全文件194→286+，159+测试全部通过无回归。

## 🔴 高优先级（P0）—— 核心质量风险，建议下次迭代优先处理

| # | 改进项 | 类别 | 对应模式 | 具体操作 | 验收标准 | 预估工时 |
|---|-------|------|---------|---------|---------|---------|
| 1 | **拆分 parser.py（1465行，红色警报区）** | 代码结构 | module-size-bug-correlation + semi-structured-parsing-complexity-budget | 按三层架构拆分为3个文件：<br>1. `parser/tokenizer.py`：Block tokenizer<br>2. `parser/section_builder.py`：section树构建<br>3. `parser/directive_parser.py`：Directive状态机解析 | - 每个文件<500行<br>- 259个单元测试全部通过<br>- 3个端到端案例输出一致<br>- Bug#10彻底解决 | ~2小时 |
| 2 | **为未验证代码添加显式STATUS标记** | 技术债务 | mvp-unvalidated-code-debt | 在文件头部添加：<br>- mcp_domain/mcp_server: `# STATUS: UNVALIDATED`<br>- jest_gen.py: `# STATUS: PARTIAL - 功能简陋`<br>- graphql_profile.py: `# STATUS: UNVALIDATED` | - 4个文件均有明确STATUS标记<br>- README说明实验性功能 | ~15分钟 |
| 3 | **补齐Jest生成器功能（对齐pytest_gen）** | 功能完善 | mvp-unvalidated-code-debt | 参照pytest_gen实现：<br>1. example_extractor集成<br>2. checklist_converter集成<br>3. 语义化Mock生成<br>4. TODO注释提示 | - Jest用例包含example和checklist断言<br>- todo-api Jest生成端到端验证通过<br>- 功能完整度达pytest_gen 90%+ | ~3小时 |

## 🟠 中优先级（P1）—— 质量提升与债务偿还，建议下2次迭代内处理

### 功能改进类

| # | 改进项 | 对应模式 | 具体操作 | 验收标准 | 预估工时 |
|---|-------|---------|---------|---------|---------|
| 4 | **补充Parser边界case测试（从10个→20+）** | semi-structured-parsing-complexity-budget | 补充嵌套3层directive、非标准人类写法、空内容/极端边界等场景 | - 新增≥10个边界case测试<br>- 所有测试通过 | ~1小时 |
| 5 | **MCP Server端到端验证或删代码决策** | mvp-unvalidated-code-debt | A) 补验证：新增mcp验证案例；B) 删代码：删除未使用的mcp模块（遵循YAGNI） | - 选A：有可运行验证案例，STATUS→VALIDATED<br>- 选B：精简942行代码 | A:~4h / B:~20m |
| 6 | **实现CLI专用测试生成器** | 原有action item | 为CliTool Profile生成subprocess风格CLI测试骨架 | - file-cli.md生成可执行CLI测试骨架<br>- 端到端测试验证 | ~2小时 |

### 代码结构类（剩余待拆分文件）

| # | 文件 | 原行数 | 拆分方案 | 预估工时 |
|---|------|--------|---------|---------|
| 7 | lib/__init__.py | 627 | 拆为纯入口导出，工具函数移至子模块 | ~1h |
| 8 | lib/patterns.py | 534 | 拆为patterns/index.py + patterns/maturity.py | ~45m |
| 9 | lib/stage_guardrails/boundary.py | 601 | 拆为boundary/rules.py + enforcer.py | ~45m |
| 10 | lib/stage_guardrails/runtime.py | 597 | 拆为runtime/hooks.py + context.py | ~45m |
| 11 | pattern-maturity.py | 603 | 拆为maturity/commands.py + calculator.py | ~45m |

## 🟡 低优先级（P2）—— 体验优化与流程改进，有空再做

### 功能改进类

| # | 改进项 | 对应模式 | 具体操作 | 验收标准 | 预估工时 |
|---|-------|---------|---------|---------|---------|
| 12 | **补全GraphQL Profile验证或标记实验性** | mvp-unvalidated-code-debt | A) 新增graphql-blog.md端到端验证；B) 标记EXPERIMENTAL | - 选A：验证通过；选B：文档有明确标记 | A:~2h / B:~10m |
| 13 | **OpenAPI→MDI反向转换** | 原有action item | 实现从OpenAPI JSON生成MDI文档初稿 | PetStore OpenAPI能生成可用MDI初稿 | ~4小时 |

### 代码结构类

| # | 文件 | 原行数 | 处理方案 | 预估工时 |
|---|------|--------|---------|---------|
| 14 | check-hardcode.py | 649 | 拆为hardcode/detectors.py + reporter.py | ~45m |
| 15 | check-stage-guardrails.py | 575 | 拆为guardrails_check/validator.py + reporter.py | ~30m |
| 16 | spec-tool.py | 535 | 拆为spec/cli.py + commands.py | ~45m |
| 17 | check-stage-guardrail-runtime.py | 525 | 考虑合并或拆分 | ~30m |
| 18 | migrate-frontmatter.py | 639 | 一次性迁移脚本，标记为LEGACY | ~10m |
| 19 | audit-metadata-ecosystem.py | 549 | 一次性审计脚本，标记为LEGACY | ~10m |

**P1-Watch观察项**：测试文件（test_mdi_parser.py 713行、test_trigger_matcher.py 701行等）<1000行可暂不拆分，属于正常现象。

### 流程建设类

| # | 改进项 | 对应模式 | 具体操作 | 验收标准 | 预估工时 |
|---|-------|---------|---------|---------|---------|
| 20 | **新增CI文件大小检查门禁** | module-size-bug-correlation | CI添加：>800行告警，>1200行阻断 | CI运行时对超限文件给出提示 | ~30分钟 |
| 21 | **Parser类项目复杂度预算checklist** | semi-structured-parsing-complexity-budget | 在docs/knowledge/添加checklist：<br>- Parser预算是Generator的2-3倍<br>- Parser必须按三层架构拆分<br>- 先写20个边界case再写代码 | checklist文档存在 | ~20分钟 |

## 拆分验收通用标准

所有代码拆分必须满足：
1. ✅ 拆分后每个文件 <500行（橙色高风险区文件<400行）
2. ✅ 所有现有单元测试通过（允许调整import路径）
3. ✅ 端到端验证案例输出与拆分前一致（MDI模块）
4. ✅ 拆分遵循单一职责原则，不是机械按行数切分
5. ✅ 更新对应的__init__.py导出（如有）
6. ✅ 拆分完成后从check-file-size.py的ALLOWLIST中移除（如有）

## 总投入与ROI估算

| 优先级 | 总工时 | 主要收益 |
|-------|-------|---------|
| P0 高优 | ~5.25小时 | 解决80%结构性质量问题（parser拆分+债务标记+Jest补齐） |
| P1 中优 | ~10.5小时 | 偿还功能债务+核心代码结构优化 |
| P2 低优 | ~9小时 | 剩余结构优化+流程固化+体验改进 |
| **总计** | **~24.75小时** | 代码质量提升、债务清零、未来项目踩坑率降低 |

**ROI分析**：P0的5小时投入可避免未来至少10-20小时Bug排查和维护成本（参考module-size-bug-correlation非线性成本曲线），ROI > 2:1。

## 导航

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [insight-extraction.md](insight-extraction.md) | [README.md](README.md) | 返回 [README.md](README.md) |

## Changelog

<!-- changelog -->
- 2026-07-03 | docs | v3.0：合并08-p1-split-plan.md——整合功能改进和代码结构优化为统一行动计划，添加阶段二已完成成果，拆分验收标准
- 2026-07-03 | docs | v2.1：导航更新——上一章指向insight-extraction（04/05/06已合并）
- 2026-07-03 | docs | v2.0：原子化拆分，从export-suggestions.md独立为改进建议清单文件
