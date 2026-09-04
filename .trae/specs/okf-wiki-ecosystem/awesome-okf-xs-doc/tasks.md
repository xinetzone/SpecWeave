# awesome-okf-xs 文档系统 - 实施计划

## [x] Task 1: 创建 pyproject.toml 文档依赖配置

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在项目根目录创建 `pyproject.toml`
  - 定义项目基本信息（name: awesome-okf-xs，version 从 git 推导或静态指定）
  - 在 `[project.optional-dependencies]` 下定义 `doc` 依赖组，包含：
    - sphinx >= 7.0
    - myst-parser >= 4.0
    - sphinx-book-theme >= 1.0
    - sphinx-design
    - sphinx-copybutton
    - sphinx-tippy
    - sphinx-sitemap
    - sphinxext-opengraph
    - sphinx-contributors
  - 遵循用户偏好：使用 py314 环境，不锁定过严版本
  - 不包含 autoapi（无 Python 源码）、不包含 bibtex（无 .bib 文件）、不包含 myst-nb（无 notebook）
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-1.1: `pip install -e ".[doc]" --dry-run` 无版本冲突
  - `programmatic` TR-1.2: pyproject.toml 是合法 TOML，可被 `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` 解析
- **Notes**: awesome-okf-xs 不是常规 Python 包，pyproject.toml 主要用于依赖管理，不需 build-system

## [x] Task 2: 创建 doc/conf.py Sphinx 配置

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 以 mystx 的 `docs/conf.py` 为模板适配
  - 项目信息：project = "awesome-okf-xs"，author = "xinetzone"
  - 语言：`language = 'zh_CN'`
  - 主题 probe-fallback：mystx → sphinx_book_theme → alabaster
  - 核心扩展：myst_parser
  - 条件扩展（probe-fallback）：sphinx_design、sphinx_copybutton、sphinx_tippy、sphinx_sitemap、sphinxext.opengraph、sphinx_contributors、sphinx.ext.intersphinx、sphinx.ext.extlinks、sphinx.ext.graphviz
  - MyST 扩展配置：dollarmath、amsmath、deflist、colon_fence、replacements、substitution
  - `myst_heading_anchors = 3`（支持标题锚点）
  - `suppress_warnings` 添加：`myst.xref_missing`、`myst.domains`、`ref.ref`、`toc.external`（bundles 跨目录引用容错）
  - intersphinx_mapping 配置 Python/Sphinx/MyST 等外部文档映射
  - html_theme_options：仓库 URL、path_to_docs="doc"、导航深度、中文 toc_title、按钮配置
  - `html_static_path = ["_static"]`，`html_css_files = ["local.css"]`
  - **关键**：在 `setup(app)` 函数中实现 bundles 链接自动创建逻辑：
    - Windows: `os.symlink(target, link, target_is_directory=True)` 失败时 fallback 到 `subprocess.run(['cmd', '/c', 'mklink', '/J', link, target])`
    - Unix: `os.symlink(target, link, target_is_directory=True)`
    - 幂等检查：链接已存在且指向正确目标时跳过
    - 安全检查：如果 `doc/bundles` 已作为普通目录存在（非链接），抛出明确错误
  - `exclude_patterns` 排除 `_build`、`.ipynb_checkpoints` 等
  - 不配置 autoapi（无 src/ 目录）、不配置 bibtex（无 .bib 文件）
  - sitemap 配置：本地环境用 `http://127.0.0.1:8000/`，CI 环境用环境变量
  - ogp 社交卡片配置
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: `python -c "import sys; sys.path.insert(0,'doc'); import conf"` 无导入错误
  - `programmatic` TR-2.2: conf.py 中 setup 函数能正确创建 bundles 链接（Windows junction / Unix symlink）
  - `programmatic` TR-2.3: 重复执行 setup 链接创建不报错（幂等性）
- **Notes**: 路径计算使用 `pathlib.Path`，`ROOT = Path(__file__).resolve().parents[1]` 指向项目根目录

## [x] Task 3: 创建 doc/index.md 首页和 toctree 导航

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `doc/index.md` 作为站点首页
  - 包含欢迎标题和项目简介（从 README.md 提炼）
  - hidden toctree 组织：
    ```markdown
    ` ``{toctree}
    :hidden:
    :caption: 文档

    readme
    ` ``

    ` ``{toctree}
    :hidden:
    :caption: 知识束库
    :maxdepth: 2

    bundles/index
    ` ``
    ```
  - 添加索引和搜索链接区域
  - bundles/index 通过 `doc/bundles` 符号链接解析到 `bundles/index.md`
  - 遵循 OKF frontmatter 规范，添加 `type: Reference` frontmatter
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `human-judgement` TR-3.1: 首页包含项目标题、README 区域、bundles 入口、搜索链接
  - `programmatic` TR-3.2: toctree 中引用的 `bundles/index` 可被 Sphinx 解析（通过符号链接）
- **Notes**: 不要直接复制 README 内容，使用 include 引用

## [x] Task 4: 创建 doc/readme.md 和静态资源

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 创建 `doc/readme.md`，内容为 `{include} ../README.md`（MyST include 指令）
  - 创建 `doc/_static/local.css`，从 mystx 适配响应式样式：
    - 保留核心响应式断点（手机 ≤768px、平板 769-1024px、小屏 ≤480px）
    - 保留代码块横向滚动、长文本换行、链接样式
    - 去除 mystx 特有的 pyscript、myst-example 等无关样式
    - 保留 admonition、表格、图片响应式样式
  - 创建 `doc/_static/.gitkeep`（确保空目录被 git 追踪）
- **Acceptance Criteria Addressed**: AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: readme.md 中的 include 指令在构建时正确解析 README.md
  - `human-judgement` TR-4.2: CSS 在三种屏幕宽度下生效，无水平溢出
- **Notes**: local.css 应精简，只保留 awesome-okf-xs 需要的样式

## [x] Task 5: 更新 .gitignore 排除构建产物和链接

- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 在现有 `.gitignore` 中追加文档构建相关规则：
    - `doc/_build/`（Sphinx 构建输出）
    - `doc/bundles/`（符号链接/联接，自动生成）
    - `doc/api/`（若有自动生成 API 文档）
    - `doc/_static/fonts/`（运行时下载字体，如有）
  - 使用注释标记区域 `# Sphinx documentation (awesome-okf-xs)`
  - 不删除现有 .gitignore 内容
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-5.1: `git status` 不显示 `doc/_build/` 和 `doc/bundles/` 为未跟踪文件
  - `programmatic` TR-5.2: `git check-ignore doc/bundles/` 返回成功
- **Notes**: 现有 .gitignore 已有 `docs/_build/`（复数），需同时保留并添加 `doc/_build/`（单数）

## [x] Task 6: 构建验证和链接完整性测试

- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 安装文档依赖：`pip install -e ".[doc]"`
  - 执行 Sphinx 构建：`sphinx-build -b html doc doc/_build/html`
  - 验证构建输出：
    - `doc/_build/html/index.html` 存在
    - `doc/_build/html/bundles/index.html` 存在（bundles 索引被渲染）
    - 至少 3 个 bundle 分组页面存在（如 bundles/conda/index.html、bundles/sphinx/index.html）
  - 验证 bundles 未被修改：`git status bundles/` 无变更
  - 验证符号链接：`doc/bundles` 存在且指向 `../bundles`
  - 收集并分析构建警告，确认无致命错误
  - 如有关键警告（如断链），修复 conf.py 配置
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: `sphinx-build` 退出码为 0
  - `programmatic` TR-6.2: `doc/_build/html/index.html` 文件存在且大小 > 1KB
  - `programmatic` TR-6.3: `doc/_build/html/bundles/index.html` 文件存在
  - `programmatic` TR-6.4: `git diff --exit-code bundles/` 退出码为 0（bundles 无修改）
  - `programmatic` TR-6.5: `doc/bundles` 是符号链接或 junction，目标解析为 `bundles/`
  - `human-judgement` TR-6.6: 浏览器打开 index.html，导航到 bundles 页面，链接可跳转
- **Notes**: 首次构建可能有较多警告（bundles 中的 OKF frontmatter 未知字段等），通过 suppress_warnings 处理；如果有大量 myst.xref_missing 警告，需确认是否为 bundles 内部链接问题
