---
id: "xuanspace-mono-repo-checklist"
version: "1.4"
x-toml-ref: "../../../.meta/toml/.trae/specs/xuanspace-mono-repo/checklist.toml"
---
# Xuanspace（玄境）Monorepo - Verification Checklist

## Python 版本要求验证
- [ ] 根 pyproject.toml 中 `requires-python = "&gt;=3.13"` 已设置
- [ ] 所有 Python 子项目的 pyproject.toml 中 `requires-python = "&gt;=3.13"` 已设置
- [ ] 在 Python 3.13 环境下 `pdm install` 成功执行
- [ ] 在 Python 3.13 环境下 `pip install -e ".[dev]"` 成功执行（无PDM环境）
- [ ] 在 Python 3.13 环境下 `uv pip install -e ".[dev]"` 成功执行
- [ ] 在 Python 3.12（或更低版本）环境下所有包管理器（pdm/pip/uv）均给出明确的版本不满足错误提示
- [ ] CI（GitHub Actions）配置仅使用 Python 3.13 运行测试
- [ ] CONTRIBUTING.md 中明确说明 Python 3.13+ 要求
- [ ] `xs init` 检查 Python 版本，不满足时给出安装指引
- [ ] `xs py-compat` 能正确验证依赖包的 Python 3.13 兼容性
- [ ] Sphinx 及所有文档扩展兼容 Python 3.13

## 目录结构验证
- [ ] apps/、libs/、vendor/、tools/、docs/、scripts/、attic/ 七个顶层目录全部存在
- [ ] .meta/toml/ 目录存在，用于存放外部 TOML 元数据文件
- [ ] .agents/ 隐藏目录存在，用于 AI 协作规范资产
- [ ] 根目录存在 AGENTS.md 智能体入口文件
- [ ] 根目录存在 README.md 导航文件
- [ ] 根目录存在 CMakePresets.json 跨平台构建预设文件
- [ ] 每个业务顶层目录（apps/libs/vendor/tools/docs/scripts/attic）包含 README.md 说明用途、准入标准和命名规范
- [ ] apps/ README 明确说明纯 HTML/JS 静态项目（如竹简悟道）的放置规则
- [ ] .gitignore 正确配置（Python __pycache__/、.pdm-python、.venv/、build/、*.egg-info/、CMake 构建产物、Node node_modules/、IDE .vscode/.idea、Sphinx _build/ 等）
- [ ] .gitattributes 配置 Git LFS 跟踪规则（*.png、*.jpg、*.pdf、*.whl、*.so、*.pth、*.onnx 等）
- [ ] LICENSE 文件存在（MIT 协议）
- [ ] 目录分类标准清晰：apps=可独立运行/部署（含静态HTML和原生扩展）、libs=可被import复用（含C++扩展库）、tools=开发/构建脚本、vendor=需patch的第三方、attic=归档项目、.meta/toml=外部元数据、.agents=AI协作规范
- [ ] 作为 SpecWeave 子模块时，xuanspace 放置于 projects/xuanspace/（SpecWeave 的 projects/ 目录存放第一方子项目，与 vendor/ 第三方区分）

## 多包管理器兼容验证（不强制PDM）
- [ ] pyproject.toml 严格遵循 PEP 621 标准，不包含 PDM 专属必填字段（[tool.pdm.workspace] 为可选增强）
- [ ] `pdm install` 正确安装所有依赖并链接 workspace 包
- [ ] `pip install -e ".[dev]"` 在无PDM环境中可成功安装
- [ ] `uv pip install -e ".[dev]"` 可成功安装（速度显著快于 pip）
- [ ] libs/ 下的纯Python示例库可被 apps/ 下的示例应用通过 pip 可编辑安装正确 import
- [ ] libs/ 下的纯Python示例库可被 apps/ 下的示例应用通过 uv 正确 import
- [ ] `xs deps check` 在无PDM环境中可通过 pip/uv 正常工作
- [ ] CONTRIBUTING.md 中明确说明三种包管理器的选择和使用方法
- [ ] README.md 快速开始中包含 pip/uv/pdm 三种安装方式
- [ ] `xs doctor` 正确报告可用包管理器及其版本

## CMake + Ninja + scikit-build-core 构建系统验证
- [ ] 示例 C++ 原生扩展项目（libs/xuanspace-native/）存在且使用 scikit-build-core 后端
- [ ] 原生扩展项目 pyproject.toml 中 build-system.requires 包含 `scikit-build-core&gt;=0.10`、`cmake&gt;=3.26`、`ninja`
- [ ] 原生扩展项目 pyproject.toml 中 `[tool.scikit-build]` 正确配置（cmake.build-type、cmake.generator="Ninja"、wheel.packages 等）
- [ ] 原生扩展项目包含 CMakeLists.txt，正确配置 CMake 最低版本（3.26）、项目名、pybind11 绑定
- [ ] 根目录 CMakePresets.json 存在，定义跨平台构建预设（debug/release/release-with-debug）
- [ ] `xs build` 命令可自动检测项目类型（python/native/static）
- [ ] `xs build` 在纯Python项目中调用 `python -m build` 成功构建 wheel
- [ ] `xs build` 在C++原生扩展项目中触发 scikit-build-core + CMake + Ninja 编译，成功构建 wheel
- [ ] 构建日志明确显示使用 Ninja 作为 CMake Generator
- [ ] 构建的 wheel 可通过 `pip install` 安装
- [ ] 安装后的 C++ 扩展可正常 import 并调用 C++ 函数
- [ ] `xs toolchain check` 正确检测 CMake、Ninja 的可用性和版本
- [ ] `xs toolchain install cmake` 和 `xs toolchain install ninja` 可通过 pip 安装对应工具（fallback方案）
- [ ] `xs new --type native &lt;name&gt;` 生成的项目包含正确的 CMakeLists.txt 和 scikit-build-core 配置
- [ ] CMakePresets.json 在 Windows/macOS/Linux 三大平台均能正确加载
- [ ] 编译选项正确配置（Release模式使用 -O2/-O3，Debug模式包含调试符号）
- [ ] docs/build-system.md 文档清晰说明构建系统的使用方法和配置
- [ ] CONTRIBUTING.md 包含 CMake/Ninja 的分平台安装说明（Windows choco/winget、macOS brew、Linux apt）

## C++ 原生扩展项目模板验证
- [ ] tools/templates/native/ 目录存在，包含完整的 C++ 扩展项目模板
- [ ] 模板包含 pyproject.toml（scikit-build-core后端）
- [ ] 模板包含 CMakeLists.txt（pybind11示例、跨平台编译选项）
- [ ] 模板包含 CMakePresets.json
- [ ] 模板包含 src/ 目录结构（C++源码 + Python包初始化）
- [ ] 模板包含 tests/ 目录（pytest测试用例）
- [ ] 模板包含 README.md（构建前置条件说明）
- [ ] 从模板生成的项目可直接 `pip install .` 成功编译

## AGENTS.md 与 .agents/ 规范目录验证
- [ ] 根目录 AGENTS.md 存在且作为 AI 智能体最高优先级入口
- [ ] AGENTS.md 包含完整启动协议（步骤1-4：读取→路由→读规范→自检）
- [ ] AGENTS.md 包含上下文路由表（任务类型→必读规范映射）
- [ ] AGENTS.md 包含核心规范入口表（ONBOARDING、全局规则、角色定义等）
- [ ] AGENTS.md 包含快速开始一句话装载指引
- [ ] AGENTS.md 包含开发规范要点（代码风格、提交规范、路径引用、构建系统约定等）
- [ ] .agents/ 目录存在且包含核心子目录结构
- [ ] .agents/README.md 作为规范目录索引存在
- [ ] .agents/ONBOARDING.md 入门指南存在
- [ ] .agents/global-core-rules.md 全局核心规则存在
- [ ] .agents/context-routing.md 上下文路由表存在
- [ ] .agents/rules/ 核心规则目录存在（内容敏感度预检、阶段守卫等）
- [ ] .agents/templates/ 模板目录存在（复用子项目模板，含纯Python和C++扩展两种）
- [ ] .agents/prompts/ 基础提示词目录存在
- [ ] .agents/protocols/ 核心协议目录存在（工作区发现、提示词自举）
- [ ] AGENTS.md 中所有链接指向 .agents/ 内存在的文件
- [ ] .agents/ 内容适配 xuanspace monorepo 特性，精简实用不冗余

## Sphinx + MyST 文档系统验证
- [ ] docs/ 目录使用 Sphinx 文档生成工具
- [ ] docs/conf.py 配置文件存在且正确
- [ ] docs/conf.py 中启用了 myst_parser 扩展支持 Markdown
- [ ] docs/conf.py 配置了必要扩展：sphinx-book-theme、sphinx-design、sphinx-copybutton、sphinxcontrib-mermaid
- [ ] docs/conf.py 中 source_suffix 支持 .md（markdown）和 .rst（restructuredtext）
- [ ] docs/conf.py 中语言设置为 zh_CN（中文）
- [ ] MyST 扩展已启用：dollarmath、amsmath、deflist、colon_fence、replacements、substitution
- [ ] docs/index.md 存在作为文档首页
- [ ] docs/index.md 通过 MyST `{include}` 指令嵌入根 README.md 内容
- [ ] docs/index.md 配置清晰的 toctree 导航（快速开始、用户指南、构建系统、API参考、贡献指南、架构设计等章节）
- [ ] 根 pyproject.toml 的 `[project.optional-dependencies].docs` 配置了所有 Sphinx 文档依赖（sphinx、myst-parser、sphinx-book-theme、sphinx-design、sphinx-copybutton、sphinxcontrib-mermaid）
- [ ] docs/requirements.txt 不存在（文档依赖统一在 pyproject.toml 中管理）
- [ ] docs/_static/ 静态资源目录存在（CSS、图片等）
- [ ] docs/_templates/ 模板目录存在
- [ ] docs/intro.md 项目介绍存在（玄境品牌、设计哲学）
- [ ] docs/quickstart.md 5分钟快速开始存在（含pdm/uv/pip三种方式）
- [ ] docs/architecture.md 架构设计文档存在（道/法/术/器四层、目录结构、依赖管理、版本管理、子模块策略）
- [ ] docs/build-system.md 构建系统文档存在（pyproject.toml标准、纯Python构建、scikit-build-core+CMake+Ninja、CMakePresets、跨平台注意事项）
- [ ] docs/user-guide/ 用户指南目录存在（子项目管理、依赖更新、版本发布、工具链管理）
- [ ] docs/contributing/ 贡献指南目录存在（含非PDM环境指南、CMake/Ninja安装）
- [ ] docs/adr/ 架构决策记录目录存在
- [ ] `sphinx-build -b html docs/ docs/_build/html/` 成功执行无错误
- [ ] 文档构建无警告（warnings treated as errors）
- [ ] 生成的 HTML 文档样式美观（sphinx-book-theme）、导航正常、搜索功能可用
- [ ] 文档中的代码示例准确可运行（含pdm/uv/pip三种方式示例）
- [ ] 文档中所有链接有效无断链
- [ ] 文档术语一致、风格统一
- [ ] Mermaid 图表在 Sphinx 文档中正确渲染
- [ ] 根 README.md 与 Sphinx 文档首页内容保持同步

## CLI 工具（xs）验证
- [ ] `xs --help` 显示完整帮助信息
- [ ] `xs list` 递归发现所有子项目（含子目录分组）并以表格格式输出
- [ ] `xs list` 能正确区分项目类型：python（pyproject.toml含setuptools/hatch）、native（pyproject.toml含scikit-build-core）、static（含index.html）、other
- [ ] `xs list --json` 输出有效 JSON 格式
- [ ] `xs affected` 基于 git diff 正确检测受影响的子项目（修改lib后能检测到依赖它的app）
- [ ] `xs deps check` 按子项目分组输出过时依赖列表（优先PDM，fallback到uv/pip）
- [ ] `xs deps update --dry-run` 预览变更但不修改任何文件
- [ ] `xs deps update --project &lt;name&gt;` 只更新指定项目
- [ ] `xs deps update --type patch|minor|major` 限制更新类型
- [ ] `xs py-compat` 查询 PyPI 检查依赖包的 Python 3.13 兼容性
- [ ] `xs build` 自动检测项目类型并执行正确构建
- [ ] `xs build --project &lt;name&gt;` 构建指定项目
- [ ] `xs doctor` 输出完整环境诊断报告（Python版本、包管理器可用性、CMake/Ninja/Sphinx版本）
- [ ] `xs toolchain check` 检测所有必需/推荐工具并给出缺失工具的安装建议
- [ ] `xs toolchain install &lt;tool&gt;` 通过 pip 安装 cmake/ninja 等工具
- [ ] `xs init` 跨平台可用（Windows PowerShell / Linux/macOS bash）
- [ ] `xs init` 检查 Python ≥3.13，不满足时给出安装指引
- [ ] `xs init` 检查 Git/Git LFS/CMake/Ninja 是否安装
- [ ] `xs init` 有PDM时执行 pdm install，无PDM时给出 pip/uv 安装指引
- [ ] `xs init` 配置 Git hooks
- [ ] `xs init` 输出清晰的下一步指引
- [ ] `xs version` 正确更新 pyproject.toml 版本号、CHANGELOG、创建 Git tag
- [ ] `xs docs build` 成功构建 Sphinx HTML 文档
- [ ] `xs docs build` 构建无警告和错误
- [ ] `xs docs serve` 启动本地 HTTP 服务器可预览文档
- [ ] `xs docs serve --port` 支持自定义端口
- [ ] `xs docs clean` 成功清理 docs/_build/ 构建产物
- [ ] `xs new --type python|native|static &lt;name&gt;` 从模板创建新项目
- [ ] `xs lfs check` 检测应使用 LFS 但未跟踪的大文件
- [ ] `xs archive &lt;project&gt;` 将项目移动到 attic/ 并更新索引
- [ ] `xs meta init &lt;md-file&gt;` 为新 Markdown 文件正确生成 YAML frontmatter（id/x-toml-ref）和配套 TOML 元数据文件
- [ ] `xs meta init` 自动计算路径深度，x-toml-ref 相对路径正确（根目录→`.meta/toml/`，docs/→`../.meta/toml/`，.agents/rules/→`../../.meta/toml/`，.trae/specs/→`../../../.meta/toml/`）
- [ ] `xs meta check` 检测缺失 id/x-toml-ref 必填字段的 MD 文件
- [ ] `xs meta check` 检测 x-toml-ref 指向不存在的 TOML 文件的情况
- [ ] `xs meta check` 检测 YAML frontmatter 中违规的元数据字段（category/date/tags/summary/changelog 等不应出现在 YAML 中）
- [ ] `xs meta sync` 为缺失 TOML 元数据的 MD 文件自动创建骨架文件
- [ ] `xs meta sync` 不覆盖已存在的 TOML 文件（幂等安全）
- [ ] 所有批量操作脚本是幂等的（重复运行结果一致）
- [ ] 脚本支持子目录分组（递归发现），不硬编码项目列表
- [ ] xs CLI 使用 typer + dataclasses 实现（符合用户偏好）
- [ ] CLI 不强制依赖 PDM，所有核心功能在仅有 pip 的环境中可运行

## 文档元数据二分法（YAML/TOML）验证
- [ ] `.meta/toml/` 目录存在于项目根目录
- [ ] `.meta/toml/` 目录路径镜像 Markdown 文件的项目内路径（如 `.meta/toml/docs/architecture.toml` 对应 `docs/architecture.md`）
- [ ] 根目录 AGENTS.md 使用二分法 frontmatter（含 id/x-toml-ref，x-toml-ref 指向 `.meta/toml/AGENTS.toml`）
- [ ] 根目录 README.md 使用二分法 frontmatter
- [ ] 根目录 CONTRIBUTING.md 使用二分法 frontmatter
- [ ] `.agents/` 下所有 Markdown 文档使用二分法 frontmatter（x-toml-ref 前缀为 `../../.meta/toml/`）
- [ ] `docs/` 下所有 Markdown 文档使用二分法 frontmatter（x-toml-ref 前缀为 `../.meta/toml/`）
- [ ] 子项目 README.md 和 CHANGELOG.md 使用二分法 frontmatter
- [ ] `xs new` 生成的项目模板中，README.md 包含正确的二分法 frontmatter
- [ ] YAML frontmatter 为扁平结构，禁止多行数组缩进和嵌套对象
- [ ] YAML frontmatter 不包含 category、date、tags、summary、changelog、title 等描述性元数据字段（这些仅存在于 TOML）
- [ ] TOML 元数据文件包含必填字段 title 和 category
- [ ] TOML 元数据文件的 version 字段与对应 MD 文件 YAML 中的 version 一致（如均存在）
- [ ] YAML 字段优先于 TOML 同名字段的合并规则正确实现
- [ ] `.agents/rules/` 中包含 frontmatter 元数据规范文档（精简版，适配 xuanspace 项目）
- [ ] `xs meta check` 在全仓库扫描时零错误（所有 Markdown 文件合规）
- [ ] 新增 Markdown 文件时通过 `xs meta init` 自动创建配套 TOML 文件

## 根文档（README/CHANGELOG/CONTRIBUTING）验证
- [ ] 根目录 README.md 包含"玄境"品牌介绍（取自《老子》"玄之又玄，众妙之门"）
- [ ] 根目录 README.md 阐述设计理念（技术为器、思想为道，器以载道）
- [ ] 根目录 README.md 包含 5 分钟快速开始（明确要求 Python 3.13+，包含pdm/uv/pip三种安装方式）
- [ ] 根目录 README.md 包含项目索引表格（名称/描述/语言/类型/状态/版本/文档链接），能同时容纳技术项目、C++扩展项目和文化项目
- [ ] 根目录 README.md 包含 Mermaid 架构图并能正确渲染
- [ ] 根目录 README.md 说明 xuanspace 作为 SpecWeave 子模块的存放位置（projects/xuanspace/）
- [ ] 每个 Python 子项目根目录包含 README.md（含 Python 3.13+ 要求、pdm/uv/pip安装方式、功能/使用/API/维护状态）
- [ ] 每个 C++ 原生扩展子项目根目录包含 README.md（含构建前置条件：CMake≥3.26、Ninja、C++编译器）
- [ ] 每个非 Python 子项目根目录包含适合其类型的 README.md
- [ ] 每个子项目根目录包含 CHANGELOG.md（遵循 Keep a Changelog + SemVer）
- [ ] tools/templates/ 目录下存在纯Python项目模板、C++原生扩展项目模板、非Python项目README模板、CHANGELOG模板
- [ ] CONTRIBUTING.md 包含环境搭建（含Python 3.13安装指引、CMake/Ninja分平台安装）、分支策略、PR流程、Commit规范、新增子项目流程（纯Python/C++扩展/非Python）
- [ ] CONTRIBUTING.md 明确说明三种包管理器的使用方法和选择建议

## Git 子模块集成验证（xuanspace in SpecWeave）
- [ ] 在 SpecWeave 项目中，xuanspace 通过 `git submodule add` 添加到 projects/xuanspace/
- [ ] .gitmodules 文件中 xuanspace 配置正确（path=projects/xuanspace, url=https://github.com/xinetzone/xuanspace.git）
- [ ] `git submodule update --init --recursive` 可正确拉取 xuanspace
- [ ] 在 SpecWeave 的 AGENTS.md 中记录了子模块位置和更新策略（projects/ 存放第一方子项目，vendor/ 存放第三方依赖）
- [ ] 子模块指向 main 分支或特定 tag（非游离状态）
- [ ] `git submodule update --remote projects/xuanspace/` 可正确更新子模块到最新版本
- [ ] 在 SpecWeave 中可正常引用和运行 xuanspace 的 CLI 工具（xs）
- [ ] 子模块更新后，SpecWeave 提交记录清晰显示子模块指针变更

## 依赖与版本管理验证
- [ ] 依赖版本有单一真相源（根目录 constraints 或各项目独立但一致）
- [ ] vendor/ 目录仅在需要 patch 第三方库时使用，默认通过包管理器引入
- [ ] 版本发布脚本创建 Git tag 格式为 `&lt;project&gt;@&lt;version&gt;`
- [ ] 版本发布脚本能自动更新 CHANGELOG 和版本号
- [ ] 新引入依赖前可通过 `xs py-compat` 预检 Python 3.13 兼容性
- [ ] C++ 扩展项目的依赖（pybind11等）通过 CMake FetchContent 或系统包管理器管理

## Git LFS 与大文件验证
- [ ] Git LFS 已初始化（`git lfs install` 已执行）
- [ ] 二进制文件和编译产物（*.so、*.pyd、*.whl、*.dll）被 LFS 正确跟踪或被 .gitignore 排除
- [ ] 二进制文件被 LFS 正确跟踪（可通过 `git lfs ls-files` 验证）
- [ ] CONTRIBUTING.md 中说明了 LFS 使用策略和不应提交的文件类型

## 跨平台构建一致性验证
- [ ] CMakePresets.json 中配置条件预设，正确处理 Windows/MSVC、macOS/clang、Linux/GCC 的编译选项差异
- [ ] 路径处理全部使用 pathlib（Python）或 CMake 内置路径函数，无硬编码路径分隔符
- [ ] Shell 命令在 Windows（PowerShell）和 Unix-like（bash）环境下均可执行
- [ ] CMake 配置中正确设置 CMAKE_CXX_STANDARD（17 或更高）
- [ ] Ninja 作为首选 Generator 在所有平台可用（pip install ninja 作为 fallback）
- [ ] 编译输出目录结构统一（build/ 目录，或 scikit-build-core 默认目录）

## CI/CD 跨平台验证
- [ ] GitHub Actions CI 配置存在（.github/workflows/ci.yml）
- [ ] CI 使用跨平台矩阵：ubuntu-latest、windows-latest、macos-latest
- [ ] CI 矩阵包含三种包管理器：pdm、pip、uv
- [ ] CI 使用 Python 3.13 作为唯一测试版本
- [ ] CI 步骤包含 CMake 和 Ninja 的安装（分平台：apt/brew/choco 或 pip install）
- [ ] CI 步骤包含 C++ 编译器安装（Linux: gcc/g++, macOS: 自带clang, Windows: VS Build Tools）
- [ ] CI 步骤包含 submodule 递归拉取
- [ ] CI 中 `xs toolchain check` 验证工具链完整性
- [ ] CI 仅运行受影响项目的测试（通过 `xs affected` 检测）
- [ ] CI 包含构建验证步骤（对原生扩展项目执行 `xs build`，验证 wheel 生成和 import）
- [ ] CI 包含文档构建步骤（`xs docs build`），文档构建失败则 CI 失败
- [ ] CI 使用 `fail-fast: false` 确保所有平台问题一次暴露
- [ ] CI 在三大平台上 C++ 原生扩展均能成功编译和 import

## 初始化与贡献流程验证
- [ ] 新成员 clone 后可通过 `xs init` 完成环境配置（无论是否安装PDM）
- [ ] Python 3.13 环境下从零到运行示例应用的完整流程可在 10 分钟内完成
- [ ] 初始化脚本输出清晰的下一步指引
- [ ] Git pre-commit hooks 运行基础检查（末尾换行、无冲突标记、大文件检查等）
- [ ] CONTRIBUTING.md 中 Conventional Commits 规范说明清晰
- [ ] 新增纯 Python 子项目流程文档化
- [ ] 新增 C++ 原生扩展子项目流程文档化
- [ ] 新增非Python（HTML/JS等）子项目流程文档化

## 可扩展性验证
- [ ] 在 libs/ 下创建子目录（如 libs/python/、libs/native/、libs/ai/）后，`xs list` 仍能正确发现项目
- [ ] 在 apps/ 下创建子目录分组（如 apps/culture/ 放竹简悟道类项目、apps/cli/ 放命令行工具）后，脚本正常工作
- [ ] 依赖图构建支持子目录嵌套
- [ ] 架构文档包含新增语言支持的扩展指南（Rust扩展、Fortran扩展等）
- [ ] 架构文档包含添加非Python项目的指南
- [ ] 构建系统可扩展支持其他构建后端（meson-python、flit等）

## 归档机制验证
- [ ] `xs archive &lt;project&gt;` 将项目移动到 attic/ 目录
- [ ] 归档操作更新根 README 项目索引（标记为已归档）
- [ ] 归档后的子项目 README 有明确的归档标记
- [ ] 归档操作可逆（文档说明如何反归档）

## 端到端流程验证
- [ ] Python 3.13 环境下从零开始（全新clone）到运行示例应用的完整流程顺畅无阻塞（分别用PDM、pip、uv验证）
- [ ] 新增一个纯 Python 子项目的完整流程（创建目录→配置pyproject.toml→写README→pip install -e验证import）顺畅
- [ ] 新增一个 C++ 原生扩展子项目的完整流程（xs new --type native→配置→xs build→pip install→import调用C++函数）顺畅
- [ ] 新增一个静态 HTML 子项目（模拟竹简悟道）的流程顺畅
- [ ] 无PDM环境（仅pip）下所有核心功能（安装、依赖检查、构建、测试、文档）正常
- [ ] CMake+Ninja+scikit-build-core 构建链在本地环境成功编译C++扩展
- [ ] 构建产物 wheel 可安装并正常import
- [ ] `xs docs build` 构建文档顺畅无错误
- [ ] `xs docs serve` 本地预览文档可正常访问
- [ ] AGENTS.md 可被 AI 智能体正确读取和执行路由
- [ ] xuanspace 作为 SpecWeave 的 git submodule 正常工作（拉取、更新、使用）
- [ ] 所有高优先级验收标准（AC-1 至 AC-8, AC-10, AC-13 至 AC-16, AC-18, AC-20 至 AC-25）通过程序化验证
- [ ] 所有 human-judgment 验收标准（AC-3, AC-4, AC-9, AC-11, AC-17, AC-19, AC-26, AC-27）经人工审核通过
- [ ] "玄境"品牌气质与竹简悟道等文化项目协调（不违和、不突兀）
- [ ] 文档描述与实际脚本行为一致（含构建系统和非PDM环境）
- [ ] Sphinx 文档内容质量符合技术文档规范（目录、导航、代码示例、说明文字完整）
- [ ] 无硬编码路径或个人环境特定配置
- [ ] 在 Python &lt; 3.13 环境下所有入口点（init、install、build、CI、docs build）均有明确错误提示而非静默失败
- [ ] CMakePresets.json 在三大平台（或至少当前开发平台）行为正确