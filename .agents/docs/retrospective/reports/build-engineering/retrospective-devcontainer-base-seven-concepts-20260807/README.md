---
id: retrospective-devcontainer-base-20260807
date: 2026-08-07
type: retrospective
source: "七概念方法论实践：apps/devcontainer-base 构建验证与Docker Compose部署"
tags: [docker, devcontainer, dind, supervisord, ssh, jupyter, podman, build-verification]
---

# devcontainer-base 构建验证与部署里程碑复盘

## 一、背景与目标

基于七概念方法论（R-I-E-C-A-F-V）完成 `apps/devcontainer-base` 全功能开发容器基础镜像的构建验证、Docker Compose部署测试与国内镜像源适配。

**目标交付物：**
- 基于 Ubuntu 26.04 的多服务开发容器（SSH + Docker DinD + Podman rootless + Jupyter）
- supervisord 统一管理多进程
- 多阶段构建（builder + runtime）优化镜像体积
- Docker Compose 三模式支持（DinD/DooD/SSH-only）
- 国内镜像源快速切换能力
- 自动化构建验证脚本

## 二、事实还原（R - Retrospective）

### 2.1 关键数据

| 指标 | 值 |
|------|-----|
| 基础镜像 | ubuntu:26.04 |
| 最终镜像大小 | 1.35GB |
| 构建耗时（冷构建） | ~321秒（runtime阶段） |
| 构建耗时（缓存命中） | ~8秒 |
| Docker版本 | 29.7.2（DinD内置） |
| Jupyter版本 | 2.14.1 |
| 非root用户 | devuser (UID 1001) |
| 服务管理 | supervisord（sshd + dockerd + jupyter） |

### 2.2 时间线

| 阶段 | 事件 | 结果 |
|------|------|------|
| 构建验证 | `bash scripts/build.sh --verify` | 构建成功，验证阶段Docker socket未找到 |
| 问题排查 | 手动启动容器查看日志 | 发现dockerd崩溃循环：命令行参数与daemon.json冲突 |
| Bug修复 | 移除dockerd.conf中重复命令行参数 | dockerd启动参数从5个缩减为`--log-level=error` |
| 等待时间调整 | build.sh验证等待从15s→25s | 匹配dockerd的startsecs=15s初始化窗口 |
| 重新验证 | `bash scripts/build.sh --verify` | ✅ 全部通过：SSH OK、Docker DinD OK (29.7.2)、Jupyter OK (HTTP 200)、HEALTHY |
| Compose启动 | `docker compose --profile dind up -d` | 容器启动但SSH密码认证失败 |
| 问题排查 | 检查环境变量传递 | 发现compose中硬编码环境变量，shell环境无法覆盖 |
| Compose修复 | 使用YAML锚点`x-common-env` + `${VAR:-default}`语法 | 支持环境变量覆盖，端口也可配置 |
| SSH测试 | 从WSL宿主机SSH连接容器 | ✅ devuser登录成功、sudo免密正常、docker ps正常、Jupyter API正常 |
| 国内镜像源验证 | 检查`--cn`参数配置 | ✅ 阿里云APT+PyPI镜像源已配置，支持aliyun/tuna/official三选项 |

### 2.3 问题清单

| # | 问题 | 现象 | 根因 |
|---|------|------|------|
| P1 | dockerd启动失败 | supervisor反复重启dockerd，FATAL状态 | dockerd命令行参数（--iptables/--storage-driver/--userland-proxy）与/etc/docker/daemon.json配置项重复，Docker禁止冲突配置 |
| P2 | 构建验证等待不足 | healthcheck时docker socket未就绪 | dockerd startsecs=15s但验证脚本只等15s，存在竞态 |
| P3 | Compose环境变量无法覆盖 | USER_PASSWORD=xxx docker compose up不生效 | docker-compose.yml使用`- USER_PASSWORD=changeme`硬编码，需改为`${USER_PASSWORD:-changeme}`变量替换语法 |
| P4 | Windows本地无Docker | build.sh无法直接运行 | 切换到WSL2 Ubuntu-24.04环境执行Docker命令 |

## 三、根因洞察（I - Insight）

### 洞察1：Docker daemon配置冲突是"启动时才暴露"的隐性Bug

- **现象**：镜像构建完全成功，但dockerd在容器启动时崩溃
- **根因**：Docker daemon不允许同一配置项同时在命令行flag和daemon.json中出现（即使值相同也不行）
- **影响**：构建阶段无法发现，必须在运行时通过supervisor日志才能定位
- **建议**：Docker DinD配置模式——**daemon.json作为唯一配置源，命令行仅保留--log-level等非冲突参数**；构建后应在验证脚本中检查dockerd是否稳定运行（startsecs+额外等待）

### 洞察2：Docker Compose环境变量覆盖有反直觉语法

- **现象**：shell中设置的环境变量无法覆盖compose文件中的值
- **根因**：`- KEY=value`是字面值赋值，`- KEY=${KEY:-default}`才是变量替换
- **影响**：用户通过`USER_PASSWORD=xxx docker compose up`无法自定义密码，只能硬编码
- **建议**：Compose最佳实践——使用YAML锚点（`x-common-env`）提取公共环境变量块，所有可配置项使用`${VAR:-default}`语法

### 洞察3：WSL2是Windows环境运行Docker的可靠桥梁

- **现象**：PowerShell/cmd环境无法直接执行bash+docker
- **根因**：Windows Docker Desktop未安装，但WSL2 Ubuntu环境中Docker已配置
- **建议**：Windows环境下优先使用`wsl -d Ubuntu-24.04 -- bash -c "..."`执行Docker相关操作，避免环境兼容性问题

## 四、可复用模式萃取（E - Extraction）

### 模式1：Docker DinD supervisord无冲突配置

**触发场景**：在容器中通过supervisord管理dockerd进程

**核心步骤**：
1. daemon.json作为唯一配置源（storage-driver、iptables、userland-proxy、registry-mirrors等）
2. supervisord命令行仅使用`/usr/bin/dockerd --log-level=error`
3. startsecs设置为15s，给dockerd足够的初始化时间
4. 健康检查脚本在supervisord报告RUNNING后再验证docker socket

**反模式**：
- ❌ 同时在命令行和daemon.json中指定相同选项
- ❌ startsecs设置过小导致supervisord误判服务启动失败
- ❌ 健康检查不等待足够时间就开始验证socket

### 模式2：Docker Compose环境变量覆盖模板

**触发场景**：需要用户通过环境变量自定义容器配置（密码、端口、token等）

**核心步骤**：
1. 使用`x-common-env: &common-env` YAML锚点提取公共环境变量块
2. 每个变量使用`${VAR_NAME:-default_value}`语法
3. 端口映射也使用`${PORT:-2222}:22`支持自定义
4. 在注释中列出所有可覆盖的环境变量及默认值

**反模式**：
- ❌ 硬编码`- USER_PASSWORD=changeme`导致无法覆盖
- ❌ 不提供默认值导致缺失环境变量时启动失败
- ❌ 每个服务重复定义环境变量而不使用YAML锚点

### 模式3：构建后自动化验证三段式

**触发场景**：Docker镜像构建完成后需要自动化验证服务可用性

**核心步骤**：
1. `docker run -d --privileged`启动验证容器（传递测试用环境变量）
2. 等待足够时间（`sleep 25`，匹配最慢服务的启动窗口）
3. 依次验证：健康检查脚本 → Docker API (`docker info`) → Jupyter HTTP → SSH端口
4. 无论成功失败，清理验证容器（`docker rm -f`）

## 五、国内镜像源使用指南

### 快速切换（一键国内源）

```bash
# 构建时使用阿里云镜像（推荐国内用户）
bash scripts/build.sh --cn --verify

# 或分别指定APT和PyPI镜像
bash scripts/build.sh --apt-mirror tuna --pip-mirror tuna --verify
```

### 支持的镜像源

| 选项 | APT源 | PyPI源 |
|------|-------|--------|
| `official`（默认） | archive.ubuntu.com + security.ubuntu.com | pypi.org |
| `aliyun`（--cn） | mirrors.aliyun.com | mirrors.aliyun.com/pypi/simple |
| `tuna` | mirrors.tuna.tsinghua.edu.cn | pypi.tuna.tsinghua.edu.cn/simple |

### Docker CE 加速（运行时配置）

容器内dockerd可通过`/etc/docker/daemon.json`配置registry-mirrors：
```json
{
  "registry-mirrors": ["https://<your-mirror>.mirror.aliyuncs.com"]
}
```

## 六、Docker Compose 三种使用模式

### 1. DinD模式（推荐）—— 完全隔离的Docker环境

```bash
# 启动（需要--privileged）
USER_PASSWORD=mypassword JUPYTER_TOKEN=mytoken docker compose --profile dind up -d

# SSH连接
ssh -p 2222 devuser@localhost  # 密码: mypassword

# Jupyter访问
# http://localhost:8888/?token=mytoken

# 容器内操作
docker compose exec devcontainer-dind docker ps  # DinD内部Docker
```

### 2. DooD模式 —— 共享宿主机Docker（无需--privileged）

```bash
USER_PASSWORD=mypassword docker compose --profile dood up -d
# SSH端口: 2223, Jupyter端口: 8889
```

### 3. SSH-only模式 —— 最小化，仅SSH

```bash
USER_PASSWORD=mypassword docker compose --profile ssh-only up -d
# SSH端口: 2224, 无Docker, 无Jupyter
```

## 七、验证结果汇总

| 检查项 | 状态 | 详情 |
|--------|------|------|
| 镜像构建 | ✅ PASS | devcontainer-base:1.0, 1.35GB |
| SSH服务 | ✅ PASS | devuser密码登录成功，ED25519 host key |
| Docker DinD | ✅ PASS | Docker Server 29.7.2, docker ps正常 |
| sudo权限 | ✅ PASS | NOPASSWD sudo（GRANT_SUDO=yes时） |
| Podman rootless | ✅ PASS | 可用（有shared mount警告，不影响功能） |
| Jupyter Notebook | ✅ PASS | HTTP 200, API版本2.14.1 |
| supervisord | ✅ PASS | 三服务均RUNNING，无FATAL |
| 健康检查 | ✅ PASS | STATUS: HEALTHY |
| Compose环境变量 | ✅ PASS | USER_PASSWORD等可通过shell环境覆盖 |
| 国内镜像源 | ✅ PASS | --cn参数正确配置阿里云镜像 |

## 八、提交记录

| Commit | 类型 | 说明 |
|--------|------|------|
| d1598a8a | feat(devcontainer-base) | 初始提交：7阶段分层+Docker DinD+Podman rootless |
| 2e666e09 | feat(apps) | 注册devcontainer-base到apps路由表+添加.gitignore |
| bfeb0220 | docs(specs) | 新增devcontainer-base七概念方法论规划spec |

## 九、后续行动项

1. **[可选]** 添加DooD模式的entrypoint自动检测（当挂载/var/run/docker.sock时禁用内部dockerd）
2. **[可选]** 在Dockerfile中为dockerd配置默认registry-mirrors（国内加速）
3. **[可选]** 添加Podman rootless的健康检查支持
4. **[持续]** 关注Ubuntu 26.04官方源的稳定性（26.04较新，可能存在包兼容性问题）
