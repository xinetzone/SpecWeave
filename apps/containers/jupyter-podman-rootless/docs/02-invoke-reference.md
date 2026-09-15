---
id: "jupyter-invoke-reference"
title: "Invoke 任务参考"
source: "README.md#invoke-任务参考"
---
# Invoke 任务参考

所有任务通过 `invoke <命令>` 执行，支持 `--help` 查看参数详情。

## 核心命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `invoke build` | 构建镜像 | `invoke build --apt-mirror aliyun --no-cache` |
| `invoke save` | 保存镜像到 `.image-cache/`（podman save 归档，**Windows 原生可用**） | `invoke save` / `invoke save --no-compress -o D:\backup\img.tar` |
| `invoke run` | 启动容器（幂等：运行中 no-op 并回显现存凭证，停止态自动重建；`--force` 强制重建） | `invoke run --grant-sudo --ssh-port 2222` |
| `invoke stop` | 停止并删除容器 | `invoke stop` |
| `invoke status` | 查看容器状态 | `invoke status` |
| `invoke shell` | 进入容器Shell | `invoke shell --user root` |
| `invoke logs` | 查看容器日志 | `invoke logs --follow --tail 50` |
| `invoke exec` | 在容器中执行命令 | `invoke exec --command "pip list"` |
| `invoke clean` | 清理资源 | `invoke clean --image` |

> **子命令集合**：所有核心命令也可通过 `invoke container.<命令>` 访问（如 `invoke container.build`、`invoke container.run`），用于命名空间隔离。

## ML 模型命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `invoke model.push` | 推送模型到 OCI registry（OMLMD） | `invoke model.push ./my-model --ref localhost:5000/models/llm:v1` |
| `invoke model.pull` | 从 OCI registry 拉取模型（OMLMD） | `invoke model.pull --ref localhost:5000/models/llm:v1 --output ./models` |
| `invoke model.config` | 查询 OCI 模型元数据配置 | `invoke model.config --ref localhost:5000/models/llm:v1` |
| `invoke model.pack` | 打包模型为 KServe ModelCar 镜像（OLOT） | `invoke model.pack ./my-model --base jupyter-podman-rootless:latest --ref localhost:5000/models/car:v1` |
| `invoke model.extract` | 从 ModelCar 镜像提取模型目录 | `invoke model.extract --ref localhost:5000/models/car:v1 --output ./models` |

> ML 模型命令需要容器内预装 omlmd/olot（默认已包含），或宿主机安装 `pip install omlmd 'olot[oras-py]'`。
> 使用本地模型仓库时先启动：`invoke registry.up`（推荐，跨平台）或 `podman-compose --profile registry up -d`（仅 WSL / podman machine 内可用）。

ML模型功能详情见 [06-ml-model-management.md](06-ml-model-management.md)。

## registry 命令（本地 OCI registry）

`model.*` 命令推送/拉取的默认目标 `localhost:5000` 由本组命令提供。它是 compose
`model-registry` 服务（`profile: registry`）的等价替代，**不依赖 podman-compose**，
故在 Windows 原生宿主上同样可用；容器名、数据卷名、端口、环境变量与 compose 服务对齐，
两种启动方式共享同一份数据卷。

| 命令 | 说明 | 示例 |
|------|------|------|
| `invoke registry.up` | 启动本地 OCI registry（`registry:2`） | `invoke registry.up --port 5001` |
| `invoke registry.down` | 停止并删除 registry 容器（保留数据卷） | `invoke registry.down --volumes` |

| registry.up 参数 | 默认值 | 说明 |
|------|--------|------|
| `--port` | `5000` | 宿主映射端口（优先级：参数 > `REGISTRY_PORT` 环境变量 > `.env` > 默认值） |

| registry.down 参数 | 默认值 | 说明 |
|------|--------|------|
| `--volumes` | `false` | 同时删除数据卷 `jupyter-podman-rootless_registry-data`（不可恢复） |

```bash
invoke registry.up
curl http://localhost:5000/v2/_catalog     # {"repositories":[]}
invoke model.push ./my-model --ref localhost:5000/models/llm:v1
invoke registry.down
```

> 容器内访问名 `http://model-registry:5000` 仅在 compose 项目网络
> （`jupyter-podman-rootless_default`）存在时可用——该网络由 compose 栈创建；
> 网络不存在时命令会打印提示并改用默认网络。

## build 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--tag` | `jupyter-podman-rootless:latest` | 镜像标签 |
| `--apt-mirror` | `official` | APT 镜像源：`official` / `tuna` / `aliyun` |
| `--conda-mirror` | `official` | Conda 镜像源：`official` / `tuna` / `aliyun` |
| `--pip-mirror` | `official` | PIP 镜像源：`official` / `tuna` / `aliyun` |
| `--no-cache` | `false` | 不使用构建缓存 |

## save 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-t` / `--tag` | `.env`/配置中的 `IMAGE_TAG` | 要保存的镜像标签 |
| `-o` / `--output` | `.image-cache/` 自动命名 | 输出文件（给目录则自动命名）；自定义路径不写 manifest/latest |
| `-n` / `--no-compress` | `false`（gzip） | 导出未压缩 tar（更快、约 3 倍体积） |
| `-f` / `--force` | `false` | 目标文件已存在时覆盖 |

默认归档 `jupyter-podman-rootless-<image-id12>-<YYYYMMDD-HHMMSS>.tar.gz`，并维护
`*-latest.tar.gz` 硬链接指针与 `manifest.txt`（与 `bash bin/jpman save` 产物同构）。
恢复：`podman load -i <归档>`（gzip 归档自动解包）。详见 [16-image-cache.md](16-image-cache.md)。

## run 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `jupyter-podman` | 容器名 |
| `--tag` | `jupyter-podman-rootless:latest` | 使用的镜像 |
| `--ssh-port` | `2222` | SSH 映射端口 |
| `--jupyter-port` | `8888` | Jupyter 映射端口 |
| `--workspace` | `./workspace` | 工作目录挂载路径 |
| `--user-password` | 自动生成16位 | devuser 密码 |
| `--jupyter-token` | 自动生成32位 | Jupyter 访问 token |
| `--ssh-public-key` | 无 | SSH 公钥内容（注入 authorized_keys） |
| `--grant-sudo` | `false` | 授予 devuser 无密码 sudo |
| `--detach/--no-detach` | `detach` | 后台/前台运行 |

## interact 参数

| 命令 | 参数 | 说明 |
|------|------|------|
| `invoke shell` | `--name`, `--user`（默认 devuser） | 进入交互式 Shell |
| `invoke logs` | `--name`, `--follow`, `--tail`（默认100） | 查看日志 |
| `invoke exec` | `--command`（必填）, `--name`, `--user` | 执行命令 |

## model 参数

| 命令 | 关键参数 | 说明 |
|------|---------|------|
| `model.push` | `--ref`（必填）, `--path`（模型目录）, `--name`, `--user` | 推送模型到 OCI registry |
| `model.pull` | `--ref`（必填）, `--output`（输出目录）, `--name`, `--user` | 从 OCI registry 拉取模型 |
| `model.config` | `--ref`（必填）, `--name`, `--user` | 查询模型元数据 |
| `model.pack` | `--ref`（必填）, `--path`（模型目录）, `--base`（基础镜像）, `--name`, `--user` | 打包为 ModelCar 镜像并推送 |
| `model.extract` | `--ref`（必填）, `--output`（输出目录）, `--name`, `--user` | 从 ModelCar 镜像提取模型 |

## clean 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `jupyter-podman` | 容器名 |
| `--tag` | `jupyter-podman-rootless:latest` | 镜像标签 |
| `--volume` | `false` | 清理未使用的卷 |
| `--image` | `false` | 删除镜像 |

## 三层后端透明性

所有invoke命令自动选择最优后端，对用户透明：
1. podman-compose后端（优先，当podman-compose可用时）
2. podman-py SDK后端（其次，当podman-py安装时）
3. CLI fallback（保底，零依赖）

详见 [09-three-tier-backend.md](09-three-tier-backend.md)。
