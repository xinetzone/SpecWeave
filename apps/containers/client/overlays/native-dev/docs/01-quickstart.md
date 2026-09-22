---
id: "native-dev-quickstart"
title: "快速开始：前置条件与两条启动路径"
source: "README.md#路径一invoke-native推荐"
---
# 快速开始：前置条件与两条启动路径

## 前置条件

1. podman machine（Windows 即 WSL2 后端）已运行；
2. 本地已有基底镜像，没有则先在 `apps/containers/client` 加载：
   ```bash
   invoke load        # localhost/jupyter-podman-rootless:latest
   ```
3. 宿主存在源码目录（默认仓库根 `external/` 对应源码树）：
   - `external/chaos/npu_tvm`（TVM 0.19.0 fork；若 `build/libtvm.so`
     已存在可直接打包，否则先 build-tvm——全量编译需先
     `git submodule update --init` 检出 dmlc-core 等子模块）
   - `external/containers/workspace/dev/npuusertools`（xmnn 包 + tools_cpp/autolibs/fonts 数据）
   - `external/chaos/models`（模型目录）
4. **Windows 原生自动桥接**：与 quant.* 相同，Windows 原生 CPython 执行时
   自动桥接到 WSL 发行版（默认 `podman-machine-default`——client 专用
   rootless 发行版，与 flapping 的 Podman Desktop 默认 machine 相互独立、
   镜像存储不互通；`COMPOSE_WSL_DISTRO` 可指定、`none` 关闭回退门禁）。也可手动二选一：
   - WSL2 发行版内（推荐）：
     ```bash
     wsl -d <发行版>
     cd /mnt/d/spaces/SpecWeave/apps/containers/client
     pip install -e ".[compose]"
     ```
   - 或 client 自举容器：`invoke env.run-cmd --cmd 'inv native.up'`

## 路径一：invoke native.*（推荐）

在 `apps/containers/client` 下（WSL2/Linux/macOS）：

```bash
# ── 过程一：镜像环境构建（有网侧，一次性）─────────────────────────────
invoke native.build                         # 构建工具链镜像（构建期自动跑双 ABI/SONAME/离线完备性守卫）
                                         #   --pip-mirror/--conda-mirror tuna|aliyun 可加速
                                         #   --torch cpu|cu130 额外装 torch（默认不装，见 [04 GPU 与 torch](04-gpu-and-torch.md)）
invoke native.save                         # 导出镜像归档（tar.gz + manifest/SHA256）→ 携带到无网机器

# ── 过程二：启动开发环境并开发（有网/无网通用）────────────────────────
invoke native.load --path <归档.tar.gz>    # 从归档导入镜像（完整性校验后导入，导入幂等）
invoke native.up --offline                 # 离线启动：不构建、不起网络请求（参见 [03 离线交付](03-offline-delivery.md)）
invoke native.up                           # 有网侧常规启动（默认随带构建；--skip-build 直接用本地镜像）
invoke native.up --gpu                     # 【可选】透传 GPU 设备（默认零透传，见 [04 GPU 与 torch](04-gpu-and-torch.md)）
invoke native.up --passthrough             # 【可选】host 网络（Jupyter 8888/SSH 2223）+ D-Bus（见 [05 参数与关系](05-params-and-relations.md)）
invoke native.up --usb                     # 【可选】追加透传 USB 总线（WSL2 先 usbipd-win attach）
invoke native.ps                           # 服务状态
invoke native.smoke                        # 工具链守卫 + 源码挂载检查（libtvm 缺席时跳过算例段）

invoke native.build-tvm                    # 【可选】栈内编译 TVM（build/libtvm.so 已存在则无需）
invoke native.wheel                        # Nuitka 打包 xmnn whl（tvm 串行→vta/xmnn 并行）
                                         #   --jobs 4 内存紧张时；--clean 禁 ccache 全量重编；
                                         #   --tvm-flags "..." 透传额外 Nuitka 参数
podman-compose -p native-dev exec native \
    bash /opt/native-builder/scripts/verify-wheel.sh   # 10 项隔离验证（临时 venv，不污染源码环境）

invoke native.logs                         # 跟踪日志（Ctrl+C 退出）
invoke native.down                         # 停止清理（workspace/源码保留；ccache/登录态/host key 卷保留）
invoke native.down --volumes               # 连 native-ccache、native-jupyter、native-ssh-host-keys 命名卷一起删除
```

启动后访问（凭证可由环境变量覆盖，见 `.env.example`）：

| 服务 | 地址 | 凭证 / 入口 |
|---|---|---|
| JupyterLab | http://localhost:8890 | `JUPYTER_TOKEN`（留空则自动生成）；内核选 **Python 3.14 (native dev)**；`invoke native.up` 横幅会打印带 token 的「直达」URL，免登录 |
| SSH | `ssh -p 2223 devuser@localhost` | `USER_PASSWORD`（留空自动生成） |

> **看不到凭证？** 两个变量留空时，密码/token 由容器内 entrypoint 生成、只进
> 容器启动日志；`invoke native.up` 收尾会从日志**头部**回读并打印
> `密码 devuser / <值>` 与带 token 的「直达」URL（C24）。回读只读容器状态，
> **不会回写 `.env`**。

> **登录态持久化**：Jupyter cookie/notebook 签名密钥存于命名卷 `native-jupyter`
> （容器内 `/home/devuser/.local/share/jupyter`），普通 `down/up` 重建容器后
> 浏览器无需重新登录；仅 `down --volumes` 才会清除（清除后重新登录属预期）。
> 旧标签页若在重建后提示失败，硬刷新（Ctrl+Shift+R）重登即可，详见
> [docs/04 排障速查 C-I6](../../../docs/04-troubleshooting-guide.md)。

> **SSH host key 持久化**：主机密钥存于命名卷 `native-ssh-host-keys`
> （容器内 `/var/lib/jpman/ssh-host-keys`），普通 `down/up` 重建容器后**不再
> 轮换指纹**，客户端 `known_hosts` 无需反复 `ssh-keygen -R` 清理；仅
> `down --volumes` 才会清除（清除后指纹轮换属预期）。卷名与落点同客户交付栈
> [offline-delivery](../../../../offline-delivery/README.md) 的交付包
> `release/compose.yaml`。

## 路径二：裸 podman-compose

在叠加层根目录（`overlays/native-dev/`）下，无需 invoke：

```bash
cp .env.example .env           # 按需修改源码路径/端口/凭证/镜像源
podman-compose up -d           # 首次自动构建
podman-compose exec native bash /opt/native-builder/scripts/build-tvm.sh    # 可选
podman-compose exec native bash /opt/native-builder/scripts/build-wheel.sh
podman-compose down
```

> **离线（裸 compose）**：invoke 侧的 `--offline` 只是帮你把下面两件事一起做了——
> 镜像已导入时加 `--no-build` 跳过构建（`podman-compose up -d --no-build`），
> 以及给容器内打包脚本注入离线段（`podman-compose exec -e NATIVE_OFFLINE=1 native
> bash /opt/native-builder/scripts/build-wheel.sh`）。镜像归档的导出/导入仍建议用
> `invoke native.save` / `invoke native.load`（带 manifest 校验），裸 compose 无对应命令。

`../compose.yaml`（叠加层根目录）已内置 rootless 三必需（`/dev/fuse`、`label=disable`、
`cgroupns: host`），五个 bind 全部长语法，**无特权容器**；
`network_mode: bridge` 是 2026-09-14 同机实证（machine 无 systemd user bus
时默认项目网络 aardvark-dns 失败），见 compose 文件头注释。

> ⚠️ **控制平面纪律（2026-09-15 实证）**：选定裸 compose 就长期在叠加层目录用
> 裸 compose，**不要与 `invoke native.*`（WSL 桥接，下发 `/mnt/d/...`）交替
> 操作同一栈**——两者给容器打的 `config_files` 标签原文不同（`D:\...` vs
> `/mnt/d/...`），交替执行会被 podman-compose 强制 recreate，并可能留下孤儿
> rootlessport 导致 `up -d` 报 2223/8890 `address already in use`。已经
> 交替翻车时直接 `invoke native.up --skip-build`，编排层 preflight 三道自愈
> （残留 down / 跨平面优雅 down / 孤儿端口定点回收）自动恢复，详见
> [30 秒修复速查表 W-I10](../../../docs/04-troubleshooting-guide.md)。
