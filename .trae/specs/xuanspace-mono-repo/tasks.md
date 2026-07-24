---
id: "xuanspace-mono-repo-tasks"
version: "1.5"
x-toml-ref: "../../../.meta/toml/.trae/specs/xuanspace-mono-repo/tasks.toml"
---

# Xuanspace（玄境）Monorepo - The Implementation Plan (Decomposed and Prioritized Task List)

## \[x] Task 1: 初始化仓库与基础目录结构

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 GitHub 创建 xuanspace 仓库（初期作为 SpecWeave 的 git submodule 放置于 projects/xuanspace/）
  - 在 SpecWeave 中执行 `git submodule add` 将 xuanspace 添加到 projects/xuanspace/
  - 创建顶层目录：apps/、libs/、vendor/、tools/、docs/、scripts/、attic/、.agents/
  - 创建基础配置文件：.gitignore、.gitattributes（Git LFS 配置）、LICENSE（MIT）、AGENTS.md（框架文件）、README.md（框架文件）、CMakePresets.json（跨平台构建预设）
  - 初始化标准 PEP 621 pyproject.toml，配置 `requires-python = "&gt;=3.13"`、build-system（支持纯Python和原生扩展两种后端）
  - PDM workspace 配置（packages 字段指向 apps/*/ 和 libs/*/）作为推荐管理方式
  - 添加 dev 依赖组：pdm（推荐但可选）、build（PEP 517构建前端）、scikit-build-core、cmake、ninja、sphinx 文档相关依赖
  - 在 SpecWeave 的 AGENTS.md/路由文档中记录子模块位置和更新策略
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-26
- **Test Requirements**:
  - `programmatic` TR-1.1: 所有顶层目录存在（含 .agents/）
  - `programmatic` TR-1.2: AGENTS.md 和 README.md 框架文件存在
  - `programmatic` TR-1.3: .gitignore 包含 Python/Node/IDE/Sphinx/\_build/CMake 等常见忽略项
  - `programmatic` TR-1.4: .gitattributes 配置 Git LFS 跟踪规则
  - `programmatic` TR-1.5: pyproject.toml 中 `requires-python = "&gt;=3.13"` 已设置
  - `programmatic` TR-1.6: build、scikit-build-core、cmake、ninja、Sphinx 相关依赖已添加到 dev 依赖组
  - `programmatic` TR-1.7: 在 Python 3.13 环境下 `pdm install` 和 `pip install -e .` 均可无错误执行
  - `programmatic` TR-1.8: CMakePresets.json 存在且包含 debug/release 标准预设
  - `programmatic` TR-1.9: xuanspace 作为 git submodule 正确注册于 projects/xuanspace/
- **Notes**: PDM 为推荐 workspace 工具但不强制；pyproject.toml 必须符合 PEP 621 标准，确保 pip/uv 均可直接使用；CMake+Ninja+scikit-build-core 仅用于有 C/C++ 扩展的子项目；.agents/ 是隐藏目录用于 AI 协作规范资产

## \[x] Task 2: 编写各顶层目录 README 与分类标准

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 为 apps/、libs/、vendor/、tools/、docs/、scripts/、attic/ 各编写 README.md
  - 明确每个目录的准入标准（什么类型的项目放这里）
  - 特别说明：纯 HTML/JS 静态项目（如竹简悟道）直接放入 apps/ 或 apps/culture/，无需 PDM 管理
  - 提供目录内项目命名规范
- **Acceptance Criteria Addressed**: AC-1, AC-11
- **Test Requirements**:
  - `human-judgement` TR-2.1: apps/ vs libs/ vs tools/ 的区别清晰无歧义
  - `human-judgement` TR-2.2: vendor/ 的使用条件明确（仅 patch 场景）
  - `human-judgement` TR-2.3: attic/ 归档流程说明清楚
  - `human-judgement` TR-2.4: 非 Python 项目（HTML/JS等）的放置规则明确

## \[x] Task 3: 配置 pyproject.toml、Python 3.13 与多类型示例子项目

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 完整配置 pyproject.toml，确保符合 PEP 621 标准（不绑定 PDM 专属字段）
  - 配置严格 Python 版本检查（所有包管理器均应尊重 requires-python）
  - 在 libs/ 下创建一个示例纯 Python 库项目（如 `xuanspace-utils`），使用 setuptools 后端，设置 `requires-python = "&gt;=3.13"`
  - 在 libs/ 下创建一个示例 C++ 原生扩展库项目（如 `xuanspace-native`），使用 scikit-build-core 后端 + CMake + Ninja，包含 pybind11 绑定示例
  - 在 apps/ 下创建一个示例 Python 应用项目，依赖示例库，设置 `requires-python = "&gt;=3.13"`
  - 在 apps/ 下放置一个简单的静态 HTML 示例（模拟竹简悟道类型项目）
  - 验证三种安装方式：`pdm install`（workspace自动链接）、`pip install -e .`（可编辑安装）、`uv pip install -e .`（快速安装）
  - 验证 Python 版本不满足时所有包管理器均给出明确错误
  - 为示例原生扩展项目创建 CMakeLists.txt 和 CMakePresets.json
- **Acceptance Criteria Addressed**: AC-2, AC-20, AC-21, AC-22
- **Test Requirements**:
  - `programmatic` TR-3.1: 示例纯Python库可被示例应用通过 pip/pdm/uv 三种方式正确 import
  - `programmatic` TR-3.2: 修改示例库代码后，应用无需重新安装即可看到变更（可编辑安装）
  - `programmatic` TR-3.3: `pdm list` 显示 workspace 包
  - `programmatic` TR-3.4: 在 Python 3.12 环境下所有包管理器给出明确版本错误提示
  - `programmatic` TR-3.5: 静态 HTML 项目存在且不干扰 Python 构建
  - `programmatic` TR-3.6: C++ 原生扩展通过 pip install 成功编译安装，import 后可调用 C++ 函数
  - `programmatic` TR-3.7: C++ 扩展构建使用 Ninja 生成器（通过 cmake.args 配置）
  - `programmatic` TR-3.8: `uv pip install -e .` 安装速度显著快于 pip（验证 uv 兼容）
- **Notes**: 纯 Python 项目使用 setuptools 后端以获得最大兼容性；原生扩展使用 scikit-build-core；CMakePresets.json 定义跨平台构建预设

## \[x] Task 4: 创建子项目文档与代码模板

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建纯 Python 子项目 README.md 模板（功能介绍、安装（要求Python 3.13+，支持pip/uv/pdm三种方式）、快速使用、API 概览、维护状态徽章）
  - 创建 C/C++ 原生扩展项目 README.md 模板（包含构建前置条件：CMake≥3.26、Ninja、C++编译器）
  - 创建静态/非Python项目 README.md 模板
  - 创建子项目 CHANGELOG.md 模板（遵循 Keep a Changelog 格式）
  - 创建纯 Python 项目代码模板（pyproject.toml + src/布局 + tests/）
  - 创建 C++ 原生扩展项目代码模板（pyproject.toml with scikit-build-core + CMakeLists.txt + CMakePresets.json + src/ + pybind11示例）
  - 在 tools/templates/ 目录下放置所有模板文件
  - 提供 `xs new --type python|native|static &lt;name&gt;` 命令从模板创建新项目
- **Acceptance Criteria Addressed**: AC-3, AC-25
- **Test Requirements**:
  - `human-judgement` TR-4.1: README 模板包含必要章节（含Python版本要求和多包管理器安装说明）
  - `human-judgement` TR-4.2: CHANGELOG 模板符合语义化版本规范
  - `programmatic` TR-4.3: 模板文件存在于正确位置
  - `programmatic` TR-4.4: `xs new --type python` 生成的项目可直接 `pip install -e .` 安装
  - `programmatic` TR-4.5: `xs new --type native` 生成的项目可通过 `pip install .` 成功编译（需CMake+Ninja环境）
  - `programmatic` TR-4.6: 生成的原生项目包含正确的 CMakeLists.txt 和 CMakePresets.json

## \[x] Task 5: 编写根目录 README 导航（玄境品牌）

- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 编写根目录 README.md，包含：
    - "玄境"品牌介绍：取自《老子》"玄之又玄，众妙之门"，是技术与文化项目共存的空间
    - 设计理念：技术为器、思想为道，器以载道
    - 5 分钟快速开始（环境要求Python 3.13+ → clone → xs init → 运行示例）
    - 项目索引表格（名称、描述、语言、类型、状态、版本、文档链接）
    - Mermaid 架构图（道/法/术/器四层结构或目录结构图）
    - 贡献指南入口链接
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-5.1: 快速开始步骤可在 5 分钟内完成（Python 3.13环境下）
  - `human-judgement` TR-5.2: 项目索引表格清晰易读，技术项目和文化项目均能涵盖
  - `human-judgement` TR-5.3: Mermaid 架构图正确渲染
  - `human-judgement` TR-5.4: "玄境"品牌阐述与竹简悟道等文化项目气质协调

## \[x] Task 6: 编写 CONTRIBUTING.md 贡献指南

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 环境搭建步骤（Git、Python 3.13 安装指引）
  - **包管理器选择说明**：PDM（推荐，workspace支持）、uv（快速替代）、pip（标准方式）三种安装方式
  - **构建工具链安装**：CMake≥3.26、Ninja 的分平台安装说明（Windows: choco/winget; macOS: brew; Linux: apt; 或 pip install cmake ninja fallback）
  - 分支策略（main 为保护分支，feature/bugfix/docs 分支命名）
  - 开发工作流（fork/branch → 开发 → 测试 → PR → review）
  - Commit message 规范（Conventional Commits）
  - 代码规范与 lint 配置
  - 新增子项目的流程（区分纯Python项目、C++原生扩展项目、非Python项目）
  - Python 3.13 兼容性要求说明
  - 跨平台开发注意事项（Windows/macOS/Linux 路径差异、CMake预设使用）
- **Acceptance Criteria Addressed**: AC-9, AC-27
- **Test Requirements**:
  - `human-judgement` TR-6.1: 新贡献者可按指南完成第一次 PR（无论是否安装PDM）
  - `human-judgement` TR-6.2: Commit message 规范与 Conventional Commits 一致
  - `human-judgement` TR-6.3: 新增子项目流程明确（纯Python vs C++扩展 vs 非Python）
  - `human-judgement` TR-6.4: CMake/Ninja 分平台安装说明清晰可操作
  - `human-judgement` TR-6.5: 三种包管理器（pdm/uv/pip）的使用方法均有说明

## \[x] Task 7: 开发 xs CLI 核心框架、项目发现与构建命令

- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**:
  - 使用 Python + typer + dataclasses 开发 CLI 工具 `xs`（xuanspace 缩写）
  - 工具包放在 tools/xs/ 目录，在根 pyproject.toml 中配置为 dev 依赖
  - 子命令 `xs --help` / `xs list`：
    - 递归发现 apps/、libs/ 下所有子项目（支持子目录分组）
    - 自动检测项目类型（python: pyproject.toml含setuptools/hatch; native: pyproject.toml含scikit-build-core; static: 含index.html; other）
    - 支持 --json 和 --table 输出格式
  - 子命令 `xs affected`：基于 `git diff` 检测受影响的子项目
    - 解析 pyproject.toml 依赖关系构建依赖图
    - 输出需要构建/测试的子项目列表
  - 子命令 `xs build`：
    - 自动检测项目类型
    - 纯Python项目：调用 `python -m build`
    - C++原生扩展：调用 `pip install .` 或 `python -m build` 触发 scikit-build-core
    - 支持在指定子项目目录运行或通过 `--project` 指定
  - 子命令 `xs doctor`：环境诊断（Python版本、pdm/uv/pip可用性、cmake/ninja版本、sphinx版本）
  - 子命令 `xs toolchain`：工具链管理
    - `xs toolchain check`：检测所有必需/推荐工具
    - `xs toolchain install &lt;tool&gt;`：通过 pip 安装 cmake/ninja 等（fallback方案）
  - 子命令 `xs new`：从模板创建新项目（--type python/native/static）
- **Acceptance Criteria Addressed**: AC-8, AC-10, AC-12, AC-13, AC-24, AC-25
- **Test Requirements**:
  - `programmatic` TR-7.1: `xs --help` 显示完整帮助信息
  - `programmatic` TR-7.2: `xs list` 正确列出所有示例子项目（含静态HTML和C++扩展项目）并正确识别类型
  - `programmatic` TR-7.3: `xs list --json` 输出有效 JSON
  - `programmatic` TR-7.4: 修改 libs 下的代码后，`xs affected` 正确检测到依赖它的 apps
  - `programmatic` TR-7.5: 支持子目录分组（递归发现）
  - `programmatic` TR-7.6: `xs build` 在纯Python项目中成功构建 wheel
  - `programmatic` TR-7.7: `xs build` 在C++扩展项目中成功触发 CMake+Ninja 编译
  - `programmatic` TR-7.8: `xs doctor` 输出完整环境诊断报告
  - `programmatic` TR-7.9: `xs toolchain check` 正确报告缺失工具
  - `programmatic` TR-7.10: `xs new --type python/native` 正确从模板生成项目
- **Notes**: 依赖图分析可使用简单的拓扑排序；Python版本检查集成到CLI中；构建命令不依赖PDM，直接调用标准PEP 517接口

## \[x] Task 8: 开发依赖检查、Python 3.13 兼容性与更新脚本

- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 在 `xs` CLI 中添加子命令：
    - `xs deps check`：检查所有 Python 子项目的过时依赖，按项目分组输出（优先使用 pdm list/uv pip list，fallback 到 pip list + importlib.metadata）
    - `xs deps update`：批量更新依赖
      - 支持 `--dry-run` 预览变更
      - 支持 `--project &lt;name&gt;` 只更新指定项目
      - 支持 `--type &lt;major/minor/patch&gt;` 限制更新类型
      - PDM 环境调用 `pdm update`，非 PDM 环境给出 `pip install --upgrade` 手动指引（pyproject.toml 为单一真相源，不生成 requirements.txt）
    - `xs py-compat`：检查依赖包与 Python 3.13 的兼容性
      - 通过查询 PyPI JSON API 检查包的 `requires-python` 元数据
      - 标记不兼容或未声明 3.13 支持的包
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: `xs deps check` 输出过时依赖列表
  - `programmatic` TR-8.2: `xs deps update --dry-run` 不修改任何文件
  - `programmatic` TR-8.3: `xs deps update --project <name>` 只更新指定项目
  - `programmatic` TR-8.4: 更新脚本是幂等的（重复运行结果一致）
  - `programmatic` TR-8.5: `xs py-compat` 能正确识别包的Python版本要求
  - `programmatic` TR-8.6: 未安装PDM时，`xs deps check` 可通过uv/pip正常工作
- **Notes**: dry-run 通过显示将要执行的命令实现；py-compat 可作为添加新依赖前的预检；脚本不强制要求PDM

## \[x] Task 9: 开发初始化与诊断脚本

- **Priority**: medium
- **Depends On**: Task 1, Task 3, Task 7
- **Description**:
  - 统一用 Python 实现 `xs init` 和 `xs doctor` 子命令（跨平台）
  - `xs init` 功能：
    - 检查 Python ≥ 3.13（不满足则给出安装指引）
    - 检查 Git、Git LFS 是否安装
    - 检查 CMake、Ninja（仅当存在 native 项目时必需，否则推荐安装）
    - 检测可用包管理器（PDM/uv/pip），PDM 存在则执行 `pdm install`，否则给出 `pip install -e .` 或 `uv pip install -e .` 指引
    - 安装 Git hooks（pre-commit 运行基础检查）
    - 打印下一步指引（查看README、浏览项目、运行示例）
  - `xs doctor` 功能（已在 Task 7 中定义框架，此处完善诊断逻辑）：
    - 报告 Python 版本和路径
    - 报告各包管理器可用性和版本
    - 报告 CMake/Ninja/Sphinx 等工具版本
    - 给出缺失工具的安装建议
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-9.1: 在 Python 3.13 环境中运行 xs init，有PDM时自动安装依赖，无PDM时给出pip/uv安装指引
  - `programmatic` TR-9.2: 在 Python < 3.13 环境中给出明确的版本错误和安装指引
  - `programmatic` TR-9.3: Git LFS 已正确安装和初始化
  - `programmatic` TR-9.4: `xs doctor` 输出结构化诊断报告
  - `human-judgement` TR-9.5: 脚本输出的下一步指引清晰
- **Notes**: init 不强制安装任何包管理器，仅检测和推荐

## \[x] Task 10: 版本管理脚本

- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**:
  - 实现 `xs version` 子命令辅助版本管理
  - 功能：
    - 引导用户输入新版本号或自动计算（bump major/minor/patch）
    - 更新子项目 pyproject.toml 中的 version 字段
    - 在子项目 CHANGELOG.md 中添加版本条目（带日期）
    - 创建 Git tag（格式 `&lt;project&gt;@&lt;version&gt;`）
  - 创建首个版本示例
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-10.1: `xs version` 正确更新 pyproject.toml 版本号
  - `programmatic` TR-10.2: CHANGELOG 添加版本条目
  - `programmatic` TR-10.3: Git tag 格式正确为 `&lt;project&gt;@&lt;version&gt;`
- **Notes**: 初期不引入 Changesets（Node.js 工具），先用 Python 脚本实现轻量版本管理；待子项目增多后可考虑迁移

## \[x] Task 11: 配置 Sphinx + MyST 文档系统

- **Priority**: high
- **Depends On**: Task 1, Task 5
- **Description**:
  - 配置 docs/ 目录的 Sphinx 项目结构
  - 创建 docs/conf.py：配置 myst\_parser、sphinx-book-theme、sphinx-design、sphinx-copybutton、sphinxcontrib-mermaid 等扩展；设置中文语言；配置 MyST 扩展（dollarmath、amsmath、deflist、colon\_fence 等）
  - 创建 docs/index.md：文档首页，通过 MyST include 嵌入根 README.md 内容，配置清晰的 toctree 导航（快速开始、用户指南、API 参考、贡献指南、架构设计等）
  - 在根 pyproject.toml 的 `[project.optional-dependencies].docs` 中配置 Sphinx 文档依赖（不使用独立的 docs/requirements.txt）
  - 创建 docs/\_static/ 目录（CSS、图片等静态资源）和 docs/\_templates/ 目录
  - 创建 docs/tasks.py（invoke 任务脚本，用于构建文档）
  - 验证文档可成功构建为 HTML
- **Acceptance Criteria Addressed**: AC-16, AC-17
- **Test Requirements**:
  - `programmatic` TR-11.1: docs/conf.py 正确配置所有必要扩展和 MyST 选项
  - `programmatic` TR-11.2: `sphinx-build -b html docs/ docs/_build/html/` 成功执行无错误
  - `programmatic` TR-11.3: docs/index.md 的 toctree 结构清晰
  - `programmatic` TR-11.4: MyST include 指令正确嵌入根 README.md
  - `human-judgement` TR-11.5: 生成的 HTML 文档样式美观、导航正常
  - `programmatic` TR-11.6: 所有 Sphinx 扩展兼容 Python 3.13
- **Notes**: 参考 SpecWeave 项目的 docs/conf.py 配置；文档主题使用 sphinx-book-theme

## \[x] Task 12: 编写 AGENTS.md 智能体入口文件

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 编写根目录 AGENTS.md，作为 AI 智能体协作的最高优先级路由
  - 包含启动协议（步骤1-4：读取本文件→上下文路由表→读取规范→自检）
  - 包含上下文路由表（任务类型→必读规范映射）
  - 包含核心规范入口表（ONBOARDING、全局规则、上下文路由、能力注册、角色定义等）
  - 包含快速开始一句话装载指引
  - 包含开发规范要点（代码风格、提交规范、文档边界、路径引用等）
  - 内容与 xuanspace monorepo 项目特性匹配，不是简单复制 SpecWeave
- **Acceptance Criteria Addressed**: AC-14
- **Test Requirements**:
  - `human-judgement` TR-12.1: 启动协议步骤清晰完整
  - `human-judgement` TR-12.2: 上下文路由表覆盖主要任务类型
  - `human-judgement` TR-12.3: 核心规范入口表链接有效
  - `human-judgement` TR-12.4: 内容与 xuanspace 项目特性匹配
  - `human-judgement` TR-12.5: 一句话装载指引可操作

## \[x] Task 13: 创建 .agents/ 规范目录核心结构

- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 在 .agents/ 目录下创建核心规范子目录和文件
  - 创建 .agents/README.md 作为规范目录索引
  - 创建必要的核心模块（精简版，适配 monorepo 项目，不复制 SpecWeave 全部内容）：
    - .agents/ONBOARDING.md（入门指南）
    - .agents/global-core-rules.md（全局核心规则）
    - .agents/context-routing.md（上下文路由表）
    - .agents/rules/（核心规则：内容敏感度预检、阶段守卫、AI编码准则等）
    - .agents/templates/（模板：子项目README模板、CHANGELOG模板等，复用 Task 4 的模板）
    - .agents/prompts/（基础提示词）
    - .agents/protocols/（核心协议：工作区发现、提示词自举）
  - 确保 AGENTS.md 中的链接指向正确的 .agents/ 内文件
  - 内容需适配 xuanspace monorepo 的实际需求，保持精简实用
- **Acceptance Criteria Addressed**: AC-15
- **Test Requirements**:
  - `programmatic` TR-13.1: .agents/ 目录下核心文件存在
  - `programmatic` TR-13.2: AGENTS.md 中所有链接指向存在的文件
  - `human-judgement` TR-13.3: 内容精简适配 monorepo 项目，不冗余
  - `human-judgement` TR-13.4: 规范内容可操作，不是空架子
- **Notes**: .agents/ 目录是隐藏目录；初始版本保持最小可用集，后续按需扩展

## \[x] Task 14: 开发 xs docs 文档命令

- **Priority**: medium
- **Depends On**: Task 7, Task 11
- **Description**:
  - 在 xs CLI 中添加文档相关子命令：
    - `xs docs build`：调用 sphinx-build 构建 HTML 文档到 docs/\_build/html/
    - `xs docs serve`：构建文档并启动本地 HTTP 服务器预览（默认端口 8000）
    - `xs docs clean`：清理 docs/\_build/ 目录
  - 检查 Sphinx 依赖是否安装，未安装时给出安装指引
  - 支持 `--port` 参数指定预览端口
- **Acceptance Criteria Addressed**: AC-18
- **Test Requirements**:
  - `programmatic` TR-14.1: `xs docs build` 成功构建 HTML 文档
  - `programmatic` TR-14.2: `xs docs build` 构建无警告和错误
  - `programmatic` TR-14.3: `xs docs serve` 启动本地服务器可访问文档
  - `programmatic` TR-14.4: `xs docs clean` 成功清理构建产物
  - `programmatic` TR-14.5: Sphinx 未安装时给出明确安装指引
- **Notes**: 可使用 Python 的 http.server 模块实现预览服务器；invoke 可作为备选方案但 xs 命令为主入口

## \[x] Task 15: 编写架构与贡献文档（Sphinx 格式）

- **Priority**: medium
- **Depends On**: Task 11, Task 6
- **Description**:
  - 在 docs/ 下创建完整的文档章节（MyST Markdown 格式）：
    - docs/intro.md：项目介绍（玄境品牌、设计哲学）
    - docs/quickstart.md：5 分钟快速开始（包含pdm/uv/pip三种安装方式）
    - docs/architecture.md：架构设计（目录结构、道/法/术/器四层、依赖管理、版本管理、子模块策略）
    - docs/build-system.md：构建系统文档（pyproject.toml标准、纯Python构建、scikit-build-core+CMake+Ninja原生扩展构建、CMakePresets使用、跨平台注意事项）
    - docs/user-guide/：用户指南（子项目管理、依赖更新、版本发布、工具链管理）
    - docs/contributing/：贡献指南（复用并扩展 CONTRIBUTING.md 内容，包含非PDM环境指南、CMake/Ninja安装）
    - docs/adr/：架构决策记录目录
  - 确保文档包含代码示例、导航链接、清晰的说明文字
  - 更新 docs/index.md 的 toctree 包含所有章节
  - 所有代码示例必须可运行
- **Acceptance Criteria Addressed**: AC-17, AC-19, AC-27
- **Test Requirements**:
  - `human-judgement` TR-15.1: 文档结构清晰，导航完整
  - `human-judgement` TR-15.2: 代码示例准确可运行（含pdm/uv/pip三种方式示例）
  - `programmatic` TR-15.3: 所有文档链接有效无断链
  - `human-judgement` TR-15.4: 文档术语一致、风格统一
  - `programmatic` TR-15.5: 文档构建无警告
  - `human-judgement` TR-15.6: 构建系统文档清晰说明CMake/Ninja/scikit-build-core的使用
- **Notes**: 架构文档中需包含"玄境"命名溯源与《老子》哲学理念的阐述；构建系统文档需包含三种包管理器对比和选择建议

## \[x] Task 16: 添加跨平台 GitHub Actions CI

- **Priority**: low
- **Depends On**: Task 3, Task 7, Task 11
- **Description**:
  - 创建 .github/workflows/ci.yml
  - 触发条件：push 和 pull request
  - **跨平台矩阵**：
    - OS: ubuntu-latest, windows-latest, macos-latest
    - Python: 3.13（严格唯一）
    - 包管理器: pdm, pip, uv（三种方式均需验证）
  - 步骤：
    1. checkout（含 submodule 递归拉取）
    2. 安装 Python 3.13
    3. **安装 CMake + Ninja**（分平台：Linux apt, macOS brew, Windows choco/winget 或 pip install cmake ninja）
    4. 安装选定包管理器（pdm/uv，pip 预装）
    5. 安装依赖（pdm install / pip install -e ".\[dev]" / uv pip install -e ".\[dev]"）
    6. `xs toolchain check` 验证工具链
    7. 使用 `xs affected` 确定受影响项目并运行测试
    8. **构建验证**：对原生扩展项目执行 `xs build`，验证 wheel 生成
    9. 使用 `xs docs build` 验证文档构建
    10. `xs doctor` 输出环境诊断（调试用）
  - 配置 Python 3.13 为唯一测试版本（初期严格要求）
  - 对 native 扩展项目，验证 wheel 可在同平台安装和 import
- **Acceptance Criteria Addressed**: NFR-1, NFR-6, NFR-7, NFR-8, AC-23, AC-27
- **Test Requirements**:
  - `programmatic` TR-16.1: PR 提交时 CI 在 Windows/macOS/Linux × Python 3.13 三大平台均通过
  - `programmatic` TR-16.2: CI 在三种包管理器（pdm/pip/uv）下均能正确安装和测试
  - `programmatic` TR-16.3: 仅测试受影响项目，而非全量
  - `programmatic` TR-16.4: Python 版本不是 3.13 时 CI 配置明确拒绝
  - `programmatic` TR-16.5: CI 中文档构建步骤成功
  - `programmatic` TR-16.6: CMake + Ninja 在三大平台均正确安装和调用
  - `programmatic` TR-16.7: C++ 原生扩展在三大平台均能成功编译和 import
  - `programmatic` TR-16.8: `xs toolchain check` 在所有平台通过
  - `programmatic` TR-16.9: submodule 递归拉取正确（xuanspace 在 SpecWeave 中的子模块场景）
- **Notes**: CI matrix 可能较慢，可使用 `fail-fast: false` 确保所有平台问题一次暴露；native 项目构建需确保 C++ 编译器可用（Linux: gcc/g++, macOS: clang, Windows: MSVC via VS Build Tools）

## \[x] Task 17: Git LFS 与大文件策略

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 配置 .gitattributes 跟踪常见二进制格式（\*.png, \*.jpg, \*.pdf, \*.whl, \*.so, \*.pth, \*.onnx 等）
  - 在 CONTRIBUTING.md 中说明何时使用 LFS、何时不应提交大文件
  - 提供 `xs lfs check` 检查是否有应使用 LFS 但未跟踪的大文件
- **Acceptance Criteria Addressed**: FR-14
- **Test Requirements**:
  - `programmatic` TR-17.1: 二进制文件被 LFS 正确跟踪
  - `human-judgement` TR-17.2: LFS 使用说明清晰
  - `programmatic` TR-17.3: `xs lfs check` 能检测到未跟踪的大文件

## \[x] Task 18: 创建项目归档脚本

- **Priority**: low
- **Depends On**: Task 7
- **Description**:
  - `xs archive <project>` 子命令
  - 功能：将子项目从 apps/ 或 libs/ 移动到 attic/、更新根 README 项目索引、在子项目 README 添加归档标记
- **Acceptance Criteria Addressed**: FR-15
- **Test Requirements**:
  - `programmatic` TR-18.1: 归档后项目移动到 attic/
  - `programmatic` TR-18.2: 根目录 README 索引更新
  - `programmatic` TR-18.3: 归档操作可逆（提供反归档说明）

## \[x] Task 19: 端到端验证与修复

- **Priority**: high
- **Depends On**: Task 1-18 中所有 high 任务完成
- **Description**:
  - 在 Python 3.13 环境中模拟新成员从 clone 到运行示例的完整流程，**分别使用 PDM、pip、uv 三种包管理器验证**
  - 模拟添加一个新纯 Python 子项目的完整流程
  - 模拟添加一个 C++ 原生扩展子项目的完整流程（验证 CMake+Ninja+scikit-build-core 构建链）
  - 模拟添加一个静态 HTML 子项目（类似竹简悟道）的流程
  - 在无PDM环境中验证安装、依赖检查、构建等功能正常
  - 验证 CMakePresets.json 在三大平台上的行为一致性
  - 验证 AGENTS.md 可被 AI 智能体正确读取和路由
  - 验证 Sphinx 文档可正常构建、预览和搜索
  - **子模块验证**：将 xuanspace 作为 git submodule 添加到 SpecWeave 的 projects/xuanspace/，验证：
    - `git submodule update --init --recursive` 正确拉取
    - 在 SpecWeave 中可正常引用和运行 xuanspace 的 CLI 工具
    - 更新子模块指针的工作流正常
  - 记录所有发现的问题并修复
  - 更新文档中不准确的步骤
- **Acceptance Criteria Addressed**: AC-1 至 AC-27
- **Test Requirements**:
  - `human-judgement` TR-19.1: Python 3.13 环境下完整流程无阻塞点（三种包管理器均验证）
  - `programmatic` TR-19.2: 所有高优先级验收标准通过
  - `human-judgement` TR-19.3: 文档与实际脚本行为一致
  - `programmatic` TR-19.4: 在 Python < 3.13 环境中所有检查点均有明确错误提示
  - `programmatic` TR-19.5: Sphinx 文档构建无错误无警告
  - `human-judgement` TR-19.6: AGENTS.md 路由逻辑清晰可执行
  - `programmatic` TR-19.7: 未安装PDM时，pip/uv安装和运行流程完全正常
  - `programmatic` TR-19.8: C++ 原生扩展项目从创建到编译到import全流程成功
  - `programmatic` TR-19.9: CMake+Ninja 构建日志确认使用 Ninja 生成器
  - `programmatic` TR-19.10: xuanspace 作为 SpecWeave 的 git submodule 正常工作（拉取、更新、使用）
  - `programmatic` TR-19.11: `xs build` 在纯Python和C++项目中均正确构建
  - `programmatic` TR-19.12: 构建产物 wheel 可安装并正常import

## \[x] Task 20: 文档元数据二分法规范与 xs meta 命令

- **Priority**: medium
- **Depends On**: Task 7, Task 13
- **Description**:
  - 在项目根目录创建 `.meta/toml/` 目录结构，用于存放外部 TOML 元数据文件
  - 在 `.agents/rules/` 中添加 frontmatter 元数据规范文档（参考 SpecWeave 的 frontmatter-metadata-standard 规则，但适配 xuanspace 精简版）
  - 在 `xs` CLI 中添加 `xs meta` 子命令组：
    - `xs meta init <md-file>`：为指定 Markdown 文件自动生成 YAML frontmatter（id/x-toml-ref）并创建配套的 TOML 元数据文件骨架（自动计算路径深度和镜像路径，预填 title/category 字段）
    - `xs meta check [path]`：验证指定目录（默认全仓库）下所有 Markdown 文件的 frontmatter 合规性：检查必填字段（id/x-toml-ref）、检查 TOML 引用文件是否存在、检查禁止字段（YAML 中不应有 category/date/tags 等元数据）、检查路径计算正确性
    - `xs meta sync`：扫描所有 Markdown 文件，自动补全缺失的 TOML 元数据文件骨架（不覆盖已有内容）
  - 更新 Task 4 的项目模板（纯Python、C++原生扩展、静态项目），确保新生成的 README.md 包含正确的 YAML/TOML 二分法 frontmatter
  - 更新 Task 12 的 AGENTS.md 和 Task 13 的 .agents/ 规范文档，确保它们自身也遵循二分法格式
  - 初始化时为根目录 AGENTS.md、README.md、CONTRIBUTING.md 自动生成配套 TOML 元数据文件
- **Acceptance Criteria Addressed**: FR-35
- **Test Requirements**:
  - `programmatic` TR-20.1: `.meta/toml/` 目录结构存在
  - `programmatic` TR-20.2: `xs meta init` 为新 MD 文件正确生成 YAML frontmatter 和 TOML 文件，路径深度计算正确
  - `programmatic` TR-20.3: `xs meta check` 能检测到缺失 x-toml-ref 的 MD 文件
  - `programmatic` TR-20.4: `xs meta check` 能检测到 TOML 引用不存在的情况
  - `programmatic` TR-20.5: `xs meta check` 能检测到 YAML 中违规的元数据字段
  - `programmatic` TR-20.6: `xs meta sync` 不覆盖已存在的 TOML 文件
  - `human-judgement` TR-20.7: frontmatter 规范文档清晰说明二分法的使用方法
  - `programmatic` TR-20.8: 项目模板生成的 README.md 包含正确的二分法 frontmatter
  - `programmatic` TR-20.9: 根目录 AGENTS.md/README.md/CONTRIBUTING.md 均有配套 TOML 元数据文件
- **Notes**: `xs meta` 命令不依赖 PDM；TOML 文件使用 Python 标准库 tomllib/tomli-w 读写；路径计算使用 pathlib 确保跨平台兼容

