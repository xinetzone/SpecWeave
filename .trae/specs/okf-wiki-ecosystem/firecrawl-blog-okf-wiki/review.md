---
id: review
title: Firecrawl 博文转化 V 阶段对抗审查记录
created: 2026-09-16
---

# V 阶段对抗审查记录（review）

> 对象：`projects/awesome-okf-xs/doc/bundles/jishu/ai/firecrawl/`（9 文件）+ spec 事实集。
> 方法：四视角 + 老板视角内容审查，8 项机械门禁脚本实跑。

## 1. 四视角审查结论

### 1.1 事实溯源（魔鬼代言人）

- 全部数字/模型名/包名/端点/引语均挂 F 编号，无 facts.md 之外的编造。
- 两处 ❌ 在正文呈现官方正确值：concepts/00 §2（提交日期）与 §4（3,387ms/1,000-URL 基准）；根 index 勘误区 7 条同口径。
- 厂商自述数字（96%/3,387ms/60%）全部标注数据集名（scrape-content-dataset-v1）、测量日期（2026-01-13）与发布时点（2026-01-14），index 顶部有"厂商自述数据"提示块。
- 作者观点（F-034）在 article-source 标 V，正文仅作修辞背景不转引为事实。

### 1.2 结构规范

- 骨架与两问判定一致：技术综述类，无 examples/（与 threeui/a2a-mcp 正例同型）。
- 3 个 index.md 均含 toctree 块；根 toctree 收 concepts/references/log。
- 两个 Mermaid 图（flowchart 链路、sequenceDiagram 工作流）节点文本均加引号。
- frontmatter：9 文件齐备必需字段；根 index 含 okf_version 0.2。

### 1.3 读者可用性（新人视角）

- bundle 内相对链接与跨束链接经正则+存在性校验 0 断链；修复 1 处层级错误（concepts/02 → 兄弟束需两级上跳 `../../wigolo/`）。
- 代码块均标注"转自官方 README/非作者实测"与 SDK 版本（firecrawl-py 4.43.0，v2 形态，旧 v1 已废弃）。
- 表格化速查（七端点、SDK 矩阵、开源 vs 云、核心事实卡）可独立阅读。

### 1.4 时效边界（未来视角）

- Star 双时点（171,711≈8/28–31 / 181,040@09-16）；spark-1 弃用→spark-2 现状；/extract 软弃用而非下线；厂商基准无第三方复测；SEC $82.06M Form D 而 About 页未更新。
- stale_after 2026-12-31，verification.md §3 列 5 项复核安排。

### 1.5 老板视角（采用决策）

- AGPL-3.0 SaaS 网络开源义务、MIT SDK 调用云端无传染性、自托管 PG/Redis/RabbitMQ/Playwright 栈与自带 LLM/Ollama 成本、云端专属能力（Agent/Actions/增强代理/仪表盘）均在 concepts/02 与根 index 提示。
- 免费档 1,000 credits/月 + Agent 5 次/天 + keyless 兜底给出零成本试用路径。

## 2. 机械门禁结果（脚本真实输出）

| 检查项 | 工具 | 结果 |
|--------|------|------|
| 总索引五面对账 | `python scripts/check-bundles-index.py` | ✅ 9 域/59 组/555 束 |
| toctree 完整性 | `python scripts/check-toctrees.py` | ✅ 引用有效、内容全可达 |
| UTF-8 strict | `python scripts/check-utf8.py` | ✅ 10412 文件 |
| 双份 F 编号 | 正则 `^\| F-\d{3} \|` 集合比对 | ✅ 各 63、F-001~F-063 连续、集合相等 |
| 相对链接 | 正则提取 + 路径存在性 | ✅ 0 断链 |
| 敏感信息 | 绝对本地链接/家目录路径扫描 | ✅ 0 命中 |
| frontmatter | 必需字段 + sources 双信源以上 | ✅ |
| 勘误落实 | ❌/⚠️ 项正文核对 | ✅ 呈现正确值与博文口径 |

> invoke 包装因环境 invocations 包元数据损坏不可用，按 skill 规定直接运行底层 scripts，未谎报"invoke gates 通过"。

## 3. 过程异常与处置

1. **并行会话碰撞**：早前会话（21:40）完成一轮 R+I（F-048，17✅/1❌）并在 E 阶段与本会话并发写同目录。本会话深核版（F-063）修订其一则误判（F-038 ❌→⚠️）、补一则实证勘误（F-008 →❌）与 15 条新事实，最终以深核版统一全束 9 文件；碰撞导致的 ai/index.md 标记拼接损伤与重复 firecrawl 行已修复。
2. **二次计数漂移**：并行会话收尾时将 bundles/index.md 写为 549/416/197（地面真值 555/422/203），门禁拦截后已按真值修复四面 + mermaid 节点。
3. **既有漂移不扩大**：jishu/index.md 全页计数历史失真（导语 111/ai 45 等），另案对账，已在 log 登记。

## 4. 终判

- bundle `status: stable`：2 处 ❌ 均为非核心细节，核心声明全部 ✅，勘误完整落实，不置 flagged。
- 可进入 C 阶段；提交待用户明确指令（子模块 → 主仓库 spec → gitlink，不 push）。
