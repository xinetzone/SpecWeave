---
version: "1.0"
---

# PyCaffe Jupyter SSH Docker - The Implementation Plan

## [x] Task 1: 创建目录结构和基础配置文件
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `projects/xuanspace/vendor/caffe/docker/standalone/pycaffe-jupyter-ssh/` 目录
  - 创建子目录：`config/supervisor/conf.d/`、`scripts/`
  - 从 `apps/jupyter-ssh-base/config/` 复制并适配配置文件：
    - `config/sshd_config`：基本保持一致
    - `config/supervisord.conf`：保持一致
    - `config/jupyter_notebook_config.py`：用户路径从 `/home/jupyteruser` 改为 `/home/builder`
    - `config/supervisor/conf.d/sshd.conf`：保持一致
    - `config/supervisor/conf.d/jupyter.conf`：用户从 `jupyteruser` 改为 `builder`，HOME 路径改为 `/home/builder`，移除 VIRTUAL_ENV 和 venv PATH（使用系统 Python）
  - 创建 `scripts/healthcheck.sh`：基于 jupyter-ssh-base 的健康检查脚本，适配系统 Python 环境
- **Acceptance Criteria Addressed**: AC-1, AC-13
- **Test Requirements**:
  - `programmatic` TR-1.1: 验证目录结构存在，所有配置文件已创建 ✅
  - `human-judgement` TR-1.2: 配置文件与 jupyter-ssh-base 对比，核心配置一致，仅用户路径等必要差异 ✅
- **Notes**: 用户统一使用 `builder`（与 pycaffe 保持一致，UID 1000）；Python 使用系统 Python，不使用 venv

## [x] Task 2: 创建 entrypoint.sh 启动脚本
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 `apps/jupyter-ssh-base/entrypoint.sh` 创建适配版本
  - 关键修改点：
    - NON_ROOT_USER 默认为 `builder`（而非 jupyteruser）
    - 用户 HOME 为 `/home/builder`
    - 移除 venv PATH 相关配置（系统 Python 直接可用）
    - Jupyter 命令直接使用系统 PATH 中的 `jupyter`（无需 /opt/venv/bin 前缀）
    - 保留所有核心功能：密码设置、SSH host key 生成、sshd 配置、SSH 公钥注入、Jupyter 动态配置、访问信息打印
    - 保留命令模式（传入参数时直接 exec，不启动服务）
    - 保留 tini + supervisord 启动方式
  - 设置脚本可执行权限（在 Dockerfile 中处理）
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-9, AC-11, AC-13
- **Test Requirements**:
  - `programmatic` TR-2.1: bash 语法检查通过（`bash -n entrypoint.sh`） ✅（WSL bash -n 验证通过）
  - `human-judgement` TR-2.2: 启动逻辑与 jupyter-ssh-base 一致，用户和路径正确适配 ✅
- **Notes**: 保持日志输出格式与 jupyter-ssh-base 一致（log_info/log_warn/log_error + banner）

## [x] Task 3: 创建 Dockerfile 多阶段构建文件
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 新 Dockerfile 需要复用 pycaffe/Dockerfile 的前 3 个构建阶段（base-system, base-builder, pycaffe-builder），但不能直接 FROM 已有的本地镜像（因为需要自包含构建）
  - 实际方案：直接在新 Dockerfile 中重新定义多阶段构建（或通过 COPY 引用，但 Dockerfile 不能跨 Dockerfile COPY）——采用完整的多阶段构建，在 runtime 阶段末尾添加 SSH/Jupyter 服务层
  - 构建阶段：
    1. 复用 pycaffe 的 base-system 阶段（apt换源、基础工具）
    2. 复用 pycaffe 的 base-builder 阶段（构建工具链、Python 科学计算包），但需要额外安装 jupyter-ssh-base 运行时需要的包：locales, openssh-server, supervisor, tini, pwgen
    3. 复用 pycaffe 的 pycaffe-builder 阶段（编译 pycaffe wheel）
    4. 新增/修改 runtime 阶段：
       - 安装 pycaffe wheel
       - 安装 Jupyter Python 包（notebook, jupyterlab, ipykernel, nbconvert, jupyter_server）
       - 配置中文 locale（zh_CN.UTF-8）和时区（Asia/Shanghai）
       - 创建/确保 builder 用户存在，HOME=/home/builder，UID=1000
       - 配置 SSH 服务（mkdir /run/sshd，复制 sshd_config，生成初始 host keys）
       - 复制 supervisord 配置
       - 复制 Jupyter 配置到 /home/builder/.jupyter/
       - 复制 entrypoint.sh 和 healthcheck.sh
       - 设置正确的权限和 ownership
       - 写入构建信息（/etc/jupyter-ssh-build-info）
       - 验证：sshd -t, supervisord --version, jupyter --version, pycaffe import
       - 配置 HEALTHCHECK
       - EXPOSE 22 8888
       - WORKDIR /workspace
       - VOLUME ["/workspace"]
       - ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
       - CMD []
  - 从 pycaffe/scripts/ 复制验证脚本：verify-pycaffe.sh, verify-parity.sh
  - 关键：所有文件 COPY 路径相对于构建上下文（vendor/）
    - Dockerfile 路径：`caffe/docker/standalone/pycaffe-jupyter-ssh/Dockerfile`
    - config 文件：`caffe/docker/standalone/pycaffe-jupyter-ssh/config/...`
    - entrypoint.sh：`caffe/docker/standalone/pycaffe-jupyter-ssh/entrypoint.sh`
    - scripts：`caffe/docker/standalone/pycaffe-jupyter-ssh/scripts/...`
    - pycaffe 源码：`caffe/caffe-slim`、`tvm-ffi`、`caffe/docker/standalone/pycaffe/scripts/verify-*.sh`
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6, AC-7, AC-8, AC-10, AC-15
- **Test Requirements**:
  - `programmatic` TR-3.1: 从 vendor/ 目录执行 docker build 成功完成 ⚠️（Docker 环境不可用，需用户验证）
  - `programmatic` TR-3.2: 构建的镜像中 pycaffe 可正常导入 ⚠️（需 Docker 环境验证）
  - `programmatic` TR-3.3: 镜像中 sshd、supervisord、jupyter 命令可用 ⚠️（需 Docker 环境验证）
  - `human-judgement` TR-3.4: Dockerfile 结构清晰，注释充分，构建日志有 [BUILD] 前缀 ✅
- **Notes**:
  - 必须保持构建上下文为 vendor/，以访问 caffe-slim/ 和 tvm-ffi/
  - Python 包安装统一使用 `--break-system-packages --no-cache-dir`
  - apt 安装使用 `--no-install-recommends`，安装后清理 `rm -rf /var/lib/apt/lists/*`
  - 不使用 venv，直接安装到系统 Python

## [x] Task 4: 创建 README.md 文档
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 创建 README.md，风格参考 pycaffe/README.md 和 jupyter-ssh-base/README.md
  - 包含内容：
    - 项目简介（PyCaffe + SSH + Jupyter 开发环境）
    - 特性列表（SSH、Jupyter、supervisord、中文环境、健康检查等）
    - 文件结构（目录树）
    - 构建流水线说明（构建阶段表格）
    - 构建命令（cd vendor && docker build ...）
    - 运行示例（端口映射、环境变量、卷挂载）
    - SSH 连接方式
    - Jupyter 访问方式
    - 环境变量配置表（USER_PASSWORD, JUPYTER_TOKEN, ALLOW_ROOT_SSH 等）
    - 服务管理（supervisorctl 命令）
    - 验证命令（verify-pycaffe.sh, pycaffe import, healthcheck）
    - 调试模式（docker run -it --rm <image> bash）
- **Acceptance Criteria Addressed**: AC-12
- **Test Requirements**:
  - `human-judgement` TR-4.1: README 内容完整、可操作，构建和运行命令准确 ✅
  - `human-judgement` TR-4.2: 风格与现有 pycaffe README 一致，信息层次清晰 ✅
- **Notes**: 中文撰写，技术术语保留英文

## [x] Task 5: 构建验证和测试（静态验证完成，动态验证需 Docker 环境）
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**:
  - 静态验证已完成：
    - ✅ 目录结构完整（config/supervisor/conf.d/、scripts/）
    - ✅ 所有配置文件已创建（sshd_config、supervisord.conf、jupyter_notebook_config.py、sshd.conf、jupyter.conf）
    - ✅ entrypoint.sh bash 语法检查通过（WSL bash -n）
    - ✅ healthcheck.sh bash 语法检查通过（WSL bash -n）
    - ✅ Dockerfile 4阶段构建结构完整，COPY 路径正确
    - ✅ README.md 文档完整
  - 动态验证（需 Docker 环境，由用户执行）：
    ```bash
    cd d:/spaces/SpecWeave/projects/xuanspace/vendor
    docker build -t caffe-cpu:pycaffe-jupyter-ssh --target runtime -f caffe/docker/standalone/pycaffe-jupyter-ssh/Dockerfile .
    ```
  - 验证 PyCaffe 导入：`docker run --rm caffe-cpu:pycaffe-jupyter-ssh python -c "import pycaffe; print(pycaffe.__version__)"`
  - 验证调试模式：`docker run -it --rm caffe-cpu:pycaffe-jupyter-ssh bash`（检查是否进入 shell，不启动服务）
  - 启动容器测试 SSH 和 Jupyter：
    ```bash
    docker run -d --name pycaffe-test -p 2222:22 -p 8888:8888 \
      -e USER_PASSWORD=testpass -e JUPYTER_TOKEN=testtoken \
      caffe-cpu:pycaffe-jupyter-ssh
    ```
  - 等待 30 秒后检查：
    - supervisorctl status（sshd 和 jupyter RUNNING）
    - SSH 连接测试（ssh builder@localhost -p 2222，密码 testpass）
    - Jupyter HTTP 检测（curl http://localhost:8888/api 返回 200/302/401/403）
    - healthcheck.sh 在容器内执行返回 HEALTHY
  - 验证中文环境：docker exec 检查 LANG 和时区
  - 清理测试容器
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11
- **Test Requirements**:
  - `programmatic` TR-5.1: docker build 成功（退出码 0） ⚠️（需 Docker 环境）
  - `programmatic` TR-5.2: pycaffe import 成功输出版本号 ⚠️（需 Docker 环境）
  - `programmatic` TR-5.3: 容器启动后 sshd 端口 22 可连接 ⚠️（需 Docker 环境）
  - `programmatic` TR-5.4: 容器启动后 jupyter 端口 8888 HTTP 响应正常 ⚠️（需 Docker 环境）
  - `programmatic` TR-5.5: supervisorctl status 显示两个服务 RUNNING ⚠️（需 Docker 环境）
  - `programmatic` TR-5.6: healthcheck.sh 返回 HEALTHY ⚠️（需 Docker 环境）
  - `programmatic` TR-5.7: 使用 USER_PASSWORD 和 JUPYTER_TOKEN 可正常认证 ⚠️（需 Docker 环境）
  - `programmatic` TR-5.8: LANG=zh_CN.UTF-8，时区为 Asia/Shanghai ⚠️（需 Docker 环境）
  - `human-judgement` TR-5.9: 调试模式正确进入 shell 而非启动服务 ⚠️（需 Docker 环境）
- **Notes**: 当前环境无 Docker，静态验证已完成；动态构建/运行验证需用户在有 Docker 的环境中执行
