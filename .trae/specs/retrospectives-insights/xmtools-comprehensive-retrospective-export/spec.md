# xmtools 全面复盘 + whl 打包 + Docker 镜像导出 Spec

## Why

`external/chaos/xmtools/` 是 XMNN NPU 推理工具包的 Python wheel 构建系统（scikit-build-core + CMake + Nuitka + Ninja），当前处于 `1.2.1-dev0` 开发状态。项目已具备完整的构建链路（Docker 一键构建、Nuitka 编译、CMake 打包、8~9 项验证）与运行时镜像（`xmnn:1.2.1-alpha`、`xmnn-runtime:1.2.2`、`xmnn-serve:1.2.1-alpha` 等），但尚未从"方法论"高度对代码结构、功能模块、潜在问题与性能优化进行系统性复盘，也未产出可归档的复盘报告与可复用的模式沉淀。同时，已有 wheel（`dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`，约 185MB）与 Docker 镜像存在体积偏大、配置一致性待验证、缺少生产级导出物等问题。

## What Changes

- 对 `xmtools` 项目执行**七概念方法论**全面复盘（R 事实采集 → I 洞察 → E 模式萃取 → V 对抗审查 → A 行动项 → C 原子提交），产出结构化复盘报告（事实清单、洞察、模式、行动项）
- 产出复盘报告归档至 SpecWeave `.agents/docs/retrospective/reports/task-reports/` 下（含 README / insight-extraction / actionable-items 三件套）
- 基于复盘发现，**修复构建/打包缺陷**（如数据目录一致性、依赖声明、RPATH 校验、Dockerfile 配置等）
- 重新打包 xmnn 为符合 Python 标准的 whl 安装包（含所有必要依赖与元数据），并执行 11 项完整验证
- 构建并导出**生产级 Docker 镜像**（配置正确、体积优化、可直接部署），提供 `docker save` 导出物

## Impact

- Affected specs: 无（新建任务）
- Affected code:
  - `external/chaos/xmtools/pyproject.toml`
  - `external/chaos/xmtools/CMakeLists.txt`
  - `external/chaos/xmtools/tasks.py`
  - `external/chaos/xmtools/docker/**`（dev-llvm22 / runtime / serve / Dockerfile）
  - `external/chaos/xmtools/scripts/verify_wheel.py`
  - `external/chaos/xmtools/.agents/**`（项目级规则，若需同步）
- 产出物：
  - 复盘报告（`.agents/docs/retrospective/reports/task-reports/retrospective-xmtools-20260803/`）
  - 新 wheel（`dist/xmnn-*.whl`）
  - 生产级 Docker 镜像导出 tar（`dist/xmnn-production-*.tar`）

## ADDED Requirements

### Requirement: 全面复盘分析
系统 SHALL 对 xmtools 项目执行代码结构审查、功能模块评估、潜在问题识别、性能优化建议四维复盘，并产出结构化复盘报告。

#### Scenario: 代码结构审查
- **WHEN** 审查 `pyproject.toml`、`CMakeLists.txt`、`tasks.py`、`docker/**`、`scripts/**`、`sdk/**` 的结构与职责
- **THEN** 报告按模块评估职责边界、耦合度、可维护性、是否符合 project 本地规则（scikit-build-core 构建、Python>=3.14、Nuitka 编译、bootstrap 注入）

#### Scenario: 功能模块评估
- **WHEN** 评估 wheel 构建、Nuitka 编译、CMake 打包、验证、Docker 构建/运行时/服务共 6 大功能模块
- **THEN** 报告给出每个模块的功能完整性、实现质量、已知缺陷与改进建议

#### Scenario: 潜在问题识别
- **WHEN** 识别构建/运行/部署中的潜在问题
- **THEN** 报告按 P0/P1/P2 分级列出问题，并给出根因与修复建议

#### Scenario: 性能优化建议
- **WHEN** 分析镜像体积、wheel 体积、构建耗时、运行时加载
- **THEN** 报告给出可量化的优化建议（如分层清理、基础镜像裁剪、依赖瘦身、构建缓存）

### Requirement: 复盘报告归档
系统 SHALL 将复盘报告按三件套格式归档到 SpecWeave 标准复盘报告目录。

#### Scenario: 归档三件套
- **WHEN** 复盘完成
- **THEN** 在 `.agents/docs/retrospective/reports/task-reports/retrospective-xmtools-20260803/` 生成 `README.md`（主报告）、`insight-extraction.md`（洞察萃取）、`actionable-items.md`（行动项）
- **THEN** 洞察萃取含 ≥3 个方法论模式，每个含反模式、边界条件、可迁移性验证
- **THEN** 行动项含优先级、Owner、验收标准

### Requirement: 基于复盘修复构建缺陷
系统 SHALL 基于复盘发现的问题，修复构建/打包缺陷，确保 wheel 与镜像配置正确。

#### Scenario: 修复缺陷
- **WHEN** 复盘发现数据目录缺失、依赖声明错误、RPATH 缺失、Dockerfile 配置不一致等问题
- **THEN** 修复对应文件，并确保不破坏既有成功构建链路

### Requirement: 打包标准 whl
系统 SHALL 打包 xmnn 为符合 Python 标准的 whl 安装包，包含所有必要依赖与元数据。

#### Scenario: 打包成功
- **WHEN** 执行打包（`python -m build --wheel --no-isolation` 或 `inv build-all`）
- **THEN** 生成 `dist/xmnn-<version>-cp314-cp314-linux_x86_64.whl`
- **THEN** wheel 包含 `_libs/`（libtvm.so + 依赖）、`tvm.cpython-*.so`、`vta.cpython-*.so`、`xmnn.cpython-*.so`、bootstrap 文件、数据目录（autolibs/tools_cpp/fonts）、`tvm/relay/std`、`vta_hw/config`

#### Scenario: 11 项验证
- **WHEN** 对新 wheel 执行 `scripts/verify_wheel.py` 或 `inv verify`
- **THEN** 全部验证项通过（import tvm/vta/xmnn、_libs 目录、libtvm.so 加载、tvm.build(llvm)、relay/std、vta_hw/config、bootstrap.pth、数据目录、依赖完整性）

### Requirement: 构建并导出生产级 Docker 镜像
系统 SHALL 构建配置正确、体积优化、可直接用于生产环境的 Docker 镜像，并导出为可移植的 tar 文件。

#### Scenario: 构建镜像
- **WHEN** 执行镜像构建
- **THEN** 基于 `ubuntu:26.04` 独立构建，配置北外 conda-forge 镜像 + 清华 pip 镜像，时区 Asia/Shanghai，空 ENTRYPOINT，预装 xmnn wheel
- **THEN** 镜像内 `import tvm/vta/xmnn` 与 `tvm.build` 冒烟测试通过

#### Scenario: 导出镜像
- **WHEN** 镜像构建成功
- **THEN** 执行 `docker save` 导出为 `dist/xmnn-production-*.tar`
- **THEN** 导出 tar 可被 `docker load` 还原并正常运行

## MODIFIED Requirements

无

## REMOVED Requirements

无