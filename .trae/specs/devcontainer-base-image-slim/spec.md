# devcontainer-base 镜像瘦身 - Product Requirements Document

## Overview
- **Summary**: 对 devcontainer-base 系列镜像（base/conda/conda-llvm/onnx-pytorch/onnx-quantized）进行深度瘦身优化，目标总体积减少40%-50%，同时保留全部核心功能（SSH/Docker/Podman/Jupyter）
- **Purpose**: 当前镜像体积过大（基础镜像1.35GB，onnx-quantized 7.7GB），导致镜像拉取/推送慢、磁盘占用高、CI/CD效率低；双Python环境冗余、LLVM全量安装含开发调试符号、缺少激进的冗余文件清理是主要膨胀源
- **Target Users**: 使用devcontainer-base作为基础镜像的上层应用开发者（chaos-ai-portable、xmnn-whl-builder、onnx量化工具等）；CI/CD环境需要快速拉取镜像的运维人员

## Goals
- 统一Python环境到Conda，移除/opt/venv系统虚拟环境（节省~250MB）
- LLVM/Clang工具链精简：移除lldb调试器、llvmdev/clangdev开发包、strip二进制符号（预期节省1.5-2GB）
- 全镜像激进清理：删除文档/man/info、静态库.a、.pyc/__pycache__、conda/pip包缓存
- 保持现有功能100%兼容：SSH/Docker/Podman/Jupyter服务、所有环境变量、entrypoint行为、变体依赖链不变
- 基础镜像（base）目标≤800MB，conda≤1.5GB，conda-llvm≤3.5GB，onnx-pytorch≤4.5GB，onnx-quantized≤4.6GB

## Non-Goals
- 不拆分core/slim分层变体（用户选择保留Docker+Podman全功能）
- 不更换基础镜像（仍使用ubuntu:26.04）
- 不升级/降级任何包版本（仅调整包选择和清理策略）
- 不修改上层应用（chaos-ai-portable、xmnn-whl-builder等）的Dockerfile，保持FROM标签兼容
- 不引入micromamba等新工具（保持miniconda3不变以降低风险）

## Background & Context
- **当前镜像体积实测**（docker images）：
  - devcontainer-base:latest → 1.35GB
  - devcontainer-base:conda-latest → 2.49GB（增量+1.14GB）
  - devcontainer-base:conda-llvm-latest → 6.1GB（增量+3.6GB）
  - devcontainer-base:onnx-pytorch-latest → 7.63GB（增量+1.5GB）
  - devcontainer-base:onnx-quantized-latest → 7.7GB（增量+70MB）
- **docker history层分析关键发现**：
  - Docker CE层：322MB（docker-ce+containerd.io+buildx）
  - 系统包层（openssh/supervisor/python3等）：225MB
  - Python /opt/venv层（Jupyter+ipykernel）：253MB
  - Conda安装层（miniconda+Python3.14基础环境）：未单独显示，但从增量看~253MB+冗余文件
  - LLVM层增量3.6GB：包含llvmdev/clangdev/lldb全量开发包+调试符号+头文件+静态库
- **七概念F阶段（第一性原理）公理推导**：
  1. 开发容器本质 = SSH远程访问 + Jupyter交互 + （可选）容器构建能力 → 三者是核心，其他都是衍生
  2. Python环境只需一个 → 双环境（venv+conda）是历史遗留冗余，Jupyter可直接用conda的Python
  3. LLVM用于Nuitka编译 → 只需clang/lld/cmake/ninja运行时，不需要lldb调试器、llvmdev/clangdev头文件和静态库
  4. 运行时不需要文档/man/静态库 → 这些是构建/开发时产物，运行容器中完全无用
  5. 包缓存是一次性的 → conda/pip/apt安装后必须立即彻底清理，不能留在最终镜像
  6. strip不影响运行 → 移除二进制符号表和调试信息，不影响功能，显著减小体积
  7. 兼容性优先 → 瘦身不能破坏现有上层应用依赖，不能改变ENTRYPOINT/WORKDIR/环境变量/服务端口

## Functional Requirements
- **FR-1**: Python环境统一
  - Jupyter Notebook/Lab使用/opt/conda的Python环境
  - 移除/opt/venv系统虚拟环境，不再从builder阶段复制venv
  - /opt/conda/bin/jupyter相关命令直接可用（加入PATH）
  - Jupyter kernel使用conda环境Python
  - supervisord的jupyter配置改为调用conda的jupyter
- **FR-2**: LLVM/Clang精简（仅conda-llvm及下游变体）
  - 移除llvmdev、clangdev、lldb、liblldb-dev等开发/调试包
  - 保留clang、clangxx、lld、cmake、ninja、compiler-rt、openmp等Nuitka编译必需运行时
  - 对LLVM二进制执行strip --strip-unneeded
  - 删除/opt/conda/lib/*.a静态库、/opt/conda/include头文件目录（运行时不需要）
- **FR-3**: 全镜像冗余文件清理
  - 删除/usr/share/doc、/usr/share/man、/usr/share/info、/usr/share/lintian
  - 删除所有__pycache__目录和*.pyc/*.pyo文件
  - apt安装后立即清理：apt-get clean + rm -rf /var/lib/apt/lists/*
  - conda安装后执行：conda clean -yafq + conda build purge-all
  - pip安装使用--no-cache-dir
  - 删除/opt/conda/pkgs下的所有tar包和缓存
- **FR-4**: 兼容性保持
  - 所有环境变量（USER_PASSWORD、JUPYTER_TOKEN、ENABLE_*等）行为不变
  - entrypoint.sh 6步启动流程不变
  - supervisord服务配置结构不变
  - 服务端口（22/8888）、VOLUME（/var/lib/docker、/workspace）、WORKDIR不变
  - devuser用户（UID 1000）、docker组权限不变
  - 变体依赖链不变：conda FROM base，conda-llvm FROM conda，onnx-* FROM conda-llvm
- **FR-5**: 构建脚本适配
  - build.sh脚本更新，构建后输出新旧镜像体积对比
  - 保留原有image tag命名不变

## Non-Functional Requirements
- **NFR-1**: 体积目标（构建后）
  - base (latest): ≤ 800MB（vs 当前1.35GB，瘦≥41%）
  - conda: ≤ 1.5GB（vs 当前2.49GB，瘦≥40%）
  - conda-llvm: ≤ 3.5GB（vs 当前6.1GB，瘦≥43%）
  - onnx-pytorch: ≤ 4.5GB（vs 当前7.63GB，瘦≥41%）
  - onnx-quantized: ≤ 4.6GB（vs 当前7.7GB，瘦≥40%）
- **NFR-2**: 功能完整性
  - 所有现有AC（AC-1到AC-14）必须100%通过
  - SSH登录、Docker DinD、Jupyter访问、Podman rootless功能正常
  - conda基础命令可用，clang --version、cmake --version、ninja --version正常输出
  - 下游变体（onnx-pytorch、onnx-quantized）中PyTorch、ONNX Runtime导入正常
- **NFR-3**: 构建稳定性
  - 国内源（APT_MIRROR=aliyun, PIP_MIRROR=aliyun + conda清华源）构建成功
  - 构建时间不超过原有时间的120%（清理操作开销可接受）
- **NFR-4**: 安全性
  - 不引入任何安全漏洞，不改变权限模型
  - strip和清理操作不破坏suid/权限位

## Constraints
- **Technical**:
  - 基础镜像固定 ubuntu:26.04
  - 不改变Dockerfile多阶段构建结构（仍用jupyter-builder阶段，但venv构建改为conda jupyter安装）
  - 所有路径兼容：/opt/conda保留，只是新增/opt/conda/bin到PATH
  - supervisord配置路径/etc/supervisor/conf.d/不变
- **Business**:
  - 遵循现有AGENTS.md和Dockerfile风格
  - 最小化变更原则：只修改Dockerfile和相关配置，不重写逻辑
  - 所有现有自动化脚本（build.sh）必须继续工作
- **Dependencies**:
  - 依赖conda-forge的llvm/llvmdev包拆分：确认clang、lld、cmake、ninja不依赖llvmdev运行
  - 依赖Jupyter在conda Python 3.14下正常工作

## Assumptions
- conda-forge的llvm包拆分合理：clang运行时不依赖llvmdev头文件包（经验证：conda install clang默认不装llvmdev，是之前显式安装了llvmdev/clangdev）
- LLVM二进制strip后Nuitka编译仍可正常工作（Nuitka调用clang，只需要二进制可执行，不需要调试符号）
- Jupyter在conda环境下安装后kernel自动注册，不需要额外配置ipykernel
- 删除静态库.a不影响任何运行时链接（运行时用.so动态链接）
- 现有上层应用（chaos-ai-portable等）未硬编码/opt/venv路径（经检查portable.Dockerfile只激活conda环境，未引用/opt/venv）

## Acceptance Criteria

### AC-1: 镜像构建成功（所有变体）
- **Type**: `rule`
- **Given**: 在apps/devcontainer-base目录，Docker已启动
- **When**: 执行 `bash scripts/build.sh` 构建所有变体
- **Then**: base/conda/conda-llvm/onnx-pytorch/onnx-quantized五个镜像全部构建成功，无错误
- **Pass Condition**: 构建退出码为0，docker images中所有标签存在
- **Evidence**: 构建日志输出、docker images列表

### AC-2: 体积瘦身目标达成
- **Type**: `rule`
- **Given**: 所有变体构建完成
- **When**: 执行 `docker images devcontainer-base` 查看各镜像SIZE
- **Then**: 
  - base ≤ 800MB
  - conda ≤ 1.5GB
  - conda-llvm ≤ 3.5GB
  - onnx-pytorch ≤ 4.5GB
  - onnx-quantized ≤ 4.6GB
- **Pass Condition**: 所有变体SIZE均满足目标值
- **Evidence**: docker images输出（含SIZE列）

### AC-3: Python环境统一验证
- **Type**: `rule`
- **Given**: base镜像启动容器
- **When**: 容器内执行 `which jupyter`、`jupyter --version`、`ls /opt/venv 2>&1 || echo "venv_removed"`
- **Then**: 
  - jupyter路径为/opt/conda/bin/jupyter
  - /opt/venv目录不存在
  - jupyter命令可正常输出版本信息
- **Pass Condition**: 以上三条同时成立
- **Evidence**: 命令执行输出

### AC-4: 基础服务全部正常
- **Type**: `rule`
- **Given**: 以 `docker run -d --privileged -p 2222:22 -p 8888:8888 -e USER_PASSWORD=test123 -e JUPYTER_TOKEN=test devcontainer-base` 启动
- **When**: 等待60秒后检查
- **Then**:
  - sshd端口22监听，SSH密码登录成功
  - dockerd运行正常，`docker info`成功，`docker run --rm hello-world`成功
  - Jupyter在8888端口可访问（HTTP 200）
  - `supervisorctl status` 显示sshd/dockerd/jupyter均为RUNNING
- **Pass Condition**: 所有服务RUNNING且功能验证通过
- **Evidence**: supervisorctl status输出、docker exec命令结果、curl HTTP状态码

### AC-5: LLVM精简后编译工具可用（conda-llvm变体）
- **Type**: `rule`
- **Given**: conda-llvm镜像启动容器
- **When**: 容器内执行 `clang --version`、`clang++ --version`、`ld.lld --version`、`cmake --version`、`ninja --version`
- **Then**: 所有命令正常输出版本信息，无"command not found"或库缺失错误
- **Pass Condition**: 五个命令均成功输出版本
- **Evidence**: 命令执行输出

### AC-6: Conda环境完整性
- **Type**: `rule`
- **Given**: conda变体容器内
- **When**: 执行 `conda --version`、`conda info`、`python --version`、`/opt/conda/bin/python -c "import sys; print(sys.executable)"`
- **Then**: conda命令正常，Python版本3.14.x，sys.executable指向/opt/conda/bin/python
- **Pass Condition**: 命令均成功，Python路径正确
- **Evidence**: 命令输出

### AC-7: PyTorch/ONNX导入正常（下游变体）
- **Type**: `rule`
- **Given**: onnx-pytorch变体容器内
- **When**: 执行 `/opt/conda/bin/python -c "import torch; import onnx; import onnxruntime; print(torch.__version__, onnx.__version__, onnxruntime.__version__)"`
- **Then**: 三个库均成功导入，无ImportError，版本号正常打印
- **Pass Condition**: 导入成功，版本号输出
- **Evidence**: 命令输出

### AC-8: 冗余文件已清理
- **Type**: `rule`
- **Given**: base/conda/conda-llvm镜像内
- **When**: 检查 `/usr/share/doc`、`/usr/share/man`、`__pycache__`、`.pyc`文件
- **Then**:
  - /usr/share/doc目录不存在或为空（<1MB）
  - /usr/share/man目录不存在或为空
  - 全镜像无.pyc文件（find / -name "*.pyc" 2>/dev/null | wc -l = 0）
  - /opt/conda/pkgs下无.tar.bz2/.conda包缓存
- **Pass Condition**: 以上清理项全部满足
- **Evidence**: find/du命令输出

### AC-9: 下游chaos-ai-portable构建兼容
- **Type**: `rule`
- **Given**: 瘦身镜像构建完成
- **When**: 在apps/chaos-ai目录执行portable镜像构建（需要时）
- **Then**: portable镜像可正常FROM devcontainer-base构建，无路径错误、无Python环境错误
- **Pass Condition**: portable镜像构建成功（如用户有此需求则验证）
- **Evidence**: 构建日志（可选，基于用户后续需求）

### AC-10: 代码评审
- **Type**: `rubric`
- **Dimension**: Dockerfile瘦身改造质量
- **Scale**: 1-5
- **Anchors**: 
  - 1 = 瘦身未生效或破坏功能，有大量冗余清理未做
  - 3 = 基本功能正常，主要清理做了，但有1-2个体积目标未达成或有残留冗余
  - 5 = 所有体积目标达成，清理干净，Dockerfile清晰，注释得当，兼容性无问题
- **Pass Threshold**: >= 4
- **Evidence**: Dockerfile diff、构建结果、功能验证结果

## Open Questions
- [ ] chaos-ai-portable的portable-slim标签是否也需要同步重新构建以获得瘦身收益？（本次不主动修改，留待用户后续构建时自动获得）
- [ ] lldb是否有上层应用依赖？经检查xmnn-whl-builder只用clang/cmake/ninja，不需要调试，可安全移除
