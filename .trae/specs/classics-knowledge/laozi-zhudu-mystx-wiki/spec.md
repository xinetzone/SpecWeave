---
title: "《帛书老子注读》MyST Wiki 教程"
status: "draft"
---

# 《帛书老子注读》MyST Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 将《帛书老子注读电子书11.11.pdf》（秦波著，297页）转换为基于 Sphinx + mystx 主题 + Python 3.14 的纯 Markdown Wiki 教程，输出目录为 `playground/books/notebook/boshu-laozi-zhudu/`。每个章节文件符合 OKF v0.2 规范（YAML frontmatter + Markdown body），内容完全忠于 PDF 原文。
- **Purpose**: 使《帛书老子注读》这部以马王堆帛书《老子》为底本的解读著作，可在 Sphinx 静态站点中结构化阅读、导航、检索，同时保持 OKF 溯源能力。
- **Target Users**: 道家经典学习者、《道德经》版本对比研究者、SpecWeave 知识库使用者。

## Goals
- 基于 `playground/books/libs/mystx` 模板，在 `notebook/boshu-laozi-zhudu/` 生成可构建的 Sphinx + Python 3.14 项目
- 用 pypdfium2 提取 PDF 全文（297页），按图书目录结构拆分为原子化 Markdown 文件
- 每个 Markdown 文件包含 OKF v0.2 合规的 YAML frontmatter（type、title、sources、part、chapter 等）
- 内容完全忠于 PDF 原文：帛书原文、传世版对照、版本差异注释、直译、解读各部分完整保留，不删节、不改写、不添加原文以外内容
- Sphinx 构建成功，HTML 输出可正常浏览（含侧边栏导航、章节目录）

## Non-Goals (Out of Scope)
- 不做 PDF OCR（pypdfium2 文本提取已验证可用）
- 不翻译/改写/补充原文解读（保持作者秦波原文）
- 不重新排版复杂表格/公式（本书无表格公式）
- 不生成 PDF/DOCX 导出版本（仅 HTML 构建）
- 不整合之前 `boshu-laozi-wiki` 的公共领域知识内容（本项目严格忠于 PDF）

## Background & Context
- **mystx 模板**: Sphinx 主题，要求 Python >=3.14，使用 myst-nb/myst-parser，pyproject.toml 管理依赖，doc/conf.py 配置 Sphinx，doc/_config.toml 配置主题选项。入口主题为 `mystx`（fallback: sphinx_book_theme → alabaster）。
- **OKF v0.2**: 开放知识格式，核心要求：
  - `type` 字段必需
  - `sources` 数组记录来源（id/resource/title/author）
  - `title`/`description`/`tags` 推荐
  - `generated` 记录生成元信息
- **PDF 结构（已验证）**:
  - P1: 空白封面
  - P2: 版权信息
  - P3-5: 目录
  - P6: 作者简介（含扫码水印，文本部分可读）
  - P7-9: 序
  - P10-11: 注读说明
  - P12: 德经注读（分节标题页）
  - P13-277: 81章正文（每章含：帛书版、传世版、版本差异、直译、解读五个子部分）
  - P278-297: 附录 帛书《老子》注音版
- **章节映射**: 81章中前44章为德经（今38→81→67→...→79章，帛书次序），后37章为道经（今1→37章）

## Functional Requirements
- **FR-1**: 创建 Sphinx 项目骨架（pyproject.toml、doc/conf.py、doc/_config.toml、doc/index.md、doc/_static/）
- **FR-2**: 提取并清洗 PDF 全文，按章节边界拆分，处理页码标记
- **FR-3**: 生成 OKF frontmatter，包含：type=BookChapter、title、part（de_jing/dao_jing/front_matter/appendix）、chapter_num（中文数字序号）、modern_chapter（对应今本章节号）、sources 指向原始 PDF
- **FR-4**: 生成前言文件（版权信息、作者简介、序、注读说明）
- **FR-5**: 生成81章正文文件，按德经/道经分子目录，每章保留完整结构：帛书版、传世版、版本差异、直译、解读
- **FR-6**: 生成附录注音版文件
- **FR-7**: 生成 Sphinx toctree 索引（index.md 根 toctree + de/dao 子目录索引）
- **FR-8**: 构建 HTML 可正常通过，无报错

## Non-Functional Requirements
- **NFR-1**: 所有 Markdown 文件为 UTF-8 编码
- **NFR-2**: 文件名采用 `NN-slug.md` 格式（NN 为两位数序号）
- **NFR-3**: 忠于原文：不删除、不合并、不改写 PDF 中任何正文文字
- **NFR-4**: 从 PDF 提取造成的换行问题应修复（段落内的硬换行应去除）
- **NFR-5**: Python 3.14 环境下 sphinx-build 成功

## Constraints
- **Technical**: Python >=3.14（mystx 要求）、Sphinx + myst-parser + mystx 主题、pypdfium2 做 PDF 提取
- **Business**: 项目位于 `playground/books/notebook/boshu-laozi-zhudu/`
- **Dependencies**: mystx 模板（`playground/books/libs/mystx/`，作为本地包引用）、pypdfium2、sphinx、myst-nb、myst-parser

## Assumptions
- pypdfium2 文本提取质量足够（已验证前15页文本提取正常）
- mystx 主题可以作为本地包安装（通过 pip install -e ../libs/mystx 或 sys.path 注入）
- PDF 中作者简介页（P6）的水印文字不影响核心内容提取
- 附录注音版可以正常提取（生僻字可能有字体映射问题，但可以接受少量缺失）

## Acceptance Criteria

### AC-1: Sphinx 项目骨架正确
- **Given**: notebook/ 目录为空
- **When**: 项目骨架生成完毕
- **Then**: 存在 pyproject.toml、doc/conf.py、doc/_config.toml、doc/index.md，pyproject.toml 中 requires-python = ">=3.14"
- **Verification**: `programmatic`

### AC-2: PDF 全文提取成功
- **Given**: PDF 文件存在且可读
- **When**: 运行提取脚本
- **Then**: 提取文本覆盖全部 297 页，81章起始位置正确（第13页为第一章，第278页为最后一章之后/附录之前）
- **Verification**: `programmatic`

### AC-3: OKF frontmatter 合规
- **Given**: 生成的 Markdown 文件
- **When**: 检查每个文件
- **Then**: 每个文件以 `---\ntype: BookChapter\n` 开头，包含 title、sources、part、chapter_num、modern_chapter 字段
- **Verification**: `programmatic`

### AC-4: 内容忠于原文
- **Given**: 生成的章节 Markdown
- **When**: 人工抽查 5 个章节（首章、中间章、末章等）
- **Then**: 帛书版原文、传世版原文、版本差异、直译、解读五个部分完整保留，文字与 PDF 一致
- **Verification**: `human-judgment`

### AC-5: Sphinx 构建成功
- **Given**: 项目文件齐全
- **When**: 在项目目录运行 `sphinx-build -b html doc doc/_build/html`
- **Then**: 构建退出码为 0，生成 HTML 文件可浏览
- **Verification**: `programmatic`

### AC-6: 章节导航完整
- **Given**: HTML 构建输出
- **When**: 打开 index.html
- **Then**: 侧边栏包含 前言、德经注读（44章）、道经注读（37章）、附录 四个部分，每章可点击跳转
- **Verification**: `human-judgment`

## Open Questions
- [ ] mystx 主题本地引用方式：是 pip install -e 还是通过 sys.path 添加？
- [ ] 作者简介页（P6）有水印干扰文字，如何处理（保留/标注/清洗）？
- [ ] 附录注音版的拼音是否能正确提取（需要验证后几页）？
