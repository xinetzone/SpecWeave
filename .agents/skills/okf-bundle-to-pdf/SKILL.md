---
name: okf-bundle-to-pdf
version: 1.0.0
description: '把多篇 Markdown 组成的 OKF bundle（分层索引 + 正文）合并导出为单文件、带双层目录（页内 TOC + 阅读器书签大纲）的可阅读 PDF。必须使用此技能：当用户提到"bundle 转 PDF"、"知识包导出 PDF"、"把整个 bundle/知识包生成 pdf"、"多文档合并成一个 pdf"、"PDF 没有目录/书签"、"md 合集导出 pdf"、"OKF PDF 导出"、"要书签大纲和目录页"时。封装七步链路：剔除嵌套 index → 相对链接降级 → h1/h2 锚点注入 → Pandoc --toc 合并 → Mermaid 运行时渲染 → CDP generateDocumentOutline 打印 → 程序化产物断言。不用于单文件 Markdown 的常规 MD→PDF 转换（用 export-md-to-pdf.py）、不用于对话方案草稿交付（用 markdown-first-deliverable-drafting）、不用于 Word/DOCX 输出。'
argument-hint: "<bundle 目录> [-o output.pdf] [--title T] [--dry-run] [--channel auto|msedge|chromium] [--no-mermaid] [--wait-ms 15000]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/okf-bundle-to-pdf/**"
title: "OKF bundle → 带双层目录 PDF 导出"
x-toml-ref: "../../../.meta/toml/.agents/skills/okf-bundle-to-pdf/SKILL.toml"
source: "来源会话（老子文化生态圈 OKF bundle 转带目录 PDF；落盘于里程碑复盘 okf-bundle-to-pdf-milestone-retrospective-20261031，模式「双层目录导出法」）"
---

# okf-bundle-to-pdf — OKF bundle → 带双层目录 PDF 导出

## 1. Skill ID

`okf-bundle-to-pdf`（脚本命令门面，对应 `scripts/build_bundle_pdf.py`；参考既有单文件转换的 CSS，补齐 bundle 合并、双层目录及 Mermaid 源码保真与失败阻断能力。不要复用提前去转义逻辑）。

> **边界（必遵守）**：不要用本技能做单文件 Markdown 的常规转换（直接跑 `.agents/scripts/export-md-to-pdf.py`）；不要用本技能做对话方案草稿的交付判定（归 [markdown-first-deliverable-drafting](../markdown-first-deliverable-drafting/SKILL.md)）；不要用本技能产出 Word/DOCX（归 docx 系列）。本技能只负责「**多篇 Markdown 的 bundle → 单文件、带双层目录 PDF**」那一段。

## 2. 功能描述

把 OKF bundle（根 `index.md` + `concepts/`、`examples/`、`references/` 等子目录正文）合并为**单个 PDF**，并同时生成两种互补导航：

| 目录形式 | 生成方式 | 作用 |
|---|---|---|
| **页内目录页** | Pandoc `--toc --toc-depth=2` | 文档首页的「目录」清单，点击可跳转 |
| **书签大纲** | CDP `Page.printToPDF(generateDocumentOutline: True)` | 阅读器侧边栏大纲，带页码、可折叠 |

核心功能：

1. **bundle 枚举与去重**：递归枚举 `*.md`，剔除嵌套 `index.md`（保留根 `index.md` 作前言），禁止凭记忆构造清单；
2. **链接降级**：合并后跨文件相对路径失效，将相对链接降级为纯文本（保留可读标题），不删除内容；
3. **锚点注入**：为 `h1` 注入 `{#doc-<slug>}`、为 `h2` 注入 `{#doc-<slug>-hN}`，且必须跳过代码围栏内的 `#`；
4. **双层目录**：Pandoc 页内目录 + CDP 书签大纲，二者并存；
5. **程序化验收**：断言页数 / outline 条目数 / 链接注释数 / 首页含「目录」，禁止以「命令退出码 0」替代结构断言。

> **为什么单独出一门面而不直接用 export-md-to-pdf.py？** 既有脚本只覆盖「单文件 MD→PDF」，不含 bundle 合并、嵌套 index 剔除、相对链接降级、h1/h2 锚点注入、`--toc` 页内目录、CDP 书签大纲，也不做产物结构断言。本次实战（老子文化生态圈 bundle，23 个 `.md`）踩到的三个真坑——`page.pdf(outline=True)` 静默吞参、`h2` 缺 id 导致页内目录点不动、Chromium 未下载而系统已有 Edge——都在既有脚本的覆盖范围之外，单独门面才能在触发时把这些处置规则前置。

## 3. 何时触发（触发词 + 强触发条件）

**主触发词**（满足任一项就用）：

- 导出形态：`bundle 转 PDF`、`知识包导出 PDF`、`把整个 bundle 生成 pdf`、`多文档合并成一个 pdf`、`md 合集导出 pdf`、`OKF PDF 导出`；
- 目录诉求：`PDF 没有目录`、`PDF 缺书签`、`要目录页和书签大纲`、`目录跳不动`；
- 输入特征：给出一个含分层索引（`index.md` + 子目录）的目录路径并要求出 PDF。

**强触发条件**：即使没有上面的词，只要用户给的输入是一个**多篇 Markdown 的目录（bundle/知识包/教程合集）**并要求 PDF，**就必须走本技能**，不要直接把路径丢给单文件转换脚本。

> **为什么触发条件要按"输入形态"而不是"关键词"来定？** 单文件与多文档目录的差异不是量上的，而是流程上的：单文件无需合并、无需剔除子 index、无需锚点注入；把目录硬塞进单文件脚本，会得到一份「没有目录、跨文档链接全断」的产物，用户还得返工。按输入形态判定，能在第一跳就选对链路。

## 4. 方案选择决策树

```
输入是否为一个含分层索引的多篇 Markdown 目录（bundle）？
├─ 否，是单个 .md 文件
│   └─ 不用本技能 → 走 .agents/scripts/export-md-to-pdf.py（单文件转换）
├─ 是（bundle），且需要可导航 PDF
│   ├─ 环境正常（pandoc + playwright 可用）
│   │   └─ 方案A：build_bundle_pdf.py 七步主路径（§7，⭐默认）
│   └─ 主路径失败
│       ├─ 浏览器二进制缺失 → 方案A 自动降级 channel=msedge（复用系统 Edge）
│       └─ 打印通道不支持大纲 → 候选文件可回退 page.pdf，但无大纲则 CLI 验收失败，不发布
└─ 只想先看会导出哪些文件（不写盘）？
    └─ --dry-run 预览模式（只读，0 副作用，§5）
```

**写操作原则**：本技能会写 PDF 文件，属写操作。**先跑 `--dry-run` 预览文件清单与规模**，用户确认输出路径后再正式导出。

> **为什么 `--dry-run` 是默认第一道闸？** 合并类操作的最大风险是「清单里混进了不该合的文件」（例如并发会话正在写的子 index，或把根 index 重复计入）。预览把「将合并哪些文件、共多少字符」摆在台面上，成本极低，却能避免产出一份内容错版的 PDF 后才发现。

## 5. 输入参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| bundle | path | 是 | — | bundle 根目录（含根 `index.md` 与子目录正文） |
| `-o` / `--output` | path | 否 | `<bundle 名>.pdf`（当前目录） | 输出 PDF 路径 |
| `--title` | string | 否 | bundle 目录名 | 产物标题（Pandoc metadata title） |
| `--dry-run` | flag | 否 | false | **只读**：打印将合并的文件清单、字符数、输出路径，不写盘 |
| `--channel` | enum | 否 | `auto` | `auto`（先 chromium 后 msedge）/ `msedge` / `chromium` |
| `--no-mermaid` | flag | 否 | false | 显式跳过渲染，保留围栏源码；不是离线渲染图表 |
| `--wait-ms` | int | 否 | 15000 | Mermaid 渲染等待超时（毫秒） |
| `--css` | path | 否 | — | 追加自定义 CSS（叠加在默认样式之后） |
| `--keep-html` | flag | 否 | false | 保留中间 HTML 用于调试 |

## 6. 依赖与前置准备

- **pandoc**：`pandoc --version` 可访问（实测 3.8 可用）；
- **playwright**：`python -c "import playwright"` 可导入（实测 1.60.0）；浏览器二进制**不强制要求**——缺失时自动降级到系统 Edge；
- **pypdf**：CLI 完整验收必需（页数 / outline / 导航目标）；缺失时不发布候选 PDF；
- **网络**：Mermaid 走 CDN（`cdn.jsdelivr.net`）；不可用时阻止打印。只有用户接受保留图表源码时才用 `--no-mermaid`。

> **为什么把浏览器二进制降级为"可选"？** 本次实战中 `playwright install chromium` 下载进度停在 0%，而系统自带 Edge（同为 Chromium 内核）直接可用。把「驱动层（playwright）」与「二进制来源（chromium/Edge）」解耦后，下载类阻塞不再构成任务终止条件。

## 7. 方案A：七步主路径（⭐默认）

### 7.1 命令速查（在 bundle 所在仓库根目录执行）

```bash
# ===== 第 0 道闸：--dry-run 预览（只读，不写盘），先给用户看清单与规模 =====
python .agents/skills/okf-bundle-to-pdf/scripts/build_bundle_pdf.py \
  "projects/awesome-okf-xs/doc/bundles/guoxue/laozi/laozi-culture-ecosystem" --dry-run

# ===== 正式：七步全流程 =====
python .agents/skills/okf-bundle-to-pdf/scripts/build_bundle_pdf.py \
  "projects/awesome-okf-xs/doc/bundles/guoxue/laozi/laozi-culture-ecosystem" \
  -o dist/laozi-culture-ecosystem.pdf --channel auto

# 输出：analysis 行(文件数/字符数) + 打印通道 + 验收表(PAGES/OUTLINE/ANNOTS/HAS_TOC)
```

### 7.2 七步原子流程（脚本自动执行，顺序不可颠倒）

| 步 | 动作 | 关键约束 / 验收 |
|---|---|---|
| 1 | 递归枚举 `*.md`，剔除嵌套 `index.md`，保留根 `index.md` 且置于首篇 | 先枚举再核对，禁止凭记忆构造清单 |
| 2 | 相对链接降级为纯文本（保留可读标题） | 降级而非删除；`http(s)` 链接保持 |
| 3 | 注入锚点：`h1` → `{#doc-<slug>}`，`h2` → `{#doc-<slug>-hN}` | 必须跳过代码围栏（```/~~~）内的 `#` |
| 4 | 转换无参数 MyST 指令围栏，Pandoc 合并 → HTML，开启 `--toc --toc-depth=2` | Mermaid 源码逐块比较；保留 HTML 转义，由 DOM `textContent` 解码一层 |
| 5 | 同步关闭自动渲染，逐块 parse/render（CDN → SVG） | 完成状态 + Markdown/HTML/渲染数量一致 + 错误节点为零；失败或超时不打印 |
| 6 | 打印时走 CDP `Page.printToPDF` + `generateDocumentOutline: True` | 参数单位英寸；`preferCSSPageSize` 走 `@page A4` |
| 7 | 验收候选 PDF：页数 / 大纲 / 显式目录标题 / 目录锚点覆盖 / 有效导航页目标 | 全部通过后才替换旧 PDF；禁止以「退出码 0」替代结构断言 |

### 7.3 方案A 内置安全机制

1. **预览隔离**：`--dry-run` 在任何写操作前完成清单与统计输出，不创建临时文件；
2. **通道自动降级**：`--channel auto` 先试内置 chromium，失败自动换系统 msedge，无需人工干预；
3. **验收不静默**：打印成功但结构不完整时输出 FAIL；CLI 同目录候选文件验收后才替换旧 PDF，底层 `html_to_pdf` 本身不提供发布保护；
4. **产物结构报告**：结尾强制打印 Markdown 验收表，Agent 可直接粘贴。

## 8. 方案B：降级路径（兜底）

触发条件：方案A 的 CDP 打印异常，或环境不支持 CDP。

1. **浏览器二进制缺失** → `--channel msedge`（Windows 自带 Edge，免下载）；
2. **CDP 不可用** → 候选文件回退 Playwright `page.pdf(format="A4")`；若无书签大纲则 CLI 返回失败，旧 PDF 保留；
3. **无 pypdf** → 无法完整验收，CLI 返回失败，不以非空文件冒充交付成功。

## 9. 安全检查清单（逐项确认）

写操作（导出 PDF）前后逐项确认：

- [ ] 已跑 `--dry-run` 预览，用户已看到将合并的文件清单（文件数、字符数）与输出路径并批准
- [ ] 已确认 bundle 路径指向**受版本控制的位置**（而非临时目录），保证产物可复现
- [ ] 已确认输出路径落在预期位置（公开产物入 `docs/` 或 `dist/`，遵守根 `.gitignore` 约定）
- [ ] 已确认不混入并发会话在途的未提交文件（枚举清单已与 `git status` 核对）
- [ ] 已确认 `--toc` 生效（验收表 `HAS_TOC` 已通过，首页含「目录」）
- [ ] 已验证书签大纲落地（验收表 `OUTLINE > 0`）；若为 0 已明确告知用户并给出回退说明
- [ ] 已确认 Mermaid 源码逐块保真、数量一致、渲染完成且无错误 SVG；未仅检查 SVG 存在
- [ ] 已核对 TOC 预期锚点在 PDF 链接中完整出现，命名目标与书签指向有效页面
- [ ] 已核对产物大小与页数合理（非 0 字节、页数与字符数量级匹配）

## 10. 常见错误处理

| 错误码/场景 | 现象 | 处理方式 |
|---|---|---|
| PDF_001 | 产物无书签大纲（outline=0） | 确认走的是 CDP 路径且 `generateDocumentOutline: True`；不要用 `page.pdf(outline=True)`（Playwright 1.60+msedge 实测静默吞参） |
| PDF_002 | 页内目录条目点击不跳转 | `h2` 未注入 `id`；回到第 3 步，`h1`/`h2` 都要注入锚点 |
| PDF_003 | Chromium 启动失败 / 下载卡 0% | 改用 `--channel msedge`（系统 Edge），不要死等下载 |
| PDF_004 | Mermaid 语法错误、库不可用或解析超时 | 停止打印；核对真实解析错误与源码保真。`--no-mermaid` 仅在用户接受源码显示时使用 |
| PDF_005 | Pandoc 报错 | 确认 pandoc 在 PATH；`pandoc --version` 自检 |
| PDF_006 | 页数/字符数与预期不符 | 核对第 1 步枚举清单是否漏文件或多计子 index；用 `--dry-run` 复核 |

## 11. Gotchas（陷阱与反直觉行为）

### 11.1 打印通道陷阱

- **Gotcha 1：`page.pdf(outline=True)` 被接受但不生效**。Playwright 1.60 + 系统 Edge 组合下，该参数不抛异常，产物却不含 `/Outlines`。验收必须落在 PDF 结构（outline 计数）上，不能看「调用没报错」。
- **Gotcha 2：CDP 参数单位是英寸，不是点**。`paperWidth: 8.27` / `paperHeight: 11.69` / `margin*: 0.7874` 对应 A4 + 2cm；与 `format` 参数混用会冲突，只保留一套。

### 11.2 目录结构陷阱

- **Gotcha 3：页内目录与书签大纲是两套独立前置**。「加了 `--toc` 就有目录」只对页内目录成立，且还要求锚点先存在；阅读器侧边栏只认 `/Outlines`。缺一即「跨文档跳不动」或「侧边栏空」。
- **Gotcha 4：`h2` 也必须注入 id**。只给 `h1` 注入时，页内目录的一级条目能跳，二级条目点了没反应。

### 11.3 环境与口径陷阱

- **Gotcha 5：Playwright 是驱动层，浏览器二进制可来自系统安装**。Windows 自带 Edge 与 Chromium 同为内核，`--channel msedge` 即可复用，不必 `install chromium`。
- **Gotcha 6：不要用会话摘要里的旧规模数字做断言**。本次摘要记「20 篇 / 117706 字符」，磁盘实测为「19 篇非 index / 124461 字符 / 共 23 个 `.md`」；基数错则覆盖率结论全错。
- **Gotcha 7：嵌套 `index.md` 剔除的是子目录索引，不是根 `index.md`**。根 index 要保留作前言；只保留一个根级 `index.md`。
- **Gotcha 8：错误占位图也是 SVG**。不能只数 SVG；默认自动渲染竞态和实体双重解码都可能把合法源码变成解析错误。
- **Gotcha 9：MyST 围栏可能吞入下一篇正文**。Pandoc 不识别原生 `{toctree}` 围栏；转换后仍以代码保留，不实现 Sphinx 指令语义。
- **已知边界（本轮未扩展）**：原生 HTML `.mermaid` 不属于标准围栏支持面；带参数指令、缩进 Mermaid、行内代码链接保护、已有页内锚点重映射、非 ASCII 或路径归一化碰撞仍需专门处理。全篇错误提示文字扫描也可能误伤讨论错误信息的正文；不要用于该类 bundle 而忽略失败。
- **版本边界**：生产 CDN 的 `@11` 是浮动版本；本轮回归使用真实 11.17.2 缓存，不代表后续 CDN 字节完全可复现。

### 11.4 回归测试与当前证据

```powershell
# 可选：MERMAID_TEST_LIBRARY 指向仓库外的真实 Mermaid JS 缓存；未设置则联网下载。
python -B -m pytest .agents/skills/okf-bundle-to-pdf/scripts/test_build_bundle_pdf.py -q -o addopts='' -p no:cacheprovider
```

测试覆盖实体单层解码、MyST 首图保真、长围栏、真实语法失败、CDN 请求阻断、已进入 parse 的超时、显式源码模式、目录目标缺失以及最终验收失败保留旧 PDF。业务样例的 12 图计数是当前集成断言，不是通用 bundle 固定规模。PDF 页目标验证不代替视觉排版与阅读器点击走查。

## 12. 关键参考速查表

| 目标 | 值/命令 | 注意事项 |
|---|---|---|
| 结构验收（页数/大纲/链接） | `pypdf.PdfReader`：`len(r.pages)`、`r.outline`、逐页 `/Annots` | outline 是嵌套 list，递归计数；顶层长度含子列表 |
| 打印通道 | `--channel auto` | 先 chromium 后 msedge |
| PDF 尺寸 | CDP `paperWidth/paperHeight`（英寸）或 `@page { size: A4 }` | 二者不要混用 |
| Mermaid CDN | `cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js` | 离线环境用 `--no-mermaid` |
| 单文件转换（非 bundle） | `.agents/scripts/export-md-to-pdf.py` | 本技能的最近邻，不重叠 |

## 13. Changelog

- **2026-10-31 修复记录（v1.0.0 包内修订）**：修复 Mermaid 自动渲染竞态、实体双重解码与 MyST 围栏吞首图；补源码保真、渲染失败阻断、导航验收、CLI 候选发布与回归测试。共享登记面及版本镜像未修改，未提交。
- **v1.0.0**（2026-10-31）：首版交付；来源 `老子文化生态圈` OKF bundle（23 个 `.md`、12 个 Mermaid 图）导出带双层目录 PDF（188 页 / 264 条大纲 / 335 个链接注释）实战沉淀；封装七步链路、`--channel auto` 降级、`--dry-run` 预览门、程序化验收、6 条错误码与 7 条 Gotchas。
