# Chaos AI NPU DevContainer - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 创建目录结构和基础配置文件
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `external/chaos/ai/` 目录
  - 创建 `external/chaos/ai/scripts/` 子目录
  - 创建 `.env.example` 文件（参考 onnx-quantized 变体，添加 XMNN 相关版本变量）
  - 创建空的 `Dockerfile`、`build.sh`、`build.bat`、`README.md` 占位文件
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录 `external/chaos/ai/` 和 `external/chaos/ai/scripts/` 存在
  - `programmatic` TR-1.2: `.env.example` 文件存在且包含 BASE_TAG、APT_MIRROR、CONDA_MIRROR、PIP_MIRROR 配置项
  - `human-judgement` TR-1.3: 文件结构与 onnx-quantized 变体保持一致的风格
- **Notes**: 参考 onnx-quantized/.env.example 的格式

## [ ] Task 2: 编写 Dockerfile（3层追加架构）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 基于 devcontainer-base:onnx-quantized-${BASE_TAG}
  - Stage 1/3: 基础验证 + 计时器初始化（验证 onnx-quantized 基础组件：torch/onnx/onnxruntime/quantization工具）
  - Stage 2/3: 安装 XMNN 构建依赖（scikit-build-core、nuitka、invoke、build、decorator、attrs、cloudpickle、typing_extensions；apt安装patchelf）
  - Stage 3/3: 创建挂载点目录、写入build-info、清理缓存、profile.d入口脚本、冒烟测试、计时汇总表
  - 使用 BuildKit cache 挂载（/opt/conda/pkgs、/root/.cache/pip）
  - LABEL 标记 variant="chaos-ai-npu"
  - ENV 设置 NPU_TOOLS_ROOT=/workspace、OpenMP 环境变量
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-2.1: Dockerfile syntax 使用 docker/dockerfile:1.7-labs
  - `programmatic` TR-2.2: FROM 指令正确引用 devcontainer-base:onnx-quantized-${BASE_TAG}
  - `programmatic` TR-2.3: SHELL 设置为 ["/bin/bash", "-e", "-o", "pipefail", "-c"]
  - `programmatic` TR-2.4: 创建挂载点目录 /workspace/npu_tvm、/workspace/npuusertools、/workspace/models
  - `programmatic` TR-2.5: 安装 scikit-build-core、nuitka、invoke、build、patchelf（apt）、decorator、attrs、cloudpickle、typing_extensions
  - `programmatic` TR-2.6: /etc/profile.d/chaos-ai-init.sh 存在且可执行，检测挂载目录并配置 PYTHONPATH
  - `programmatic` TR-2.7: /etc/devcontainer-variant-chaos-ai-npu-build-info 元数据文件写入
  - `programmatic` TR-2.8: Stage3 冒烟测试验证所有 XMNN 依赖可导入、工具版本正确
  - `human-judgement` TR-2.9: 3阶段计时输出格式与 onnx-quantized 变体一致
- **Notes**: 
  - patchelf 通过 apt 安装（base 可能已有，需检查）
  - 挂载点目录仅创建空目录，不复制源码
  - profile.d 脚本要优雅处理未挂载情况（不报错，给出INFO提示）

## [ ] Task 3: 编写 chaos-ai-init.sh 入口脚本（profile.d）
- **Priority**: high
- **Depends On**: Task 2（在Dockerfile中COPY）
- **Description**: 
  - 创建 `scripts/chaos-ai-init.sh`（在build时COPY到/etc/profile.d/）
  - 检测 /workspace/npuusertools 是否存在，存在则添加到 PYTHONPATH
  - 检测 /workspace/npu_tvm/python 是否存在，存在则添加到 PYTHONPATH
  - 检测 /workspace/npu_tvm/vta/python 是否存在，存在则添加到 PYTHONPATH
  - 设置 XMNN_TOOLS_ROOT=/workspace/npuusertools
  - 设置 TVM_LIBRARY_PATH 候选路径提示
  - 未挂载时输出友好 INFO 信息（非错误）
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 脚本语法正确（bash -n 检查通过）
  - `programmatic` TR-3.2: 挂载点存在时正确设置 PYTHONPATH
  - `programmatic` TR-3.3: 挂载点不存在时不报错，仅输出信息
  - `human-judgement` TR-3.4: 脚本输出信息清晰，帮助用户了解当前环境状态

## [ ] Task 4: 编写 build.sh 构建脚本（Linux/WSL）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 创建 `build.sh`，支持参数：--variant（默认cpu）、--tag（默认latest）、--cn（国内镜像）、--no-cache、-h/--help
  - 自动检测 devcontainer-base:onnx-quantized 基础镜像是否存在，不存在给出构建提示
  - 支持从 .env 文件加载默认配置
  - 构建完成后输出镜像大小和快速验证命令
  - 设置 DOCKER_BUILDKIT=1
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-4.1: 脚本可执行（chmod +x）
  - `programmatic` TR-4.2: bash -n 语法检查通过
  - `programmatic` TR-4.3: --help 参数输出使用说明
  - `programmatic` TR-4.4: --cn 参数正确传递 APT_MIRROR=aliyun CONDA_MIRROR=bfsu PIP_MIRROR=aliyun
  - `human-judgement` TR-4.5: 输出格式清晰，有颜色/emoji标记（参考现有build脚本风格）

## [ ] Task 5: 编写 build.bat 构建脚本（Windows WSL调用）
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 创建 `build.bat`，Windows下自动调用WSL执行build.sh
  - 自动转换Windows路径到WSL路径（/mnt/d/...）
  - 支持参数透传（--cn、--tag等）
  - 参考 onnx-quantized 变体或 xmtools 的 build.bat 风格
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-5.1: 脚本在Windows CMD/PowerShell中可执行
  - `programmatic` TR-5.2: 参数正确透传给WSL中的build.sh
  - `human-judgement` TR-5.3: 错误提示清晰（如WSL未安装时给出提示）
- **Notes**: 首期可简化，优先保证 build.sh 可用，build.bat 作为便捷包装

## [ ] Task 6: 编写 verify-deployment.py 验证脚本
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 创建 `scripts/verify-deployment.py`，在容器内运行
  - 验证项：
    1. 基础服务：sshd、docker、supervisord、jupyter
    2. Python版本：3.14.x
    3. 核心包导入：torch、onnx、onnxruntime、onnxruntime.quantization
    4. XMNN构建包：scikit_build_core、nuitka、invoke、decorator、attrs、cloudpickle
    5. 系统工具：cmake、ninja、llvm-config、patchelf
    6. 挂载点目录存在性检查（仅检查目录，不要求已挂载）
    7. devuser 权限验证
    8. profile.d 脚本加载测试
  - 输出彩色PASS/FAIL/SKIP结果
  - 有失败时返回非零退出码
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: Python语法正确，可在容器内运行
  - `programmatic` TR-6.2: 所有验证项都有明确的PASS/FAIL/SKIP输出
  - `programmatic` TR-6.3: 有失败项时退出码为1
  - `human-judgement` TR-6.4: 输出格式清晰，有总结统计
- **Notes**: 参考 onnx-quantized 变体的验证模式和 xmtools/verify_wheel.py 风格

## [ ] Task 7: 编写 README.md 使用文档
- **Priority**: medium
- **Depends On**: Task 2, Task 4, Task 6
- **Description**: 
  - 创建 README.md，包含：
    1. 镜像概述和依赖链说明
    2. 版本信息表格（Python/LLVM/Cmake/Ninja/PyTorch/ONNX/ORT等）
    3. 构建步骤（本地构建、国内镜像构建）
    4. 运行命令（含 -v 挂载 npuusertools/npu_tvm/models 的完整示例）
    5. 验证方法（运行verify-deployment.py）
    6. 服务访问（SSH/Jupyter/Docker API端口和凭证）
    7. 环境变量说明
    8. 快速开始：在容器内构建npuusertools的示例命令
    9. 目录结构说明
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `human-judgement` TR-7.1: 文档结构清晰，包含所有必要章节
  - `human-judgement` TR-7.2: 命令示例可直接复制使用
  - `programmatic` TR-7.3: Markdown链接有效（无断链）
- **Notes**: 参考 onnx-quantized/README.md 的风格和结构

## [ ] Task 8: Dockerfile语法检查和静态验证
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 使用 hadolint 或 docker build --pull=false --no-cache 进行语法检查（如果本地有Docker）
  - 验证所有 COPY 源文件存在
  - 验证 shell 脚本语法（bash -n）
  - 验证 Python 脚本语法（python -m py_compile）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有 shell 脚本通过 bash -n 语法检查
  - `programmatic` TR-8.2: 所有 Python 脚本通过 py_compile 语法检查
  - `programmatic` TR-8.3: Dockerfile 中 COPY 的源文件都存在
  - `human-judgement` TR-8.4: Dockerfile 分层合理，Layer缓存友好（apt→pip→copy配置→cleanup）

## [ ] Task 9: 端到端构建验证（如Docker可用）
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 执行 build.sh 构建镜像
  - 运行容器并执行 verify-deployment.py
  - 测试挂载 npuusertools 和 npu_tvm 后 PYTHONPATH 是否正确
  - 测试 devuser 登录和权限
  - 验证所有服务端口正常监听
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-9
- **Test Requirements**:
  - `programmatic` TR-9.1: 镜像构建成功，无错误
  - `programmatic` TR-9.2: docker run 启动容器无错误
  - `programmatic` TR-9.3: verify-deployment.py 所有项PASS
  - `programmatic` TR-9.4: 挂载后 python -c "import xmnn" 路径检测正确（如果挂载了npuusertools）
  - `programmatic` TR-9.5: SSH可连接，Jupyter可访问（端口检查）
- **Notes**: 如果当前环境没有运行中的Docker，此任务可由用户在有Docker的环境中执行验证
