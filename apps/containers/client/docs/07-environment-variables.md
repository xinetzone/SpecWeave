---
id: "jupyter-podman-client-environment-variables"
title: ".env 配置完整清单"
source: "README.md#8-env-配置完整清单"
---
# .env 配置完整清单

复制 `.env.example` 为 `.env`，按需修改（与构建端容器级变量名保持一致；新增 **Windows WSL SDK 级变量** 四个）。
配置合并优先级：**命令行参数 > shell export 的环境变量 > .env 文件 > ContainerConfig 默认值**。

## 容器级（两端通用，与构建端一致）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CONTAINER_NAME` | `jupyter-podman` | 容器名，`--name` 参数覆盖 |
| `IMAGE_TAG` | `localhost/jupyter-podman-client:latest` | 加载镜像后运行的 tag |
| `SSH_PORT` | `2222` | 宿主 → 容器的 SSH `-p 2222:22` 映射 |
| `JUPYTER_PORT` | `8888` | 宿主 → 容器的 Jupyter `-p 8888:8888` 映射 |
| `WORKSPACE` | `./workspace` | 挂载到容器 `/home/devuser/workspace` 的宿主工作区 |
| `USER_PASSWORD` | （空 = 自动生成 12 位打印） | devuser shell 登录密码 |
| `JUPYTER_TOKEN` | （空 = 自动生成 32 位打印） | Jupyter 登录 token |
| `SSH_PUBLIC_KEY` | （空） | 追加到 `~devuser/.ssh/authorized_keys` 的公钥内容 |
| `GRANT_SUDO` | `yes` | 是否给 devuser 开 NOPASSWD sudo，opt-out 写 `no` |

## Windows WSL SDK 级（仅消费端，可选；默认 auto 可全省略）

| 变量 | 合法值 | 说明 |
|------|--------|------|
| `PODMAN_CLIENT_SDK_STRATEGY` | `auto` / `legacy` / `wsl` / `machine` | SDK 连接策略，shell 优先级高于 .env |
| `WSL_DISTRO_NAME` | 任意 `wsl.exe -l -q` 能列出的发行版名 | P1 WSL9P 路径第一级回退，省略则 3 级探测 |
| `CONTAINER_HOST` | 合法 podman-py scheme | **最高优先级**显式 daemon URL，用于 P0 覆盖；常见值见速查表 |
| `DOCKER_HOST` | 同上 | 兼容兜底，优先级低于 `CONTAINER_HOST` |

> `.env` 文件中的 SDK 级变量由 `src/jpman_client/tasks/manage.py::_load_env_overrides` 中的 `load_dotenv(override=False)` 同步到 `os.environ`，
> 因此 shell 里已显式 `export` / `$env:` 的值不会被 `.env` 覆盖，符合"命令行 > .env > 默认"约定。

## 运行时透传（消费端新增；与构建端 `docs/07-toolbx-passthrough.md` 的分层覆盖逐项对应）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PASSTHROUGH_HOST_NETWORK` | `no` | ① Host 网络模式（不发布端口；SSH=`localhost:<SSH_PORT>`，Jupyter=`localhost:8888`） |
| `PASSTHROUGH_WAYLAND` | `no` | ② Wayland 套接字透传 |
| `PASSTHROUGH_GPU` | `no` | ③ GPU 透传 |
| `PASSTHROUGH_DBUS` | `no` | ④ D-Bus 会话总线透传 |
| `PASSTHROUGH_USB` | `no` | ⑤ USB 透传 |
| `HOST_XDG_RUNTIME_DIR` | `/run/user/<运行时 UID>`（Linux 默认取 `$XDG_RUNTIME_DIR` 末段/`id -u`，Windows 原生默认 1000；均可由 `PODMAN_RUNTIME_UID` 覆盖，见 C-I5） | daemon 宿主运行时目录（②④ 的基准路径） |
| `HOST_WAYLAND_DISPLAY` | `wayland-0` | ② Wayland socket 名（**daemon 宿主**侧的实例名，不是客户端环境变量） |
| `DBUS_SESSION_BUS_PATH` | `<HOST_XDG_RUNTIME_DIR>/bus` | ④ 会话总线 socket 路径 |
| `GPU_DEVICE` | `/dev/dri` | ③ GPU 设备节点 |
| `USB_DEVICE` | `/dev/bus/usb` | ⑤ USB 设备路径 |

> 布尔项写法：`yes/true/1/on` 为真，`no/false/0/off` 为假。**三态优先级**：
> `--x`（显式开启）> `--no-x`（显式关闭，可覆盖 `.env`）> 未指定时才读 `.env` > 内置默认。
> 资源路径全部在 **daemon 宿主** 侧解析，缺失时表现为 C-I3（见 [04-troubleshooting-guide.md](04-troubleshooting-guide.md)）。