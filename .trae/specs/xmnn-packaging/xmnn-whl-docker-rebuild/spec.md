---
version: "1.0"
source: "seven-concepts-cmd | sc-20260722-xmnn-rebuild"
---

# XMNN 从零构建 Whl + 导出 Docker 镜像 Spec

## Why

tvm、vta、xmnn 源码已更新，需要从零开始重新构建 xmnn whl 安装包，并导出完整的 Docker 客户端镜像，确保最新的源码更新内容包含在产物中，版本号正确反映此次更新。

## What Changes

- 从零执行 Nuitka 编译（TVM + VTA + XMNN）→ Wheel 打包 → Docker 客户端镜像构建全链路
- 版本号同步：`pyproject.toml` 当前为 `1.2.2-alpha`，`Containerfile` 中标签为 `1.2.1`，需统一为正式版本号
- 导出 Docker 镜像为 `tar.gz` 并生成 SHA256 校验文件
- 构建全程基于 `d:\spaces\SpecWeave\external\xmhub\xmnn` 目录，所有依赖和构建脚本均从该目录获取

## Impact

- Affected specs: 无（新 spec）
- Affected code: `packaging/pyproject.toml`（版本号确认）、`client/Containerfile`（版本标签同步）、`scripts/full_build.py`（构建入口）
- Build environment: 需要 Docker + `nuitka-gcc-llvm:latest` 基础镜像

## ADDED Requirements

### Requirement: 版本号统一

系统 SHALL 在构建前确认并统一所有版本号引用，确保 `pyproject.toml` 的 `version` 字段与 `client/Containerfile` 的 `LABEL version` 和镜像 tag 一致。

#### Scenario: 版本号一致
- **WHEN** 构建前检查版本号
- **THEN** `pyproject.toml` 中 `version = "1.2.2-alpha"` 与 `Containerfile` 中 `LABEL version="1.2.2-alpha"` 和 `docker build -t xmnn-client:1.2.2-alpha` 一致

#### Scenario: 版本号不一致时自动修复
- **WHEN** 检测到版本号不一致
- **THEN** 以 `pyproject.toml` 为准，更新 `Containerfile` 中的版本标签和 `full_build.py` 中的默认 `--image-tag`

### Requirement: 从零构建 Whl

系统 SHALL 通过 `full_build.py` 执行完整的 Nuitka 编译 + Wheel 打包流水线，使用 `--force` 标志强制重新编译所有组件。

#### Scenario: 完整构建成功
- **WHEN** 在 WSL/Linux 环境中执行 `python xmnn/scripts/full_build.py --force`
- **THEN** Nuitka 编译阶段成功生成 tvm/vta/xmnn 三个 `.so` 文件
- **AND** Wheel 打包阶段在 `packaging/dist/` 输出 `xmnn-1.2.2a0-cp314-cp314-linux_x86_64.whl`（或对应版本号的 wheel 文件）

#### Scenario: 构建失败时终止
- **WHEN** Nuitka 编译或 Wheel 打包任一步骤失败
- **THEN** 构建流水线终止，输出错误信息，不继续后续步骤

### Requirement: 构建客户端 Docker 镜像

系统 SHALL 在 wheel 打包成功后，通过 `client/Containerfile` 构建客户端 Docker 镜像。

#### Scenario: 客户端镜像构建成功
- **WHEN** wheel 文件已存在于 `client/.temp/` 目录
- **THEN** `docker build` 成功生成 `xmnn-client:1.2.2-alpha` 镜像
- **AND** 镜像内验证通过：`import tvm`, `import vta`, `import xmnn` 均成功

### Requirement: 导出 Docker 镜像

系统 SHALL 将构建好的 Docker 客户端镜像导出为 `tar.gz` 压缩包，并生成 SHA256 校验文件。

#### Scenario: 镜像导出成功
- **WHEN** 客户端镜像 `xmnn-client:1.2.2-alpha` 已构建完成
- **THEN** 执行 `docker save` + `gzip` 生成 `xmnn-client-1.2.2-alpha.tar.gz`
- **AND** 生成 `xmnn-client-1.2.2-alpha.tar.gz.sha256` 校验文件

### Requirement: 构建环境前置检查

系统 SHALL 在构建前检查必要的环境条件，包括 Docker 可用性、基础镜像存在性、源码目录完整性。

#### Scenario: 环境检查通过
- **WHEN** 执行构建前检查
- **THEN** Docker daemon 可用
- **AND** `nuitka-gcc-llvm:latest` 镜像存在
- **AND** `npu_tvm/`、`npuusertools/`、`xmnn/packaging/pyproject.toml` 均存在