---
id: "docker-container-management-script-checklist"
title: "Docker容器一键管理脚本开发检查清单"
source: ".agents/docs/retrospective/reports/task-reports/retrospective-caffe-jupyter-docker-build-20260726/README.md"
related_patterns:
  - "docker-one-click-management-script.md"
  - "wsl-environment-detection.md"
  - "dockerfile-layer-cache-optimization.md"
tags: ["docker", "checklist", "bash-script", "container-management", "wsl", "devops"]
---

# Docker容器一键管理脚本开发检查清单

> 基于 Caffe Jupyter Docker 镜像构建 + run-jupyter.sh 脚本开发复盘萃取，覆盖环境探测、脚本健壮性、容器生命周期、WSL兼容 4 大维度共 24 个检查项。
>
> **适用场景**：为 Docker 镜像开发一键启动/停止/管理 Shell 脚本（支持 WSL/Linux/macOS 环境）。

---

## 使用方法

在开发 Docker 管理脚本过程中，按阶段逐项打勾。每完成一个阶段后必须通过该阶段所有检查项才能进入下一阶段。

```
阶段1：环境探测与前置检查 → 阶段2：脚本结构与健壮性 → 阶段3：容器生命周期管理 → 阶段4：WSL兼容性与验证
```

---

## 阶段1：环境探测与前置检查（Pre-flight）

### 1.1 WSL环境探测

| # | 检查项 | 反模式 | 对应问题/模式 |
|---|--------|--------|--------------|
| 1 | ✅ **执行前先探测可用WSL发行版**：`wsl --list --all` 获取发行版列表 | ❌ 硬编码发行版名称（如`wsl -d Ubuntu-22.04`），用户环境可能不存在 | 问题1：WSL发行版假设错误 |
| 2 | ✅ **优先使用默认WSL发行版**：无 `-d` 参数直接 `wsl bash -c "cmd"` | ❌ 强制指定特定发行版名称，与Docker基础镜像版本混淆（Ubuntu:22.04 ≠ WSL发行版名） | 模式2：WSL环境探测先行 |
| 3 | ✅ **跨平台检测当前运行环境**：通过 `/proc/version` 判断是否在WSL内 | ❌ 假设脚本总是在原生Linux运行，或总是在Windows PowerShell运行 | 模式2：WSL环境探测先行 |
| 4 | ✅ **验证docker命令可用性**：`command -v docker` 检查docker是否安装且在PATH中 | ❌ 直接调用docker命令，用户未安装时报错不友好 | — |
| 5 | ✅ **验证Docker服务运行状态**：`docker info` 或 `docker ps` 确认daemon可连接 | ❌ 不检查Docker服务状态，socket未挂载/服务未启动时直接失败 | — |
| 6 | ✅ **验证目标镜像存在**：`docker image inspect <image>` 检查镜像是否已构建 | ❌ 镜像不存在时直接docker run失败，无明确提示用户先构建 | — |

### 1.2 环境探测三步法（标准流程）

| 步骤 | 操作 | 命令示例 |
|------|------|---------|
| 探测 | 获取所有可用资源列表 | `wsl --list --all`、`docker images`、`docker ps -a` |
| 选择 | 优先使用默认值，或按优先级选第一个可用 | 默认WSL发行版、已存在容器优先检查 |
| 验证 | 简单命令验证资源可用 | `wsl echo ok`、`docker run --rm <image> echo ok` |

---

## 阶段2：脚本结构与健壮性

### 2.1 脚本基础结构

| # | 检查项 | 反模式 | 对应模式 |
|---|--------|--------|---------|
| 7 | ✅ **脚本开头使用 `set -euo pipefail`**，错误立即退出，未定义变量报错，管道错误传播 | ❌ 不设置errexit，错误被静默忽略，后续命令在错误状态下继续执行 | 模式1：一键管理脚本模板 |
| 8 | ✅ **配置变量集中定义在脚本头部**：镜像名、容器名、端口映射、环境变量、密码、挂载路径等 | ❌ 配置散落在脚本各处，修改时容易遗漏 | 模式1：一键管理脚本模板 |
| 9 | ✅ **敏感信息通过环境变量覆盖**，提供合理默认值但允许用户通过环境变量修改（密码、Token等） | ❌ 硬编码密码/密钥在脚本中，存在安全风险且不易修改 | 模式1：一键管理脚本模板 |
| 10 | ✅ **统一日志函数**：`log_info`/`log_success`/`log_warn`/`log_error` 带颜色输出 | ❌ 直接echo，成功/失败/警告信息无视觉区分 | 模式1：一键管理脚本模板 |
| 11 | ✅ **工具函数封装**：`check_environment()`、`is_container_running()`、`is_container_exists()`、`print_access_info()` | ❌ 逻辑重复散落在各个命令函数中，难以维护 | 模式1：一键管理脚本模板 |

### 2.2 命令与入口

| # | 检查项 | 反模式 | 对应模式 |
|---|--------|--------|---------|
| 12 | ✅ **提供5个标准命令**：`start`/`stop`/`restart`/`status`/`logs` | ❌ 只提供start不提供stop/status，生命周期管理不完整 | 模式1：一键管理脚本模板 |
| 13 | ✅ **提供 `help` 命令或 `-h/--help` 选项**，清晰说明用法、参数、默认配置 | ❌ 无帮助信息，用户需要读源码才能知道怎么用 | — |
| 14 | ✅ **`main()` 函数作为入口**，参数解析清晰，无效命令给出提示 | ❌ 顶层直接写逻辑，参数解析混乱 | — |
| 15 | ✅ **启动成功后打印完整访问信息**：URL、端口、账号、密码、SSH命令等 | ❌ 启动成功无输出，用户不知道如何访问容器 | 模式1：一键管理脚本模板 |

---

## 阶段3：容器生命周期管理

### 3.1 容器创建与启动

| # | 检查项 | 反模式 | 对应问题/模式 |
|---|--------|--------|--------------|
| 16 | ✅ **提供 `--force-recreate` 选项**，允许自动删除旧容器并重建（解决旧配置不兼容问题） | ❌ 检测到同名容器存在直接 `docker start`，旧容器挂载/端口/环境变量配置与当前脚本不兼容导致启动失败 | 问题2：旧容器残留配置 |
| 17 | ✅ **容器启动策略设置 `--restart unless-stopped`**，容器意外退出后自动重启 | ❌ 不设置restart策略，机器重启或Docker重启后容器需要手动启动 | 模式1：一键管理脚本模板 |
| 18 | ✅ **端口映射冲突检测**：启动前检查宿主机端口是否被占用（`netstat -tlnp` 或 `ss -tlnp`） | ❌ 端口被占用时docker run直接失败，错误信息不直观 | — |
| 19 | ✅ **挂载目录自动创建**：`mkdir -p` 确保宿主机挂载路径存在 | ❌ 挂载路径不存在时docker自动创建为目录（预期是文件挂载时出问题） | — |
| 20 | ✅ **后台运行模式 `-d`**，启动后返回容器ID | ❌ 前台运行阻塞终端，用户无法继续操作 | — |

### 3.2 容器停止与清理

| # | 检查项 | 反模式 | 对应问题/模式 |
|---|--------|--------|--------------|
| 21 | ✅ **stop命令优雅停止容器**：先 `docker stop`（发送SIGTERM，等待超时），失败再 `docker kill` | ❌ 直接 `docker kill` 强制终止，应用来不及清理状态 | — |
| 22 | ✅ **可选提供 `rm`/`clean` 命令**，停止后删除容器（保留数据卷） | ❌ 没有清理命令，旧容器残留占用磁盘空间 | — |

---

## 阶段4：WSL兼容性与验证

### 4.1 WSL路径与跨平台兼容

| # | 检查项 | 反模式 | 对应模式 |
|---|--------|--------|---------|
| 23 | ✅ **工作目录挂载使用绝对路径**，WSL下自动转换Windows路径（`wsl path "C:\path"` 或使用 `/mnt/c/`） | ❌ 使用相对路径挂载，WSL与Windows路径格式不一致导致挂载失败 | 模式2：WSL环境探测先行 |
| 24 | ✅ **脚本测试覆盖WSL环境**：实际在WSL中执行start/stop/restart/status全流程验证 | ❌ 只在原生Linux测试，WSL下路径转换、权限等问题未暴露 | 问题1+2验证 |

---

## 快速验证命令（复制即用）

### 脚本功能验证矩阵

```bash
# 1. 帮助信息
./run-xxx.sh help

# 2. 环境检查（start前自动执行）
./run-xxx.sh start 2>&1 | head -20

# 3. 强制重建容器（关键场景）
./run-xxx.sh start --force-recreate

# 4. 状态查看（验证访问信息完整）
./run-xxx.sh status

# 5. 日志查看（后台运行无报错）
./run-xxx.sh logs &
sleep 3
kill %1

# 6. 重启流程（stop→start完整链路）
./run-xxx.sh restart

# 7. 停止容器
./run-xxx.sh stop

# 8. 验证容器已停止
docker ps | grep <container-name>  # 应该无输出
```

### WSL环境下验证

```powershell
# Windows PowerShell中测试WSL探测
wsl --list --all
wsl bash -c "cd /path/to/script && ./run-xxx.sh start"
```

---

## 质量门总结

开发Docker管理脚本必须通过的**五个零容忍红线**：

| 红线 | 验证方式 | 失败后果 |
|------|---------|---------|
| 🔴 不硬编码WSL发行版名称 | 脚本中无 `wsl -d Ubuntu-XX.XX` 硬编码 | 换个环境直接报错找不到发行版 |
| 🔴 支持--force-recreate选项 | 存在该参数且能正常删除旧容器重建 | 旧容器配置变更后用户无法启动，需手动docker rm |
| 🔴 set -euo pipefail | 脚本开头包含该设置 | 静默失败导致问题难以排查 |
| 🔴 启动后打印完整访问信息 | status命令输出URL/端口/账号/密码 | 用户启动后不知道怎么访问 |
| 🔴 敏感信息支持环境变量覆盖 | 密码/Token变量有默认值但可通过环境变量覆盖 | 安全风险，且不易部署到不同环境 |

---

## 脚本模板骨架（参考）

```bash
#!/bin/bash
set -euo pipefail

# ========== 配置变量区 ==========
IMAGE_NAME="your-image:tag"
CONTAINER_NAME="your-container"
HOST_PORT=8888
CONTAINER_PORT=8888
# 敏感信息允许环境变量覆盖
PASSWORD="${PASSWORD:-default-password}"
WORKSPACE_MOUNT="${WORKSPACE_MOUNT:-$PWD/workspace}"

# ========== 日志函数 ==========
log_info()    { echo -e "\033[32m[INFO]\033[0m $*"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $*"; }
log_warn()    { echo -e "\033[33m[WARN]\033[0m $*"; }
log_error()   { echo -e "\033[31m[ERROR]\033[0m $*"; }

# ========== 工具函数 ==========
check_environment() { ... }
is_container_running() { ... }
is_container_exists() { ... }
print_access_info() { ... }

# ========== 核心命令 ==========
cmd_start() { ... }
cmd_stop() { ... }
cmd_restart() { ... }
cmd_status() { ... }
cmd_logs() { ... }
cmd_help() { ... }

# ========== 主入口 ==========
main() {
    case "${1:-help}" in
        start)    cmd_start "${@:2}" ;;
        stop)     cmd_stop ;;
        restart)  cmd_restart "${@:2}" ;;
        status)   cmd_status ;;
        logs)     cmd_logs ;;
        help|-h|--help) cmd_help ;;
        *)        log_error "未知命令: $1"; cmd_help; exit 1 ;;
    esac
}

main "$@"
```

---

## 关联资源索引

| 资源 | 位置 |
|------|------|
| 复盘原始报告 | [retrospective-caffe-jupyter-docker-build-20260726](../docs/retrospective/reports/task-reports/retrospective-caffe-jupyter-docker-build-20260726/README.md) |
| Docker构建优化清单 | [docker-build-optimization-checklist.md](docker-build-optimization-checklist.md) |
| Docker老旧项目风险预警 | [docker-legacy-project-risk-warning-checklist.md](docker-legacy-project-risk-warning-checklist.md) |
