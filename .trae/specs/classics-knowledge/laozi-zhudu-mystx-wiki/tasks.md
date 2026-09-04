# 《帛书老子注读》MyST Wiki 教程 - Implementation Plan

## [x] Task 1: 创建 Sphinx + mystx 项目骨架 ✅
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `playground/books/notebook/boshu-laozi-zhudu/` 创建项目目录
  - 编写 pyproject.toml（requires-python >=3.14，依赖 sphinx、myst-parser、myst-nb、sphinx-design、sphinx-copybutton，mystx 以本地路径引用）
  - 编写 doc/conf.py（参考 mystx 模板，配置项目名、作者、语言 zh_CN、myst 扩展、主题）
  - 编写 doc/_config.toml（主题选项：关闭仓库链接、设置中文公告）
  - 创建 doc/_static/ 目录（必要时放 favicon）
  - 使用 uv 创建 Python 3.14 虚拟环境并安装依赖
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: pyproject.toml 存在且 requires-python = ">=3.14" ✅
  - `programmatic` TR-1.2: doc/conf.py 存在且 html_theme = 'mystx'（或 fallback）✅
  - `programmatic` TR-1.3: uv run python -c "import mystx; print(mystx.__version__)" 成功 ✅
- **Verification**: mystx 导入成功，pyproject.toml 正确，预构建通过

## [x] Task 2: PDF 全文提取与章节边界精确定位 ✅
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 修复 extract_pdf.py 的 sections 检测逻辑（从正文区域 P6+ 检测前言/附录起始页）
  - 提取全部 297 页文本，保存为结构化 JSON
  - 精确定位每个章节的页码范围（start_page 到 end_page）
  - 确定前言部分页面：版权(P2)、作者简介(P6)、序(P7-9)、注读说明(P10-11)、德经注读标题页(P12)
  - 确定附录起始页（注音版）
  - 处理章节标题在页内的偏移（章节标题可能在页中间，只截取标题之后的内容）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 81个章节全部检测到，start_page 从 12(0-indexed, 即P13)开始 ✅
  - `programmatic` TR-2.2: 第一章文本包含"上德不德，是以有德"，末章文本包含"真实"相关内容 ✅
  - `programmatic` TR-2.3: 附录起始页正确，包含注音内容特征 ✅
- **Verification**: extract_chapters.py 输出 chapters.json，81章（德经44+道经37），dao_jing_title_page=139(P140)，附录P281-297

## [x] Task 3: 文本清洗与结构化转换 ✅
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 编写转换脚本，逐章提取文本内容
  - 清洗 PDF 提取的硬换行（段落内行尾换行合并为空格，段落间空行保留）
  - 识别每章内的子结构：帛书版、传世版、版本差异、直译、解读，转换为 Markdown 小标题（### 帛书版、### 传世版、### 版本差异、### 直译、### 解读）
  - 修复 PDF 中常见的断字问题
  - 处理作者简介页水印干扰（"扫码添加作者微信"等推广文字已去除）
  - 每个章节生成 OKF frontmatter
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1: 每个 .md 文件以 `---\ntype: BookChapter\n` 开头，包含 title/sources/part/chapter_num/modern_chapter ✅
  - `human-judgement` TR-3.2: 抽查5章，帛书版/传世版/版本差异/直译/解读各部分完整可读，无乱码 ✅
  - `programmatic` TR-3.3: 每个文件 sources 数组中包含原始 PDF 引用 ✅
- **Verification**: convert_to_md.py 生成93个md文件，fix_md_format.py 修复frontmatter整数类型和一级标题

## [x] Task 4: 生成 Sphinx 文档结构与索引 ✅
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 doc 下的目录结构：
    - doc/front-matter/（版权、作者简介、序、注读说明）
    - doc/de-jing/（德经44章）
    - doc/dao-jing/（道经37章）
    - doc/appendix/（注音版）
  - 生成每个目录的 index.md（含 toctree）
  - 编写 doc/index.md 根文档，包含全书 toctree
  - toctree 按图书顺序排列：前言 → 德经 → 道经 → 附录
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: doc/de-jing/ 下有 44 个章节文件，doc/dao-jing/ 下有 37 个章节文件 ✅
  - `programmatic` TR-4.2: 所有 index.md 包含正确的 toctree 指令（MyST {toctree} 语法）✅
  - `human-judgement` TR-4.3: toctree 顺序与图书目录一致 ✅
- **Verification**: 目录结构完整，toctree 使用 MyST 标准语法，无孤立文件

## [x] Task 5: Sphinx HTML 构建验证 ✅
- **Priority**: high
- **Depends On**: Task 1, Task 4
- **Description**:
  - 在项目目录下运行 sphinx-build -b html doc doc/_build/html
  - 修复所有构建错误和警告（myst 语法问题、断链等）
  - 确认 HTML 输出可正常浏览
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: sphinx-build 退出码为 0 ✅
  - `programmatic` TR-5.2: doc/_build/html/index.html 存在 ✅
  - `human-judgement` TR-5.3: 抽查 HTML 页面，中文渲染正常，章节间链接可用 ✅
- **Verification**: sphinx-build 成功（exit 0），97个HTML文件，mystx主题正常加载，本地服务器 http://localhost:8090/ 已启动

## [x] Task 6: 最终校验与清理 ✅
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 检查所有文件 OKF frontmatter 合规性
  - 清理临时文件（.gitignore 已创建）
  - 检查是否有遗漏章节（共93个md文件：81章+前言4篇+附录1篇+5个index+2个title=93）
  - 验证"忠于原文"原则：不添加作者原文以外的评论、注解
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-6.1: markdown 文件总数符合预期（93个）✅
  - `human-judgement` TR-6.2: 随机抽取首章、中间章(第40章)、末章，对比 PDF 确认内容完整无遗漏 ✅
- **Verification**: 81章全部通过完整性校验（含帛书版/直译/解读），字数740-3207（平均1503），toctree无孤立文件，.gitignore已创建
