# Caffe Jupyter SSH Dockerfile - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建适配的配置文件（sshd_config、supervisord配置、jupyter配置）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 从 `apps/jupyter-ssh-base/config/` 复制配置文件到 `docker/origin/config/` 目录下
  - 检查并适配 Ubuntu 22.04 环境，确保配置文件路径和权限正确
  - 调整 jupyter 配置以使用系统 Python（而非 venv）
  - 配置文件包括：
    - `config/sshd_config` - SSH 服务配置
    - `config/supervisord.conf` - supervisord 主配置
    - `config/supervisor/conf.d/sshd.conf` - sshd 服务配置
    - `config/supervisor/conf.d/jupyter.conf` - jupyter 服务配置
    - `config/jupyter_notebook_config.py` - Jupyter 基础配置
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: 配置文件存在于正确路径 ✅
  - `human-judgement` TR-1.2: 配置文件内容适配 Ubuntu 22.04 和系统 Python，无 venv 相关路径 ✅
- **Notes**: jupyter-ssh-base 使用 /opt/venv，新配置需要改为系统路径；**额外修复**：在 jupyter.conf 中添加了完整的 Caffe 环境变量（CAFFE_ROOT、PYTHONPATH、LD_LIBRARY_PATH、PATH），确保 Jupyter 中可以直接 `import caffe`

## [x] Task 2: 创建适配的 entrypoint.sh 启动脚本
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 `apps/jupyter-ssh-base/entrypoint.sh` 创建适配版本
  - 将用户名从 `jupyteruser` 改为 `caffe-origin`
  - 移除 venv 相关的 PATH 配置（直接使用系统 Python 路径）
  - 适配 Ubuntu 22.04 的路径（如 sshd 路径可能为 /usr/sbin/sshd）
  - 保留 6 步初始化流程：密码设置、host key 生成、sshd 配置、SSH 密钥注入、Jupyter 配置、访问信息输出
  - 保留命令模式支持（传入参数时直接 exec，不启动服务）
  - 保留 DEBUG 模式、环境变量支持（USER_PASSWORD、JUPYTER_TOKEN、SSH_PUBLIC_KEY 等）
  - 放置于 `docker/origin/entrypoint-jupyter.sh`
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-2.1: 脚本语法正确（bash -n 检查通过） ✅
  - `programmatic` TR-2.2: 脚本中所有 jupyteruser 替换为 caffe-origin ✅
  - `human-judgement` TR-2.3: 无 /opt/venv 路径引用，使用系统 Python ✅
- **Notes**: 注意保持 tini 作为 init 的 exec 调用方式；**关键安全修复**：命令模式下新增 `gosu` 降权到 `caffe-origin` 用户执行，避免以 root 运行用户命令；显式设置 HOME/USER/LOGNAME 环境变量和 /workspace 工作目录

## [x] Task 3: 创建适配的 healthcheck.sh 健康检查脚本
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 基于 `apps/jupyter-ssh-base/scripts/healthcheck.sh` 创建适配版本
  - 同时检查 sshd 进程/端口和 jupyter HTTP 响应
  - 适配系统 Python 路径（jupyter 命令路径）
  - 放置于 `docker/origin/scripts/healthcheck-jupyter.sh`
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-3.1: 脚本语法正确（bash -n 检查通过） ✅
  - `human-judgement` TR-3.2: 检查逻辑覆盖 sshd 和 jupyter 两个服务 ✅
- **Notes**: 健康检查需要在容器内可用；脚本已存在，检查 sshd 进程+端口连通性、jupyter 进程+API 响应，逻辑正确

## [x] Task 4: 创建 Dockerfile.jupyter-ssh 多阶段构建文件
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 复制现有 Dockerfile 的前 3 个阶段（base-system、base-builder、builder）保持不变
  - 在 runtime 阶段基础上新增 runtime-jupyter 阶段：
    - 基于 base-builder（保持与现有 runtime 相同的基础）
    - 先复制 Caffe 编译产物（与现有 runtime 阶段相同）
    - 安装中文 locale 包（locales）并生成 zh_CN.UTF-8
    - 安装 OpenSSH Server、supervisor、tini、pwgen 等系统包
    - 安装 Jupyter 相关 Python 包（notebook、jupyterlab、ipykernel 等）到系统 Python
    - 将用户从 builder 改为 caffe-origin（UID 1000）
    - 创建必要的运行时目录（/run/sshd、/var/log/supervisor、/workspace、~/.jupyter、~/.ssh）
    - 复制配置文件（Task 1 的产出）
    - 复制 entrypoint-jupyter.sh 和 healthcheck-jupyter.sh 并设置可执行权限
    - 配置环境变量（LANG、LC_ALL、TZ、NON_ROOT_USER=caffe-origin 等）
    - 配置 SSH host keys 初始化
    - 写入构建信息到 /etc/caffe-jupyter-build-info
    - 设置 WORKDIR /workspace、VOLUME、EXPOSE 22 8888
    - 配置 HEALTHCHECK
    - 设置 ENTRYPOINT 为 tini -- entrypoint-jupyter.sh
  - 保持注释风格与原 Dockerfile 一致，使用 `[BUILD]` 前缀的构建日志
  - 确保每个 RUN 后清理 apt 缓存
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6, AC-7, AC-10, AC-11
- **Test Requirements**:
  - `programmatic` TR-4.1: Dockerfile 语法正确（可通过 docker build 解析） ✅
  - `programmatic` TR-4.2: docker build --target runtime-jupyter 成功完成 - 需用户在有 Docker 环境中验证
  - `human-judgement` TR-4.3: 多阶段结构清晰，注释与原文件风格一致 ✅
  - `human-judgement` TR-4.4: pip install 使用 --no-cache-dir，apt 包安装后清理缓存 ✅
- **Notes**: 关键是在现有 Caffe runtime 基础上叠加 jupyter-ssh-base 的功能层，不破坏 Caffe 编译环境；**关键修复**：
  - 移除了末尾错误的 `USER ${NON_ROOT_USER}` 指令，让 entrypoint 以 root 启动完成系统初始化
  - 新增 `gosu` 包用于安全的用户切换
  - 移除了不需要的 `python3-venv` 包
  - 统一构建阶段编号为 1/7 ~ 7/7，合并不必要的层
  - 新增 `/etc/profile.d/caffe.sh` 环境配置，并在 `/etc/bash.bashrc` 中 source，确保所有 shell 上下文（SSH登录、Jupyter终端、命令模式）都有正确的 Caffe 环境变量

## [x] Task 5: 验证构建和功能测试
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 尝试执行 docker build 验证语法和构建流程
  - 如无 Docker 环境则进行静态检查：
    - 检查 Dockerfile 语法正确性
    - 检查所有 COPY 源文件存在
    - 检查所有脚本的 bash 语法
    - 检查环境变量和路径一致性
  - 验证 Caffe 相关路径配置正确（CAFFE_ROOT、PYTHONPATH、LD_LIBRARY_PATH）
  - 验证用户 caffe-origin 对 /workspace 有读写权限
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-10
- **Test Requirements**:
  - `programmatic` TR-5.1: Dockerfile 语法检查通过 ✅
  - `programmatic` TR-5.2: 所有引用的配置文件和脚本存在 ✅
  - `programmatic` TR-5.3: entrypoint 和 healthcheck 脚本 bash -n 检查通过 ✅
  - `human-judgement` TR-5.4: Caffe 环境变量（PYTHONPATH、LD_LIBRARY_PATH）配置正确 ✅
- **Notes**: 如无法实际构建，提供详细的构建和测试命令供用户手动验证；静态验证已全部完成，所有 COPY 源文件路径正确，环境变量在所有上下文中一致配置

## [x] Task 6 (新增): 环境一致性与安全加固
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建 `/etc/profile.d/caffe.sh` 提供登录 shell 环境变量
  - 在 `/etc/bash.bashrc` 中 source caffe.sh，覆盖非登录 shell（Jupyter 终端、非交互式 SSH）
  - Supervisor 的 jupyter 进程显式配置所有 Caffe 环境变量
  - 命令模式通过 gosu 自动降权，显式设置用户环境变量
  - 确保三种执行模式下 `import caffe` 和 `caffe` 命令均可直接使用：
    1. Supervisor 服务模式（Jupyter + SSH）
    2. 命令模式（`docker run ... <command>`）
    3. SSH 登录会话和 Jupyter 终端
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-9
- **Files Modified/Created**:
  - `config/profile.d/caffe.sh` (新增)
  - `config/supervisor/conf.d/jupyter.conf` (更新环境变量)
  - `entrypoint-jupyter.sh` (命令模式 gosu 降权)
  - `Dockerfile.jupyter-ssh` (COPY profile.d 脚本并配置 bashrc)
- **Test Requirements**:
  - `human-judgement` 所有执行上下文环境变量一致 ✅

---

## 构建与测试命令

构建镜像：
```bash
cd projects/xuanspace/vendor/caffe
docker build -f docker/origin/Dockerfile.jupyter-ssh -t caffe:jupyter-ssh .
```

启动服务模式（SSH + Jupyter）：
```bash
docker run -d -p 2222:22 -p 8888:8888 \
  -v $(pwd)/your-workspace:/workspace \
  -e USER_PASSWORD=your-password \
  -e JUPYTER_TOKEN=your-token \
  caffe:jupyter-ssh
```

命令模式（直接执行命令）：
```bash
docker run --rm -v $(pwd)/your-workspace:/workspace \
  caffe:jupyter-ssh python -c "import caffe; print(caffe.__file__)"
```
