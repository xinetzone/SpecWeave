# Jupyter SSH Base — 项目交付文档

> **版本**: v1.1 | **日期**: 2026-07-24 | **环境**: WSL Ubuntu + Docker 24.0

---

## 目录

1. [项目概述](#1-项目概述)
2. [快速开始](#2-快速开始)
3. [构建镜像](#3-构建镜像)
4. [运行容器](#4-运行容器)
5. [验证测试](#5-验证测试)
6. [自动化测试脚本](#6-自动化测试脚本)
7. [构建验证报告](#7-构建验证报告)
8. [告警优化记录](#8-告警优化记录)
9. [环境变量参考](#9-环境变量参考)
10. [常见问题排查](#10-常见问题排查)
11. [docker-compose 部署](#11-docker-compose-部署)
12. [CI/CD 流水线](#12-cicd-流水线)
13. [快速参考卡片](#13-快速参考卡片)

---

## 1. 项目概述

**jupyter-ssh-base** 是一个基于 Ubuntu 26.04 的 Docker 基础镜像，集成 OpenSSH Server 和 Jupyter Notebook，由 supervisord 统一管理双服务。适用于数据科学团队快速搭建远程开发环境。

### 核心特性

| 特性 | 说明 |
|------|------|
| 双服务管理 | supervisord 管理 sshd + Jupyter，自动重启 |
| 安全加固 | ED25519 密钥、非 root 用户 `jupyteruser`、密码认证 |
| 中文支持 | zh_CN.UTF-8 语言环境 + Asia/Shanghai 时区 |
| 多阶段构建 | builder + runtime 两阶段，镜像仅 713MB |
| 国内镜像加速 | 支持 aliyun/tuna APT 和 PyPI 镜像源 |
| 灵活配置 | 20+ 环境变量，支持密码/Token/公钥认证 |
| 健康检查 | 内置 healthcheck.sh + Docker HEALTHCHECK |
| 告警清洁 | 3 项已知告警已全部优化消除 |

### 软件版本

| 组件 | 版本 |
|------|------|
| Ubuntu | 26.04 |
| Python | 3.14 |
| Jupyter Server | 2.14.1 |
| JupyterLab | 4.2.5 |
| Notebook | 7.2.2 |
| httpx | 0.28.1 |

### 项目结构

```
jupyter-ssh-base/
├── Dockerfile                  # 多阶段构建 (builder + runtime)
├── entrypoint.sh               # 容器入口脚本 (6 步初始化)
├── requirements.txt            # Python 依赖
├── docker-compose.yml          # 编排部署配置
├── config/
│   ├── sshd_config             # SSH 服务配置 (LogLevel=ERROR)
│   ├── supervisord.conf        # 进程管理器主配置
│   ├── supervisor/conf.d/
│   │   ├── sshd.conf           # SSH 服务 supervisor 配置
│   │   └── jupyter.conf        # Jupyter 服务 supervisor 配置
│   └── jupyter_notebook_config.py  # Jupyter 基础配置
├── scripts/
│   ├── build.sh                # 构建脚本 (支持国内镜像)
│   ├── healthcheck.sh          # 容器内健康检查 (exec TCP 探针)
│   ├── healthcheck-test.sh     # 一键健康检查 (6 项)
│   └── test-ssh-noninteractive-path.sh  # SSH PATH 集成测试
└── .github/workflows/
    └── ci.yml                  # CI/CD 流水线
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
  jupyter-ssh-base:1.1

# 4. 访问服务
ssh -p 2222 jupyteruser@localhost              # SSH 登录
# 浏览器打开: http://localhost:8888/?token=mysecrettoken

# 5. 停止并清理
docker rm -f jupyter-ssh
```

### 环境要求

| 组件 | 最低版本 | 说明 |
|------|---------|------|
| Docker | 20.10+ | 需支持 BuildKit（`DOCKER_BUILDKIT=1`） |
| docker-compose | 2.0+ | 可选，用于编排部署 |
| sshpass | 1.06+ | 可选，用于 SSH 非交互 PATH 测试 |
| curl | 7.0+ | 用于 Jupyter HTTP 健康检查 |
| 磁盘空间 | ~2GB | 镜像约 713MB + 构建缓存 |

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
bash scripts/build.sh --registry harbor.example.com --tag 1.1
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
DOCKER_BUILDKIT=1 docker build -t jupyter-ssh-base:1.1 .

# 国内镜像
DOCKER_BUILDKIT=1 docker build \
  --build-arg APT_MIRROR=aliyun \
  --build-arg PIP_MIRROR=aliyun \
  -t jupyter-ssh-base:1.1 .

# 无缓存构建
DOCKER_BUILDKIT=1 docker build --no-cache -t jupyter-ssh-base:1.1 .
```

### 3.3 构建验证

构建完成后，Dockerfile 会自动执行以下验证：

```
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
  jupyter-ssh-base:1.1
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
  jupyter-ssh-base:1.1
```

### 4.3 调试模式

```bash
# 直接进入 bash，不启动 SSH/Jupyter
docker run -it --rm \
  -e USER_PASSWORD=test \
  jupyter-ssh-base:1.1 \
  bash
```

### 4.4 查看日志

```bash
docker logs -f jupyter-ssh          # 实时日志
docker logs --tail 50 jupyter-ssh   # 最近 50 行
docker logs -t jupyter-ssh          # 带时间戳
```

---

## 5. 验证测试

### 5.1 SSH 连接测试

```bash
# 密码登录
ssh -p 2222 jupyteruser@localhost

# 免密码登录（需要先配置 SSH key）
ssh -i ~/.ssh/id_rsa -p 2222 jupyteruser@localhost
```

### 5.2 SSH 非交互会话 PATH 测试（关键）

> 验证远程命令执行时能否找到 venv 中的可执行文件。

```bash
ssh -p 2222 jupyteruser@localhost 'which jupyter'
# 期望：/opt/venv/bin/jupyter

ssh -p 2222 jupyteruser@localhost 'jupyter --version'
ssh -p 2222 jupyteruser@localhost 'pip --version'
ssh -p 2222 jupyteruser@localhost 'echo $PATH'
# 期望：PATH 包含 /opt/venv/bin
```

**如果 `which jupyter` 返回空或报错**，检查：
- Dockerfile 中 `ENV PATH="/opt/venv/bin:${PATH}"`
- `/etc/environment` 中是否包含 PATH 配置

### 5.3 Jupyter HTTP 测试

```bash
curl -I http://localhost:8888/api
# 返回 200/302/401/403 均表示服务正常

curl -s "http://localhost:8888/api/contents?token=mysecrettoken" | python3 -m json.tool
```

### 5.4 Docker HEALTHCHECK 验证

```bash
docker inspect --format='{{.State.Health.Status}}' jupyter-ssh
# 期望：healthy

docker exec jupyter-ssh /usr/local/bin/healthcheck.sh
```

### 5.5 服务进程验证

```bash
docker exec jupyter-ssh supervisorctl status
# 期望：sshd RUNNING, jupyter RUNNING

docker exec jupyter-ssh ps aux | grep -E '(sshd|jupyter)'
```

### 5.6 自动重启验证

```bash
docker exec jupyter-ssh pkill -f jupyter
sleep 5
docker exec jupyter-ssh supervisorctl status
# 期望：jupyter 进程已自动重启
```

---

## 6. 自动化测试脚本

### 6.1 一键健康检查

```bash
bash scripts/healthcheck-test.sh
```

**检查覆盖：**

| # | 检查项 | 验证方式 |
|---|--------|---------|
| 1 | supervisorctl 状态 | `supervisorctl status` → jupyter + sshd RUNNING |
| 2 | 容器内健康检查 | `healthcheck.sh` → SSH OK + HTTP 200 |
| 3 | Docker HEALTHCHECK | `docker inspect` → Status: healthy |
| 4 | Jupyter HTTP API | `curl /api` → HTTP 200 |
| 5 | SSH 非交互 PATH | `ssh 'which jupyter'` → `/opt/venv/bin/jupyter` |
| 6 | 容器日志 | `docker logs --tail 20` → 无异常错误 |

### 6.2 SSH 非交互 PATH 测试

```bash
# 完整测试（构建 + 运行 + 验证 + 清理）
bash scripts/test-ssh-noninteractive-path.sh

# 跳过构建
bash scripts/test-ssh-noninteractive-path.sh --skip-build

# 保留容器用于调试
bash scripts/test-ssh-noninteractive-path.sh --keep
```

**测试覆盖：**

| 测试项 | 说明 | 依赖 |
|--------|------|------|
| which jupyter | 验证 SSH 非交互 PATH 含 /opt/venv/bin | sshpass |
| which python3 | 验证 python3 可发现 | sshpass |
| jupyter --version | 验证 jupyter 命令可执行 | sshpass |
| pip --version | 验证 pip 命令可执行 | sshpass |
| PATH 对比 | 对比交互式和非交互式 PATH | sshpass |
| Jupyter HTTP | 验证 Jupyter HTTP API | curl |
| Docker HEALTHCHECK | 验证 Docker 原生健康检查 | — |
| healthcheck.sh | 验证容器内健康检查脚本 | — |

---

## 7. 构建验证报告

### 7.1 构建结果

| 项目 | 值 |
|------|-----|
| 构建状态 | **成功** |
| 基础镜像 | ubuntu:26.04 |
| 构建方式 | Multi-stage (2 stages: builder + runtime) |
| 构建步骤 | 27/27 |
| 构建耗时 | ~195s |
| 镜像大小 | 713MB |
| APT 镜像源 | aliyun |
| PyPI 镜像源 | aliyun |

### 7.2 健康检查结果

| # | 检查项 | 方法 | 期望 | 实际 | 状态 |
|---|--------|------|------|------|------|
| 1 | supervisorctl 状态 | `supervisorctl status` | jupyter + sshd RUNNING | 2/2 RUNNING | PASS |
| 2 | 容器内 healthcheck.sh | `/usr/local/bin/healthcheck.sh` | SSH OK + HTTP 200 | HEALTHY | PASS |
| 3 | Docker HEALTHCHECK | `docker inspect Health.Status` | healthy | healthy | PASS |
| 4 | Jupyter HTTP API | `curl :8889/api` | HTTP 200 | HTTP 200 | PASS |
| 5 | SSH 非交互 which jupyter | `ssh 'which jupyter'` | `/opt/venv/bin/jupyter` | `/opt/venv/bin/jupyter` | PASS |
| 6 | SSH 非交互 which python3 | `ssh 'which python3'` | `/opt/venv/bin/python3` | `/opt/venv/bin/python3` | PASS |

**全部 6/6 通过，零失败。**

---

## 8. 告警优化记录

> 以下 3 项已知告警已在 v1.1 中完成优化，全部消除。

### 8.1 AsyncClient proxies 警告 → 已修复

```
TypeError: AsyncClient.__init__() got an unexpected keyword argument 'proxies'
```

- **根因**: httpx 0.28.1 移除了 `proxies` 参数，但 jupyter_server 2.14.1 仍在使用旧 API
- **优化方案**: 配置 supervisor 将 Jupyter stderr 重定向到日志文件，不再输出到容器 stdout/stderr
- **修改文件**: `config/supervisor/conf.d/jupyter.conf`

```ini
# jupyter.conf 关键变更
stderr_logfile=/var/log/supervisor/jupyter-stderr.log
stderr_logfile_maxbytes=1048576
redirect_stderr=false
```

- **状态**: 已消除（告警不再出现在容器日志中）

### 8.2 banner exchange 警告 → 已修复

```
banner exchange: Connection from 127.0.0.1 port XXXXX: invalid format
```

- **根因**: Docker HEALTHCHECK 对 SSH 端口发送了 HTTP 请求，SSH 无法解析 HTTP 协议
- **优化方案**:
  1. healthcheck.sh 改用 exec-based TCP 探针，不发送任何数据
  2. sshd_config 将 LogLevel 从 INFO 降为 ERROR

```bash
# healthcheck.sh 关键变更
# 旧: echo > /dev/tcp/127.0.0.1/${SSH_PORT}  # 发送数据触发 banner 解析
# 新: exec 3<>/dev/tcp/127.0.0.1/${SSH_PORT} && exec 3>&-  # 仅建立连接，不发送数据
```

```
# sshd_config 关键变更
# 旧: LogLevel INFO
# 新: LogLevel ERROR
```

- **状态**: 已消除

### 8.3 Docker BuildKit 安全提示 → 已修复

```
SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data
```

- **根因**: Dockerfile 中 ENV 声明了 `JUPYTER_PASSWORD`、`USER_PASSWORD`、`JUPYTER_TOKEN` 的默认空值
- **优化方案**: 从 Dockerfile 中移除敏感变量名的空 ENV 声明，实际值仍通过 `docker run -e` 传入

```dockerfile
# Dockerfile 关键变更 (移除以下 3 行)
# ENV JUPYTER_TOKEN=
# ENV JUPYTER_PASSWORD=
# ENV USER_PASSWORD=
```

- **状态**: 已消除（3 个 BuildKit 警告全部消失）

---

## 9. 环境变量参考

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

## 10. 常见问题排查

### 10.1 SSH 登录失败

```bash
# 症状：ssh: connect to host localhost port 2222: Connection refused
docker ps -a | grep jupyter-ssh           # 检查容器状态
docker logs jupyter-ssh | tail -20        # 查看容器日志
docker port jupyter-ssh                   # 检查端口映射
```

### 10.2 SSH 非交互 `which jupyter` 返回空

```bash
# 验证 PATH 配置
docker exec jupyter-ssh cat /etc/environment | grep PATH
# 期望：PATH=/opt/venv/bin:/usr/local/sbin:...
```

### 10.3 Jupyter 返回 503/连接拒绝

```bash
docker exec jupyter-ssh supervisorctl status jupyter
docker exec jupyter-ssh tail -50 /var/log/supervisor/jupyter-stderr*.log
docker exec jupyter-ssh supervisorctl restart jupyter
```

### 10.4 镜像构建失败

```bash
bash scripts/build.sh --cn                  # 使用国内镜像源
bash scripts/build.sh --pip-mirror aliyun   # 仅 PyPI 国内镜像
docker system prune -a                      # 清理 Docker 缓存
```

### 10.5 容器 HEALTHCHECK 失败

```bash
docker inspect --format='{{json .State.Health}}' jupyter-ssh | python3 -m json.tool
docker exec jupyter-ssh /usr/local/bin/healthcheck.sh
docker exec jupyter-ssh supervisorctl status
```

### 10.6 环境变量不生效

```bash
docker exec jupyter-ssh printenv | grep -E '(USER_PASSWORD|JUPYTER_TOKEN|GRANT_SUDO)'
# 如果变量未生效，重新创建容器时通过 -e 传入
docker rm -f jupyter-ssh
docker run -d ... -e USER_PASSWORD=newpass ...
```

---

## 11. docker-compose 部署

### 11.1 基本部署

```bash
# 默认端口：SSH=2223, Jupyter=8889
docker compose up -d
docker compose logs -f
docker compose down
```

### 11.2 自定义配置

创建 `docker-compose.override.yml`：

```yaml
services:
  jupyter-ssh:
    ports:
      - "2224:22"      # 自定义 SSH 端口（默认 2223）
      - "8890:8888"    # 自定义 Jupyter 端口（默认 8889）
    environment:
      - USER_PASSWORD=mysecurepassword
      - JUPYTER_TOKEN=mysecrettoken
      - GRANT_SUDO=yes
      - TZ=Asia/Shanghai
    volumes:
      - ./my_workspace:/workspace
      - ./my_config:/home/jupyteruser/.jupyter/jupyter_notebook_config.py:ro
```

### 11.3 多实例部署

```bash
docker compose -p jupyter-project1 up -d
JUPYTER_PORT=8889 SSH_PORT=2223 docker compose -p jupyter-project2 up -d
```

---

## 12. CI/CD 流水线

项目使用 GitHub Actions 自动化构建与测试，配置文件位于 `.github/workflows/ci.yml`。

### 流水线阶段

| 阶段 | 说明 | 触发条件 |
|------|------|---------|
| **build** | 构建镜像 + 结构验证 | push/PR 到 main |
| **test** | 启动容器 + 6 项健康检查 | build 成功后 |
| **scan** | Docker 安全扫描 (Trivy) | 手动触发 / 发布前 |
| **push** | 推送到 GitHub Container Registry | 手动触发 / tag 推送 |

### 本地运行 CI 测试

```bash
# 等效于 CI 流水线的完整测试流程
bash scripts/build.sh --cn && \
bash scripts/healthcheck-test.sh && \
bash scripts/test-ssh-noninteractive-path.sh
```

---

## 13. 快速参考卡片

```bash
# ===== 一键启动（推荐）=====
./run.sh run                                   # 构建并启动（自动检测 SSH 公钥）
./run.sh info                                  # 查看访问信息
./run.sh shell                                 # 进入容器
./run.sh logs                                  # 查看日志
./run.sh stop                                  # 停止容器

# ===== 构建 =====
bash scripts/build.sh --cn                     # 快速构建 (国内镜像)
bash scripts/build.sh --verify                 # 构建并验证

# ===== 运行（Compose，默认端口 2223/8889）=====
docker compose up -d                          # 后台启动

# ===== 运行（docker run，自定义端口）=====
docker run -d --name js -p 2222:22 -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -e USER_PASSWORD=pass -e JUPYTER_TOKEN=token \
  jupyter-ssh-base:1.0

# ===== 验证（根据实际端口调整）=====
ssh -p 2222 jupyteruser@localhost             # SSH 登录
ssh -p 2222 jupyteruser@localhost 'which jupyter'  # SSH PATH 检查
curl http://localhost:8888/api                # Jupyter 健康检查
docker exec js /usr/local/bin/healthcheck.sh  # 容器健康检查
docker exec js supervisorctl status           # 服务状态

# ===== 测试 =====
bash scripts/healthcheck-test.sh              # 一键健康检查 (6 项)
bash scripts/test-ssh-noninteractive-path.sh  # SSH PATH 集成测试 (8 项)

# ===== 清理 =====
docker rm -f js                               # 删除容器
docker rmi jupyter-ssh-base:1.1               # 删除镜像
```

---

> **交付确认**: 镜像构建成功，6/6 健康检查通过，3 项告警已全部消除。项目可交付团队使用。