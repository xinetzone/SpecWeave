# JupyterLab Extension Template - 架构洞察（Insights）

> I阶段产出。基于 facts.md 中 177 条事实提炼核心洞察和知识地图。

## 核心洞察（四元组）

### 洞察 I-001：这是代码生成器模板，不是运行时库

- **陈述**：extension-template 本质是一个 Copier 模板引擎项目，通过 Jinja2 条件渲染在用户本地生成完整的 JupyterLab 扩展项目骨架。它没有可导入的运行时 API，所有"代码"都是 .jinja 模板。
- **证据**：F-001~F-010（copier.yml 配置、README 中 copier copy 命令）、F-009（所有核心文件均为 .jinja 后缀模板）
- **反常识**：初学者可能以为这是一个需要 import 的 JupyterLab 开发库，实际上 `pip install copier` 后执行 `copier copy` 就会在本地生成一个独立的、可直接开发的扩展项目。模板本身不需要在开发时被引用。
- **行动**：文档组织必须先讲"如何用模板生成项目"，再讲生成后的项目结构。不能把它当作传统库来写 API 参考，而是要写"模板参数参考"和"生成的项目结构解释"。

### 洞察 I-002：四种扩展类型通过 Jinja2 条件块在同一模板中差异化输出

- **陈述**：frontend、mimerenderer、frontend-and-server、theme 四种扩展类型不是四个独立模板，而是共享同一套文件结构，通过 `{% if kind == ... %}` / `{% if has_settings %}` 等条件块控制哪些代码段被渲染。
- **证据**：F-011（kind 参数四选一）、F-053（package.json dependencies 按 kind 条件分支）、F-081~F-097（index.ts.jinja 用 if/else 分支出完全不同的插件定义）、F-107~F-115（Python 代码仅在 frontend-and-server 时包含 routes）
- **反常识**：四种类型看起来差异很大（纯前端 vs 前后端 vs MIME渲染器 vs 主题），但模板复用率极高——package.json、pyproject.toml、tsconfig.json、CI 工作流等基础文件是同一套模板，只在依赖项、入口代码、配置节处有条件差异。理解条件渲染逻辑比逐文件阅读更重要。
- **行动**：概念文档需要一张"条件渲染矩阵表"，清晰标注每个模板文件中哪些条件块对应哪种扩展类型，帮助读者快速定位自己需要关注的代码段。

### 洞察 I-003：双包分发架构（NPM + Python）是核心设计

- **陈述**：JupyterLab 扩展采用"双包"分发模式——前端代码是 NPM 包（编译为 JS），但通过 Python 包（pip install）分发到 JupyterLab 环境。hatchling + jupyter-builder + hatch-nodejs-version 三个工具协同实现版本同步和构建集成。
- **证据**：F-061~F-080（pyproject.toml 中 hatch-nodejs-version 从 package.json 读取版本、hatch-jupyter-builder 在构建时调用 npm）、F-072（wheel shared-data 将 labextension 映射到 JupyterLab 的 share 目录）、F-046~F-051（npm scripts 中 build:labextension 调用 jupyter-builder）
- **反常识**：即使是纯前端扩展（不需要 Python 后端），也必须有 Python 包——因为 JupyterLab 的扩展发现机制基于 Python 包入口点（`_jupyter_labextension_paths()`）。NPM 包不直接安装到 JupyterLab，而是被打包进 Python wheel 的 `share/jupyter/labextensions/` 目录。这导致初学者常犯的错误是"只运行 jlpm build 不 pip install"。
- **行动**：必须有专门概念讲解双包架构和构建流程，明确区分"编译"（tsc → JS）和"安装"（pip install -e . + jupyter-builder develop）两个步骤。

### 洞察 I-004：模板预置了完整的工程化工具链和质量门禁

- **陈述**：模板不仅生成扩展代码，还预置了完整的前端工程化配置（TypeScript strict模式、ESLint 9.x flat config、Stylelint、Prettier、Jest）、后端测试（pytest + pytest-jupyter）、集成测试（Playwright + Galata）、CI/CD（GitHub Actions 多job流水线）、发布（Jupyter Releaser + PyPI + npm）。
- **证据**：F-128（eslint.config.mjs.jinja 使用 ESLint 9 flat config）、F-122（tsconfig strict + strictNullChecks）、F-141~F-151（Jest + pytest + Playwright 三套测试配置）、F-156~F-167（GitHub Actions 包含 build、test_isolated、integration-tests、check_links、check-release 五个job）
- **反常识**：模板默认开启 test（F-021: default yes），生成的项目开箱即用包含单元测试、集成测试和CI流水线。很多开发者以为模板只是个"Hello World"骨架，实际上它已经是一个符合 JupyterLab 社区标准的可发布项目模板。
- **行动**：概念文档需要覆盖测试策略和CI流水线，帮助开发者理解每个工具的作用，而不是把配置当作"黑箱"忽略。

### 洞察 I-005：可选的 AGENTS.md 体现了 AI 辅助开发的新趋势

- **陈述**：模板提供可选的 `has_ai_rules` 参数（F-022），开启后生成 AGENTS.md 文件（F-177），包含详细的 JupyterLab 扩展开发编码规范、外部文档优先级指引、前后端集成工作流、常见陷阱等。还支持自动创建 CLAUDE.md 和 GEMINI.md 符号链接（F-031~F-033）。
- **证据**：F-022~F-024（has_ai_rules/create_claude_symlink/create_gemini_symlink 参数）、F-032~F-033（copier _tasks 自动创建符号链接）、F-177（AGENTS.md.jinja 长达925行，包含编码规范、开发工作流、最佳实践、常见陷阱）
- **反常识**：这是传统项目模板中罕见的设计——模板不仅生成代码和构建配置，还为 AI 编程助手（Cursor/Copilot/Claude Code/Gemini）生成上下文规则文件。这反映了 2025-2026 年软件开发中"AI 结对编程"成为主流的趋势。
- **行动**：文档应包含 AI 规则文件的介绍，说明其作用和如何自定义，这是该模板区别于旧版 cookiecutter 模板的重要新特性。

## 知识地图

### 文档分组与学习路径

```
入门组（零基础必读）
├── 00-introduction.md          → 什么是 JupyterLab Extension Template
├── 01-getting-started.md       → 安装 copier、生成第一个扩展、项目运行
└── 02-copier-basics.md         → Copier 模板引擎基础、参数详解、更新机制

核心组（理解架构）
├── 03-four-extension-types.md  → 四种扩展类型对比与选型指南
├── 04-project-structure.md     → 生成后项目目录结构与文件职责
├── 05-build-system.md          → 双包构建系统（hatchling + jupyter-builder + tsc）
├── 06-frontend-extension.md    → 前端扩展开发（JupyterFrontEndPlugin、activate 生命周期）
├── 07-server-extension.md      → 服务端扩展开发（APIHandler、路由注册、认证）
├── 08-mime-renderer.md         → MIME 渲染器开发（IRenderMime、OutputWidget、安全模型）
├── 09-theme-extension.md       → 主题扩展开发（CSS 变量、IThemeManager、明暗模式）
└── 10-settings-schema.md       → 设置系统（schema/plugin.json、ISettingRegistry）

高级组（生产级开发）
├── 11-testing-strategy.md      → 三层测试策略（Jest + pytest + Playwright/Galata）
├── 12-ci-cd-workflows.md       → GitHub Actions CI/CD 流水线解析
├── 13-packaging-release.md     → 打包与发布（PyPI + npm + Jupyter Releaser）
└── 14-ai-coding-rules.md       → AGENTS.md AI 编码规范与工具链集成

示例组（动手实践）
├── basic-frontend.md           → 最小前端扩展示例
├── basic-server-extension.md   → 前后端扩展示例（含 API 通信）
├── basic-mime-renderer.md      → MIME 渲染器示例
├── basic-theme.md              → 主题扩展示例
└── custom-settings.md          → 带用户设置的扩展示例

信源组（事实溯源）
├── copier-config.md            → copier.yml 参数全参考
├── package-json-source.md      → package.json 模板字段解析
├── pyproject-source.md         → pyproject.toml 模板字段解析
├── frontend-entry-source.md    → src/index.ts 模板条件渲染解析
├── server-routes-source.md     → Python 后端 routes.py 与 __init__.py 解析
└── ci-workflows-source.md      → GitHub Actions 工作流解析
```

### 学习路径建议

1. **快速体验**：00 → 01 → 运行生成的项目 → 04（看结构）
2. **前端开发**：02 → 03 → 06 → 05 → 10 → examples/basic-frontend → 11
3. **全栈开发**：完成前端路径 → 07 → examples/basic-server-extension → 12 → 13
4. **MIME/主题**：02 → 03 → 08/09 → 对应示例
5. **发布开源**：核心组全部 → 12 → 13 → 14

### 概念文档覆盖的事实编号

| 文档 | 覆盖事实 |
|------|---------|
| 00-introduction | F-001~F-010 |
| 01-getting-started | F-004~F-007, F-011~F-030（核心参数） |
| 02-copier-basics | F-001~F-003, F-011~F-033 |
| 03-four-extension-types | F-011, F-053, F-056, F-081~F-097, F-107~F-115 |
| 04-project-structure | F-009, F-041~F-045, F-061~F-062, F-121~F-135 |
| 05-build-system | F-046~F-051, F-069~F-080, F-122 |
| 06-frontend-extension | F-081~F-088, F-041~F-052 |
| 07-server-extension | F-101~F-115 |
| 08-mime-renderer | F-089~F-097 |
| 09-theme-extension | F-082, F-086, F-130~F-133 |
| 10-settings-schema | F-017, F-043, F-056, F-083, F-087, F-126 |
| 11-testing-strategy | F-021, F-052, F-068, F-141~F-151 |
| 12-ci-cd-workflows | F-156~F-167 |
| 13-packaging-release | F-061~F-080, F-174 |
| 14-ai-coding-rules | F-022~F-024, F-031~F-033, F-177 |
