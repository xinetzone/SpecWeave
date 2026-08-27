---
id: "pdf-book-to-okf-wiki"
title: "PDF书籍→OKF-MyST Wiki 四阶段工作流"
type: process-pattern
date: 2026-08-21
maturity: L1-draft
maturity_note: "单案例验证（《帛书老子注读》297页PDF→93个MD+97个HTML，L1待升级）"
source: "../../reports/task-reports/retrospective-boshu-laozi-pdf-to-myst-wiki-20260821.md#四可复用模式萃取e阶段"
related_patterns:
  - "../code-patterns/sphinx-conf-probe-fallback.md"
  - "../methodology-patterns/tools-automation/tool-failure-three-tier-degradation.md"
tags: ["pdf-conversion", "okf", "sphinx", "myst", "knowledge-engineering", "books", "document-conversion"]
validation_count: 1
reuse_count: 0
---

# PDF书籍→OKF-MyST Wiki 四阶段工作流

## 触发场景

- 需要将**纯文本排版**的中文/外文书籍 PDF（非扫描件、非图册）转换为符合 OKF 规范的 Markdown 知识库
- 需要基于 Sphinx + MyST + mystx 主题构建可浏览的静态 Wiki 站点
- 书籍具有明确章节结构（章标题、子结构小节：原文/译文/解读等）

**识别信号**：
- 输入 PDF 由文字层构成（可选中、可复制文本），非图片扫描
- 目标输出为多文件 Markdown（每章一个文件）+ YAML frontmatter
- 需要构建可导航浏览的 HTML 站点而非单一文档

**不适用场景**：
- **扫描件 PDF**（无文字层）→ 需 OCR/版面分析，应用 MinerU 等专业工具，本模式仅提供降级参考
- **图文混排图册/画册** → 文本块与图片块交错，pypdfium2 纯文本提取会丢失版面结构
- **混合排版风险**：拼音注音/行间注释/多栏布局/复杂表格与正文混排的 PDF（如注音版附录），pypdfium2 提取时文字块顺序会混乱，产出需降级标注 + 人工校对（见"已知边界"）
- 单篇短文档（无章节结构）→ 直接手动转换即可，无需四阶段流水线

## 问题背景

AI Agent 在受限沙箱环境中将 PDF 书籍转换为结构化知识库时，常遭遇三类系统性障碍：

1. **工具选择悖论**：重量级专用解析器（MinerU）功能强大但依赖多模型/外部二进制/缓存目录写入，在权限受限环境（TRAE Sandbox 拒绝 uv.exe）中反复失败；而轻量纯 Python 库（pypdfium2）一次成功。
2. **批量生成格式噪声**：LLM 批量生成带 YAML frontmatter 的 Markdown 时，整数字段加引号、toctree 语法错误、缺一级标题等格式错误是**系统性高发**问题，无法靠"详细 prompt + 一次生成"避免。
3. **"忠于原文"边界模糊**：PDF 是物理排版格式（硬换行为适应页宽、水印为出版商附加物），Markdown 是逻辑结构格式，两者混用导致段落被切碎、水印当原文保留。

本模式通过**四阶段流水线 + 工具降级链 + 独立校验修复层 + 三层忠实边界**系统性解决上述问题。

## 核心步骤（6步）

1. **环境准备与模板复制**：基于 mystx 模板创建项目骨架（pyproject.toml/conf.py/_config.toml），用 uv 创建 Python 3.14 虚拟环境，验证 mystx 可导入，确保项目可预构建。
2. **PDF 结构探查**：先提取**首尾样本页**识别物理结构（封面/版权/目录/前言/正文/附录），确定章标题正则模式，跳过目录页避免误识别，输出结构化 JSON（front_matter/chapters/appendix）。**可用正则参考**（中文书籍章标题）：
   ```
   ^\s*([一二三四五六七八九十百零〇]+)、\s*(.+?)\s*（今\s*(\d+)\s*章）\s*$
   ```
3. **工具降级链执行**：优先 MinerU 等专用解析器，**1-2 次尝试失败立即降级**到 pypdfium2/PyMuPDF 等纯 Python 库；降级后标注提取质量等级（A/B/C），并在产出中明确标注需人工校对部分。
4. **文本清洗与结构化转换**：硬换行修复（行尾非句末标点且下一行非空行/小节标题则合并，**F-020 规则**）、水印/页码移除、子结构标记识别（正则 → `###` 小标题）、OKF frontmatter 生成（**注意整数类型不加引号**）。
5. **确定性格式校验修复（强制独立阶段）**：用**确定性 Python 脚本（非 LLM）**校验：YAML 字段类型、一级标题、toctree 语法、孤立文件；自动修复可修复问题。
6. **Sphinx 构建验证**：`sphinx-build -b html -W --keep-going` 零错误退出；必要时 `suppress_warnings` 抑制**已确认无害**的非关键警告（如 `myst.header` 已知跳级）；启动本地 HTTP 服务器预览，确认导航顺序。

> **警告抑制边界**：仅当确认警告对应的是**有意为之的结构选择**（如章节自带 H1、页面无 H1 前的层级跳级）才可 suppress；**禁止**为通过构建而无差别抑制 ERROR 级问题或掩盖正文结构混乱。

## 反模式（不要这么做）

- ❌ **AP-1 指望 LLM 一次生成完全正确的 YAML 类型和 MyST 语法**：整数字段变字符串、toctree 语法错误（` ```toctree ` 与 ` ```{toctree} `）、缺一级标题，构建阶段才暴露 → **正确做法**：独立后置校验阶段，确定性脚本检查自动修复，禁止跳过 step 5。
- ❌ **AP-2 强推最强工具但环境不支持，卡在工具安装上浪费时间**：MinerU 反复尝试失败数小时，pypdfium2 其实一次就能跑通 → **正确做法**：设定 1-2 次尝试超时阈值，立即降级到能跑通的方案，降级后标注质量等级。
- ❌ **AP-3 "忠于原文"理解为"保留 PDF 物理排版"**：段落被硬换行切碎、水印被当原文保留、分页符混入文本 → **正确做法**：三层忠实边界——内容层（文字/标点/注释编号）零修改，排版层（硬换行/分页/水印）主动清洗，结构层（章节/子部分）主动重组标记。

## 检验标准

- [ ] 章节总数与 PDF 一致，每章字数在合理范围（无空章/截断）
- [ ] `sphinx-build` 退出码 0，无 ERROR
- [ ] 无孤立文档，所有 .md 被 toctree 引用
- [ ] 抽查 3 章（首/中/末）核心原文句子与 PDF 一致
- [ ] frontmatter 字段类型正确（chapter_num/modern_chapter 为无引号整数）
- [ ] 本地 HTTP 服务器可浏览，导航顺序正确
- [ ] 混合排版部分（若有）已降级标注质量等级并标记人工校对

## 已知边界

- **注音/混排附录提取不可靠**：pypdfium2 提取拼音注音版时拼音与汉字文字块分离、文本顺序混乱（本案例 P281-297 注音版附录），必须标注"需人工校对"；如需高质量注音版，应使用 MinerU 等支持版面分析的工具重新提取。
- **OKF 规范来源**：frontmatter 字段定义以 `vendor/knowledge-catalog/okf/SPEC.md` 为准（本案例要求 type/title/sources 等字段），不同 OKF 版本字段可能有差异，实施前先读规范。
- **降级后人工成本**：工具降级链产生 B/C 级提取质量时，需预留人工校对预算（建议至少通读首/中/末 5 章确认无提取遗漏）。

## 迁移示例

- **场景 1（非当前领域）**：学术论文 PDF → OKF 知识卡片 Wiki——步骤通用，子结构正则改为"摘要/方法/结果/讨论"。
- **场景 2（跨领域）**：技术手册/API 文档 PDF → 结构化知识库——同一流水线，frontmatter 字段按目标规范调整，校验阶段复用（YAML 类型 + 标题层级 + toctree + 孤立文件四查）。

## 实际案例

| 案例 | 输入 | 输出 | 验证结果 | 日期 |
|------|------|------|---------|------|
| 《帛书老子注读》 | 297 页纯文本 PDF | 93 个 Markdown + 97 个 HTML 页面，约 14.8 万正文字 | sphinx-build 零错误，抽查 3 章原文一致，无孤立文档 | 2026-08-21 |

## 关联模式

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [sphinx-conf-probe-fallback](../code-patterns/sphinx-conf-probe-fallback.md) | 互补 | step 6 构建验证的 conf.py 配置基础（probe-fallback 保证多环境兼容） |
| [tool-failure-three-tier-degradation](../methodology-patterns/tools-automation/tool-failure-three-tier-degradation.md) | 互补 | step 3 工具降级链的通用故障降级方法论（2 次失败即降级） |
| [python-wheel-dependency-audit-wda4](python-wheel-dependency-audit-wda4.md) | 相似 | 同为"确定性校验修复层"思路——LLM/手动产出后必须确定性验证，WDA-4 用于依赖声明，本模式用于文档格式 |
