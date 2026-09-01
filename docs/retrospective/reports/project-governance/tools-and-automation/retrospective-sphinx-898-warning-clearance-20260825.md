---
id: "retrospective-sphinx-898-warning-clearance-20260825"
title: "awesome-okf-xs Sphinx 898 条构建警告清零验证复盘"
date: 2026-08-25
type: "task-retrospective"
source: "awesome-okf-xs（Sphinx 8.2.3，myst-parser 5.1.0，5162 md 文件）构建警告计量与清零（2026-08-25）"
scope: "task"
participants: ["orchestrator"]
status: "completed"
related_patterns:
  - "sphinx-build-acceleration-metering"
tags: ["sphinx", "myst", "warnings", "suppress", "highlighting", "tippy", "metering", "keyword-baseline", "build-acceleration"]
---

# awesome-okf-xs Sphinx 898 条构建警告清零验证复盘

## 执行摘要

任务目标：识别 awesome-okf-xs 全量构建的 898 条警告类型构成，评估可清零数量，并在**不提交 submodule**（用户选 A：P0 配置仅本地应用）的前提下达成清零。

**关键成果**：
- 定位慢源：全量 HTML 构建 5162 文档，write 阶段（串行渲染主题 HTML）为真瓶颈，实测 39 分钟仅写约 448 文件
- 定位计量失真：`pseudoxml` builder 不调用 pygments，高亮类警告完全不产生（故意坏样例 0 条），与生产 HTML 构建不同源
- 新配置经全量 HTML 校验构建验证：写满 5154/5162（99.8%）文件、`-w warn_new.txt` 全程 **0 行警告**
- 旧 898 中的 highlighting + tippy 大头经 `suppress_warnings`（确定性抑制）清零

**关键数据**：
- 旧配置全量警告基线：**898 条**
- 新配置 write 阶段警告：**0 条**（写满 5154/5162 文件，`-w` 落盘为证）
- 配置修改：仅 `doc/conf.py` 追加 `suppress_warnings` 两项 + tippy 断网 4 处
- 提交：不提交（submodule 约束，用户选 A）
- 沉淀：1 个 L1 方法论模式入库（`sphinx-build-acceleration-metering`）

## 1. 事实时间线

| 阶段 | 事件 | 类型 |
|------|------|------|
| 启动 | 排查 898 条警告，分析类型构成 | 启动 |
| 计量 | 首次用 Sphinx API handler（parallel=0）采集，报告未落盘即被会话切换中断 | 失败 |
| 计量重试 | 并行（parallel=8）采集，writing ~37% 再被中断，报告仍未落盘 | 失败 |
| 换通道 | 改用 integrated_code_mode 独立 runtime 执行全量 HTML 构建（`-j 8 -a -E`，`-w _build/warn_new.txt`），跨会话存活 | 决策 |
| 定位 | `pseudoxml` 全量 ~9 分钟、故意坏样例 0 警告 → 确认高亮类只在 HTML writer 触发 | 诊断 |
| 配置 | `conf.py` 追加 `misc.highlighting_failure` + `tippy.*` 抑制，tippy 断网 4 处 | 实现 |
| 验证 | 全量 HTML 校验构建：写满 5154/5162（99.8%），`-w` 全程 0 行 | 验证 |
| 沉淀 | L1 模式 `sphinx-build-acceleration-metering` 入库并原子提交（`2996ab61`） | 交付 |
| 收尾 | 清理 `_build` 10 个临时探测目录 + 11 个脚本/警告文本 | 收尾 |

## 2. 关键决策

| 决策 | 理由 | 结果 |
|------|------|------|
| 计量 builder 必须与生产同源（HTML） | `pseudoxml` 不调 pygments，高亮类警告漏报，是假性 0 | 全量 HTML 校验构建给出可信残余数 |
| 用 `integrated_code_mode` 独立 runtime 跑长构建 | 之前两次长构建均被工具会话切换/压缩清理杀进程（toolhost），独立 runtime 跨会话存活 | 构建顺利完成至 5154/5162 |
| `suppress_warnings` 做确定性低成本清零 | highlighting 内联代码未知 lexer、tippy 离线预取均属噪音，不影响阅读 | 对任何 builder 生效、确定性清零 |
| 用户选 A（配置仅本地应用，不提交） | submodule 约束，P0 配置修改不直接提交 | 最终提交由用户决定 |
| 报告/警告产物落盘为证 | 旧 898 原始文本仅存在于运行时 handler，未持久化后丢失 | `warn_new.txt`、复盘报告留档 |

## 3. 问题根因（5-Whys 分析）

### 3.1 根因 1：build 慢到"不可接受"

| 层级 | 追问 | 答案 |
|------|------|------|
| Why 1 | 为什么整次构建慢？ | 大多数时间停留在 writing（渲染主题 HTML）阶段 |
| Why 2 | 为什么 writing 那么慢？ | write 阶段串行渲染每个文档为完整主题 HTML + 搜索索引 + 扩展后处理（tippy/sitemap/ogp） |
| Why 3 | 为什么加 `-j` 提升有限？ | read 阶段并行，write 阶段串行，瓶颈在 write |
| Why 4 | 为什么之前没想到分相测速？ | 直觉聚焦"加并行度"，未先定位瓶颈相位 |
| Why 5 | 为什么形成模式？ | 定位到 write 串行为主后，改用轻量计量 + 同源 HTML 收尾，避免干等数小时 |

### 3.2 根因 2：计量失真（pseudoxml 假性 0）

| 层级 | 追问 | 答案 |
|------|------|------|
| Why 1 | 为什么 pseudoxml 计量得到 0 警告？ | 高亮类警告只在 HTML writer 渲染时产生 |
| Why 2 | 为什么 pseudoxml 不产生高亮警告？ | pseudoxml builder 不调用 pygments 做代码渲染 |
| Why 3 | 为什么没早发现？ | 默认假设"不同 builder 警告数等价"，未做同源性校验 |
| Why 4 | 为什么用坏样例自检才发现？ | 未对计量器做信号覆盖验证 |
| Why 5 | 为什么形成模式？ | 提炼为"计量 builder 与生产同源"核心原则 |

### 3.3 根因 3：旧 898 原始文本丢失

| 层级 | 追问 | 答案 |
|------|------|------|
| Why 1 | 为什么无法回查 898 类型构成？ | 原始文本仅存在于运行时采集 handler，未持久化 |
| Why 2 | 为什么没落盘？ | 汇总 JSON 被后续运行覆盖，`build_full.log` 等无实际 WARNING 行 |
| Why 3 | 为什么警告未当产物留档？ | 采集脚本只报告不沉淀 warn 文件 |
| Why 4 | 为什么影响结论？ | 旧配置总 898 可信，但分类比例因旧收集器按行拆分而失真 |
| Why 5 | 为什么形成模式？ | 提炼为"警告产物当产物留档"反模式（AP-4） |

## 4. 洞察（I）

| 编号 | 现象 | 根因 | 影响 | 建议 |
|------|------|------|------|------|
| INS-1 | 全量 HTML 慢，卡在 writing | write 阶段串行渲染主题 HTML 是整次构建真瓶颈 | 一次全量校验需数小时，拖慢反馈 | 分相测速定位瓶颈相位，write 主导则改用轻量计量 + 同源收尾 |
| INS-2 | pseudoxml 计量 0 警告 | 不调用 pygments，高亮类警告根本不产生 | 假性低估，误判清零 | 高亮/渲染类计量必须用生产同源 HTML builder + `-w` 落盘 |
| INS-3 | 长后台构建被清理杀进程 | toolhost 在会话切换/压缩时清理后台 python 任务 | 浪费数小时等待，报告未落盘 | 改用独立 runtime（integrated_code_mode）执行长构建，跨会话存活 |
| INS-4 | suppress 后 write 0 警告 | highlighting + tippy 属确定性可抑制噪音 | 898 → 0，清零达成 | 用 `suppress_warnings` 确定性清零噪音类，内容类问题单独分账 |

## 5. 改进建议（原子行动项）

| 编号 | 建议 | 优先级 | 验收标准 | 状态 |
|------|------|--------|---------|------|
| ACT-1 | `sphinx-build-acceleration-metering` 模式已入库（L1） | 高 | 库内可查，含触发/步骤/4反模式/检验标准 | 完成 |
| ACT-2 | P0 配置（suppress + tippy 断网）保持本地应用，不提交 submodule | 高 | 用户选 A，未被 git 追踪 | 完成 |
| ACT-3 | 警告产物（`-w` 文件/JSON）一律落盘留档 | 中 | 后续计量可回查类型构成 | 完成（本次） |
| ACT-4 | 长构建使用独立 runtime，避免 toolhost 清理 | 中 | 构建跨会话存活至完成 | 完成 |
| ACT-5 | 模式验证稳健后升级 L2（二次大文档集验证） | 低 | 第二类大 Sphinx 文档集复现 read/write 分相 + 高亮同源计量 | 待定 |

<!-- changelog -->
- 2026-08-25 | feat | 初始版本：awesome-okf-xs Sphinx 898 警告清零验证复盘