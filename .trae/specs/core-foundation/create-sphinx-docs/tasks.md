# SpecWeave Sphinx 文档站点创建 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建 docs 目录结构骨架
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `d:\spaces\SpecWeave\docs\` 下创建完整的目录结构
  - 需要创建的目录：`_static/`、`_static/images/`、`tech/`、`general/`、`topics/`、`_templates/`
  - 参考 `vendor/flexloop/docs/` 的目录组织方式
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 使用 Glob 或 LS 验证 `docs/_static/`、`docs/_static/images/`、`docs/tech/`、`docs/general/`、`docs/topics/`、`docs/_templates/` 目录均存在
  - `human-judgement` TR-1.2: 目录结构与参考模板 `vendor/flexloop/docs/` 的核心子目录一致（不含 general/ 下的 philosophy/cosmology 等内容子目录）
- **Notes**: `_templates/` 目录可以为空，仅需存在即可

## [x] Task 2: 复制并适配静态资源文件 (_static/)
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 从 `vendor/flexloop/docs/_static/` 复制 CSS 文件到 `docs/_static/`：
    - `local.css`（响应式样式）
    - `variables.css`（CSS 变量定义）
    - `mermaid.css`（Mermaid 图表样式）
  - 复制或创建 favicon 和 logo 图片：
    - 优先从 `assets/brand/` 复用 xuantong-logo.png 作为 logo
    - 创建简单的 favicon（复用 logo 图片）
  - 不复制 `switcher.json`（版本切换暂不需要）
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1: 验证 `docs/_static/local.css`、`docs/_static/variables.css`、`docs/_static/mermaid.css` 文件存在
  - `programmatic` TR-2.2: 验证 `docs/_static/images/` 目录下存在 favicon 和 logo 文件（至少各一个图片文件）
  - `human-judgement` TR-2.3: CSS 文件内容完整，没有截断
- **Notes**: CSS 文件直接从 flexloop 复制无需修改

## [x] Task 3: 创建 conf.py Sphinx 核心配置
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 `vendor/flexloop/docs/conf.py` 创建适配 SpecWeave 的配置文件
  - 已完成的关键修改：
    - 项目信息：project = "SpecWeave"，author = "SpecWeave Team"，copyright = "2026, SpecWeave Team"
    - release/version = "1.0.0"
    - 语言：language = "zh_CN"
    - 扩展列表智能检测：core_exts + optional_exts（自动检测是否安装）
    - 移除 AutoAPI 和 BibTeX 配置
    - ROOT 路径正确指向项目根目录
    - 从 _config.toml 加载 html_theme_options
    - Windows 事件循环兼容（hasattr 检查）
    - 主题 fallback 链：sphinx_book_theme → sphinx_rtd_theme → alabaster
    - 额外修复：exclude_patterns 添加 `.venv` 以排除虚拟环境
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-9
- **Test Requirements**:
  - `programmatic` TR-3.1: `python -m py_compile docs/conf.py` 无语法错误
  - `programmatic` TR-3.2: conf.py 中 project == "SpecWeave"、author 包含 "SpecWeave"、language == "zh_CN"
  - `programmatic` TR-3.3: conf.py 中不包含 "autoapi" 字符串
  - `programmatic` TR-3.4: Windows SelectorEventLoopPolicy 处理存在
  - `human-judgement` TR-3.5: 扩展列表合理，myst 配置正确

## [x] Task 4: 创建 _config.toml 主题配置
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 `vendor/flexloop/docs/_config.toml` 创建 SpecWeave 版本
  - 已完成的关键修改：
    - logo 配置指向 `_static/images/logo.png`
    - repository_url = "https://gitcode.com/daoCollective/SpecWeave"
    - 额外修复：添加 repository_provider = "gitlab" 以支持 GitCode
    - 移除 launch_buttons section（binder/colab等）
    - icon_links 设为空列表
    - toc_title = "目录"，导航深度配置保留
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: TOML 格式有效（tomllib 加载成功）
  - `programmatic` TR-4.2: repository_url 包含 "SpecWeave"
  - `programmatic` TR-4.3: 不包含 "binderhub_url" 或 "colab_url"
  - `human-judgement` TR-4.4: 主题选项配置合理

## [x] Task 5: 创建 tasks.py Invoke 构建脚本
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 从 `vendor/flexloop/docs/tasks.py` 复制并适配
  - 包含 help、build、html、clean、linkcheck、doctest 任务
  - Windows 兼容性已保留（shlex.split posix 参数）
- **Acceptance Criteria Addressed**: AC-2, AC-10
- **Test Requirements**:
  - `programmatic` TR-5.1: `python -m py_compile docs/tasks.py` 无语法错误
  - `programmatic` TR-5.2: 包含 @task 装饰的函数：help、build、html、clean、linkcheck
  - `human-judgement` TR-5.3: 脚本逻辑完整

## [x] Task 6: 创建根入口 index.md
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `docs/index.md` 作为文档站点首页
  - 使用 `{include}` 指令引用根目录 `README.md`（end-before 标记）
  - 添加 `# 📚 文档导航` 标题
  - toctree 引用 tech/index、general/index、topics/index
  - 添加"重点阅读"部分和索引引用
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-6.1: `docs/index.md` 文件存在
  - `programmatic` TR-6.2: 包含 toctree 指令且引用三个子入口
  - `programmatic` TR-6.3: README.md 中存在 `<!-- end-doc-include -->` 标记
  - `human-judgement` TR-6.4: 首页结构清晰

## [x] Task 7: 创建 tech/index.md 技术文档入口
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `docs/tech/index.md`
  - 标题：`# 📦 技术文档`
  - toctree 列出 intro、quickstart、features、contributing、changelog
  - 目录清单表格、边界说明、接入约定
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在
  - `programmatic` TR-7.2: toctree 引用 5 个初始文档
  - `human-judgement` TR-7.3: 内容说明清晰

## [x] Task 8: 创建 tech/ 目录初始占位文档
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 创建 5 个初始 Markdown 文档：intro.md、quickstart.md、features.md、contributing.md、changelog.md
  - 每个文档有一级标题、简介、基本骨架
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 5 个文件都存在
  - `programmatic` TR-8.2: 每个文件有一级标题
  - `human-judgement` TR-8.3: 文档内容与标题相符

## [x] Task 9: 创建 general/index.md 通用知识入口
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 创建 `docs/general/index.md`
  - 标题：`# 🌐 通用知识`
  - 初始 toctree 为空，说明计划承载内容
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件存在
  - `human-judgement` TR-9.2: 说明文字清晰

## [x] Task 10: 创建 topics/index.md 设计洞见入口
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 创建 `docs/topics/index.md`
  - 标题：`# 🔬 设计洞见与深度研究`
  - 初始 toctree 为空
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件存在
  - `human-judgement` TR-10.2: 内容定位清晰

## [x] Task 11: 在 README.md 中添加文档截断标记
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 在 README.md 第171行添加 `<!-- end-doc-include -->` 标记
  - 位置在"## 文档导航"章节之前
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-11.1: README.md 中包含 `<!-- end-doc-include -->` 字符串
  - `human-judgement` TR-11.2: 标记位置合理

## [x] Task 12: 验证 Sphinx 配置解析能力
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10
- **Description**:
  - 使用虚拟环境安装所有依赖（阿里云镜像源）
  - conf.py 加载成功，project/author/language 配置正确
  - 首次构建发现 .venv 目录被扫描问题，已修复（添加到 exclude_patterns）
  - 首次构建发现 GitCode 需要 repository_provider 配置，已修复
- **Acceptance Criteria Addressed**: AC-7, AC-9
- **Test Requirements**:
  - `programmatic` TR-12.1: conf.py 可被 Python 导入，无致命错误
  - `programmatic` TR-12.2: sphinx-build 返回码为 0
  - `human-judgement` TR-12.3: 无 Configuration error 类致命错误

## [x] Task 13: 构建 HTML 并验证输出
- **Priority**: medium
- **Depends On**: Task 12
- **Description**:
  - 创建 docs/.venv 虚拟环境
  - 使用阿里云镜像安装所有依赖
  - 成功执行 sphinx-build，exit code 0
  - index.html 大小 56KB，所有子页面正常生成
  - 添加 docs/_build/ 到 .gitignore
  - 本地预览服务器启动在 http://localhost:8765/
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-13.1: docs/_build/html/index.html 存在，大小 56KB > 1KB
  - `programmatic` TR-13.2: tech/ 下 6 个 HTML 文件均正常生成
  - `human-judgement` TR-13.3: HTML 页面标题包含 "SpecWeave"
  - `human-judgement` TR-13.4: 页面可在浏览器中正常渲染

## [x] Task 14: 最终一致性检查
- **Priority**: medium
- **Depends On**: Task 13
- **Description**:
  - vendor/flexloop/ 目录无变更
  - .gitignore 已添加 docs/_build/
  - 所有 Markdown 和 Python 文件使用 UTF-8 编码
  - 整体结构与参考模板风格一致
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-14.1: vendor 目录无变更
  - `programmatic` TR-14.2: .gitignore 已包含 docs/_build/
  - `human-judgement` TR-14.3: 整体结构与参考模板风格一致
