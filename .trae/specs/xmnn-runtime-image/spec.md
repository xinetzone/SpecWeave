# XMNN 客户运行时镜像 - Product Requirement Document

## Overview
- **Summary**: 在 `external/chaos/ai/` 下创建 `xmnn-runtime/` 子目录，构建面向终端客户的轻量级运行时镜像。该镜像基于 `devcontainer-base:conda-latest`，从 `xmnn-whl-builder:latest` 复制 XMNN whl 的运行时依赖（不包含 LLVM/cmake/ninja 等构建工具链），镜像内预装 XMNN，后续版本升级只需 `pip install` 新 whl 即可完成，无需重新构建整个镜像。
- **Purpose**: 现有 `xmnn-whl-builder:latest` 和 `devcontainer-base:chaos-ai-npu-latest` 是开发镜像，体积庞大（包含 LLVM 22.1.8、clang、cmake、ninja、scikit-build-core、nuitka、PyTorch 等构建工具链），不适合分发给客户使用。客户只需要运行时环境，不需要编译工具链，且升级时希望最小化操作成本。
- **Target Users**: XMNN whl 包的终端使用者（客户），需要稳定、轻量、易于升级的 Docker 运行时环境。

## Goals
- 创建轻量级客户运行时镜像 `devcontainer-base:xmnn-runtime-latest`
- 基于 `devcontainer-base:conda-latest`（Ubuntu 26.04 + Miniconda + Python 3.14 + SSH/Docker/Jupyter 基础服务）
- 从 `xmnn-whl-builder:latest` 多阶段构建 COPY 必要的运行时文件，**不包含** LLVM/clang/cmake/ninja/Nuitka/scikit-build-core 等构建工具
- 不包含 PyTorch/torchvision（可选依赖，客户按需 `pip install xmnn[torch]`）
- 镜像内预装可直接运行的 XMNN（import tvm/vta/xmnn 全部可用）
- 支持后续升级：客户只需 `pip install /path/to/new-xmnn.whl` 即可升级版本，无需重新构建基础镜像
- 镜像配置时区 Asia/Shanghai（三层保证，遵循现有规范）
- 空 ENTRYPOINT，允许客户覆盖 CMD（如 `bash` 进入交互式 shell）

## Non-Goals (Out of Scope)
- 不包含源码（npu_tvm/npuusertools），源码不内置、不暴露
- 不包含 LLVM/Clang/cmake/ninja 等编译工具链（已打包进 whl 的 `_libs/` 目录）
- 不包含 PyTorch/torchvision/onnx2pytorch（可选依赖，客户自行安装）
- 不包含 Nuitka/scikit-build-core/invoke/build 等构建工具
- 不做 ONNX 量化/QCHECK（这是开发镜像功能）
- 不包含 volume 挂载配置脚本（客户自行决定挂载方式）
- 不重新设计 whl 打包流程（whl 构建流程保持不变）

## Background & Context
- 现有构建链：base → conda → conda-llvm → onnx-pytorch → onnx-quantized → chaos-ai-npu → xmnn-whl-builder（共7层，含完整构建工具链）
- XMNN whl 包已通过 Nuitka 编译 tvm/vta/xmnn 为原生二进制，并通过 patchelf 将 `_libs/` 目录的 libtvm.so 及依赖（含 libLLVM.so.22.1）设置了 `$ORIGIN` RPATH，运行时不依赖系统级 LLVM
- whl 依赖列表（来自 pyproject.toml）：numpy, scipy, pandas, matplotlib, Pillow, onnx, protobuf, openpyxl, tabulate, rich, tqdm, tomlkit, decorator, attrs, psutil, cloudpickle, typing_extensions, pytest（运行时需要）, telnetlib3
- devcontainer-base:conda-latest 已提供：Ubuntu 26.04、SSH/Docker DinD/Podman/Jupyter/Supervisor基础服务、Miniconda3 at /opt/conda、Python 3.14、不自动激活 conda base、/opt/venv 系统虚拟环境
- 项目硬约束（来自 project_memory）：Python ≥3.14、Docker 空 ENTRYPOINT、时区 Asia/Shanghai 三层保证、国内镜像源支持、不使用 setuptools/setup.py

## Functional Requirements
- **FR-1**: 新目录结构 `external/chaos/ai/xmnn-runtime/`，包含 Dockerfile、build.sh、build.bat、必要的辅助脚本和 .agents/rules/
- **FR-2**: Dockerfile 采用三阶段构建：
  - Stage `runtime-base`：FROM devcontainer-base:conda-latest（作为构建参数 BASE_IMAGE），
    - 重新声明所有 ARG（BASE_TAG/APT_MIRROR/CONDA_MIRROR/PIP_MIRROR）
    - 重置 SHELL 指令
    - 设置 LABEL（maintainer/description/variant=xmnn-runtime）
    - 设置 ENV PATH=/opt/conda/bin:${PATH}、OpenMP 环境变量
    - **Stage 1/3：系统层**——配置时区（三层保证：tzdata + ln -sf + ENV TZ）、安装必要系统运行时库（libgomp1 等 OpenMP 依赖）、初始化计时器
    - **Stage 2/3：Python 运行时层**——配置 pip 镜像源（根据 PIP_MIRROR 参数选择 aliyun/tuna/official）、准备 pip 安装环境
  - Stage `whl-artifacts`：FROM xmnn-whl-builder:latest（不运行任何命令，仅作为文件来源）
    - 该阶段只用于 COPY --from，不执行 RUN
  - Stage `final`：FROM runtime-base
    - **Stage 3/3：XMNN 安装层**——
      - COPY --from=whl-artifacts /builder/dist/xmnn-*.whl /tmp/whl/
      - 执行 pip install /tmp/whl/xmnn-*.whl（不带 --no-deps，让 pip 自动解析安装所有运行时依赖）
      - 运行精简验证（核心项：import tvm/vta/xmnn、_libs 目录检查、libtvm.so 加载、tvm.build(llvm) 计算、bootstrap .pth 检查）
      - 删除 whl 文件（减小镜像体积）
      - 写入 build-info 元数据
      - 清理（pip cache purge、apt clean、rm -rf /tmp/*）
      - 输出 [TIMER] 汇总表
      - 输出 [VALIDATION CHECKPOINT]
    - 设置 ENTRYPOINT []
    - CMD 为打印版本信息的 python 命令（参考 xmnn-whl-builder FINAL 阶段）
- **FR-3**: 构建脚本支持 `--cn` 国内镜像源参数（APT/Conda/Pip），与现有变体保持一致
- **FR-4**: 预装 XMNN 后运行精简版验证（核心 5 项：import tvm/vta/xmnn、_libs 目录存在、tvm.build(llvm) 可执行），确保镜像开箱即用
- **FR-5**: 提供版本升级文档/说明：客户如何在运行容器中 pip install 新版本 whl
- **FR-6**: 镜像 LABEL 正确标注 variant=xmnn-runtime、包含版本信息、构建日期等元数据

## Non-Functional Requirements
- **NFR-1**: 镜像体积应显著小于 chaos-ai-npu 和 xmnn-whl-builder（目标 < 3GB，chaos-ai-npu 约 5-6GB，不含 LLVM/PyTorch 可大幅减小）
- **NFR-2**: 构建时间应短于 xmnn-whl-builder（无需 Nuitka 编译，只需 COPY+pip install+验证）
- **NFR-3**: 稳定性：基础镜像 conda-latest 变化频率低，客户镜像基础层稳定，升级只动 Python 包层
- **NFR-4**: 兼容性：pip install 升级时，新 whl 必须与基础镜像的 Python 版本（3.14.x）和 ABI 兼容
- **NFR-5**: 安全性：不包含开发工具、不包含源码、不暴露不必要的端口（基础镜像的 SSH/Jupyter 保留，由客户控制）

## Constraints
- **Technical**:
  - Dockerfile syntax 必须使用 `# syntax=docker/dockerfile:1.7-labs`（支持 BuildKit 特性）
  - 必须遵循 devcontainer-base 变体的共享约定（FROM后重置SHELL、[TIMER]阶段计时、[VALIDATION CHECKPOINT]、build-info元数据）
  - SHELL 必须是 `["/bin/bash", "-e", "-o", "pipefail", "-c"]`
  - 时区配置必须三层保证（apt-get install tzdata + ln -sf + ENV TZ=Asia/Shanghai）
  - ENTRYPOINT 必须为空数组 `[]`
  - Python 版本必须 3.14+（继承自 conda-latest）
  - 不得使用 setuptools/setup.py（whl 已用 scikit-build-core 构建，本镜像只 pip install）
- **Business**:
  - 面向客户分发，需要稳定、可复现
  - 升级流程必须简单（一条 pip install 命令）
- **Dependencies**:
  - 依赖已构建的 `devcontainer-base:conda-latest` 镜像
  - 依赖已构建的 `xmnn-whl-builder:latest` 镜像（作为运行时文件来源）
  - 不新增外部依赖（所有依赖来自现有镜像或 pip/conda）

## Assumptions
- xmnn-whl-builder:latest 的构建产物 whl 位于 `/builder/dist/xmnn-*.whl`（已由 build-wheel.sh 输出确认）
- pip install whl 时会自动下载并安装 pyproject.toml 中声明的所有运行时依赖（numpy/scipy/pandas/matplotlib/Pillow/onnx/protobuf/openpyxl/tabulate/rich/tqdm/tomlkit/decorator/attrs/psutil/cloudpickle/typing_extensions/pytest/telnetlib3），无需手动列举
- 系统运行时库（libgomp1、libstdc++6 等）可通过 apt-get 安装，Ubuntu 26.04 提供的版本与 whl 编译时兼容
- pip install 新版本 whl 时，whl 内的 `_libs/` 目录（含 libLLVM）会被正确安装，RPATH `$ORIGIN` 仍然有效
- conda-latest 基础镜像的 Python 3.14 次要版本升级（如 3.14.6 → 3.14.7）不会破坏已安装 whl 的 ABI 兼容性
- 构建时需要网络连接以下载 pip 依赖（国内构建通过 PIP_MIRROR 使用镜像源加速）
- 构建前必须确保本地已存在 `devcontainer-base:conda-latest` 和 `xmnn-whl-builder:latest` 两个镜像（构建脚本会检查）
- 客户会自行处理跨 Python 小版本的兼容性问题（如 whl 要求的 Python 版本与镜像内版本不匹配时，客户需使用对应版本的镜像）

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 执行实施计划后
- **When**: 查看 `external/chaos/ai/xmnn-runtime/` 目录
- **Then**: 目录包含 Dockerfile、build.sh、build.bat、.env.example、README.md、.agents/rules/dockerfile.md
- **Verification**: `programmatic`
- **Notes**: 参考现有 xmnn-whl-builder/ 和 chaos-ai-npu/ 的目录结构

### AC-2: 镜像构建成功
- **Given**: 本地已有 devcontainer-base:conda-latest 和 xmnn-whl-builder:latest 镜像
- **When**: 在 external/chaos/ai/ 下执行 `cd xmnn-runtime && bash build.sh --cn`（或 build.bat --cn）
- **Then**: 镜像构建成功，标签为 `devcontainer-base:xmnn-runtime-latest`，无构建错误
- **Verification**: `programmatic`

### AC-3: XMNN 核心功能可用
- **Given**: 镜像构建完成
- **When**: 运行 `docker run --rm devcontainer-base:xmnn-runtime-latest python -c "import tvm, vta, xmnn; print('OK')"`
- **Then**: 三个模块均成功导入，无报错，输出 "OK"
- **Verification**: `programmatic`

### AC-4: tvm.build(llvm) 计算验证
- **Given**: 镜像构建完成
- **When**: 在容器内运行 tvm.build(llvm) 并执行简单计算（向量加倍）
- **Then**: 计算结果正确（A[i]*2 == B[i]），无 LLVM 链接错误
- **Verification**: `programmatic`
- **Notes**: 这验证了 _libs/ 中的 libLLVM.so.22.1 和 libtvm.so 可正常加载和使用

### AC-5: 镜像不包含构建工具链
- **Given**: 镜像构建完成
- **When**: 检查容器内是否存在 llvm-config、clang、cmake、ninja、nuitka、scikit-build-core
- **Then**: 这些命令/包均不存在
- **Verification**: `programmatic`

### AC-6: 不包含 PyTorch（可选依赖）
- **Given**: 镜像构建完成
- **When**: 尝试 `import torch`
- **Then**: 导入失败（ModuleNotFoundError），客户可后续 `pip install xmnn[torch]`
- **Verification**: `programmatic`

### AC-7: 时区配置正确
- **Given**: 镜像构建完成
- **When**: 在容器内运行 `date` 并检查 /etc/timezone 和 TZ 环境变量
- **Then**: 时区为 Asia/Shanghai，/etc/localtime 指向正确时区文件
- **Verification**: `programmatic`

### AC-8: ENTRYPOINT 为空，可交互式进入
- **Given**: 镜像构建完成
- **When**: 运行 `docker run --rm -it devcontainer-base:xmnn-runtime-latest bash`
- **Then**: 成功进入 bash shell，可正常交互
- **Verification**: `programmatic`

### AC-9: pip install 升级路径可行
- **Given**: 镜像构建完成，有一个新版本的 xmnn whl 文件
- **When**: 启动容器，执行 `pip install /path/to/new-xmnn.whl --force-reinstall`
- **Then**: 安装成功，新版本 import 正确，tvm.build(llvm) 仍可正常工作
- **Verification**: `programmatic`
- **Notes**: 可先用当前镜像内已安装版本做降级再升级模拟，或构建两个版本验证

### AC-10: 镜像体积显著减小
- **Given**: 镜像构建完成
- **When**: 检查镜像大小 `docker images devcontainer-base:xmnn-runtime-latest`
- **Then**: 镜像体积小于 xmnn-whl-builder:latest 的 70%（目标 < 3GB）
- **Verification**: `programmatic`

### AC-11: 基础服务保留
- **Given**: 镜像构建完成
- **When**: 检查 sshd、docker、supervisord、jupyter 等基础服务是否存在
- **Then**: 这些基础服务的二进制仍在镜像中（继承自 conda-latest）
- **Verification**: `programmatic`

### AC-12: build-info 元数据完整
- **Given**: 镜像构建完成
- **When**: 查看 /etc/devcontainer-variant-xmnn-runtime-build-info
- **Then**: 文件存在且包含 BUILD_DATE、VARIANT=xmnn-runtime、BASE_IMAGE、PYTHON_VERSION、XMNN_VERSION 等字段
- **Verification**: `programmatic`

## Open Questions
- [x] ~~客户运行时镜像是否需要保留 Jupyter/SSH/Docker DinD 等开发服务？~~ → 已解决：用户明确要求"基于 devcontainer-base:conda-latest"，直接继承该基础镜像的所有服务（SSH/Docker/Jupyter/Supervisor），不做删减
- [x] ~~是否需要提供一个快速验证脚本（如 verify-runtime.sh）供客户自检？~~ → 已解决：在 Dockerfile 内置精简验证（构建时运行），额外提供 verify-runtime.sh 到 /opt/ 供客户手动验证
- [ ] 镜像标签策略：是否需要版本化标签（如 `xmnn-runtime-1.2.1`），还是只有 `latest`？（当前默认：构建脚本支持 --tag 参数，默认 latest）
- [ ] 是否需要在 README 中提供 docker-compose.yml 示例或典型运行命令？（当前默认：README 提供 docker run 示例命令）
