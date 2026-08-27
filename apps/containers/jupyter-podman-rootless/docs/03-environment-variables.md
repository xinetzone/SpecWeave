---
id: "jupyter-environment-variables"
title: "环境变量参考"
source: "README.md#环境变量参考"
---
# 环境变量参考

## 运行时环境变量（`podman run -e` / `.env` 文件）

通过 `.env` 文件或 `-e` 参数传递给容器：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `USER_PASSWORD` | 随机生成16位 | devuser 用户密码 |
| `JUPYTER_TOKEN` | 随机生成32位 | Jupyter 访问 token |
| `JUPYTER_PASSWORD` | 无 | Jupyter 密码（与 token 二选一） |
| `SSH_PUBLIC_KEY` | 无 | SSH 公钥（追加到 authorized_keys） |
| `GRANT_SUDO` | `no` | 是否授予 devuser 无密码 sudo（`yes`/`no`） |
| `ALLOW_ROOT_SSH` | `no` | 是否允许 root SSH 登录（`yes`/`no`） |
| `ROOT_PASSWORD` | 随机生成 | root 密码（仅 ALLOW_ROOT_SSH=yes 时生效） |
| `APT_MIRROR` | `official` | 运行时 APT 源（容器内 apt 使用） |
| `DEBUG` | `0` | 设为 `1` 启用 entrypoint 调试输出（set -x） |
| `REGISTRY_URL` | `localhost:5000` | ML 模型 OCI registry 地址 |
| `REGISTRY_PORT` | `5000` | 本地 model-registry 服务端口 |
| `REGISTRY_PLAIN_HTTP` | `true` | 本地 registry 使用 HTTP（非 HTTPS） |

### 运行时变量使用示例

```bash
# 使用自定义密码和token
podman run -d \
  -e USER_PASSWORD=mypassword \
  -e JUPYTER_TOKEN=mytoken \
  -p 2222:22 -p 8888:8888 \
  jupyter-podman-rootless

# 授予sudo权限 + SSH公钥登录
invoke run \
  --grant-sudo \
  --ssh-public-key "$(cat ~/.ssh/id_ed25519.pub)"

# 启用调试输出
podman run -it --rm -e DEBUG=1 jupyter-podman-rootless bash
```

## 构建时环境变量（`--build-arg`）

构建镜像时通过 `--build-arg` 传递：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APT_MIRROR` | `official` | APT 镜像源：`official` / `tuna` / `aliyun` |
| `CONDA_MIRROR` | `official` | Conda 镜像源：`official` / `tuna` / `aliyun` |
| `PIP_MIRROR` | `official` | PIP 镜像源：`official` / `tuna` / `aliyun` |
| `PYTHON_VERSION` | `3.14` | Python 版本 |
| `PYTHON_BUILD` | `cp314t` | Python 构建类型（cp314t = free-threading，cp314 = 标准GIL） |

### 构建时变量使用示例

```bash
# 使用清华镜像源构建
podman build -t jupyter-podman-rootless \
  --build-arg APT_MIRROR=tuna \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=tuna \
  .

# 构建标准GIL版本Python（非free-threading）
podman build -t jupyter-podman-rootless:cp314 \
  --build-arg PYTHON_BUILD=cp314 \
  .
```

> **注意**：切换到cp314标准构建时，可能需要同时修改Containerfile中的conda包匹配规则。free-threading说明见 [11-free-threading.md](11-free-threading.md)。

## .env 文件模板

从 `.env.example` 复制并编辑：

```bash
cp .env.example .env
```

`.env.example` 内容：
```bash
# 服务端口
SSH_PORT=2222
JUPYTER_PORT=8888
REGISTRY_PORT=5000

# 认证（留空则自动生成）
USER_PASSWORD=
JUPYTER_TOKEN=
JUPYTER_PASSWORD=
SSH_PUBLIC_KEY=

# 权限控制
GRANT_SUDO=no
ALLOW_ROOT_SSH=no

# 镜像源（构建和运行时都可用）
APT_MIRROR=official
CONDA_MIRROR=official
PIP_MIRROR=official

# ML模型仓库
REGISTRY_URL=localhost:5000
REGISTRY_PLAIN_HTTP=true

# 调试
DEBUG=0
```
