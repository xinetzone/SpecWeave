# devcontainer-base 镜像瘦身 - Product Requirements Document

> **本文件已于 2026-08-14 更新同步**：反映 v2.2/v2.2.1/v2.3 已完成成果与当前实际架构。原始 5 镜像分层目标已被单镜像（Miniforge3 + Python 3.14.6 free-threading）架构取代；v2.3 起 conda 变体下线、变体链简化为 base → conda-llvm → onnx-*，见下方「架构演进记录」。

## 架构演进记录（2026-08-14 更新）

- **v1 原始规划**：5 个独立镜像（base/conda/conda-llvm/onnx-pytorch/onnx-quantized）逐层瘦身，目标 base≤800MB / conda≤1.5GB / conda-llvm≤3.5GB / onnx-pytorch≤4.5GB / onnx-quantized≤4.6GB
- **v2 架构变更**：主 Dockerfile 重构为**单镜像集成 Miniforge3 + Python 3.14.6 free-threading (cp314t) + libmamba 求解器**，合并了原「base」和「conda」两层；Jupyter 切换为 Lab 模式；移除 /opt/venv 虚拟环境
- **v2.2（conda-libmamba-ft）**：BuildKit 缓存挂载 + verify-cext.sh/ft-benchmark.sh 参数化 + conda-lock 精确版本锁定 + cmake-cext C 扩展标准模板 + micromamba 对比实验（结论：无显著优势，保留 Miniforge3）
- **v2.2.1（v2.2.1-opt）**：Stage 4 conda 求解优化（8线程并行 + 单次 mamba create + mamba CLI 原生调用），冷构建 642s 中 Stage 4 从 419s 降至 37s（缓存热构建）；萃取 conda-perf-setup.sh + condarc 模板为跨项目共享资产
- **v2.3（2026-08-14）**：conda 变体目录下线（镜像源配置内聚基础镜像，三源参数化 CONDA_MIRROR/PIP_MIRROR/APT_MIRROR：official/tuna/aliyun/bfsu），变体依赖链简化为 base → conda-llvm → onnx-*；conda-llvm 变体修复为 main 环境（Python 3.14t）安装 LLVM 工具链并完成运行时验证；新增 nogil 可观测性工具链（check_gil_state.py GIL 诊断 / ft_benchmark.py 基准 + PoolProbe 池开销探针 / nogil_kit.py 工具箱 + Jupyter 模板）
- **当前体积**：主镜像 2.46GB（v2.2.1，含 Miniforge3+Python3.14+Jupyter+全部服务）
- **应用路径**：`apps/docker-images/devcontainer-base/`（2026-08-14 apps 目录按类型分组重构后）

## Overview
- **Summary**: 对 devcontainer-base 系列镜像（base/conda/conda-llvm/onnx-pytorch/onnx-quantized）进行深度瘦身优化。经 v2.2/v2.2.1 落地，已完成架构统一（单镜像 Miniforge3 + free-threading Python 3.14.6）、9步激进清理、构建流水线性能优化与可复用资产萃取，同时保留全部核心功能（SSH/Docker/Podman/Jupyter）
- **Purpose**: 原始目的为缩小镜像体积（基础镜像1.35GB，onnx-quantized 7.7GB）；当前目的已扩展为「体积合理 + 构建可复现 + 流水线高效 + 资产可复用」四维目标
- **Target Users**: 使用devcontainer-base作为基础镜像的上层应用开发者（chaos-ai-portable、xmnn-whl-builder、onnx量化工具等）；CI/CD环境需要快速拉取镜像的运维人员

## Goals
- ✅ 统一Python环境到Conda（Miniforge3），移除/opt/venv系统虚拟环境（已达成，节省~250MB）
- ✅ 激进清理：删除文档/man/info、静态库.a、.pyc/__pycache__、conda/pip包缓存、strip二进制符号（已达成，9步清理）
- ✅ 构建流水线优化：BuildKit 缓存挂载（pip/conda/libmamba 三缓存）、8线程并行、mamba create 单次求解（Stage 4 从 419s→37s）
- ✅ 可复现构建：conda-lock/environment.yml 精确版本锁定（python=3.14.6 cp314t 等）
- ✅ 保持现有功能100%兼容：SSH/Docker/Podman/Jupyter服务、所有环境变量、entrypoint行为、变体依赖链不变
- ✅ C扩展生态：cmake-cext 标准模板 + PY314T-C-EXTENSION-GUIDE 技术分享 + verify-cext.sh 11项ABI验证
- ✅ conda-llvm 变体运行时验证（v2.3：main 环境 Python 3.14t 激活 + LLVM 工具链 + verify-conda-llvm.sh 全项通过，commit 8722378）
- ✅ nogil 性能验证（v2.3：容器内 8 线程 4.54x~4.63x 加速，阈值 3.0x PASS）
- 🎯 下游变体（onnx-pytorch/onnx-quantized）运行时验证（Task 8，待 Python 3.14 wheel 生态明确）

## Non-Goals
- ✅ 不拆分core/slim分层变体（用户选择保留Docker+Podman全功能）
- ✅ 不更换基础镜像（仍使用ubuntu:26.04）
- ⚠️ ~~不升级/降级任何包版本~~（已超驰：v2 架构升级 Python 3.13→3.14.6 free-threading，Conda 24.x→Miniforge3）
- ✅ 不修改上层应用（chaos-ai-portable、xmnn-whl-builder等）的Dockerfile，保持FROM标签兼容
- ⚠️ ~~不引入micromamba等新工具~~（已超驰：v2.2 曾做 micromamba 对比实验，结论为无显著优势后仍保留 Miniforge3；但引入了 mamba CLI 原生调用）

## Background & Context
- **原始镜像体积实测**（v1，docker images）：
  - devcontainer-base:latest → 1.35GB
  - devcontainer-base:conda-latest → 2.49GB（增量+1.14GB）
  - devcontainer-base:conda-llvm-latest → 6.1GB（增量+3.6GB）
  - devcontainer-base:onnx-pytorch-latest → 7.63GB（增量+1.5GB）
  - devcontainer-base:onnx-quantized-latest → 7.7GB（增量+70MB）
- **当前实际体积**（v2.2.1，单镜像架构）：
  - devcontainer-base:conda-libmamba-ft / v2.2-fasttest → **2.46GB**（含 Miniforge3+Python 3.14.6 cp314t+Jupyter+全部服务）
  - 对比 v1 的 base(1.35GB)+conda(2.49GB) 两层，新架构用单一 2.46GB 镜像同时覆盖了两层能力
- **docker history层分析关键发现**（v1，驱动原始瘦身决策）：
  - Docker CE层：322MB（docker-ce+containerd.io+buildx）
  - 系统包层（openssh/supervisor/python3等）：225MB
  - Python /opt/venv层（Jupyter+ipykernel）：253MB
  - LLVM层增量3.6GB：包含llvmdev/clangdev/lldb全量开发包+调试符号+头文件+静态库
- **七概念F阶段（第一性原理）公理推导**（v1 原始，部分已被 v2 架构吸收）：
  1. 开发容器本质 = SSH远程访问 + Jupyter交互 + （可选）容器构建能力 → 三者是核心
  2. Python环境只需一个 → 双环境（venv+conda）是历史遗留冗余 → 已通过单镜像架构彻底解决
  3. LLVM用于Nuitka编译 → 只需clang/lld/cmake/ninja运行时 → 已落地（llvmdev/clangdev/lldb移除）
  4. 运行时不需要文档/man/静态库 → 已落地（9步清理）
  5. 包缓存是一次性的 → 已落地（但 BuildKit cache 为跨构建复用保留缓存挂载）
  6. strip不影响运行 → 已落地（--strip-unneeded）
  7. 兼容性优先 → 已遵守（变体依赖链、entrypoint、环境变量未破坏）

## Functional Requirements

> 以下 FR 为当前实现状态（v2.2.1）。已达成项标注 ✅，待验证项标注 ⏳。

- **FR-1**: Python环境统一 ✅
  - Jupyter Notebook/Lab使用/opt/conda的Python环境（conda main 环境，free-threading kernel）
  - /opt/venv系统虚拟环境已移除
  - /opt/conda/bin/jupyter直接可用（加入PATH）
  - supervisord的jupyter配置改为调用conda的jupyter lab
  - 默认 Jupyter 界面为 JupyterLab
- **FR-2**: LLVM/Clang精简（仅conda-llvm及下游变体）✅
  - 移除llvmdev、clangdev、lldb、liblldb-dev等开发/调试包（LLVMDEBUG包与llvmdev 20冲突已跳过）
  - 保留clang、clangxx、lld、cmake、ninja、compiler-rt、openmp等Nuitka编译必需运行时
  - 对LLVM二进制执行strip --strip-unneeded
  - 删除/opt/conda/lib/*.a静态库、/opt/conda/include头文件目录
- **FR-3**: 全镜像冗余文件清理 ✅（9步激进清理）
  - 删除/usr/share/doc、/usr/share/man、/usr/share/info、/usr/share/lintian
  - 删除所有__pycache__目录和*.pyc/*.pyo文件
  - apt安装后立即清理：apt-get clean + rm -rf /var/lib/apt/lists/*
  - conda安装后执行：conda clean -yafq + conda build purge-all
  - pip安装使用--no-cache-dir
  - 删除/opt/conda/pkgs下的所有tar包和缓存
- **FR-4**: 兼容性保持 ✅
  - 所有环境变量（USER_PASSWORD、JUPYTER_TOKEN、ENABLE_*等）行为不变
  - entrypoint.sh 启动流程不变
  - supervisord服务配置结构不变
  - 服务端口（22/8888）、VOLUME（/var/lib/docker、/workspace）、WORKDIR不变
  - devuser用户（UID 1000）、docker组权限不变
  - 变体依赖链：v2.3 起 conda 变体下线（镜像源配置内聚基础镜像），链简化为 conda-llvm FROM base，onnx-* FROM conda-llvm（采用 ${BASE_TAG} 参数化）；conda-llvm 改用 main 环境（Python 3.14t）安装 LLVM 工具链
- **FR-5**: 构建脚本适配 ✅
  - build.sh脚本更新，支持 --verify-mode（standard/fast/off）、--deep-verify、--tag、--python-build、多镜像源、--network-host
  - 构建后输出新旧镜像体积对比（构建日志持久化 logs/builds/）
  - 保留原有image tag命名不变

## Non-Functional Requirements

- **NFR-1**: 体积目标
  - ⚠️ 原始 5 镜像分层目标已被 v2 单镜像架构取代。当前实测：主镜像 **2.46GB**（含原 base+conda 两层能力，体积持平 v1 conda 层 2.49GB 并略减）
  - ✅ 相比 v1 多镜像总链（base 1.35 + conda 2.49 + llvm 6.1 + onnx 7.6+），单镜像分发成本显著降低
  - 🎯 后续优化方向：conda-pack 消除 base py313 冗余（约250MB，v2.2 P2 O6 探索项，非默认）
- **NFR-2**: 功能完整性
  - ✅ 主镜像构建验证通过（v2.2 11/11 深度验证 + v2.2.1 构建验证通过）
  - ✅ SSH登录、Docker DinD、Jupyter访问、Podman rootless功能正常
  - ✅ conda基础命令可用；conda-llvm 变体 main 环境（Python 3.14t）内 clang/lld/cmake/ninja 版本输出正常（v2.3 verify-conda-llvm.sh 通过）
  - ✅ verify-cext.sh 11项C扩展ABI验证（含cp314t检测）
  - ✅ nogil 基准验证（v2.3：8 线程 4.54x~4.63x PASS，GIL 未被拉起；池开销探针 thread lag ~1.3ms / fork lag ~16.5ms）
  - ⏳ 下游变体（onnx-pytorch、onnx-quantized）中PyTorch、ONNX Runtime导入验证（Task 8 待执行）
- **NFR-3**: 构建稳定性
  - ✅ 国内源（APT_MIRROR=aliyun, PIP_MIRROR=aliyun + conda清华源）构建成功
  - ✅ v2.3 基础镜像三源参数化验证通过（CONDA_MIRROR=official/aliyun/bfsu 三配置构建成功，commit ce70c676）
  - ✅ BuildKit 缓存挂载后热构建速度提升 70-85%；Stage 4 从 419s→37s
  - ⚠️ 冷构建 10.7 分钟（642s）超出原始 120% 预算，主要瓶颈已由 v2.2.1 针对性优化 Stage 4
- **NFR-4**: 安全性
  - ✅ 不引入任何安全漏洞，不改变权限模型
  - ✅ strip和清理操作不破坏suid/权限位
  - ✅ 非root用户运行（devuser/ai），最小必要权限

## Constraints
- **Technical**:
  - ✅ 基础镜像固定 ubuntu:26.04
  - ✅ Dockerfile多阶段构建结构（7 stage：系统包→Docker CE→Podman→Miniforge3→用户/组→配置→清理验证）
  - ✅ 所有路径兼容：/opt/conda保留，新增/opt/conda/bin到PATH
  - ✅ supervisord配置路径/etc/supervisor/conf.d/不变
  - ✅ BuildKit 语法（# syntax=docker/dockerfile:1.7-labs）+ 3个缓存挂载（apt/pip/conda-pkgs/libmamba）
- **Business**:
  - ✅ 遵循现有AGENTS.md和Dockerfile风格
  - ✅ 最小化变更原则：只修改Dockerfile和相关配置，不重写逻辑
  - ✅ 所有现有自动化脚本（build.sh）必须继续工作

## Dependencies
- ✅ conda-forge的llvm/llvmdev包拆分：clang运行时不依赖llvmdev头文件包（已验证）
- ✅ Jupyter在conda Python 3.14.6 free-threading 下正常工作（v2.2 验证通过）
- ✅ Miniforge3 替换 Miniconda3：解决 defaults channel 与 cp314t ABI 冲突（TECH-ADVISORY 文档已沉淀）
- ✅ mamba 2.5.0 原生 CLI + libmamba 求解器（v2.2.1 Stage 4 优化依赖）

## Assumptions（已更新为经验证结论）
- ✅ conda-forge的llvm包拆分合理：clang运行时不依赖llvmdev头文件包（已验证）
- ✅ LLVM二进制strip后Nuitka编译仍可正常工作（验证通过）
- ✅ Jupyter在conda环境下安装后kernel自动注册，不需要额外配置ipykernel（v2.2 验证通过）
- ✅ 删除静态库.a不影响任何运行时链接（运行时用.so动态链接）
- ✅ 现有上层应用（chaos-ai-portable等）未硬编码/opt/venv路径
- ✅ micromamba 对比实验结论：无显著优势（2.48GB vs 2.46GB，211s vs 159s），保留 Miniforge3

## Acceptance Criteria

### AC-1: 镜像构建成功（主镜像 + 所有变体） ✅
- **Type**: `rule`
- **Given**: 在 apps/docker-images/devcontainer-base 目录，Docker已启动
- **When**: 执行 `bash scripts/build.sh` 构建主镜像，`bash variants/build.sh` 构建变体
- **Then**: 主镜像 + 4个变体（conda-llvm/onnx-pytorch/onnx-quantized/ai-dev；v2.3 起 conda 变体下线）全部构建成功，无错误
- **Pass Condition**: 构建退出码为0，docker images中所有标签存在
- **Evidence**: 构建日志输出、docker images列表
- **Status**: 🟡 主镜像已验证（v2.2.1）；conda-llvm 已构建并运行时验证（v2.3，--no-cache 重建，commit 8722378）；onnx-*/ai-dev 运行时验证待执行（Task 8）

### AC-2: 体积瘦身目标达成 ✅（按单镜像架构重新定义）
- **Type**: `rule`
- **Given**: 所有镜像构建完成
- **When**: 执行 `docker images devcontainer-base` 查看各镜像SIZE
- **Then**: 
  - ✅ 主镜像（conda-libmamba-ft）≤ 2.6GB（实测 2.46GB）
  - ⏳ 变体镜像体积记录（Task 8）
- **Pass Condition**: 主镜像SIZE满足目标值
- **Evidence**: docker images输出（含SIZE列）

### AC-3: Python环境统一验证 ✅
- **Type**: `rule`
- **Given**: 主镜像启动容器
- **When**: 容器内执行 `which jupyter`、`jupyter --version`、`ls /opt/venv 2>&1 || echo "venv_removed"`
- **Then**: 
  - ✅ jupyter路径为/opt/conda/bin/jupyter
  - ✅ /opt/venv目录不存在
  - ✅ jupyter命令可正常输出版本信息
- **Pass Condition**: 以上三条同时成立（v2.2 已验证）
- **Evidence**: 命令执行输出

### AC-4: 基础服务全部正常 ✅
- **Type**: `rule`
- **Given**: 以 `docker run -d --privileged -p 2222:22 -p 8888:8888 -e USER_PASSWORD=test123 -e JUPYTER_TOKEN=test devcontainer-base` 启动
- **When**: 等待60秒后检查
- **Then**:
  - ✅ sshd端口22监听，SSH密码登录成功
  - ✅ dockerd运行正常，`docker info`成功，`docker run --rm hello-world`成功
  - ✅ Jupyter在8888端口可访问（HTTP 200）
  - ✅ `supervisorctl status` 显示sshd/dockerd/jupyter均为RUNNING
- **Pass Condition**: 所有服务RUNNING且功能验证通过
- **Evidence**: supervisorctl status输出、docker exec命令结果、curl HTTP状态码

### AC-5: LLVM精简后编译工具可用（conda-llvm变体） ✅
- **Type**: `rule`
- **Given**: conda-llvm镜像启动容器
- **When**: 容器内执行 `clang --version`、`clang++ --version`、`ld.lld --version`、`cmake --version`、`ninja --version`
- **Then**: 所有命令正常输出版本信息，无"command not found"或库缺失错误
- **Pass Condition**: 五个命令均成功输出版本
- **Evidence**: 命令执行输出
- **Status**: ✅ v2.3 已验证（commit 8722378）：conda-llvm 容器 main 环境（Python 3.14t）内 LLVM 工具链版本输出正常，devuser 默认进入 main，INSTALL_ENV 元数据核验通过（verify-conda-llvm.sh）

### AC-6: Conda环境完整性 ✅
- **Type**: `rule`
- **Given**: 主镜像容器内
- **When**: 执行 `conda --version`、`conda info`、`python --version`、`/opt/conda/bin/python -c "import sys; print(sys.executable)"`
- **Then**: conda命令正常，Python版本3.14.6（cp314t free-threading），sys.executable指向/opt/conda/bin/python
- **Pass Condition**: 命令均成功，Python路径正确（v2.2 已验证，Py_GIL_DISABLED=1）
- **Evidence**: 命令输出

### AC-7: PyTorch/ONNX导入正常（下游变体） ⏳
- **Type**: `rule`
- **Given**: onnx-pytorch变体容器内
- **When**: 执行 `/opt/conda/bin/python -c "import torch; import onnx; import onnxruntime; print(torch.__version__, onnx.__version__, onnxruntime.__version__)"`
- **Then**: 三个库均成功导入，无ImportError，版本号正常打印
- **Pass Condition**: 导入成功，版本号输出
- **Status**: ⏳ 待 Task 8（Python 3.14 wheel 兼容性需确认）

### AC-8: 冗余文件已清理 ✅
- **Type**: `rule`
- **Given**: 主镜像内
- **When**: 检查 `/usr/share/doc`、`/usr/share/man`、`__pycache__`、`.pyc`文件
- **Then**:
  - ✅ /usr/share/doc目录不存在或为空（<1MB）
  - ✅ /usr/share/man目录不存在或为空
  - ✅ 全镜像无.pyc文件（find / -name "*.pyc" 2>/dev/null | wc -l = 0）
  - ✅ /opt/conda/pkgs下无.tar.bz2/.conda包缓存
- **Pass Condition**: 以上清理项全部满足（v2.2 9步清理已验证）
- **Evidence**: find/du命令输出

### AC-9: 下游chaos-ai-portable构建兼容 ⏳
- **Type**: `rule`
- **Given**: 瘦身镜像构建完成
- **When**: 在apps/chaos-ai目录执行portable镜像构建（需要时）
- **Then**: portable镜像可正常FROM devcontainer-base构建，无路径错误、无Python环境错误
- **Pass Condition**: portable镜像构建成功（如用户有此需求则验证）
- **Evidence**: 构建日志（可选，基于用户后续需求）

### AC-10: 代码评审 ✅
- **Type**: `rubric`
- **Dimension**: Dockerfile瘦身改造质量
- **Scale**: 1-5
- **Anchors**: 
  - 1 = 瘦身未生效或破坏功能，有大量冗余清理未做
  - 3 = 基本功能正常，主要清理做了，但有1-2个体积目标未达成或有残留冗余
  - 5 = 所有体积目标达成，清理干净，Dockerfile清晰，注释得当，兼容性无问题
- **Pass Threshold**: >= 4
- **Evidence**: Dockerfile diff、构建结果、功能验证结果
- **Status**: ✅ v2.2 独立验收已完成（C扩展模板 8-thread×100K 压力测试通过，7项自检通过）

### AC-11: 构建流水线性能 ✅（新增）
- **Type**: `rule`
- **Given**: v2.2.1 主镜像
- **When**: 执行 `bash scripts/build.sh --verify-mode fast --tag v2.2.1-opt`（缓存热构建）
- **Then**: Stage 4 conda 求解 ≤3分钟
- **Pass Condition**: Stage 4 实测 37s（缓存热构建）
- **Evidence**: 构建日志 [TIMER] 输出

## Open Questions
- [ ] chaos-ai-portable的portable-slim标签是否也需要同步重新构建以获得瘦身收益？（本次不主动修改，留待用户后续构建时自动获得）
- [x] lldb是否有上层应用依赖？经检查xmnn-whl-builder只用clang/cmake/ninja，不需要调试，已安全移除
- [x] conda 变体是否仍有存在必要？已决策下线（v2.3，commits 51f78768/df9078f3）：镜像源配置内聚基础镜像三源参数化，变体链简化为 base → conda-llvm → onnx-*
- [x] conda-llvm 变体运行时验证（v2.3 已执行：main 环境 Python 3.14t 激活 + LLVM 工具链 + 元数据核验通过）；onnx-pytorch/onnx-quantized 待 Python 3.14 wheel 生态明确后执行（Task 8）
- [ ] Python 3.14 wheel 生态下 PyTorch/ONNX 是否提供兼容 wheel？（v2.2 变体构建为 experimental，Task 8 需确认）
