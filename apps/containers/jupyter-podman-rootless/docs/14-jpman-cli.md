---
id: "jupyter-jpman-cli"
title: "jpman 零依赖 CLI 参考"
source: "bin/jpman"
---
# jpman 零依赖 CLI 参考

`jpman` 是一个纯 bash 实现的零依赖命令行工具，无需安装 Python 或任何 Python 包即可管理 jupyter-podman-rootless 容器。提供容器生命周期管理、镜像缓存、WSL2 发行版导出、增量重建等功能。

## 跨平台支持

| 平台 | 脚本 |
|------|------|
| WSL/Linux/macOS | `bin/jpman` (bash) |
| Windows cmd | `bin\jpman.cmd` |
| Windows PowerShell | `bin\jpman.ps1` |

## 快速开始

```bash
# WSL/Linux/macOS：从项目根目录直接运行
bash bin/jpman rebuild-all   # 全量构建镜像（默认清华源）
bash bin/jpman start         # 启动容器
bash bin/jpman info          # 查看访问信息

# 安装为全局命令（可选）
bash bin/jpman install       # 创建 symlink 到 ~/.local/bin/jpman
jpman status                 # 之后可在任意目录使用
```

## 命令参考

### 容器生命周期

| 命令 | 说明 |
|------|------|
| `jpman start [-w PATH]` | 启动容器（幂等）：若已运行则直接显示信息；若存在但停止则删除重建；自动等待健康检查通过。`-w/--workspace` 指定宿主机工作目录（覆盖 .env WORKSPACE） |
| `jpman stop` | 停止并删除容器 |
| `jpman restart [-w PATH]` | 重启（先 stop 再 start），透传所有参数给 start（如 `-w`） |
| `jpman status` / `jpman ps` | 查看容器状态、健康状态、镜像信息 |
| `jpman info` | 显示详细访问信息（Jupyter URL、SSH、密码、挂载点等） |
| `jpman url` | 仅打印 Jupyter Lab URL（方便复制粘贴） |

### 交互命令

| 命令 | 说明 |
|------|------|
| `jpman shell` | 以 devuser 身份进入容器 shell |
| `jpman shell --root` | 以 root 身份进入容器 shell |
| `jpman logs` | 查看最近 100 行日志 |
| `jpman logs -f` / `--follow` | 实时跟踪日志 |
| `jpman exec CMD` | 以 devuser 身份在容器内执行命令 |
| `jpman root CMD` | 以 root 身份在容器内执行命令 |

### 构建与缓存

| 命令 | 说明 |
|------|------|
| `jpman rebuild` | 增量重建（基于主 Containerfile 层缓存，配置变更仅重建 Layer 4/5，<10秒，自动重启容器） |
| `jpman rebuild-all` | 全量重建（从 Containerfile 完整构建，需要网络） |
| `jpman save` | 保存镜像到 `.image-cache/`（使用 pigz 多线程压缩） |
| `jpman load` | 从 `.image-cache/` 加载镜像 |

### WSL2 集成

| 命令 | 说明 |
|------|------|
| `jpman wsl-export` | 一键导出当前镜像为 WSL2 发行版 |
| `jpman wsl-export --force` | 强制覆盖已存在的 WSL 发行版 |
| `jpman wsl-export --distro-name NAME` | 指定 WSL 发行版名称（默认 jupyter-podman-rootless） |
| `jpman wsl-export --install-dir DIR` | 指定安装目录（默认 .wsl-cache/） |
| `jpman wsl-verify` | 验证 WSL2 发行版环境（冒烟测试） |
| `jpman wsl-verify DISTRO` | 验证指定名称的 WSL 发行版 |
| `jpman keepalive` | 启动 WSL 保活进程（sleep infinity，防止容器自动退出） |

### 其他

| 命令 | 说明 |
|------|------|
| `jpman install [DIR]` | 安装 symlink 到指定目录（默认 ~/.local/bin） |
| `jpman help` / `-h` / `--help` | 显示帮助信息 |

## 配置

jpman 通过环境变量和 `.env` 文件进行配置，自动加载项目根目录和当前目录的 `.env`：

> **.env 加载机制**：jpman 使用安全逐行解析（非 `source`），自动剥离 CRLF 行结尾、支持引号值，Windows 反斜杠路径不会被 bash 转义破坏。短变量名（`CONTAINER_NAME`/`SSH_PORT` 等）与 `JUPYTER_*` 前缀变量均支持，自动 fallback。

| 环境变量 | 短名兼容 | 默认值 | 说明 |
|----------|----------|--------|------|
| `JUPYTER_CONTAINER_NAME` | `CONTAINER_NAME` | `jupyter-podman` | 容器名称 |
| `JUPYTER_IMAGE` | `IMAGE_TAG` | `localhost/jupyter-podman-rootless:latest` | 镜像标签 |
| `JUPYTER_SSH_PORT` | `SSH_PORT` | `2222` | SSH 端口映射 |
| `JUPYTER_PORT` | — | `8888` | Jupyter 端口映射 |
| `JUPYTER_PASSWORD` | `USER_PASSWORD` | `devpass123` | 用户密码（留空自动生成） |
| `JUPYTER_TOKEN` | — | `chaostest2026` | Jupyter token（留空自动生成） |
| `JUPYTER_WORKSPACE` / `WORKSPACE` | — | `$PROJECT_ROOT/workspace` | 工作区挂载路径（Windows 路径自动转换为 WSL `/mnt/` 路径） |
| `JUPYTER_WSL_TARGET_DISTRO` | — | `jupyter-podman-rootless` | WSL 发行版名称 |
| `JUPYTER_WSL_DEFAULT_USER` | — | `devuser` | WSL 默认用户 |

### WORKSPACE 优先级

`-w CLI 参数 > WORKSPACE 环境变量 > JUPYTER_WORKSPACE 环境变量（兼容） > .env 文件 WORKSPACE > $PROJECT_ROOT/workspace 默认值`

### Windows 路径自动转换

在 WSL 中运行时，Windows 盘符路径（如 `D:\spaces\SpecWeave`）会自动转换为 WSL 路径（`/mnt/d/spaces/SpecWeave`），无需手动转换。支持 `-w` 参数、`.env` 文件、环境变量三种入口。

> ⚠️ **注意**：默认密码和 token 仅用于开发测试，生产环境请务必修改。

## 镜像缓存

镜像保存在 `.image-cache/` 目录：
- 带时间戳的归档：`jupyter-podman-rootless-<image-id>-<timestamp>.tar.gz`
- 最新版本软链接：`jupyter-podman-rootless-latest.tar.gz`
- 清单文件：`manifest.txt`（包含镜像ID、大小、SHA256、保存时间）

使用 pigz 进行多线程压缩（如已安装），否则 fallback 到 gzip。

详见 [16-image-cache.md](16-image-cache.md)。

## WSL 保活

在 WSL2 中运行时，若没有前台进程，WSL 会自动退出导致容器停止。`jpman start` 会自动启动保活进程，也可手动运行：

```bash
bash bin/jpman keepalive
```

该命令启动 `setsid sleep infinity` 作为后台守护进程。

## 与 invoke 的对比

| 特性 | jpman | invoke |
|------|-------|--------|
| Python 依赖 | ❌ 无 | ✅ 需要 |
| 镜像缓存 | ✅ save/load | ❌ |
| WSL2 导出 | ✅ wsl-export | ❌ |
| 增量重建 | ✅ rebuild | ❌ |
| ML 模型管理 | ❌ | ✅ model.push/pack/pull |
| 三层后端 | ❌ 仅 CLI | ✅ compose→SDK→CLI |
| 路径自动转换 | ✅ Windows→WSL 自动 | ✅ |
| .env 安全加载 | ✅ 逐行解析（无 source） | ✅ |
| 自定义工作区挂载 | ✅ `-w` CLI 参数 | ✅ |
| 自动密码生成 | ❌ | ✅ |
| 跨平台脚本 | ✅ bash/cmd/ps1 | ✅ Python |

**推荐**：快速上手和日常使用 jpman；需要 ML 模型管理或完整功能时使用 invoke。
