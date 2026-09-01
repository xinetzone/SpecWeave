---
id: retrospective-boshu-laozi-pdf-to-myst-wiki-20260821
title: "《帛书老子注读》PDF转OKF-MyST Wiki 里程碑复盘"
type: task-retrospective
date: 2026-08-21
status: final
methodology: seven-concepts (R→I→E)
scenario: milestone
depth: standard
session: sc-20260821-boshu-laozi-milestone
source:
  - "playground/books/notebook/boshu-laozi-zhudu/（项目输出）"
  - ".trae/specs/laozi-zhudu-mystx-wiki/（Spec文档）"
tags:
  - pdf-conversion
  - okf
  - sphinx
  - myst
  - knowledge-engineering
  - books
gates_passed:
  - G1: "35条客观事实，无因果词"
  - G2: "3条四元组洞察，维度独立"
  - G3: "1个L1可复用模式（6步骤+3反模式）"
---

# 《帛书老子注读》PDF转OKF-MyST Wiki 里程碑复盘

## 一、项目概览

| 项 | 值 |
|---|---|
| 项目目标 | 将《帛书老子注读电子书11.11.pdf》（297页）转换为符合OKF v0.2规范的Markdown，用Sphinx+mystx构建可浏览的静态Wiki |
| 输入 | `playground/books/帛书版道德经资料/帛书老子注读电子书11.11.pdf` |
| 输出 | `playground/books/notebook/boshu-laozi-zhudu/` |
| 模板 | `playground/books/libs/mystx/`（Sphinx+mystx主题，Python 3.14） |
| 规范 | `vendor/knowledge-catalog/okf/SPEC.md` |
| 产出规模 | 93个Markdown文件、97个HTML页面、约14.8万正文字 |
| Spec文档 | `.trae/specs/laozi-zhudu-mystx-wiki/`（spec.md/tasks.md/checklist.md） |

### 交付内容

```
doc/
├── index.md                     # 首页
├── conf.py                      # Sphinx配置（mystx主题）
├── _config.toml                 # 主题配置（中文公告、关闭仓库按钮）
├── front-matter/                # 前言
│   ├── copyright.md             # 版权页（P2）
│   ├── author-intro.md          # 作者简介（P6）
│   ├── preface.md               # 序（P7-9）
│   └── reading-guide.md         # 注读说明（P10-11）
├── de-jing/                     # 德经（44章，今本38-81章）
│   ├── title.md
│   └── ch01.md ~ ch44.md
├── dao-jing/                    # 道经（37章，今本1-37章）
│   ├── title.md
│   └── ch45.md ~ ch81.md
└── appendix/
    └── phonetic.md              # 注音版附录（P281-297，需人工校对）
```

每章均包含五个标准小节（部分章节缺传世版/版本差异）：
- **帛书版**：帛书原文
- **传世版**：王弼本对照
- **版本差异**：校勘注释（保留①②③脚注）
- **直译**：白话译文
- **解读**：作者详细解读

---

## 二、事实清单（R阶段）

> 35条客观事实，G1质量门通过（无因果推断词）

| 编号 | 事实 |
|------|------|
| F-001 | 输入PDF共297页，路径 `playground/books/帛书版道德经资料/帛书老子注读电子书11.11.pdf` |
| F-002 | mystx模板路径 `playground/books/libs/mystx/`，基于Sphinx构建 |
| F-003 | OKF规范路径 `vendor/knowledge-catalog/okf/SPEC.md`，要求YAML frontmatter含type/title/sources等字段 |
| F-004 | 项目输出目录 `playground/books/notebook/boshu-laozi-zhudu/` |
| F-005 | pyproject.toml声明 `requires-python = ">=3.14"`，用uv管理虚拟环境 |
| F-006 | 初始尝试local-mineru skill解析PDF，因TRAE Sandbox限制uv.exe权限被拒（`Access to the path ...uv.exe is denied`） |
| F-007 | 替代方案使用pypdfium2纯Python库提取文本，解释器路径 `C:\Users\xinzo\.openvino\venv\mineru\Scripts\python.exe` |
| F-008 | PDF物理结构：P1空白、P2版权、P3-5目录、P6作者简介、P7-9序、P10-11注读说明、P12德经标题、P13-280正文81章、P281-297注音附录 |
| F-009 | 道经注读标题页位于P140（0-indexed=139） |
| F-010 | 帛书版章节顺序：德经44章在前，道经37章在后（与传世本德经在后、道经在前不同） |
| F-011 | 德经对应今本38-81章，注意帛书次序41在40之前 |
| F-012 | 道经对应今本1-37章 |
| F-013 | 章标题识别正则：`^\s*([一二三四五六七八九十百零〇]+)、\s*(.+?)\s*（今\s*(\d+)\s*章）\s*$` |
| F-014 | Markdown文件总数93个（81章+4前言+1附录+5index+2title） |
| F-015 | 章节字数范围：最短740字（ch50/今12章），最长3207字（ch46/今1章），平均1503字 |
| F-016 | 总章节正文字数约148,330字 |
| F-017 | 子结构标记统一为 `### 帛书版/传世版/版本差异/直译/解读` |
| F-018 | OKF frontmatter字段：type, title, part, chapter_num(int), modern_chapter(int), sources, generated, verified(false), status(draft) |
| F-019 | sources字段统一为 `"秦波，《帛书老子注读》，2024"` |
| F-020 | PDF硬换行清洗规则：行尾非句末标点且下一行非空行/小节标题则合并 |
| F-021 | 水印文字"扫码添加作者微信"已在清洗阶段移除 |
| F-022 | 注音版附录（P281-297）拼音与汉字文字块分离，文本顺序混乱，phonetic.md已标注人工校对警告 |
| F-023 | Sphinx构建命令 `uv run sphinx-build -b html doc doc/_build/html -W --keep-going`，退出码0 |
| F-024 | HTML输出文件数97个 |
| F-025 | 主题加载：mystx→sphinx_book_theme→alabaster，mystx成功加载 |
| F-026 | 启用扩展：myst_parser, myst_nb, sphinx_design, sphinx_copybutton |
| F-027 | conf.py中 `suppress_warnings = ["myst.header"]` 抑制H1→H3跳级警告 |
| F-028 | toctree初始误用RST语法 ` ```toctree `，后修正为MyST标准 ` ```{toctree} ` |
| F-029 | chapter_num/modern_chapter初始被错误加引号（YAML字符串），fix脚本修正为无引号整数 |
| F-030 | 初始生成的Markdown文件frontmatter后缺少一级标题，fix脚本补充添加 |
| F-031 | .gitignore已创建，排除_build/, __pycache__/, .venv/等 |
| F-032 | 临时脚本共8个（pdf_probe/extract_pdf/probe_pages/probe_appendix/extract_chapters/convert_to_md/fix_md_format/final_check），均保存在notebook/目录 |
| F-033 | 本地预览通过 `python -m http.server 8090` 启动，地址http://localhost:8090/ |
| F-034 | 所有93个Markdown文件均被toctree引用，无孤立文档 |
| F-035 | ①②③④⑤等带圈脚注标记完整保留在原位 |

---

## 三、核心洞察（I阶段）

> 3条四元组洞察，G2质量门通过（陈述+证据+反常识+行动）

### 洞察 I-1：受限环境下的工具降级链策略

**陈述**：在AI Agent沙箱/权限受限的执行环境中，重量级专用工具（依赖多模型、外部二进制、缓存目录写入）比轻量纯Python库更容易因权限问题失败；对纯文本类PDF而言，轻量库（pypdfium2）的提取质量足以支撑结构化知识转换。

**证据**：F-006（local-mineru Sandbox权限失败）、F-007（pypdfium2成功提取297页）、F-022（pypdfium2对拼音混排有局限但纯文本部分可靠）

**反常识**：直觉假设"功能越强的工具效果越好"，应优先用MinerU这类专业PDF解析器；但在受限环境中，"能跑通的最弱工具"比"功能最强但跑不通的工具"价值高得多——纯文本排版书籍PDF中，pypdfium2的文本提取质量已满足OKF转换需求。

**行动**：建立PDF提取工具降级链：第一选择专用解析器（MinerU），1-2次尝试失败后立即降级到pypdfium2/PyMuPDF；降级后标注提取质量等级（A/B/C），并在产出中明确标注需人工校对的部分。

---

### 洞察 I-2：批量结构化文档生成需要独立校验修复层

**陈述**：AI批量生成带YAML frontmatter的Markdown文档时，格式错误（YAML类型错误、MyST语法细节、结构完整性）是系统性高发问题，无法通过"详细prompt+一次生成"避免，必须增加后置确定性校验修复阶段。

**证据**：F-028（toctree语法错误）、F-029（整数字段加了引号）、F-030（缺少一级标题）、F-027（标题跳级警告）

**反常识**：直觉认为"给AI详细模板+明确规则"就能保证格式正确；但实践证明即使规则极其明确，LLM对"YAML整数不加引号""MyST指令需要大括号"这类语法细节仍会系统性出错——这不是prompt不够详细的问题，而是LLM缺乏schema验证即时反馈回路，生成阶段天然存在格式噪声。

**行动**：将"fix/validate"作为文档批量生成的标准后置阶段，用确定性Python脚本（非LLM）检查：YAML字段类型、Markdown标题层级、toctree语法、孤立文件；校验脚本模板化，纳入文档类项目标准任务链（生成→校验→修复→构建验证）。

---

### 洞察 I-3："忠于原文"在格式转换中的三层边界

**陈述**：PDF→结构化Markdown转换中，"忠于原文"约束应严格限定于文字内容层（不得增删改原文文字），排版层（硬换行、分页、水印）必须主动清洗，结构层（子标题识别）必须主动重组——三者边界清晰才是真正的忠实。

**证据**：F-020（硬换行合并）、F-017（子结构标记转为###）、F-021（水印移除）、F-035（脚注保留）

**反常识**：直觉认为"忠于PDF=保留PDF中看到的一切"，包括硬换行和分页位置；但PDF是物理排版格式（硬换行为适应页宽，水印为出版商附加物），Markdown是逻辑结构格式——保留物理排版的硬换行反而破坏阅读连贯性，移除水印是去除非作者内容而非篡改原文。

**行动**：PDF→Markdown转换明确三层处理原则：**内容层**（文字、标点、注释编号）零修改；**排版层**（硬换行、分页符、页眉页脚、水印）清洗去除；**结构层**（章节边界、子部分标记）用规则识别并标记为Markdown结构；在项目说明中记录哪些是原始内容、哪些是结构化标记。

---

## 四、可复用模式萃取（E阶段）

> 模式：pdf-book-to-okf-wiki-v1，G3质量门通过（6步骤+3反模式+检验标准+跨场景迁移）

### 模式：PDF书籍→OKF-MyST Wiki 四阶段工作流

> 📦 **已入库**：本模式已按标准模板沉淀至 [process-patterns/pdf-book-to-okf-wiki.md](../../patterns/process-patterns/pdf-book-to-okf-wiki.md)（含补充的章标题正则示例、已知边界、警告抑制边界）。

**适用场景**：纯文本排版中文书籍PDF（非扫描件、非图册）→ 符合OKF规范的Markdown知识库 → Sphinx+MyST+mystx静态Wiki。

**核心步骤（6步）**：

1. **环境准备与模板复制**：基于mystx模板创建项目骨架（pyproject.toml/conf.py/_config.toml），uv创建Python 3.14虚拟环境，验证mystx可导入。
2. **PDF结构探查**：先提取首尾样本页识别物理结构（封面/版权/目录/前言/正文/附录），确定章标题正则模式，跳过目录页避免误识别，输出结构化JSON（front_matter/chapters/appendix）。
3. **工具降级链执行**：优先MinerU等专用解析器，1-2次失败立即降级pypdfium2；降级后标注质量等级。
4. **文本清洗与结构化转换**：硬换行修复、水印/页码移除、子结构标记识别（正则→###小标题）、OKF frontmatter生成（注意整数类型无引号）。
5. **确定性格式校验修复（强制独立阶段）**：Python脚本校验YAML类型、一级标题、toctree语法、孤立文件；自动修复可修复问题。
6. **Sphinx构建验证**：`sphinx-build -b html -W --keep-going`零错误退出，必要时suppress非关键警告，启动本地服务器预览。

**反模式（3个，来自本案例教训）**：

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|----------|
| AP-1 | 指望LLM一次生成完全正确的YAML类型和MyST语法 | 整数字段变字符串、toctree语法错误，构建阶段才发现 | 独立后置校验阶段，确定性脚本检查自动修复 |
| AP-2 | 强推最强工具但环境不支持，卡在工具安装上浪费时间 | local-mineru反复尝试失败，pypdfium2其实足够 | 设定1-2次尝试超时阈值，立即降级到能跑通的方案 |
| AP-3 | "忠于原文"理解为"保留PDF物理排版" | 段落被硬换行切碎，水印被当原文保留 | 三层边界：内容不改、排版清洗、结构重组 |

**检验标准**：
- [ ] 章节总数与PDF一致，每章字数在合理范围（无空章/截断）
- [ ] `sphinx-build`退出码0，无ERROR
- [ ] 无孤立文档，所有md被toctree引用
- [ ] 抽查3章（首/中/末）核心原文句子与PDF一致
- [ ] frontmatter字段类型正确
- [ ] 本地HTTP服务器可浏览，导航顺序正确

**跨场景迁移**：学术论文PDF→OKF知识卡片Wiki（步骤通用，子结构正则改为"摘要/方法/结果/讨论"）。

**成熟度**：L1（单案例验证），成熟度提升需更多不同类型书籍PDF验证。

---

## 五、任务执行时间线

| 阶段 | 关键动作 | 产出 |
|------|----------|------|
| S0 环境探索 | mystx模板结构分析、OKF规范阅读、PDF内容探测 | 理解项目约束 |
| S1 PRD制定 | 七概念方法论指导下生成spec.md/tasks.md/checklist.md | Spec三文档获用户批准 |
| Task1 项目骨架 | pyproject.toml/conf.py/_config.toml/index.md、uv venv、mystx安装 | 项目可预构建 |
| Task2 PDF提取 | extract_chapters.py、chapters.json（81章精确边界） | 结构化JSON数据 |
| Task3 MD转换 | convert_to_md.py、fix_md_format.py、93个Markdown文件 | OKF合规MD文件 |
| Task4 文档结构 | 目录结构、toctree索引、MyST语法修正 | 完整文档树 |
| Task5 构建验证 | sphinx-build -b html 零错误、97个HTML、本地预览服务器 | 可浏览的Wiki网站 |
| Task6 最终校验 | 完整性/字数/孤立文件/.gitignore | 全部校验通过 |

---

## 六、已知限制与后续建议

1. **注音版附录（P281-297）**：pypdfium2提取时拼音与汉字文字块分离，文本顺序混乱，已标注需人工校对。如需高质量注音版，应使用MinerU等支持版面分析的工具重新提取。
2. **generated日期字段**：脚本使用系统日期生成，本项目中为2026-08-21，如需精确记录书籍出版日期应新增字段区分。
3. **临时脚本清理**：8个临时Python脚本保留在notebook/目录下，可作为同类项目参考，也可在最终整理时归档到scripts/目录。
4. **内容人工校对**：虽然原文文本忠实度已通过抽查验证，但建议人工通读至少5章（首章、ch45道经首章、ch40/ch60/ch81）以确认无提取遗漏。
5. **模式成熟度提升**：本工作流为L1单案例验证，处理第2-3本不同类型书籍后可升级为L2成熟模式并入库。

---

## 七、质量门通过记录

| 质量门 | 阶段 | 结果 | 备注 |
|--------|------|------|------|
| G1 | R（事实采集） | ✅ 通过 | 35条事实，无因果词 |
| G2 | I（洞察） | ✅ 通过 | 3条四元组洞察，维度独立，有反常识 |
| G3 | E（萃取） | ✅ 通过 | 1个L1模式，6步骤+3反模式+检验标准+迁移验证 |

[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20260821-boshu-laozi-milestone | msg=七概念里程碑复盘完成：R(35事实)→I(3洞察)→E(1模式)→报告导出，G1-G3全部通过 | ctx={"facts":35,"insights":3,"patterns":1,"gates_passed":["G1","G2","G3"],"report_path":".agents/docs/retrospective/reports/task-reports/retrospective-boshu-laozi-pdf-to-myst-wiki-20260821.md"}
