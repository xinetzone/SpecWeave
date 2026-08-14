# IDE Jupyter 桥接模式使用指南

> 基于「容器开发服务宿主桥接模式」五要素，将容器内 Jupyter Kernel 暴露给宿主机 VSCode/Trae IDE 使用。

## 概述

本模式让你在宿主机使用 VSCode/Trae 等 IDE 的 Jupyter 插件，而代码实际执行在容器内的 Python 3.14 free-threading 环境中。相比 VSCode Dev Containers 扩展，本方案更轻量——仅连接 Jupyter 服务，IDE UI 完全运行在宿主机。

### 架构

```
┌─────────────────────────────────────────────────┐
│  宿主机 (Windows/macOS/Linux)                    │
│                                                  │
│  ┌──────────────┐    HTTP/WebSocket    ┌───────┐│
│  │ VSCode/Trae  │◄────────────────────►│ :8888 ││
│  │ Jupyter插件  │    localhost:8888    │ 端口  ││
│  └──────────────┘                      └───┬───┘│
│       │                                     │    │
│       │ 编辑 .ipynb                         │端口│
│       ▼                                     │映射│
│  ┌──────────────┐     volume 挂载     ┌───┴───┐│
│  │  ./workspace │◄──────────────────►│/worksp││
│  │  (宿主机目录)│    文件双向同步     │(容器内)││
│  └──────────────┘                     └───┬───┘│
└────────────────────────────────────────────┼────┘
                                             │
                                    ┌────────▼────────┐
                                    │  容器内          │
                                    │  Jupyter Server  │
                                    │     ↕ ZeroMQ     │
                                    │  Python 3.14t    │
                                    │  (cp314t Kernel) │
                                    └─────────────────┘
```

## 快速开始（3步）

### 步骤1：启动容器

提供3种启动方式，任选其一：

**方式A：专用 Compose 文件（推荐，开箱即用）**
```bash
cd apps/docker-images/devcontainer-base
cp .env.ide.example .env       # 复制环境变量模板（可按需修改）
docker compose -f docker-compose.ide.yml up -d
```

**方式B：专用启动脚本（含健康检查+引导信息）**
```bash
cd apps/docker-images/devcontainer-base
bash scripts/run-jupyter-ide.sh
```

**方式C：在现有 compose 配置基础上叠加**
```bash
cd apps/docker-images/devcontainer-base
# 确保 .env 中 JUPYTER_ALLOW_ORIGIN=*
docker compose --profile dind up -d
```

> ⚠️ **重要**：三种方式都必须确保 `JUPYTER_ALLOW_ORIGIN=*`，否则 IDE WebView 会被 CORS 跨域策略阻止。

### 步骤2：配置 IDE 连接

**VSCode / Trae 操作步骤：**

1. 确保已安装 Jupyter 扩展（VSCode 已内置，Trae 需手动安装）
2. 按 `Ctrl+Shift+P`（Mac: `Cmd+Shift+P`）打开命令面板
3. 输入并选择 **"Jupyter: Specify Jupyter Server for Connections"**
4. 选择 **"Existing"**（现有服务器）
5. 输入连接 URL：
   ```
   http://localhost:8888/?token=devtoken123
   ```
   > token 值请查看 `.env` 文件中的 `JUPYTER_TOKEN`，或查看容器启动日志
6. 按 Enter 确认

### 步骤3：开始使用

1. 在宿主机 `./workspace` 目录下创建或打开 `.ipynb` 文件
2. 右上角 Kernel 选择器 → 选择 **"Python 3"**（容器内注册的 kernel）
3. 运行代码单元格——执行在容器内 Python 3.14 cp314t 环境中

## 五要素配置检查清单

根据「容器开发服务宿主桥接模式」，确保以下5个要素全部满足：

| # | 要素 | 配置位置 | 当前状态 |
|---|------|---------|---------|
| ① | 服务绑定 `0.0.0.0` | 镜像内 `jupyter_notebook_config.py` | ✅ 已配置 |
| ② | 端口映射 `-p 8888:8888` | `docker-compose*.yml` / `docker run -p` | ✅ ide.yml 已配置 |
| ③ | 认证（JUPYTER_TOKEN） | 环境变量 | ✅ 已配置 |
| ④ | CORS（`JUPYTER_ALLOW_ORIGIN=*`）| 环境变量 | ✅ ide.yml 已配置 |
| ⑤ | 文件卷挂载 `./workspace:/workspace` | volumes | ✅ ide.yml 已配置 |

### 常见配置问题

#### ❌ IDE 连接无响应（无明确报错）

**症状**：浏览器能正常访问 `http://localhost:8888`，但 IDE 连接后单元格一直显示 `[*]` 无输出。

**原因**：缺少 `JUPYTER_ALLOW_ORIGIN=*` 配置。IDE 的 WebView 使用 `vscode-webview://` 协议作为 Origin 发起请求，被 Jupyter 的 CORS 策略阻止。

**解决**：确保启动时传入 `-e JUPYTER_ALLOW_ORIGIN="*"`，或在 `.env` 中设置：
```bash
JUPYTER_ALLOW_ORIGIN=*
```

#### ❌ 文件保存后容器内看不到

**症状**：IDE 中创建的 notebook 在容器内 `ls /workspace` 看不到，或容器内创建的文件宿主机看不到。

**原因**：缺少 volume 挂载，或挂载路径不一致。

**解决**：确保有 `-v $(pwd)/workspace:/workspace`（docker run）或对应的 volumes 配置（compose），且容器内 `WORKDIR` 为 `/workspace`。

#### ❌ 端口映射成功但连接被拒绝

**症状**：`curl http://localhost:8888` 返回 `Connection reset` 或 `Connection refused`。

**原因**：Jupyter 绑定了 `127.0.0.1` 而非 `0.0.0.0`。

**解决**：确认镜像配置中 `c.ServerApp.ip = '0.0.0.0'`（devcontainer-base 已默认配置）。

#### ❌ Notebook 保存后重启容器丢失

**原因**：notebook 保存在容器内非挂载目录（如 `/home/devuser/`），容器删除后文件丢失。

**解决**：始终在 `/workspace` 目录下创建和编辑 notebook，该目录通过 volume 挂载到宿主机。

## 环境变量参考

| 变量 | 默认值 | 说明 |
|------|-------|------|
| `JUPYTER_TOKEN` | `devtoken123`（ide.yml）| Jupyter 认证 token，IDE 连接 URL 中使用 |
| `JUPYTER_ALLOW_ORIGIN` | `*` | **IDE 连接必需**，允许跨域请求来源 |
| `JUPYTER_PORT` | `8888`（DinD）/ `8889`（DooD）| 宿主机 Jupyter 端口 |
| `USER_PASSWORD` | `devpass`（ide.yml）| SSH 登录密码 |
| `SSH_PORT` | `2222`（DinD）/ `2223`（DooD）| 宿主机 SSH 端口 |
| `GRANT_SUDO` | `yes` | 是否授予 devuser 免密 sudo |

## 多服务并行暴露

需要同时暴露其他开发服务时，在 compose 文件中添加端口和环境变量：

```yaml
services:
  dev-ide:
    # ... 现有配置 ...
    ports:
      - "2222:22"      # SSH
      - "8888:8888"    # Jupyter
      - "6006:6006"    # TensorBoard（新增）
    environment:
      # ... 现有变量 ...
      - TENSORBOARD_HOST=0.0.0.0  # 确保绑定0.0.0.0
```

> 注意：非 Web 服务（如 SSH、debugpy 原生TCP）不需要 CORS 配置。

## SSH 隧道模式（远程服务器）

当容器运行在远程服务器而非本机 Docker 时，使用 SSH 隧道：

```bash
# 1. 在远程服务器上启动容器（不映射8888到公网，仅映射SSH）
ssh user@remote-server
cd devcontainer-base
docker run -d --privileged -p 2222:22 \
  -e USER_PASSWORD=pass -e JUPYTER_TOKEN=secret \
  -e JUPYTER_ALLOW_ORIGIN="*" \
  -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
  devcontainer-base:1.0

# 2. 在宿主机建立SSH隧道（本地8888 → 远程容器内localhost:8888）
ssh -p 2222 -N -L 8888:localhost:8888 devuser@remote-server

# 3. IDE连接地址不变：http://localhost:8888/?token=secret
```

## 验证方法

启动后可通过以下命令验证 Jupyter 正常工作：

```bash
# 检查容器健康状态
docker compose -f docker-compose.ide.yml ps

# 从宿主机验证Jupyter API可达
curl -s http://localhost:8888/api?token=devtoken123 | python -m json.tool

# 查看容器日志确认服务启动
docker compose -f docker-compose.ide.yml logs -f

# 查看连接信息（脚本方式）
bash scripts/run-jupyter-ide.sh status
```

## 容器管理命令

```bash
# 查看状态
docker compose -f docker-compose.ide.yml ps

# 查看日志
docker compose -f docker-compose.ide.yml logs -f

# 停止
docker compose -f docker-compose.ide.yml down

# 停止并删除数据卷（会丢失Docker镜像缓存）
docker compose -f docker-compose.ide.yml down -v

# 重启
docker compose -f docker-compose.ide.yml restart
```

## 与其他模式的对比

| 特性 | IDE 桥接模式 | Dev Containers 扩展 | 纯浏览器 JupyterLab |
|------|-------------|-------------------|-------------------|
| IDE UI 位置 | 宿主机 | 容器内（VSCode Server）| 浏览器 |
| 资源占用 | 低 | 高（完整VSCode Server）| 最低 |
| 配置复杂度 | 低（端口映射即可）| 中（需要 .devcontainer.json）| 最低 |
| LSP/补全/调试 | 宿主机插件负责 | 容器内插件负责 | 无 |
| 文件同步 | volume 挂载 | 自动绑定挂载 | volume 挂载 |
| Python 环境 | 容器内 cp314t | 容器内 | 容器内 |
| 适合场景 | 快速连接 Jupyter | 全功能容器内开发 | 快速数据探索 |

## 配置文件归档

经过实际验证的完整配置文件归档于 [examples/ide-bridge/](examples/ide-bridge/INDEX.md)，包含：

| 文件 | 说明 | 项目内位置 | 归档位置 |
|------|------|-----------|---------|
| `docker-compose.ide.yml` | IDE桥接Compose配置（DinD+DooD）| [项目根目录](../docker-compose.ide.yml) | [examples/ide-bridge/](examples/ide-bridge/docker-compose.ide.yml) |
| `.env.ide.example` | 环境变量模板 | [项目根目录](../.env.ide.example) | [examples/ide-bridge/](examples/ide-bridge/.env.ide.example) |
| `run-jupyter-ide.sh` | 一键启动脚本 | [scripts/](../scripts/run-jupyter-ide.sh) | [examples/ide-bridge/](examples/ide-bridge/run-jupyter-ide.sh) |

归档目录包含独立复用说明和完整验证记录，可直接复制到其他项目使用。详见 [examples/ide-bridge/INDEX.md](examples/ide-bridge/INDEX.md)。

## 架构模式参考

本配置基于 SpecWeave 架构模式库中的「容器开发服务宿主桥接模式」：
- 模式文档：[.agents/docs/retrospective/patterns/architecture-patterns/container-service-host-ide-bridge.md](../../../../.agents/docs/retrospective/patterns/architecture-patterns/container-service-host-ide-bridge.md)
- 可行性分析报告：[.agents/docs/retrospective/reports/build-engineering/insight-jupyter-kernel-expose-host-ide-20260814.md](../../../../.agents/docs/retrospective/reports/build-engineering/insight-jupyter-kernel-expose-host-ide-20260814.md)
- 配置归档：[examples/ide-bridge/INDEX.md](examples/ide-bridge/INDEX.md)
- 五要素：服务绑定0.0.0.0 → 端口映射 → 认证 → CORS → 文件卷挂载
- 反模式：遗漏CORS、遗漏volume、绑定127.0.0.1、直接暴露Kernel、无认证暴露端口
