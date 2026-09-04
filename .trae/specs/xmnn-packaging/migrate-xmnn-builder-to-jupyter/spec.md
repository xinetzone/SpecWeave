# xmnn-whl-builder 迁移 jupyter 容器重建并编译 demo 模型 Spec

## Why
现有 XMNN 模型编译验证（`test-model-compile.sh`）依赖 WSL 宿主机 docker 会话。用户希望在 `jupyter-podman-rootless` 容器（自带 rootless Podman DinP）内自包含地重建 `xmnn-whl-builder` 镜像，并保证 `external/chaos/models/demo` 下全部 4 个模型组编译通过（SIM_VTA2.0），使流程脱离宿主机 docker 依赖。

## What Changes
- 在 `apps/containers/jupyter-podman-rootless/.temp/` 下创建 `external/chaos/ai/xmnn-whl-builder` 的**自适应副本**（`.temp/xmnn-whl-builder/`）
- 副本自包含化：消除对 `external/chaos/ai/scripts/lib/logging.sh` 等副本外路径的依赖
- 新增容器内编排脚本（位于 `.temp/`）：基础镜像导入（宿主 `podman save` → 容器内 `podman load`）、构建上下文搬运（`/workspace/external/chaos` → 容器原生 FS）、镜像重建、demo 模型编译
- 在容器内 rootless Podman 中重建 `xmnn-whl-builder:latest` 并编译 `models/demo` 全部 4 个模型组
- **不修改** `external/chaos/**` 任何原件（只读源，副本隔离）

## Impact
- Affected specs: 无（新独立任务；`chaos-ai-xmnn-whl-builder` 为已完成的历史创建任务，`fix-xmnn-whl-data-dirs` 为 CMake 修复任务，均不冲突）
- Affected code: `apps/containers/jupyter-podman-rootless/.temp/`（新增副本与脚本；`.temp` 为 git 忽略的临时工作区）
- 依赖环境：jupyter-podman-rootless 容器运行中、容器内 rootless Podman 可用（`--cgroup-manager=cgroupfs`）、宿主机存在 `devcontainer-base:onnx-quantized-latest` 镜像、磁盘空间充足（基础镜像 + whl-builder 镜像 + 构建缓存）

## ADDED Requirements

### Requirement: xmnn-whl-builder 自包含副本
系统 SHALL 在 `apps/containers/jupyter-podman-rootless/.temp/xmnn-whl-builder/` 提供 `external/chaos/ai/xmnn-whl-builder` 的完整副本，副本 SHALL 不依赖 `external/chaos/ai/` 下副本外的任何文件（共享日志库 `scripts/lib/logging.sh` 内联到副本内）。

#### Scenario: 副本自包含可运行
- **WHEN** 在副本目录内执行 `bash build.sh --help`
- **THEN** 正常显示帮助，不因 `source ${CHAOS_AI_ROOT}/scripts/lib/logging.sh` 路径失效而报错

#### Scenario: 副本脚本行尾兼容
- **WHEN** 副本内 `.sh` 脚本被拷贝到 Linux 容器内执行
- **THEN** 所有脚本为 LF 行尾（无 CRLF），`bash -n` 语法检查通过

### Requirement: 基础镜像导入容器内 Podman
系统 SHALL 将宿主机（WSL Podman）中的 `devcontainer-base:onnx-quantized-latest` 镜像通过 `podman save` → `podman load` 导入 jupyter 容器内的 rootless Podman 存储。

#### Scenario: 镜像导入成功
- **WHEN** 容器内执行 `podman images`
- **THEN** 列表包含 `devcontainer-base:onnx-quantized-latest`，且 `podman run --rm <image> python -V` 可正常运行

### Requirement: 容器内重建 xmnn-whl-builder 镜像
系统 SHALL 在 jupyter 容器内通过 rootless Podman（`--cgroup-manager=cgroupfs`、`--format docker`）以 `external/chaos` 为构建上下文重建 `xmnn-whl-builder:latest`：

- 构建上下文 SHALL 先从 9p 挂载（`/workspace/external/chaos`）复制到容器原生文件系统（如 `~/build/chaos`），规避 9p 慢 I/O
- 构建上下文中的 `ai/xmnn-whl-builder/` SHALL 使用 `.temp` 副本（同步自 `/workspace/.temp/xmnn-whl-builder`），确保构建的是适配副本
- bind mount 的源码路径（`npu_tvm/`、`npuusertools/`）随上下文正确解析

#### Scenario: 镜像重建并通过 11 项验证
- **WHEN** 容器内 `~/build/chaos/ai/xmnn-whl-builder` 下执行 `bash build.sh --cn`
- **THEN** 构建成功，`verify-wheel.sh` 11 项检查全部 PASS（含 `tvm.build(llvm)` 计算验证）

### Requirement: models/demo 全部模型编译通过
系统 SHALL 使用容器内重建的 `xmnn-whl-builder:latest` 镜像（Podman run，挂载模型目录）对 `external/chaos/models/demo` 下全部 4 个模型组执行 `xmnn.compile_api.compile_xmnn` 编译并全部成功：

- `pytorch/resnet18`（冒烟首选，最小）
- `caffe/resnet50`
- `onnx/yolov5s`
- `two_inputs`（双输入模型）

#### Scenario: 单模型编译成功
- **WHEN** 对模型组（如 `pytorch/resnet18`）执行编译
- **THEN** 输出 `COMPILE_DONE: pytorch/resnet18`，编译产物目录生成，退出码 0

#### Scenario: 全部 4 个模型编译通过
- **WHEN** 依次编译 4 个模型组
- **THEN** 4 个模型全部编译成功，无 FAIL

### Requirement: 源目录只读保护
`external/chaos/` 下所有原件（xmnn-whl-builder 原目录、npu_tvm、npuusertools、models）SHALL 保持未修改；所有适配改动 SHALL 仅发生在 `.temp` 副本与容器内 `~/build/` 拷贝中。

#### Scenario: 源目录无污染
- **WHEN** 任务完成后在 `external/chaos` git 仓库执行 `git status`
- **THEN** 无本任务引入的变更

## MODIFIED Requirements
无。

## REMOVED Requirements
无。

## 实施结果附录（2026-08-28 验收完成）

### torch 依赖补充方案（实施中发现）

xmnn-whl-builder 镜像仅含 onnx 前端依赖（torch 被 Nuitka `--nofollow-import-to=torch` 排除且镜像内未安装）。`models/demo` 中 `pytorch/resnet18` 与 `two_inputs` 为 pytorch 前端（`torch.jit.load` + `relay.frontend.from_pytorch`），需要 torch。

**方案**：派生镜像 `xmnn-whl-builder-full:latest` = `xmnn-whl-builder:latest` + CPU 版 torch 2.13.0（`--index-url https://download.pytorch.org/whl/cpu`，避免数 GB CUDA 依赖）。定义位于 `.temp/xmnn-whl-builder-full/{Dockerfile,build-full.sh}`。`compile-demo-models.sh` 按前端自动选镜像：pytorch 前端模型用 `-full`，onnx/caffe 前端用基础镜像（caffe 前端为纯 protobuf 实现，无需 caffe 包）。

### 验收结果

- 4/4 模型组编译成功（rc=0）：onnx/yolov5s(478s)、caffe/resnet50(122s)、pytorch/resnet18、two_inputs
- 产物 `~/build/models-demo/temp/<tag>/<group>/<model>/compile/{network.xmnn,param.bin}` 全部存在（`verify-artifacts.sh` 4 pass 0 fail）
- `external/chaos` 无本任务引入变更（源目录只读保护通过）

### 运维备注

- 容器运行时状态异常（podman 元数据 running 但 crun 已死）时，通过 `podman machine ssh` + `sudo podman start jupyter-podman` 恢复；直接 `wsl -d` 会话因 systemd 命名空间隔离无法操作容器（healthcheck timer 报 systemd connection 错误）
- 嵌套容器需网络时必须 `--network=host`（内嵌 netavark/aardvark-dns 二层嵌套 DNS 不可用）
