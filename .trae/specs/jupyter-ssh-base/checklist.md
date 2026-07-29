---
id: "jupyter-ssh-base-checklist"
version: "1.1"
x-toml-ref: "../../../.meta/toml/.trae/specs/jupyter-ssh-base/checklist.toml"
---
# Jupyter SSH Base - 验收标准检查清单

## P0 核心功能验收 (必须通过)

### 1. 基础环境配置
- [x] Dockerfile 可成功构建，退出码为 0（2阶段多阶段构建）
- [x] 镜像大小 < 800MB（**实际：713MB**）
- [x] 容器启动后无错误退出（tini PID=1 → supervisord → sshd + jupyter）
- [x] `locale` 输出包含 `zh_CN.UTF-8`，`LANG=zh_CN.UTF-8`
- [x] `/etc/localtime` 指向 `/usr/share/zoneinfo/Asia/Shanghai`
- [x] `date` 输出显示 CST 时区
- [x] Python 虚拟环境 `/opt/venv` 存在，`/opt/venv/bin/python` 可执行
- [x] `/etc/environment` 包含 venv PATH，SSH非交互shell可访问 jupyter 命令
- [x] `/etc/profile.d/venv.sh` 配置登录shell的venv环境
- [x] `/etc/jupyter-ssh-build-info` 包含构建信息（image/build_time/python_version/tz/locale/user）

### 2. 用户系统
- [x] 用户 `jupyteruser` 存在（UID 1001，因 ubuntu:26.04 镜像 ubuntu 用户占用 UID 1000，自动分配）
- [x] `HOME` 目录为 `/home/jupyteruser`
- [x] 默认 shell 为 `/bin/bash`
- [x] `/workspace` 是 `jupyteruser` 可读写的工作目录
- [x] 未设置 `USER_PASSWORD` 时，密码自动生成并打印到 stdout（pwgen 24字符）
- [x] 设置 `USER_PASSWORD` 时，使用指定密码
- [x] 默认情况下 `jupyteruser` 无 sudo 权限（sudo 需要密码）
- [x] 设置 `GRANT_SUDO=yes` 时，`jupyteruser` 具有 NOPASSWD sudo 权限
- [x] 环境变量别名 `ENABLE_SUDO_NOPASSWD=1` 正确映射为 `GRANT_SUDO=yes`

### 3. SSH 服务
- [x] SSH 服务在端口 22 运行，监听 `0.0.0.0:22`
- [x] 密码认证已启用（`PasswordAuthentication yes`）
- [x] 公钥认证已启用（`PubkeyAuthentication yes`）
- [x] 默认禁止 root 登录（`PermitRootLogin no`）
- [x] 设置 `ALLOW_ROOT_SSH=yes` 时允许 root 密码登录（验证配置逻辑正确）
- [x] 空密码登录已禁止（`PermitEmptyPasswords no`）
- [x] SSH 主机密钥在容器启动时自动生成（首次启动）
- [x] 预挂载 `.ssh/authorized_keys` 时自动设置正确权限（600/700）
- [x] SSH 配置语法验证通过（`sshd -t` 退出码 0）
- [x] SSH 密码登录功能正常（sshpass 非交互验证通过）
- [x] SSH 非交互shell中 jupyter 命令可访问（/etc/environment PATH修复验证通过）
- [x] root SSH 登录默认被拒绝（Permission denied）
- [x] X11 转发已禁用（`X11Forwarding no`）

### 4. Jupyter Notebook 服务
- [x] Jupyter Notebook 在端口 8888 运行
- [x] Jupyter 监听 `0.0.0.0:8888`，支持外部访问
- [x] 默认启用 token 认证
- [x] 设置 `JUPYTER_TOKEN` 时使用指定 token
- [x] 未设置 token 或密码时自动生成随机 token（uuid4，打印到 stdout）
- [x] 设置 `JUPYTER_PASSWORD` 时启用密码认证
- [x] Jupyter 工作目录为 `/workspace`（c.ServerApp.root_dir）
- [x] Jupyter 配置文件语法正确，可正常加载（jupyter server --generate-config 兼容）
- [x] 默认禁用 CORS 跨域（允许同源访问）
- [x] 环境变量别名 `JUPYTER_CORS_ORIGIN` 正确映射为 `JUPYTER_ALLOW_ORIGIN`
- [x] Jupyter HTTP端点返回200（curl验证通过）
- [x] 安装 notebook + jupyterlab + jupyter_server（版本固定）

### 5. 进程管理与健壮性
- [x] supervisord 作为 PID 1 下的主进程管理器（tini PID 1 → supervisord）
- [x] SSH 和 Jupyter 都由 supervisord 管理
- [x] 任意一个服务崩溃后，supervisord 自动重启（验证：kill jupyter → 6秒内重启）
- [x] 容器停止时信号正确传递，服务优雅关闭
- [x] 健康检查 (HEALTHCHECK) 正确验证两个服务状态
- [x] 容器健康状态为 `healthy`（约15秒后）

### 6. 国内镜像源支持
- [x] Dockerfile 支持 `APT_MIRROR` build-arg 选择 APT 镜像源
  - `official`：默认官方源
  - `aliyun`：阿里云镜像
  - `tuna`：清华大学镜像
- [x] Dockerfile 支持 `PIP_MIRROR` build-arg 选择 pip 镜像源
  - `official`：默认官方PyPI
  - `aliyun`：阿里云PyPI
  - `tuna`：清华TUNA PyPI
- [x] build.sh `--cn` 参数一键启用双阿里云镜像
- [x] build.sh `--apt-mirror` 和 `--pip-mirror` 独立选择

### 7. 作为基础镜像支持
- [x] ENTRYPOINT 正确设置（tini -- entrypoint.sh），子镜像可继承
- [x] CMD 可被子镜像覆盖（supervisord -c /config/supervisord.conf）
- [x] 默认用户为 root，子镜像可自由切换 USER
- [x] 子镜像可以 `RUN pip install` 安装额外包（验证：numpy安装成功）
- [x] supervisord 配置支持包含子镜像的额外配置目录
- [x] `/workspace` 声明为 VOLUME
- [x] 端口 22 和 8888 已 EXPOSE

## P1 开发体验验收 (应该通过)

### 8. 构建脚本与文档
- [x] `scripts/build.sh` 可执行，带 `-h` 输出帮助信息
- [x] `scripts/build.sh` 默认成功构建镜像
- [x] `scripts/build.sh` 支持 `-t/--tag` 指定标签
- [x] `scripts/build.sh` 支持 `-r/--registry` 指定镜像仓库
- [x] `scripts/build.sh` 支持 `--no-cache` 无缓存构建
- [x] `scripts/build.sh` 支持 `--cn` 国内镜像一键构建
- [x] `scripts/healthcheck.sh` 可在容器内执行
- [x] `docker-compose.yml` 提供可用示例
- [x] `README.md` 包含完整使用文档（快速开始、环境变量、构建说明）
- [x] `README.md` 包含国内构建说明
- [x] `.dockerignore` 排除无关文件

### 9. 配置文件
- [x] `config/supervisord.conf` 配置正确（nodaemon=true, logfile=/dev/stdout）
- [x] `config/sshd_config` 配置正确（安全加固，禁用不常用功能）
- [x] `config/jupyter_notebook_config.py` 包含基础默认配置
- [x] Jupyter 运行时配置（密码/token/CORS/ip/root_dir）由 entrypoint 动态生成
- [x] SSH 配置运行时根据 ALLOW_ROOT_SSH 动态调整

### 10. 环境变量支持
- [x] `USER_PASSWORD` - 设置用户密码
- [x] `JUPYTER_PASSWORD` - 设置 Jupyter 密码
- [x] `JUPYTER_TOKEN` - 设置 Jupyter token
- [x] `GRANT_SUDO=yes` - 授予 sudo 权限
- [x] `ENABLE_SUDO_NOPASSWD=1` - sudo 权限别名（兼容旧版规范）
- [x] `ALLOW_ROOT_SSH=yes` - 允许 root SSH 登录
- [x] `JUPYTER_ALLOW_ORIGIN` - 设置 CORS 允许源
- [x] `JUPYTER_CORS_ORIGIN` - CORS 别名（兼容旧版规范）
- [x] `TZ=Asia/Shanghai` - 时区设置
- [x] `DEBUG=1` - 启用调试日志

## P2 安全与质量验收 (建议通过)

### 11. 安全最佳实践
- [x] 不在镜像中硬编码密码或密钥（均为运行时环境变量配置）
- [x] SSH 禁用空密码登录
- [x] SSH 禁用 X11 转发
- [x] SSH 禁用 TCP 转发（AllowTcpForwarding no）
- [x] SSH 禁用 Agent 转发（AllowAgentForwarding no）
- [x] SSH 禁用 PermitTunnel 和 PermitUserEnvironment
- [x] SSH 禁用 Kerberos/GSSAPI/PAM/Chroot等不常用功能
- [x] SSH MaxAuthTries=3 防止暴力破解
- [x] SSH LoginGraceTime=20s 防止连接占用
- [x] SSH ClientAliveInterval/CountMax 配置僵尸连接清理
- [x] 容器不以 jupyteruser 启动，保持 root 执行 supervisord 灵活性
- [x] /workspace 是 VOLUME，数据不丢失
- [x] Python使用虚拟环境隔离，不污染系统Python
- [x] 多阶段构建隔离编译工具链（runtime镜像无gcc/build-essential）

### 12. 日志与可观测性
- [x] supervisord 日志输出到 stdout/stderr（docker logs 可查看）
- [x] SSH 登录密码/token 信息在启动时打印到 stdout（含中文提示）
- [x] Jupyter 链接信息在启动时打印到 stdout（含中文链接格式）
- [x] entrypoint.sh 带中文日志前缀（[INFO]/[WARN]/[ERROR]）
- [x] HEALTHCHECK 脚本提供清晰的退出状态码
- [x] DEBUG=1 模式可启用详细调试信息（set -x）

### 13. 预装工具
- [x] Python venv 包含 notebook/jupyterlab/jupyter_server
- [x] 包含 vim（基础编辑器）
- [x] 包含 sudo（权限管理）
- [x] 包含 wget/curl（网络工具）
- [x] 包含 supervisor/openssh-server/tini（核心服务）
- [x] 包含 tzdata/locales（本地化）
- [x] 包含 procps（进程管理，supervisorctl 需要）
- [x] 包含 pwgen（密码生成）
- [x] 包含 python3-venv（虚拟环境支持）
- [x] 系统精简：不预装 git/nano/gcc/build-essential 等非必需工具，镜像保持最小化

### 14. 容器行为
- [x] `docker run <image>` 默认启动 SSH+Jupyter 服务
- [x] `docker run <image> <command>` 直接执行命令（命令模式）
- [x] 命令模式 exec 直接替换 PID 1，信号正确传递
- [x] 容器前台运行（不 daemonize）
- [x] `docker stop` 发送 SIGTERM，容器在合理时间内优雅关闭（trap kill %1）
- [x] SIGINT/SIGTERM 信号正确传递给 supervisord
- [x] 重复启动容器时密码/token不重复生成（除非重新设置环境变量）
