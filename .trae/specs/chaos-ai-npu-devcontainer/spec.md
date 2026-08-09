# Chaos AI NPU DevContainer - Product Requirement Document

## Overview
- **Summary**: 基于 devcontainer-base:onnx-quantized 变体，在 `external/chaos/ai` 目录创建新的开发容器镜像，支持挂载 npuusertools 和 npu_tvm 源码目录，提供 XMNN NPU 工具链完整开发环境。
- **Purpose**: 为芯劢微电子 NPU 工具链（npu_tvm 编译器 + npuusertools 用户工具链）提供标准化、可复现的 Docker 开发环境，与现有 devcontainer-base 体系保持一致的分层架构和服务（SSH/Docker DinD/Jupyter/Supervisord）。
- **Target Users**: XMNN NPU 工具链开发者、模型编译工程师、需要在隔离环境中调试 TVM/VTA/XMNN 的 AI 工程师。

## Goals
- 创建 `external/chaos/ai/` 目录结构，包含完整的 Docker 构建配置
- 基于 `devcontainer-base:onnx-quantized-latest` 基础镜像构建
- 支持通过 volume 挂载 `npuusertools/` 和 `npu_tvm/` 源码目录（不内置源码，保持镜像通用性）
- 预置 npuusertools/npu_tvm 所需的构建依赖（CMake/Ninja/LLVM/Patchelf等，已在base中）
- 配置环境变量和入口脚本，使挂载的工具链可直接使用
- 提供构建脚本、验证脚本和使用文档
- 保持与现有 devcontainer-base 变体一致的3层追加架构、BuildKit缓存、计时统计

## Non-Goals (Out of Scope)
- **不内置 npuusertools/npu_tvm 源码**：源码通过 volume 挂载，镜像不包含具体业务代码
- **不预编译 XMNN wheel**：编译在容器内由开发者执行，镜像仅提供环境
- **不包含 GPU/CUDA 支持**：首期仅 CPU 版本，GPU 变体后续迭代
- **不修改 devcontainer-base 主仓库代码**：新镜像独立在 external/chaos/ai/，不侵入 apps/devcontainer-base
- **不包含模型文件或测试数据**：用户自行挂载 models/ 目录

## Background & Context
- 现有 devcontainer-base 体系已构建完成5层依赖链：base → conda → conda-llvm → onnx-pytorch → onnx-quantized
- onnx-quantized 变体已包含：Python 3.14.6、LLVM/Clang 22.1.8、CMake 4.4.0、Ninja 1.13.2、PyTorch CPU、ONNX Runtime、量化工具链
- npuusertools 要求：Python >= 3.14、scikit-build-core + CMake + Ninja、Nuitka
- npu_tvm (Apache TVM) 要求：LLVM/Clang、CMake、Python 3.14、相关编译依赖
- xmtools 现有 Docker 环境（xmnn-dev:llvm22）可作为参考，但需要整合到 devcontainer-base 统一体系中
- 新镜像位置：`d:\spaces\SpecWeave\external\chaos\ai\`（外部项目区，独立于 apps/devcontainer-base）

## Functional Requirements
- **FR-1**: 目录结构 - 在 `external/chaos/ai/` 创建完整的镜像构建目录：Dockerfile、.env.example、build.sh、scripts/、README.md
- **FR-2**: 基础镜像继承 - FROM devcontainer-base:onnx-quantized-${BASE_TAG}，继承所有服务（sshd/dockerd/jupyter/supervisord）
- **FR-3**: 3层追加架构 - 遵循 onnx-quantized 变体模式：Stage1(基础验证+计时)、Stage2(安装XMNN特有依赖)、Stage3(配置+冒烟测试+汇总)
- **FR-4**: XMNN依赖安装 - 安装 npuusertools/npu_tvm 构建所需但 base 中缺失的包：scikit-build-core、nuitka、invoke、build、patchelf、decorator、attrs、cloudpickle、typing_extensions
- **FR-5**: 环境变量配置 - 设置 XMNN 相关环境变量：NPU_TOOLS_ROOT、PYTHONPATH 扩展、NPU_* 构建配置预设
- **FR-6**: 挂载点准备 - 创建标准挂载点目录：/workspace/npu_tvm、/workspace/npuusertools、/workspace/models（不复制源码，仅创建目录）
- **FR-7**: 入口脚本 - 提供 /etc/profile.d/chaos-ai-init.sh，检测挂载目录是否存在并自动配置 PYTHONPATH
- **FR-8**: 构建脚本 - 提供 build.sh（Linux/WSL）和 build.bat（Windows），支持 --cn 国内镜像、--tag 参数
- **FR-9**: 验证脚本 - 提供 verify-deployment.py，验证：基础服务、Python包导入、挂载点存在、构建工具可用
- **FR-10**: 冒烟测试 - Stage3 内置冒烟测试：scikit-build-core/nuitka/invoke 导入、cmake/ninja 版本检查、Python 3.14 验证
- **FR-11**: 文档 - README.md 包含：快速开始、构建命令、运行命令（含volume挂载示例）、验证方法

## Non-Functional Requirements
- **NFR-1**: 构建性能 - 使用 BuildKit cache（/opt/conda/pkgs、/root/.cache/pip），追加层构建时间 < 5分钟（有缓存时 < 2分钟）
- **NFR-2**: 镜像大小 - 追加层新增 < 500MB（主要是 pip 包），总镜像大小控制在合理范围
- **NFR-3**: 可复现性 - 固定关键包版本或提供版本锁定机制，支持 .env 配置版本
- **NFR-4**: 国内镜像支持 - 完整支持 APT_MIRROR/CONDA_MIRROR/PIP_MIRROR 构建参数，与现有变体一致
- **NFR-5**: 权限一致性 - devuser 可访问所有工具和挂载点，遵循现有变体权限模型
- **NFR-6**: 服务完整性 - 所有基础服务（SSH 22、Docker 2375、Jupyter 8888）必须正常运行

## Constraints
- **Technical**:
  - 基础镜像必须是 devcontainer-base:onnx-quantized（Python 3.14.6、LLVM 22.1.8 已就绪）
  - Dockerfile syntax 必须使用 docker/dockerfile:1.7-labs（与现有变体一致）
  - SHELL 必须是 ["/bin/bash", "-e", "-o", "pipefail", "-c"]
  - 必须设置时区 Asia/Shanghai（三层保证：apt tzdata + ln + ENV TZ）—— base 已处理
  - 必须使用北外 conda-forge 镜像（国内构建时），清空 default_channels—— base 已处理
  - ENTRYPOINT 必须为空，允许用户覆盖 command
  - 必须保留所有现有服务：sshd、dockerd、podman、jupyter、supervisord
- **Business**:
  - 镜像位于 external/chaos/ai/，不修改 apps/devcontainer-base 现有代码
  - 源码通过 volume 挂载，镜像本身是通用开发环境，不绑定特定代码版本
- **Dependencies**:
  - 依赖 devcontainer-base:onnx-quantized 镜像已预先构建
  - 依赖 docker BuildKit 支持（--mount=type=cache）

## Assumptions
- devcontainer-base:onnx-quantized 镜像已在本地构建或可从 registry 获取
- 用户运行容器时会通过 -v 参数挂载 npuusertools 和 npu_tvm 目录
- 宿主机目录结构遵循：external/chaos/npuusertools、external/chaos/npu_tvm
- Docker 版本 >= 23.0（支持 BuildKit 和 dockerfile:1.7-labs）
- WSL2 或 Linux 环境用于构建（Windows 容器不支持，通过 WSL2 后端运行 Linux 容器）

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 构建任务已启动
- **When**: 检查 external/chaos/ai/ 目录
- **Then**: 目录包含 Dockerfile、.env.example、build.sh、build.bat、scripts/verify-deployment.py、README.md
- **Verification**: `programmatic`
- **Notes**: 文件权限正确，shell脚本可执行

### AC-2: 镜像成功构建
- **Given**: devcontainer-base:onnx-quantized-latest 存在
- **When**: 执行 build.sh（或 docker build）
- **Then**: 镜像 chaos-ai-npu:latest 构建成功，无错误退出
- **Verification**: `programmatic`
- **Notes**: 支持 --cn 参数使用国内镜像

### AC-3: 基础服务继承正常
- **Given**: 镜像已构建
- **When**: 启动容器并检查服务
- **Then**: sshd (22)、dockerd (2375)、jupyter (8888)、supervisord 全部运行正常
- **Verification**: `programmatic`

### AC-4: XMNN构建依赖已安装
- **Given**: 容器已启动
- **When**: 在容器内检查 Python 包
- **Then**: scikit-build-core、nuitka、invoke、build、patchelf（系统）、decorator、attrs、cloudpickle、typing_extensions 均可导入/使用
- **Verification**: `programmatic`

### AC-5: 构建工具版本正确
- **Given**: 容器已启动
- **When**: 检查 cmake、ninja、llvm-config、python 版本
- **Then**: cmake >= 4.4、ninja >= 1.13、llvm == 22.1.8、python == 3.14.x
- **Verification**: `programmatic`

### AC-6: 挂载点与自动配置
- **Given**: 容器通过 -v 挂载 npuusertools 和 npu_tvm
- **When**: 容器启动并登录
- **Then**: /workspace/npu_tvm、/workspace/npuusertools、/workspace/models 目录存在，PYTHONPATH 自动包含挂载的源码目录，profile.d 脚本正常加载
- **Verification**: `programmatic`
- **Notes**: 未挂载时不应报错，给出友好提示

### AC-7: devuser权限正常
- **Given**: 容器已启动
- **When**: 使用 devuser 登录（ssh或su）
- **Then**: devuser 可运行所有构建命令，可读写 /workspace 挂载点，可使用 docker 命令
- **Verification**: `programmatic`

### AC-8: 构建计时统计输出
- **Given**: 镜像构建过程
- **When**: 构建完成
- **Then**: 输出3阶段计时表格（Stage1/2/3）和总耗时，格式与 onnx-quantized 变体一致
- **Verification**: `human-judgment`

### AC-9: 冒烟测试通过
- **Given**: Stage3构建阶段
- **When**: 运行内置冒烟测试
- **Then**: 所有冒烟测试通过（包导入、工具版本、基础功能验证）
- **Verification**: `programmatic`

### AC-10: 文档完整可用
- **Given**: README.md已生成
- **When**: 用户阅读README
- **Then**: 包含构建命令、运行命令（含volume挂载示例）、验证方法、环境变量说明
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要预配置 ccache 加速 TVM 重复编译？（参考 xmtools/docker 已有 .ccache 目录）
- [ ] 是否需要预置 npu_tvm 的 conda 环境配置（npu_tvm/conda/condarc）？
- [ ] 镜像名称和标签命名规范：chaos-ai-npu vs xmnn-dev-chaos？建议 `chaos-ai-npu:latest`
- [ ] 是否需要同时支持 CPU 和 GPU 变体？首期仅 CPU，GPU 作为后续迭代
- [ ] verify-deployment.py 需要验证哪些 npuusertools 特定功能？（仅工具可用性 vs 完整编译流程）
