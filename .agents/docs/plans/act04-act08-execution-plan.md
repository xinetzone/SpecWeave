---
id: "act04-act08-execution-plan"
title: "ACT-04 至 ACT-08 执行计划"
version: 1.1
date: 2026-07-19
completed_date: "2026-07-19"
type: execution-plan
status: completed
source: "retrospective-specweave-full-project-20260719"
---

# ACT-04 至 ACT-08 执行计划

> **执行状态：✅ 全部完成**（TG1→TG5 共5个Task Group，8个原子提交，79项测试全通过）

**Goal:** 落实 SpecWeave 全项目复盘报告中 5 个剩余行动项（ACT-04 迭代复盘节奏、ACT-05 CI stats审核、ACT-06 测试覆盖率、ACT-07 insight报告去重、ACT-08 三防线模式入库）。

**执行结果：** 全部5项行动项于2026-07-19完成闭环，主复盘报告同步更新至v1.2。

| TG | 行动项 | 状态 | 提交Hash | 测试新增 | 关键交付物 |
|----|--------|------|---------|---------|-----------|
| TG1 | ACT-04 迭代复盘节奏 | ✅ 完成 | 3 commits | 4 | weekly模板 + docgen weekly子命令 + CI周提醒 |
| TG2 | ACT-05 CI stats审核 | ✅ 完成 | 1 commit | 7 | --strict-anomaly参数 + daily-stats-update异常告警Issue |
| TG3 | ACT-06 CI测试覆盖率 | ✅ 完成 | 1 commit | 0 | pytest.ini配置 + ci-quality-gates覆盖率步骤 |
| TG4 | ACT-07 insight重复度扫描 | ✅ 完成 | 2 commits | 17 | check-markdown-duplication.py + 46组重复分析报告 |
| TG5 | ACT-08 三防线模式入库 | ✅ 完成 | 1 commit | 0 | automated-stats-three-defense-lines L1模式 |

---

## 文件结构总览（交付状态）

| 操作 | 文件路径 | 职责 | 状态 |
|---|---|---|---|
| Create | `.agents/templates/weekly-retrospective-template.md` | 周复盘模板 | ✅ |
| Create | `.agents/scripts/tests/test_docgen_weekly.py` | weekly 子命令测试（4个） | ✅ |
| Create | `.github/workflows/weekly-iteration-reminder.yml` | 周复盘提醒 CI | ✅ |
| Modify | `.agents/scripts/docgen.py` | weekly 子命令 + --strict-anomaly 参数 | ✅ |
| Modify | `.github/workflows/daily-stats-update.yml` | 异常告警（创建issue） | ✅ |
| Modify | `.github/workflows/ci-quality-gates.yml` | pytest-cov 覆盖率步骤 | ✅ |
| Create | `pytest.ini` | 覆盖率配置 | ✅ |
| Create | `.agents/scripts/check-markdown-duplication.py` | Markdown 重复度检测脚本 | ✅ |
| Create | `.agents/scripts/tests/test_check_markdown_duplication.py` | 重复度脚本测试（17个） | ✅ |
| Create | `.agents/docs/retrospective/reports/insight-extraction/duplication-report-20260719.json` | 重复度扫描JSON数据 | ✅ |
| Create | `.agents/docs/retrospective/reports/insight-extraction/duplication-report-20260719.md` | insight 重复度分析报告 | ✅ |
| Create | `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/automated-stats-three-defense-lines.md` | 三防线模式 | ✅ |
| Create | `.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/automated-stats-three-defense-lines.toml` | 模式元数据 | ✅ |
| Modify | `.agents/docs/retrospective/reports/project-reports/retrospective-specweave-full-project-20260719/README.md` | 主复盘报告v1.2 | ✅ |

---

## TG1: ACT-04 迭代复盘节奏机制 ✅

### Task 1.1: 创建周复盘模板
- [x] 创建 `.agents/templates/weekly-retrospective-template.md`，含基本信息/本周数据快照/关键事件/成就问题/5-Whys/下周行动项/模式沉淀等6个章节

### Task 1.2: docgen.py 添加 weekly 子命令
- [x] **TDD** 创建 `.agents/scripts/tests/test_docgen_weekly.py`，4个测试（原计划3个，增加cmd_weekly_returns_zero测试）
- [x] docgen.py 新增 `_weekly_count_test_commits(root, days)`、`_weekly_collect(root, days=7)`、`cmd_weekly(args)` 函数
- [x] main() 注册 weekly 子命令（--days 参数默认7）
- [x] 回归测试全部通过

### Task 1.3: 周复盘提醒 CI
- [x] 创建 `.github/workflows/weekly-iteration-reminder.yml`：schedule `0 0 * * 0` UTC（北京时间周日08:00），自动创建周复盘Issue含数据快照和模板指引
- [x] YAML 语法验证通过（修复了初版JS template literal缩进问题）

**原子提交记录：**
- feat(docgen): 添加 weekly 子命令生成本周数据快照 + 周复盘模板
- feat(ci): 添加 weekly-iteration-reminder 工作流（每周日提醒复盘）
- 以及模板文件提交

---

## TG2: ACT-05 CI stats 审核环节 ✅

### Task 2.1: docgen stats --strict-anomaly 模式
- [x] **TDD** 创建 `.agents/scripts/tests/test_docgen_strict_anomaly.py`，7个测试（覆盖无快照/正常增长/50%降幅/返回类型/strict模式阻断/非strict不阻断/正常模式零退出码）
- [x] `_validate_with_snapshot()` 返回警告列表，cmd_stats 根据 strict-anomaly 参数决定退出码（0或2）
- [x] argparse p_stats 添加 `--strict-anomaly` 参数
- [x] 全量回归通过

### Task 2.2: daily-stats-update.yml 异常告警
- [x] 修改 workflow：使用 `--strict-anomaly` 运行，异常退出码2时通过 `gh issue create` 自动创建告警Issue（labels: stats-anomaly/automated/needs-review）
- [x] 正常模式退出码0才提交变更；异常时不提交只告警
- [x] YAML 语法验证通过

**原子提交记录：**
- feat(docgen/ci): stats添加--strict-anomaly严格模式 + daily-stats-update异常告警（7个测试）

---

## TG3: ACT-06 CI 测试覆盖率 ✅

### Task 3.1: pytest-cov 覆盖率输出
- [x] 创建 `pytest.ini`：`[coverage:run]` source=.agents/scripts，omit=tests/*和lib/mdi/*，exclude_lines=pragma: no cover
- [x] ci-quality-gates.yml：Install deps添加pytest-cov，测试步骤改为 `--cov=. --cov-report=term-missing`
- [x] 本地验证覆盖率正常输出

**原子提交记录：**
- test(ci): 添加pytest.ini覆盖率配置 + ci-quality-gates pytest-cov步骤

---

## TG4: ACT-07 insight-extraction 重复度扫描 ✅

### Task 4.1: check-markdown-duplication.py 脚本
- [x] **TDD** 创建 `.agents/scripts/tests/test_check_markdown_duplication.py`，17个测试（strip_frontmatter/normalize/代码块跳过/空文件/不同内容无重复/相同内容检测/排除README/frontmatter剥离/N-gram窗口/JSON输出等）
- [x] 创建 `.agents/scripts/check-markdown-duplication.py`，基于N元语法指纹+滑动窗口+块扩展算法，Markdown专属归一化（剥离标题/列表/粗体/斜体/链接/HTML/表格/图片/代码块标记），排除README.md和_*.md，支持--threshold/--window/--json/--path参数
- [x] 实际扫描insight-extraction目录成功
- [x] 79/79 回归测试通过

### Task 4.2: 重复度扫描报告与归并方案
- [x] 运行扫描生成 `duplication-report-20260719.json`（46组重复，约4116行，影响48个文件）
- [x] 创建 `duplication-report-20260719.md` 分析报告：三类重复（A类模板复制73%/B类同目录重叠20%/C类跨复盘模板7%），建议提取4个共享模板+3组同目录合并审核
- [x] 链接验证通过；索引已更新
- [x] 注意：只输出方案，实际文件合并在后续独立任务执行

**原子提交记录：**
- `e9d10891` feat(scripts): 添加 Markdown 文档重复度检测工具 check-markdown-duplication（TDD，17个测试）
- `9c3d5e19` docs(insight): 添加 insight-extraction 重复度扫描报告与归并方案（46组重复/4116行）

---

## TG5: ACT-08 三防线模式入库 ✅

### Task 5.1: 创建 automated-stats-three-defense-lines 模式
- [x] 创建 `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/automated-stats-three-defense-lines.md`，frontmatter含id/source/x-toml-ref/maturity:L1/validation_count:1/reuse_count:0/5个关联模式
- [x] 章节结构：模式概述/问题现象/三防线架构（Mermaid流程图+代码示例）/防线协作关系（绕过矩阵6场景）/实现清单（8个组件）/适用条件/反模式7条/推广场景5个/成熟度评估
- [x] 创建对应的 TOML 元数据文件
- [x] 所有内部链接验证通过（8个文件引用+source/x-toml-ref路径）
- [x] docgen 导航索引更新
- [x] 79/79 回归测试通过

**原子提交记录：**
- `ed726d17` feat(patterns): 入库L1模式 automated-stats-three-defense-lines（自动化统计三防线，Mermaid图+绕过矩阵+反模式+推广场景）

---

## 最终验收清单（全部完成）

- [x] 所有新增测试通过：79/79 PASSED（原62个+新17个）
- [x] docgen stats 严格模式正常：`python docgen.py stats --strict-anomaly` 退出码0
- [x] weekly 命令正常输出：`python docgen.py weekly` 输出周数据摘要
- [x] 更新全项目复盘报告至v1.2（`cf679dc3`）：ACT-04~08 全部标记✅，核心问题2/3标记已解决，changelog新增v1.2条目

## 遗留后续事项（非本计划范围）

1. **第一篇周复盘**：需等下一个周日CI触发或手动创建，基于 weekly-retrospective-template.md
2. **insight-extraction 实际文件归并**：duplication-report已输出方案，提取4个共享模板+合并重叠文件在后续独立任务执行
3. **check-markdown-duplication.py 纳入CI**：等类型A模板提取完成后，设warn-only阈值纳入CI
4. **Bus Factor=1改进计划**：已生成草案（`dfd0c3d5`），待xinetzone审阅5个关键问题后执行
