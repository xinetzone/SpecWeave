---
id: "jupyter-ssh-base-tasks"
version: "1.1"
x-toml-ref: "../../../.meta/toml/.trae/specs/jupyter-ssh-base/tasks.toml"
---
# Jupyter SSH Base - 实施计划（原子化任务清单）

## [x] Task 1: 项目目录结构初始化与基础文件创建
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 完成
- **Description**: 
  - 在 `apps/jupyter-ssh-base/` 创建项目目录结构
  - 创建 `.dockerignore` 文件（排除 .git/.trae/.agents/docs 等）
  - 创建 `requirements.txt`（版本固定）
  - 创建 `config/` 目录和 `config/supervisor/conf.d/` 子目录
  - 创建 `scripts/` 目录（build.sh, healthcheck.sh）
  - 创建 AGENTS.md AI协作者入口文件

## [x] Task 2: supervisord 配置文件编写
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 完成
- **Description**: 
  - 编写 `config/supervisord.conf` 主配置（nodaemon=true，日志到 stdout，禁用 web UI）
  - 编写 `config/supervisor/conf.d/sshd.conf`：sshd 服务配置
  - 编写 `config/supervisor/conf.d/jupyter.conf`：jupyter 服务配置（含 venv PATH）
- **Verified**: supervisorctl status 双服务 RUNNING ✓

## [x] Task 3: SSH 配置文件编写
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 完成
- **Description**: 
  - 编写 `config/sshd_config` 定制配置
  - PermitRootLogin no（默认）、PasswordAuthentication yes、PubkeyAuthentication yes
  - PermitEmptyPasswords no、X11Forwarding no、UsePAM yes、PrintMotd no
  - HostKey 优先 ED25519
- **Verified**: sshd -t 语法通过 ✓，密码登录成功 ✓，root 默认拒绝 ✓

## [x] Task 4: Jupyter Notebook 配置文件编写
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 完成
- **Description**: 
  - 编写 `config/jupyter_notebook_config.py` 基础配置
  - 使用 c.ServerApp.root_dir（Jupyter Server 现代API）替代已弃用的 notebook_dir
  - 密码和 token 在 entrypoint 运行时通过 runtime.py 动态生成
  - CORS 默认同源限制
- **Verified**: Jupyter HTTP 200 ✓，密码/token认证正常 ✓

## [x] Task 5: requirements.txt 依赖版本固定
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 完成
- **Description**: 
  - notebook==7.2.2、jupyterlab==4.2.5、jupyter_server==2.14.1
  - 所有包版本使用 == 固定
  - 兼容 Python 3.12+（Ubuntu 26.04 系统 Python）

## [x] Task 6: Dockerfile 编写（多阶段构建）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Status**: ✅ 完成
- **Implementation Notes**:
  - 采用2阶段多阶段构建：builder（含 build-essential/python3-dev）→ runtime（仅运行时）
  - Python 使用 /opt/venv 虚拟环境，通过 COPY --from=builder 复制到 runtime
  - 支持 APT_MIRROR/PIP_MIRROR build-arg 选择国内镜像源（aliyun/tuna）
  - profile.d/venv.sh + /etc/environment 确保 SSH 非交互 shell 也能访问 venv
  - 用户创建逻辑：UID 1000 空闲则使用，否则自动分配（ubuntu:26.04 默认 ubuntu 用户占用 UID 1000）
  - 构建信息写入 /etc/jupyter-ssh-build-info
  - VOLUME ["/workspace"]，EXPOSE 22 8888，HEALTHCHECK 双服务检查
- **Verified**: 构建成功 ✓，镜像 713MB ✓

## [x] Task 7: entrypoint.sh 启动脚本编写
- **Priority**: high
- **Depends On**: Task 6
- **Status**: ✅ 完成
- **Description**: 
  - set -e，DEBUG=1 开启 set -x
  - log_info/log_warn/log_error 结构化日志
  - 6步启动流程：diagnose → passwords → host keys → sshd config → ssh keys → jupyter config → supervisord
  - 支持 USER_PASSWORD/JUPYTER_TOKEN/JUPYTER_PASSWORD/ALLOW_ROOT_SSH/GRANT_SUDO/JUPYTER_ALLOW_ORIGIN
  - 环境变量别名：ENABLE_SUDO_NOPASSWD→GRANT_SUDO、JUPYTER_CORS_ORIGIN→JUPYTER_ALLOW_ORIGIN
  - 命令模式：docker run 带命令时直接 exec
  - SIGTERM/SIGINT trap 优雅关闭
- **Verified**: 命令模式 ✓，自动密码生成 ✓，CORS配置 ✓

## [x] Task 8: build.sh 一键构建脚本
- **Priority**: medium
- **Depends On**: Task 6
- **Status**: ✅ 完成
- **Description**: 
  - 参数：-t/--tag, -n/--name, -r/--registry, --no-cache, --cn, --apt-mirror, --pip-mirror, -h/--help
  - 默认 DOCKER_BUILDKIT=1
  - 构建后显示镜像大小和快速开始命令

## [x] Task 9: docker-compose.yml 示例编写
- **Priority**: medium
- **Depends On**: Task 6
- **Status**: ✅ 完成
- **Verified**: 文件存在，包含端口映射、卷挂载、环境变量、healthcheck

## [x] Task 10: README.md 完整文档编写
- **Priority**: high
- **Depends On**: Task 7, Task 8, Task 9
- **Status**: ✅ 完成

## [x] Task 11: 镜像构建与基础功能验证
- **Priority**: high
- **Depends On**: Task 7, Task 8
- **Status**: ✅ 完成（WSL2 Docker环境实测通过）
- **Verification Results**:
  - ✅ 构建成功，退出码 0
  - ✅ locale 显示 zh_CN.UTF-8
  - ✅ date 显示 CST (Asia/Shanghai)
  - ✅ jupyteruser 存在（UID 1001，因 UID 1000 被 ubuntu 用户占用）
  - ✅ 镜像大小 713MB（< 800MB 目标）
  - ✅ build-info 文件存在，信息完整

## [x] Task 12: 服务运行与集成测试
- **Priority**: high
- **Depends On**: Task 11
- **Status**: ✅ 完成（WSL2 Docker环境实测通过）
- **Verification Results**:
  - ✅ supervisorctl status: sshd RUNNING + jupyter RUNNING
  - ✅ 健康检查状态 healthy
  - ✅ SSH 密码登录成功（sshpass 非交互验证）
  - ✅ SSH 非交互shell可访问 jupyter 命令（/etc/environment PATH修复）
  - ✅ root SSH 默认被拒绝（Permission denied）
  - ✅ Jupyter HTTP 返回 200（curl 验证）
  - ✅ 杀死 jupyter 进程后 6 秒内自动重启
  - ✅ 命令模式正常（docker run --rm echo hello）
  - ✅ GRANT_SUDO=yes 正确配置 NOPASSWD sudo
  - ✅ ENABLE_SUDO_NOPASSWD=1 别名正常工作

## [x] Task 13: 作为基础镜像复用验证
- **Priority**: medium
- **Depends On**: Task 12
- **Status**: ✅ 完成
- **Verification Results**:
  - ✅ pip install 在容器中正常工作（venv 环境）
  - ✅ docker run --rm jupyter-ssh-base:test pip install numpy 成功
  - ✅ ENTRYPOINT 使用 tini init，支持 FROM jupyter-ssh-base 扩展
  - ✅ /etc/profile.d/venv.sh + /etc/environment 确保扩展镜像 PATH 正确

## [x] Task 14: apps/README.md 索引更新
- **Priority**: low
- **Depends On**: Task 10
- **Status**: ✅ 完成（docgen自动管理）

---

## 关键设计决策记录

### 1. 多阶段构建策略（与原Spec的7阶段单阶段构建不同）
- **决策**: 采用2阶段构建（builder + runtime），而非7阶段单阶段构建
- **原因**: 真正隔离编译工具链（build-essential, gcc, python3-dev）仅在builder阶段，runtime镜像更小（713MB），且不会在最终镜像中残留编译工具，减小攻击面
- **runtime逻辑分6个Stage块**（Stage 1/6-6/6），保持构建日志清晰

### 2. Python virtualenv 隔离
- **决策**: 创建 /opt/venv 虚拟环境，而非直接使用系统 pip install
- **原因**: 避免污染系统Python包，保持系统包管理器和pip包隔离，防止依赖冲突；多阶段COPY更清晰

### 3. UID 自动分配（与原Spec的UID 1000固定不同）
- **决策**: 优先 UID 1000，若被占用则自动分配下一个可用UID
- **原因**: Ubuntu 26.04 Docker基础镜像预创建了 `ubuntu` 用户（UID 1000），强制UID 1000会导致冲突；自动分配更健壮
- **实际结果**: jupyteruser UID=1001

### 4. 国内镜像源可选而非默认
- **决策**: 使用 build-arg 可选配置（--cn、--apt-mirror、--pip-mirror），默认使用官方源
- **原因**: 镜像应具有通用性，国际用户不应默认使用中国镜像源；国内用户通过 --cn 参数一键切换

### 5. SSH非交互Shell PATH修复
- **决策**: 将venv PATH写入 /etc/environment，而非仅依赖Dockerfile ENV
- **原因**: SSH非交互会话不继承Dockerfile ENV中的PATH，需通过PAM读取/etc/environment获取
