---
id: "ide-jupyter-bridge-config-archive"
title: "IDE Jupyter 桥接模式 — 配置归档"
type: "config-archive"
date: "2026-08-14"
version: "1.0.0"
status: "validated"
maturity: "L2-validated"
app: "devcontainer-base"
app_version: "v2.2.1-opt"
pattern_id: "container-service-host-ide-bridge"
source:
  - "session sc-20260814-jupyter-kernel-expose（七概念 F→V→I 链路）"
  - "insight-jupyter-kernel-expose-host-ide-20260814 可行性分析报告"
  - "container-service-host-ide-bridge 架构模式萃取"
test_environment:
  os: "WSL2 Ubuntu"
  docker: "29.1.3"
  compose: "Docker Compose v2"
  python: "3.14.6 (cpython-314)"
  jupyter: "2.20.0"
tags: [docker, compose, jupyter, ide, vscode, trae, devcontainer, cors, port-mapping, volume-mount, config-archive]
file_count: 3
validation_count: 10
last_verified: "2026-08-14"
---

# IDE Jupyter 桥接模式 — 配置归档

## 归档元信息

| 属性 | 值 |
|------|---|
| **归档版本** | 1.0.0 |
| **归档日期** | 2026-08-14 |
| **最后验证** | 2026-08-14 |
| **适用镜像** | `devcontainer-base:v2.2.1-opt` 及以上 |
| **验证状态** | ✅ 已验证通过（10/10 验证项） |
| **验证环境** | WSL2 Ubuntu + Docker 29.1.3 + Jupyter 2.20.0 |
| **架构模式** | [容器开发服务宿主桥接模式](../../../../../../.agents/docs/retrospective/patterns/architecture-patterns/container-service-host-ide-bridge.md) |
| **关联报告** | [可行性分析报告](../../../../../../.agents/docs/retrospective/reports/build-engineering/insight-jupyter-kernel-expose-host-ide-20260814.md) |

## 归档内容

本目录包含 IDE Jupyter 桥接模式的全部配置文件和脚本，作为经过验证的参考版本归档。

```
docs/examples/ide-bridge/
├── INDEX.md                # 本文件（归档索引与使用说明）
├── docker-compose.ide.yml  # IDE桥接模式专用Compose配置（含DinD+DooD双profile）
├── .env.ide.example        # 环境变量模板（五要素完整配置）
└── run-jupyter-ide.sh      # 一键启动脚本（健康检查+连接引导）
```

## 文件位置说明

| 文件 | 可执行位置（项目内） | 归档位置（docs参考） |
|------|-------------------|-------------------|
| `docker-compose.ide.yml` | [项目根目录](../../../docker-compose.ide.yml) | [本目录](./docker-compose.ide.yml) |
| `.env.ide.example` | [项目根目录](../../../.env.ide.example) | [本目录](./.env.ide.example) |
| `run-jupyter-ide.sh` | [scripts/](../../../scripts/run-jupyter-ide.sh) | [本目录](./run-jupyter-ide.sh) |

> **说明**：项目根目录和 `scripts/` 下的文件为可执行版本；本目录下为归档参考副本，内容通过 MD5 校验一致。修改时请以项目根目录版本为准，归档副本仅作查阅与独立复用参考。若修改了可执行版本，请同步更新归档副本并更新 `last_verified` 日期。

## 快速使用（独立复用）

如需在其他项目中复用此配置，可直接复制本目录文件：

```bash
# 1. 复制归档文件到目标项目
cp -r docs/examples/ide-bridge/* /your/project/

# 2. 重命名环境变量模板
cp .env.ide.example .env
# 编辑 .env 修改 JUPYTER_TOKEN、USER_PASSWORD、端口等

# 3. 确保项目根目录有 Dockerfile 或修改 compose 中的 image 字段
#    docker-compose.ide.yml 默认使用 build: {context: ., dockerfile: Dockerfile}
#    如需使用预构建镜像，将 build 段替换为 image: your-image:tag

# 4. 创建工作目录
mkdir -p workspace

# 5. 启动
docker compose -f docker-compose.ide.yml up -d

# 或使用脚本
bash run-jupyter-ide.sh
```

## 五要素配置对照

本归档配置严格遵循「容器开发服务宿主桥接模式」五要素：

| # | 要素 | 配置位置 | 默认配置值 |
|---|------|---------|-----------|
| ① | 服务绑定 0.0.0.0 | 镜像内 `jupyter_notebook_config.py`（entrypoint动态写入） | `c.ServerApp.ip = '0.0.0.0'` |
| ② | 端口映射 | `docker-compose.ide.yml` → `ports` | `2222→22`（SSH）, `8888→8888`（Jupyter）|
| ③ | 认证 | 环境变量 | `JUPYTER_TOKEN`（自动生成随机值或手动指定）, `USER_PASSWORD` |
| ④ | CORS 跨域 | 环境变量 | `JUPYTER_ALLOW_ORIGIN=*`（IDE WebView 必需，缺失则静默失败）|
| ⑤ | 文件卷挂载 | `docker-compose.ide.yml` → `volumes` | `./workspace:/workspace`（双向实时同步）|

> **注意**：验证时使用了 `JUPYTER_PORT=18888 SSH_PORT=12222` 规避端口冲突，默认端口为 8888/2222。

## 验证记录

| # | 验证项 | 结果 | 备注 |
|---|--------|------|------|
| 1 | 容器启动 | ✅ 通过 | 启动时间 ~9秒（含健康检查等待） |
| 2 | 健康检查 | ✅ healthy | `healthcheck.sh` 6秒内通过 |
| 3 | Jupyter API | ✅ Jupyter 2.20.0 | `curl http://localhost:PORT/api` 正常返回版本信息 |
| 4 | CORS 预检 | ✅ 通过 | OPTIONS 返回 `Access-Control-Allow-Origin: vscode-webview://*` |
| 5 | Token 认证 | ✅ 通过 | 无 token 返回 403，正确 token 正常访问 |
| 6 | 文件挂载 | ✅ 双向同步 | 宿主机写入→容器内立即可读，反之亦然 |
| 7 | SSH 访问 | ✅ 通过 | `ssh -p PORT devuser@localhost` 可登录 |
| 8 | Python 版本 | ✅ Python 3.14.6 | 容器内 `python3 --version` 正确 |
| 9 | `status` 命令 | ✅ 通过 | 正确显示容器状态、健康状态、连接URL |
| 10 | `stop` 命令 | ✅ 通过 | 容器停止并删除，清理干净 |
| 11 | YAML 语法 | ✅ 合法 | `docker-compose.ide.yml` 通过 PyYAML 校验 |
| 12 | Bash 语法 | ✅ 合法 | `run-jupyter-ide.sh` 通过 `bash -n` 校验 |
| 13 | 文件一致性 | ✅ MD5匹配 | 归档副本与可执行版本 MD5 完全一致 |

## 已知限制

1. **Windows 原生 Docker Desktop**：脚本在 WSL2 环境下验证通过；Windows 原生 PowerShell 需自行调整路径语法
2. **端口冲突**：若宿主机 8888/2222 端口被占用，需通过环境变量 `JUPYTER_PORT`/`SSH_PORT` 指定备用端口
3. **free-threading 版本**：当前验证使用 `conda-libmamba-v2` 镜像（标准 CPython 3.14），free-threading 版本（cp314t）需使用 `conda-libmamba-ft` 标签
4. **DooD profile**：DooD profile（`--profile dood`）需宿主机 Docker Socket 可用，WSL2 中需确保 Docker Desktop WSL 集成已启用

## 关联文档

- [使用指南](../../IDE-JUPYTER-BRIDGE.md) — 完整使用说明、架构图、常见问题排查
- [最佳实践](../../best-practices.md) — Docker DinD/Compose/镜像源最佳实践
- [项目README](../../../README.md) — 项目总览和快速开始
- [v2.2.1 更新日志](../../../CHANGELOG.md) — 镜像版本变更记录
- [架构模式文档](../../../../../../.agents/docs/retrospective/patterns/architecture-patterns/container-service-host-ide-bridge.md) — 模式定义、公理、反模式
- [可行性分析报告](../../../../../../.agents/docs/retrospective/reports/build-engineering/insight-jupyter-kernel-expose-host-ide-20260814.md) — F→V→I 完整分析链路

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-08-14 | 1.0.0 | 初始归档：Compose配置、环境变量模板、启动脚本，13项验证通过 |
