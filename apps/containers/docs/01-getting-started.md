---
id: "containers-group-getting-started"
title: "跨成员端到端快速开始"
source: "client/README.md + jupyter-podman-rootless/AGENTS.md 快速开始 + 三成员 pyproject.toml"
---
# 01 · 跨成员端到端快速开始

本文覆盖单成员文档无法承载的**跨成员顺序**：shared → 构建端 → 缓存交接 → 消费端 → 可选工作负载栈。

## 0. 前置

- Python ≥ 3.14（推荐 conda 环境 py314；镜像内运行时为 Python 3.14t free-threading）
- Podman rootless：
  - **WSL2/Linux/macOS**：rootless Podman 4/5（WSL2 需一次性 `systemctl --user enable --now podman.socket`）
  - **Windows 11 原生 CPython**：安装 Podman Machine（消费端自动探测 WSL9P / Machine / tcp，详见 [client/docs/03](../client/docs/03-windows-wsl.md)）
- invoke 随 editable 安装自动获得

## 1. 安装共享包（G2：必须最先）

```bash
cd apps/containers
pip install -e shared
```

`jpman-common` 未发布到索引，由本地 editable 提供；跳过本步直接装两端会因找不到
`jpman-common` 而失败。

## 2. 安装成员包（按需）

```bash
# 消费端（含三栈编排器）
pip install -e client                     # 仅 load/run：SDK→CLI
pip install -e "client[compose]"          # 需要 quant/xmnn/monetize 工作负载栈时

# 构建端（要在宿主侧构建镜像时）
pip install -e "jupyter-podman-rootless[compose]"
# 可选 extras：[sdk] podman-py / [model] omlmd+olot / [full] 全装
```

> 不想装 Python 依赖、只做日常驾驶：直接用构建端零依赖 CLI
> `bash jupyter-podman-rootless/bin/jpman`（Windows 有 `jpman.cmd` / `jpman.ps1`）。

## 3. 路径 A：构建端 → 缓存 → 消费端（完整链路）

```bash
# 3.1 构建镜像（清华源加速；约数 GB，WSL 原生文件系统构建远快于 /mnt/d）
cd jupyter-podman-rootless
invoke build --apt-mirror tuna --conda-mirror tuna --pip-mirror tuna

# 3.2 导出 tar 到 .image-cache/（供消费端 load；具体命令见）
#      jupyter-podman-rootless/docs/16-image-cache.md

# 3.3 消费端加载并启动
cd ../client
invoke --list                                    # 核对命名空间：load/run/stop/status/clean + container.* + env.* + 三栈
invoke load                                      # 自动取 ../jupyter-podman-rootless/.image-cache/ 最新 tar
invoke run --workspace D:/spaces/SpecWeave       # 打印 SSH 与 Jupyter URL（Windows 路径自动转 /mnt/d）
invoke status
invoke stop                                      # 停止并删除容器
```

## 4. 路径 B：只日常驾驶构建端容器

```bash
cd jupyter-podman-rootless
bash bin/jpman rebuild-all   # 或 invoke build
bash bin/jpman start
bash bin/jpman info
```

## 5. 可选：工作负载栈（WSL2/Linux 内）

三栈为 podman-compose 子进程层，Windows 原生宿主门禁退出（C11-C13）；
在 WSL2 发行版内、已装 `client[compose]` 后：

```bash
cd client
invoke quant.build && invoke quant.up      # ONNX 量化栈（2222/8888）
invoke quant.ps && invoke quant.logs
invoke quant.smoke                         # 三项冒烟（int8/fp16/QDQ）
invoke quant.down
```

xmnn（`xmnn.*`，含 `build-tvm`/`wheel`）与 monetize（`monetize.*`，含 `build-native`/`wheel`）
同构，详见 [client/docs/10-12](../client/docs/README.md) 与各叠加层 README。

## 6. 验证清单

| 检查 | 期望 |
|------|------|
| `python -c "import jpman_common; print(jpman_common.__version__)"` | `0.1.0` |
| client 目录 `invoke --list` | 根任务 + container.* + env.* + quant/xmnn/monetize 命名空间齐全 |
| `invoke load` | 从 `.image-cache/` 取 tar 并完成完整性校验 |
| `invoke run` 后 `invoke status` | 容器 running，打印 SSH/Jupyter 入口 |
| WSL2 内 `invoke quant.smoke` | 三冒烟 PASS（仅安装 [compose] 后） |

## 7. 排障入口

- Windows 原生坑 W-I1~W-I4 / 容器内坑 C-I1~C-I5：[client/docs/04](../client/docs/04-troubleshooting-guide.md)
- 构建端 FAQ、健康检查：[jupyter docs/13](../jupyter-podman-rootless/docs/13-faq.md)、[12-healthcheck](../jupyter-podman-rootless/docs/12-healthcheck.md)
- rootless 三必需与连接层纪律（G1-G4）：[../AGENTS.md](../AGENTS.md)
