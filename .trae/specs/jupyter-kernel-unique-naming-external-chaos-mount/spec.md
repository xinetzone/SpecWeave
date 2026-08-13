# Jupyter 内核唯一命名与 external/chaos 统一挂载 Spec

## Why

chaos AI Docker 生态中的三个 Jupyter 内核配置（[ai/Dockerfile](file:///d:/spaces/SpecWeave/external/chaos/ai/Dockerfile) 的 `npu`、[xmnn-whl-builder](file:///d:/spaces/SpecWeave/external/chaos/ai/xmnn-whl-builder) 的 `xmnn-conda`、[xmnn-runtime](file:///d:/spaces/SpecWeave/external/chaos/ai/xmnn-runtime) 的 `xmnn-conda`）中，whl-builder 与 runtime 复用了相同的内核名 `xmnn-conda`，存在环境污染与命名冲突风险；同时三者未能统一挂载宿主源码目录 `d:\spaces\SpecWeave\external\chaos`，导致运行期内核无法一致访问该目录下的资源（npuusertools / npu_tvm / xmnn-client / models / ai 等）。

## What Changes

- 为三个 Jupyter 内核分配**全局唯一**且**明确区分**的内核名与显示名：
  - `ai/Dockerfile`（开发镜像）→ 内核名 `npu`，显示名 `Python 3 (NPU Dev)`
  - `xmnn-whl-builder` → 内核名 `xmnn-whl-builder`，显示名 `Python 3.14 (xmnn whl-builder)`
  - `xmnn-runtime` → 内核名 `xmnn-runtime`，显示名 `Python 3.14 (xmnn runtime)`
- 三个内核的 kernel.json 统一新增对宿主目录 `d:\spaces\SpecWeave\external\chaos` 的挂载感知（通过环境变量 `PYTHONPATH` / `CHAOS_ROOT` 指向容器内统一挂载点，实现运行时对 `external/chaos` 下资源的访问）。
- 同步更新各内核注册逻辑（Dockerfile 内核注册块 + setup-npu-kernel.sh）中的内核名引用，避免残留旧名 `xmnn-conda` 造成冲突。
- 验证挂载路径正确性与访问权限（容器内资源目录存在、可读、权限正确）。

## Impact

- Affected specs: `chaos-ai-xmnn-whl-builder`（whl-builder 内核注册逻辑）、xmnn-runtime 相关构建流程
- Affected code:
  - `external/chaos/ai/Dockerfile`（开发镜像内核注册/启动）
  - `external/chaos/ai/config/jupyter/kernels/npu/kernel.json`
  - `external/chaos/ai/scripts/setup-npu-kernel.sh`
  - `external/chaos/ai/xmnn-whl-builder/kernelspec/xmnn-conda/kernel.json` → 重命名为 `xmnn-whl-builder`
  - `external/chaos/ai/xmnn-whl-builder/Dockerfile`（内核注册块）
  - `external/chaos/ai/xmnn-runtime/kernelspec/xmnn-conda/kernel.json` → 重命名为 `xmnn-runtime`
  - `external/chaos/ai/xmnn-runtime/Dockerfile`（内核注册块）

## ADDED Requirements

### Requirement: 内核唯一命名
系统 SHALL 为 ai/Dockerfile、xmnn-whl-builder、xmnn-runtime 三个环境的 Jupyter 内核分配全局唯一的内核名，防止环境污染与命名冲突。

#### Scenario: 成功场景
- **WHEN** 用户在三者任一容器中执行 `jupyter kernelspec list`
- **THEN** 三个内核名两两互不相同，且 display_name 清晰标示所属环境

### Requirement: external/chaos 统一挂载
系统 SHALL 在三个内核的 kernel.json 中注入对宿主目录 `d:\spaces\SpecWeave\external\chaos` 的统一挂载感知（容器内统一挂载点 + PYTHONPATH/CHAOS_ROOT 环境变量），确保运行期能访问该目录资源。

#### Scenario: 成功场景
- **WHEN** 用户在任一内核中执行 `import os; os.environ['CHAOS_ROOT']` 并访问挂载点资源
- **THEN** 可正确读取 `external/chaos` 目录下的 npuusertools / npu_tvm / xmnn-client 等资源，无 ModuleNotFoundError 或路径不存在错误

### Requirement: 挂载路径与权限验证
系统 SHALL 提供验证能力，确认容器内挂载点路径存在、可读，且权限正确。

#### Scenario: 成功场景
- **WHEN** 运行挂载验证（容器内 `ls -ld` 挂载点 + 读取测试文件）
- **THEN** 挂载点存在、可读、属主权限符合预期，验证脚本返回 PASS

## MODIFIED Requirements

### Requirement: 内核注册逻辑同步
将 whl-builder 与 runtime 的 Dockerfile 内核注册块、以及 setup-npu-kernel.sh 中所有旧内核名 `xmnn-conda` / `npu` 的引用，同步更新为新的唯一内核名，确保注册路径（`/opt/venv/share/jupyter/kernels/<name>/`、`/opt/conda/share/jupyter/kernels/<name>/`）与配置一致。

## REMOVED Requirements

### Requirement: 旧内核名 `xmnn-conda` 复用
**Reason**: whl-builder 与 runtime 复用 `xmnn-conda` 造成命名冲突与环境风险。
**Migration**: 分别重命名为 `xmnn-whl-builder` 与 `xmnn-runtime`；旧镜像需重建后方生效。
