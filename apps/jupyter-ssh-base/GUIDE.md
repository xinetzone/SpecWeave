# Jupyter SSH Base — Docker 构建与运行测试指南

> 最后更新：2026-07-24 | 基于 jupyter-ssh-base v1.0

## 目录

1. [环境要求](#1-环境要求)
2. [快速开始](#2-快速开始)
3. [构建镜像](#3-构建镜像)
4. [运行容器](#4-运行容器)
5. [验证测试](#5-验证测试)
6. [自动化测试脚本](#6-自动化测试脚本)
7. [环境变量参考](#7-环境变量参考)
8. [常见问题排查](#8-常见问题排查)
   - [8.7 AsyncClient proxies 警告](#87-asyncclient-proxies-警告非关键)
   - [8.8 banner exchange 警告](#88-banner-exchange-警告非关键)
9. [docker-compose 部署](#9-docker-compose-部署)
10. [构建验证记录](#10-构建验证记录)

---

## 1. 环境要求

| 组件 | 最低版本 | 说明 |
|------|---------|------|
| Docker | 20.10+ | 需支持 BuildKit（`DOCKER_BUILDKIT=1`） |
| docker-compose | 2.0+ | 可选，用于编排部署 |
| sshpass | 1.06+ | 可选，用于 SSH 非交互 PATH 测试 |
| curl | 7.0+ | 用于 Jupyter HTTP 健康检查 |
| 磁盘空间 | ~2GB | 镜像约 713MB + 构建缓存 |

**验证环境：**

```bash
docker --version      # Docker version 24.0+
docker compose version # Docker Compose version v2.0+
```

---

## 2. 快速开始

```bash
# 1. 进入项目目录
cd apps/jupyter-ssh-base

# 2. 构建镜像（使用国内镜像源加速）
bash scripts/build.sh --cn

# 3. 启动容器
docker run -d \
  --name jupyter-ssh \
  -p 2222:22 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -e USER_PASSWORD=mypassword \
  -e JUPYTER_TOKEN=mysecrettoken \
  jupyter-ssh-base:1.0

# 4. 访问服务
ssh -p 2222 jupyteruser@localhost          # SSH 登录
open http://localhost:8888/?token=mysecrettoken  # Jupyter Notebook

# 5. 停止并清理
docker rm -f jupyter-ssh
```

---

## 3. 构建镜像

### 3.1 使用 build.sh（推荐）

```bash
# 默认构建（官方源）
bash scripts/build.sh

# 国内镜像加速
bash scripts/build.sh --cn

# 指定镜像源
bash scripts/build.sh --apt-mirror aliyun --pip-mirror tuna

# 自定义标签
bash scripts/build.sh --tag latest --name my-jupyter-ssh

# 推送到私有仓库
bash scripts/build.sh --registry harbor.example.com --tag 1.0
```

**镜像源选项：**

| 参数 | 可选值 | 说明 |
|------|--------|------|
| `--apt-mirror` | `official`, `aliyun`, `tuna` | APT 软件源 |
| `--pip-mirror` | `official`, `aliyun`, `tuna` | PyPI 软件源 |
| `--cn` | — | 快捷方式：同时启用 aliyun APT + aliyun PyPI |

### 3.2 直接使用 docker build

```bash
# 标准构建
DOCKER_BUILDKIT=1 docker build -t jupyter-ssh-base:1.0 .

# 国内镜像
DOCKER_BUILDKIT=1 docker build \
  --build-arg APT_MIRROR=aliyun \
  --build-arg PIP_MIRROR=aliyun \
  -t jupyter-ssh-base:1.0 .

# 无缓存构建
DOCKER_BUILDKIT=1 docker build --no-cache -t jupyter-ssh-base:1.0 .
```

### 3.3 构建验证

构建完成后，Dockerfile 会自动执行以下验证：

```bash
# 验证清单（在 docker build 日志中可见）
[OK] sshd config valid
[OK] supervisord available
[OK] python available
[OK] pip available
[OK] jupyter available
[OK] entrypoint.sh syntax valid
[OK] healthcheck.sh syntax valid
```

---

## 4. 运行容器

### 4.1 基本运行

```bash
docker run -d \
  --name jupyter-ssh \
  -p 2222:22 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -e USER_PASSWORD=mypassword \
  -e JUPYTER_TOKEN=mysecrettoken \
  jupyter-ssh-base:1.0
```

### 4.2 高级配置

```bash
docker run -d \
  --name jupyter-ssh \
  --restart unless-stopped \
  -p 2222:22 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v $(pwd)/ssh_authorized_keys:/home/jupyteruser/.ssh/authorized_keys:ro \
  -e USER_PASSWORD=mypassword \
  -e JUPYTER_TOKEN=mysecrettoken \
  -e GRANT_SUDO=yes \
  -e ALLOW_ROOT_SSH=no \
  -e TZ=Asia/Shanghai \
  -e DEBUG=0 \
  jupyter-ssh-base:1.0
```

### 4.3 调试模式（不启动服务）

```bash
# 直接进入 bash，不启动 SSH/Jupyter
docker run -it --rm \
  -e USER_PASSWORD=test \
  jupyter-ssh-base:1.0 \
  bash
```

### 4.4 查看日志

```bash
# 实时日志
docker logs -f jupyter-ssh

# 最近 50 行
docker logs --tail 50 jupyter-ssh

# 带时间戳
docker logs -t jupyter-ssh
```

---

## 5. 验证测试

### 5.1 SSH 连接测试

```bash
# 密码登录
ssh -p 2222 jupyteruser@localhost
# 输入密码：mypassword（或你设置的 USER_PASSWORD）

# 免密码登录（需要先配置 SSH key）
ssh -i ~/.ssh/id_rsa -p 2222 jupyteruser@localhost
```

### 5.2 SSH 非交互会话 PATH 测试（关键）

> 这是验证 SSH PATH 配置是否正确的关键测试，确保远程命令执行时能找到 venv 中的可执行文件。

```bash
# 测试 1：which jupyter（验证 PATH 是否包含 /opt/venv/bin）
ssh -p 2222 jupyteruser@localhost 'which jupyter'
# 期望输出：/opt/venv/bin/jupyter

# 测试 2：jupyter --version
ssh -p 2222 jupyteruser@localhost 'jupyter --version'
# 期望输出：版本号信息

# 测试 3：pip --version
ssh -p 2222 jupyteruser@localhost 'pip --version'
# 期望输出：pip 版本信息

# 测试 4：echo $PATH（对比交互式和非交互式 PATH）
ssh -p 2222 jupyteruser@localhost 'echo $PATH'
# 期望：PATH 包含 /opt/venv/bin
```

**如果 `which jupyter` 返回空或报错**，说明 SSH 非交互 PATH 配置有问题。检查：
- Dockerfile 中是否有 `ENV PATH="/opt/venv/bin:${PATH}"`
- `/etc/environment` 中是否包含 PATH 配置
- 参考 [docker-ssh-noninteractive-path-fix 模式](../../.agents/docs/retrospective/patterns/code-patterns/docker-ssh-noninteractive-path-fix.md)

### 5.3 Jupyter HTTP 测试

```bash
# 健康检查（返回 200/302/401/403 均表示服务正常）
curl -I http://localhost:8888/api

# 完整访问（带 token）
curl -s "http://localhost:8888/api/contents?token=mysecrettoken" | python3 -m json.tool

# 浏览器访问
# Windows: start http://localhost:8888/?token=mysecrettoken
# macOS:   open http://localhost:8888/?token=mysecrettoken
# Linux:   xdg-open http://localhost:8888/?token=mysecrettoken
```

### 5.4 Docker HEALTHCHECK 验证

```bash
# 查看健康状态
docker inspect --format='{{.State.Health.Status}}' jupyter-ssh
# 期望输出：healthy

# 查看健康检查日志
docker inspect --format='{{json .State.Health}}' jupyter-ssh | python3 -m json.tool

# 手动执行健康检查脚本
docker exec jupyter-ssh /usr/local/bin/healthcheck.sh
```

### 5.5 服务进程验证

```bash
# 查看 supervisord 管理的服务状态
docker exec jupyter-ssh supervisorctl status
# 期望输出：
#   sshd     RUNNING   pid 123, uptime 0:05:30
#   jupyter  RUNNING   pid 124, uptime 0:05:30

# 查看进程
docker exec jupyter-ssh ps aux | grep -E '(sshd|jupyter)'
```

### 5.6 自动重启验证

```bash
# 测试 supervisor 自动重启：杀掉 jupyter 进程
docker exec jupyter-ssh pkill -f jupyter

# 等待 5 秒后检查
sleep 5
docker exec jupyter-ssh supervisorctl status
# 期望：jupyter 进程已自动重启，状态显示 RUNNING
```

---

## 6. 自动化测试脚本

项目提供了两个自动化测试脚本：

### 6.1 SSH 非交互 PATH 测试

```bash
# 完整测试（构建 + 运行 + 验证 + 清理）
bash scripts/test-ssh-noninteractive-path.sh

# 跳过构建（使用已有镜像）
bash scripts/test-ssh-noninteractive-path.sh --skip-build

# 保留容器用于调试
bash scripts/test-ssh-noninteractive-path.sh --keep
```

**测试覆盖：**

| 测试项 | 说明 | 依赖 |
|--------|------|------|
| 4.1 which jupyter | 验证 SSH 非交互会话 PATH 是否包含 /opt/venv/bin | sshpass |
| 4.2 which python3 | 验证 python3 可执行文件可被发现 | sshpass |
| 4.3 jupyter --version | 验证 jupyter 命令可正常执行 | sshpass |
| 4.4 pip --version | 验证 pip 命令可正常执行 | sshpass |
| 4.5 PATH 对比 | 对比交互式和非交互式 PATH 是否一致 | sshpass |
| 5 Jupyter HTTP | 验证 Jupyter HTTP API 响应 | curl |
| 6 Docker HEALTHCHECK | 验证 Docker 原生健康检查 | — |
| 6.1 healthcheck.sh | 验证容器内健康检查脚本 | — |

### 6.2 快速验证脚本

```bash
# 镜像大小检查
docker images jupyter-ssh-base:1.0 --format '{{.Size}}'
# 期望：< 800MB（实际约 713MB）

# 构建信息
docker run --rm jupyter-ssh-base:1.0 cat /etc/jupyter-ssh-build-info

# entrypoint 语法检查
docker run --rm --entrypoint bash jupyter-ssh-base:1.0 -n /usr/local/bin/entrypoint.sh
```

### 6.3 一键健康检查脚本

```bash
# 启动容器 + 全部 6 项健康检查（自动清理）
bash scripts/healthcheck-test.sh
```

**检查覆盖：**

| 步骤 | 检查项 | 验证方式 |
|------|--------|---------|
| 1 | supervisorctl 状态 | `supervisorctl status` → jupyter + sshd 均为 RUNNING |
| 2 | 容器内健康检查 | `healthcheck.sh` → SSH OK + Jupyter HTTP 200 |
| 3 | Docker HEALTHCHECK | `docker inspect` → Status: healthy |
| 4 | Jupyter HTTP API | `curl http://localhost:8889/api` → HTTP 200 |
| 5 | SSH 非交互 PATH | `ssh 'which jupyter'` → `/opt/venv/bin/jupyter` |
| 6 | 容器日志 | `docker logs --tail 20` → 无异常错误 |

---

## 7. 环境变量参考

### 必需变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `USER_PASSWORD` | (随机生成) | 非 root 用户的 SSH 密码 |
| `JUPYTER_TOKEN` | (随机生成) | Jupyter Notebook 访问令牌 |

### 可选变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `NON_ROOT_USER` | `jupyteruser` | 非 root 用户名 |
| `ROOT_PASSWORD` | (随机生成) | root 用户 SSH 密码 |
| `ALLOW_ROOT_SSH` | `no` | 是否允许 root SSH 登录 |
| `GRANT_SUDO` | `no` | 是否授予非 root 用户 sudo 权限 |
| `JUPYTER_PORT` | `8888` | Jupyter 监听端口 |
| `JUPYTER_PASSWORD` | (空) | Jupyter 密码（优先于 TOKEN） |
| `JUPYTER_ALLOW_ORIGIN` | (空) | Jupyter CORS 允许的来源 |
| `SSH_PUBLIC_KEY` | (空) | SSH 公钥（追加到 authorized_keys） |
| `SSH_PORT` | `22` | SSH 监听端口 |
| `TZ` | `Asia/Shanghai` | 时区 |
| `DEBUG` | `0` | 启用 `set -x` 调试输出 |

### 向后兼容别名

| 旧变量名 | 新变量名 | 说明 |
|---------|---------|------|
| `ENABLE_SUDO_NOPASSWD` | `GRANT_SUDO` | 仅当 `GRANT_SUDO=no` 时生效 |
| `JUPYTER_CORS_ORIGIN` | `JUPYTER_ALLOW_ORIGIN` | 仅当 `JUPYTER_ALLOW_ORIGIN` 为空时生效 |

---

## 8. 常见问题排查

### 8.1 SSH 登录失败

```bash
# 症状：ssh: connect to host localhost port 2222: Connection refused
# 原因：容器未启动或端口映射错误

# 检查容器状态
docker ps -a | grep jupyter-ssh

# 查看容器日志
docker logs jupyter-ssh | tail -20

# 检查端口映射
docker port jupyter-ssh
```

### 8.2 SSH 非交互 `which jupyter` 返回空

```bash
# 症状：ssh user@host 'which jupyter' 无输出
# 原因：/etc/environment 未配置 PATH

# 验证修复
docker exec jupyter-ssh cat /etc/environment | grep PATH
# 期望：PATH=/opt/venv/bin:/usr/local/sbin:...

# 检查 PAM 配置
docker exec jupyter-ssh grep -r pam_env /etc/pam.d/ 2>/dev/null || echo "PAM env module may not be loaded"
```

### 8.3 Jupyter 返回 503/连接拒绝

```bash
# 症状：curl http://localhost:8888/api 返回 503 或连接拒绝
# 原因：Jupyter 服务未启动或端口冲突

# 检查 Jupyter 进程
docker exec jupyter-ssh supervisorctl status jupyter

# 查看 Jupyter 日志
docker exec jupyter-ssh tail -50 /var/log/supervisor/jupyter-stderr*.log

# 重启 Jupyter
docker exec jupyter-ssh supervisorctl restart jupyter
```

### 8.4 镜像构建失败

```bash
# 症状：apt-get update 失败
# 解决：使用国内镜像源

bash scripts/build.sh --cn

# 症状：pip install 超时
# 解决：使用国内 PyPI 镜像

bash scripts/build.sh --pip-mirror aliyun

# 症状：磁盘空间不足
# 清理 Docker 缓存

docker system prune -a
```

### 8.5 容器 HEALTHCHECK 失败

```bash
# 症状：docker inspect 显示 Status: unhealthy
# 原因：sshd 或 jupyter 进程未正常启动

# 查看健康检查日志
docker inspect --format='{{json .State.Health}}' jupyter-ssh | python3 -m json.tool

# 手动运行健康检查
docker exec jupyter-ssh /usr/local/bin/healthcheck.sh

# 查看 supervisor 状态
docker exec jupyter-ssh supervisorctl status
```

### 8.6 环境变量不生效

```bash
# 症状：设置的环境变量在容器中未生效
# 原因：容器启动后才能设置环境变量

# 验证环境变量
docker exec jupyter-ssh printenv | grep -E '(USER_PASSWORD|JUPYTER_TOKEN|GRANT_SUDO)'

# 重新创建容器（docker run 时设置环境变量）
docker rm -f jupyter-ssh
docker run -d ... -e USER_PASSWORD=newpass ...
```

### 8.7 AsyncClient proxies 警告（v1.1 已修复）

```bash
# 症状：日志中出现以下警告
#   TypeError: AsyncClient.__init__() got an unexpected keyword argument 'proxies'
```

**根因分析：** httpx 0.28.1 移除了 `proxies` 参数，但 jupyter_server 2.14.1 仍在使用旧 API。

**修复方案（v1.1）：** 配置 supervisor 将 Jupyter stderr 重定向到日志文件，不再输出到容器 stdout/stderr。

```ini
# config/supervisor/conf.d/jupyter.conf 关键变更
stderr_logfile=/var/log/supervisor/jupyter-stderr.log
stderr_logfile_maxbytes=1048576
redirect_stderr=false
```

**状态：** 已消除。如需查看 stderr 日志：`docker exec <container> tail -f /var/log/supervisor/jupyter-stderr.log`

### 8.8 banner exchange 警告（v1.1 已修复）

```bash
# 症状：日志中出现
#   banner exchange: Connection from 127.0.0.1 port XXXXX: invalid format
```

**根因：** Docker HEALTHCHECK 对 SSH 端口发送了 HTTP 请求，SSH 无法解析 HTTP 协议。

**修复方案（v1.1）：**
1. healthcheck.sh 改用 exec-based TCP 探针，不发送任何数据
2. sshd_config 将 LogLevel 从 INFO 降为 ERROR

**状态：** 已消除。

---

## 9. docker-compose 部署

### 9.1 基本部署

```bash
# 启动
docker compose up -d

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

### 9.2 自定义配置

编辑 `docker-compose.yml` 或创建 `docker-compose.override.yml`：

```yaml
version: '3.8'
services:
  jupyter-ssh:
    ports:
      - "2222:22"      # 自定义 SSH 端口
      - "8888:8888"
    environment:
      - USER_PASSWORD=mysecurepassword
      - JUPYTER_TOKEN=mysecrettoken
      - GRANT_SUDO=yes
      - TZ=Asia/Shanghai
    volumes:
      - ./my_workspace:/workspace
      - ./my_config:/home/jupyteruser/.jupyter/jupyter_notebook_config.py:ro
```

### 9.3 多实例部署

```bash
# 实例 1
docker compose -p jupyter-project1 up -d

# 实例 2（需要修改端口和环境变量）
JUPYTER_PORT=8889 SSH_PORT=2223 docker compose -p jupyter-project2 up -d
```

---

## 附录：快速参考卡片

```bash
# ===== 构建 =====
bash scripts/build.sh --cn                    # 快速构建

# ===== 运行 =====
docker run -d --name js -p 2222:22 -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -e USER_PASSWORD=pass -e JUPYTER_TOKEN=token \
  jupyter-ssh-base:1.0

# ===== 验证 =====
ssh -p 2222 jupyteruser@localhost             # SSH 登录
ssh -p 2222 jupyteruser@localhost 'which jupyter'  # SSH PATH 检查
curl http://localhost:8888/api                # Jupyter 健康检查
docker exec js /usr/local/bin/healthcheck.sh  # 容器健康检查
docker exec js supervisorctl status           # 服务状态

# ===== 测试 =====
bash scripts/test-ssh-noninteractive-path.sh  # 自动化测试
bash scripts/healthcheck-test.sh              # 一键健康检查

# ===== 清理 =====
docker rm -f js                               # 删除容器
docker rmi jupyter-ssh-base:1.0              # 删除镜像
```

---

## 10. 构建验证记录

> 以下记录基于 2026-07-24 在 WSL (Ubuntu) + Docker 24.0 环境中的实际构建与验证结果。

### 10.1 构建信息

| 项目 | 值 |
|------|-----|
| 构建日期 | 2026-07-24 |
| 版本 | v1.1 |
| 基础镜像 | ubuntu:26.04 |
| 构建方式 | Multi-stage (2 stages) |
| 构建步骤 | 27/27 全部完成 |
| 构建耗时 | ~195s |
| 镜像大小 | 713MB |
| APT 镜像 | aliyun |
| PyPI 镜像 | aliyun |

### 10.2 健康检查结果

| # | 检查项 | 方式 | 结果 |
|---|--------|------|------|
| 1 | supervisorctl 状态 | `supervisorctl status` | 2/2 RUNNING |
| 2 | 容器内健康检查 | `healthcheck.sh` | HEALTHY (SSH OK + HTTP 200) |
| 3 | Docker HEALTHCHECK | `docker inspect` | healthy |
| 4 | Jupyter HTTP API | `curl /api` | HTTP 200 |
| 5 | SSH 非交互 which jupyter | `ssh 'which jupyter'` | `/opt/venv/bin/jupyter` |
| 6 | SSH 非交互 which python3 | `ssh 'which python3'` | `/opt/venv/bin/python3` |

**结论：全部 6 项检查通过，零失败。**

### 10.3 告警优化（v1.1）

| 告警 | 优化方案 | 状态 |
|------|---------|------|
| `AsyncClient.__init__() got an unexpected keyword argument 'proxies'` | supervisor 将 Jupyter stderr 重定向到日志文件 | 已消除 |
| `banner exchange: invalid format` | healthcheck.sh 改用 exec TCP 探针 + sshd LogLevel=ERROR | 已消除 |
| `SecretsUsedInArgOrEnv` (3 warnings) | Dockerfile 移除敏感 ENV 空声明 | 已消除 |

### 10.4 本次验证新增内容

| 类别 | 内容 | 文件 |
|------|------|------|
| 文档 | 项目交付文档（13 章） | [DELIVERY.md](DELIVERY.md) |
| 文档 | 完整构建与运行测试指南 | [GUIDE.md](GUIDE.md) |
| 文档 | 构建验证报告 | [VERIFICATION-REPORT.md](VERIFICATION-REPORT.md) |
| 脚本 | 一键健康检查脚本（6 项检查） | [scripts/healthcheck-test.sh](scripts/healthcheck-test.sh) |
| 脚本 | SSH 非交互 PATH 集成测试（8 项测试） | [scripts/test-ssh-noninteractive-path.sh](scripts/test-ssh-noninteractive-path.sh) |
| CI/CD | GitHub Actions 自动化流水线 | [.github/workflows/jupyter-ssh-base-ci.yml](../../.github/workflows/jupyter-ssh-base-ci.yml) |
| 修复 | entrypoint.sh 加固（set -euo pipefail） | [entrypoint.sh](entrypoint.sh) |
| 优化 | Jupyter stderr 重定向到日志文件 | [config/supervisor/conf.d/jupyter.conf](config/supervisor/conf.d/jupyter.conf) |
| 优化 | healthcheck.sh TCP 探针优化 | [scripts/healthcheck.sh](scripts/healthcheck.sh) |
| 优化 | sshd LogLevel 降为 ERROR | [config/sshd_config](config/sshd_config) |
| 优化 | Dockerfile 移除敏感 ENV 声明 | [Dockerfile](Dockerfile) |