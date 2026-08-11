# Chaos AI 可移植Docker镜像优化 - The Implementation Plan

## [x] Task 1: 创建新的portable.Dockerfile基础框架
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建独立的Dockerfile（命名为portable.Dockerfile或重构现有Dockerfile，建议保留原Dockerfile，新建portable.Dockerfile作为独立可移植版本）
  - 第一阶段：基于Ubuntu 26.04基础镜像，配置apt镜像源，安装基础系统包（tzdata、curl、wget、git、build-essential、g++、openssh-server、sudo、supervisor等）
  - 配置时区Asia/Shanghai（三层保证：tzdata+ln+ENV TZ）
  - 配置BuildKit缓存挂载（apt/conda/pip）
- **Acceptance Criteria Addressed**: AC-1, NFR-1
- **Deliverables**: `portable.Dockerfile` (544行, 8阶段构建)
- **Notes**: 保留原Dockerfile不动，新建portable.Dockerfile作为独立可移植版本

## [x] Task 2: 安装Miniconda并创建py314专用环境
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 下载并安装Miniconda3到/opt/conda
  - 配置conda镜像源（支持bfsu/tuna/official通过CONDA_MIRROR参数）
  - 创建py314 conda环境，安装Python 3.14+
  - 配置conda默认不自动激活base，而是默认激活py314
  - 安装基础Python包：pip、ipython、ipykernel、jupyterlab等
  - 配置pip镜像源
  - 设置/opt/conda目录权限为ai用户可读写
- **Acceptance Criteria Addressed**: AC-4, AC-9, AC-10, FR-3
- **Deliverables**: Stage 3+4 in portable.Dockerfile

## [x] Task 3: 安装LLVM/CMake/Ninja等NPU构建工具链
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在py314环境中通过conda安装llvmdev 22.1.8、clang 22.1.8、cmake 4.4.0、ninja 1.13.2
  - 安装系统依赖patchelf
  - 安装XMNN构建相关Python包：scikit-build-core、nuitka、invoke、build、decorator、attrs、cloudpickle、typing_extensions、pytest等
  - 验证工具版本符合要求
- **Acceptance Criteria Addressed**: FR-10
- **Deliverables**: Stage 4 in portable.Dockerfile (含llvm-config符号链接修复)

## [x] Task 4: 创建ai用户并配置权限
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 创建ai组（可配置GID），创建ai用户（可配置UID）
  - 配置ai用户home目录/home/ai
  - 根据GRANT_SUDO参数决定是否添加sudo权限
  - 配置sudo免密（如果GRANT_SUDO=yes）
  - 设置/opt/conda、/workspace等目录权限为ai:ai
  - 预创建/workspace子目录：npu_tvm、npuusertools、models、project
  - 配置默认umask 0027（写入/etc/profile、/etc/bash.bashrc、ai用户.bashrc）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8, FR-2, FR-5, FR-6, FR-9
- **Deliverables**: Stage 5 in portable.Dockerfile

## [x] Task 5: 配置多入口环境一致性（Shell/SSH/Jupyter）
- **Priority**: high
- **Depends On**: Task 2, Task 4
- **Description**:
  - 编写/etc/profile.d/conda-init.sh：登录shell自动激活py314环境
  - 配置sshd：禁止root登录（PermitRootLogin no），配置ForceCommand或pam_env加载conda环境
  - 编写sshd启动脚本确保环境变量正确传递
  - 更新Jupyter kernel配置：使用/opt/conda/envs/py314/bin/python，设置正确PATH和PYTHONPATH
  - 安装Jupyter到py314环境，移除/opt/venv（不再需要单独venv）
  - 配置supervisord管理sshd、jupyter、docker等服务
  - 适配chaos-ai-init.sh逻辑到新的profile.d脚本
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7, AC-11, FR-4, FR-8, FR-11
- **Deliverables**: 
  - `config/profile/conda-init.sh`
  - `config/ssh/sshd_config`
  - `config/jupyter/jupyter_notebook_config.py`
  - `config/supervisor/` (主配置+conf.d子目录)

## [x] Task 6: 创建fix-permissions.sh和文档
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 编写/opt/bin/fix-permissions.sh脚本，用于调整挂载卷权限（将/workspace下挂载目录的权限调整为ai用户可访问）
  - 脚本支持指定目标目录，递归修改属主为ai:ai（仅用于首次初始化）
  - 脚本支持dry-run(-d)、verbose(-v)、quiet(-q)模式，含彩色诊断日志
  - 创建/opt/docs/conda-environment-guide.md，说明如何管理conda环境、安装包、创建新环境
  - 在Dockerfile注释和build-info中包含使用说明
  - 写入build metadata到/etc/chaos-ai-portable-build-info
- **Acceptance Criteria Addressed**: FR-7, FR-12
- **Deliverables**:
  - `scripts/fix-permissions.sh` (439行, 含详细日志/dry-run/verbose)
  - `docs/portable/conda-environment-guide.md`
  - Stage 7 build-info generation

## [x] Task 7: 配置Docker-in-Docker和服务管理
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 安装Docker CE（支持DinD）
  - 配置daemon.json（兼容国内镜像加速）
  - 配置supervisord启动sshd、jupyter、dockerd
  - 配置entrypoint.sh或启动脚本支持服务启动
  - 保留现有容器启动逻辑兼容性
  - ENTRYPOINT为空数组，允许用户覆盖CMD
- **Acceptance Criteria Addressed**: NFR-2
- **Deliverables**:
  - `config/docker/daemon.json`
  - `config/supervisor/conf.d/dockerd.conf`
  - `scripts/start.sh` (525行, 含详细诊断日志/ERR trap/步骤计时)
  - ENTRYPOINT=[], CMD=["/usr/local/bin/start.sh"]

## [x] Task 8: 设置USER指令和最终清理
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 设置USER ai为默认运行用户 → 注意：构建时以root完成安装，运行时通过start.sh以ai用户执行服务
  - 设置WORKDIR /workspace
  - 配置ENV PATH确保py314/bin优先
  - 清理apt缓存、conda缓存、pip缓存、/tmp文件
  - 运行冒烟测试验证所有组件正常
  - 设置CMD默认启动supervisord（与现有行为兼容）
  - Dockerfile最终阶段输出构建信息和使用提示
- **Acceptance Criteria Addressed**: AC-2, NFR-1
- **Deliverables**: Stage 7 validation (8项检查) + WORKDIR/ENV/EXPOSE/CMD

## [ ] Task 9: 端到端验证测试
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 编写验证脚本test-portable-image.sh验证所有AC项
  - 测试独立构建（无本地基础镜像）
  - 测试默认非root运行
  - 测试UID/GID自定义构建
  - 测试SSH/Jupyter/CMD三环境一致性
  - 测试umask权限保护
  - 测试conda环境创建和包安装
  - 测试NPU工具链挂载兼容
- **Acceptance Criteria Addressed**: AC-1~AC-11
- **Status**: 待Docker环境实际构建后验证
