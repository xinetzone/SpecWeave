---
id: "jupyter-podman-client-env-bootstrap"
title: "容器内自举（env.* 命令）"
source: "README.md#10-在容器中使用客户端自举env-命令"
---
# 在容器中使用客户端自举（env.* 命令）

如果宿主没有 Python ≥ 3.14 / podman-py SDK / invoke，或希望在**隔离环境**
中使用消费端（例如 CI、临时排障、给不希望安装本地依赖的同事），
可直接基于 `localhost/jupyter-podman-rootless:latest` 构建一个叠加层镜像，
镜像内已经装好 conda `main`（即 Python 3.14t cp314t free-threading，
`/opt/conda/envs/main/bin` 位于 PATH 顶端）+ editable 版本的
`jupyter-podman-client`，进入后可直接 `inv load/run/stop/status`。

> **注意**：基础镜像的 conda 环境名是 **`main`**（不是 `py314`），登录
> shell（bash -l）会通过 `~/.bashrc` + `/etc/profile.d/conda-init.sh`
> 自动激活；非交互 RUN 阶段直接用 PATH 上的 `python -m pip` 即可，
> 不要 `conda activate py314`（不存在）。

## 首次/源码修改后：构建叠加层

```bash
cd apps/containers/client

# 构建叠加层（client/shared 双 COPY + 先 shared 后 client 两个 pip install -e，<1 分钟）
invoke env.build-layer
# 等价：invoke env.build-layer --tag localhost/jupyter-podman-client:latest \
#                        --base-image localhost/jupyter-podman-rootless:latest

# 强制全量重建（忽略所有 Docker 层缓存，适用于基础镜像或 Containerfile 改动后）
invoke env.build-layer --no-cache
```

> **构建上下文说明（双上下文，2026-09-15 起）**：
> - 主 context = client 根目录，`COPY .` 受 `.containerignore` 过滤（`.image-cache/`、`workspace/`、`.env`、`__pycache__/` 等已剔除）；
> - **命名 context `shared`** = 兄弟目录 `apps/containers/shared/`，由任务自动以
>   `--build-context shared=<abs path>` 注入，供 `COPY --from=shared` 装入
>   jpman-common（client 运行时依赖的组内共享包，PyPI 无发布；镜像内按
>   「先 shared 后 client」顺序 editable 安装）。
> - **手动 `podman build` 必须自行追加同一参数**，否则构建在 `COPY --from=shared`
>   处直接失败；正常使用请始终走 `invoke env.build-layer`。

产出镜像：`localhost/jupyter-podman-client:latest`。

## 单条命令执行（脚本化）

```bash
# 在容器内跑 inv --list，验证环境 OK
invoke env.run-cmd --cmd "inv --list"

# 在容器内加载宿主缓存的镜像（宿主 ./.image-cache 会自动挂载到容器 /workspace/.image-cache）
invoke env.run-cmd --cmd "inv load"

# 启动 jupyter-podman-rootless 容器（与在宿主本地直接 inv run 行为一致）
invoke env.run-cmd --cmd "inv run --workspace /workspace"
```

默认挂载（宿主路径 → 容器路径）：
- `$IMAGE_CACHE_DIR`（或 `./.image-cache`）→ `/workspace/.image-cache`
- `workspace`（或 `IMAGE_CACHE_DIR` 的父目录）→ `/workspace`

额外挂载：
```bash
invoke env.run-cmd \
  --cmd "ls /extra" \
  --extra-mount "D:/data:/extra" \
  --extra-mount "D:/models:/models"
```

## 交互式 shell（人类排障）

```bash
invoke env.shell
# 进入后会自动激活 conda main + cd /workspace + 打印欢迎语
#   === jupyter-podman-client 自举环境 ===
#   [可用命令]  inv --list   inv load   inv run   inv stop   inv status
#   [退出]      exit
(in-container) $ inv --list
(in-container) $ inv load
(in-container) $ inv run --workspace /workspace
```

> **🛟 中文乱码排查（仅 Windows / Trae Sandbox 默认 chcp 936 时）**
>
> 症状：`invoke env.*` / `inv --list` 等命令的中文任务描述出现 `娓呯悊瀹瑰櫒` 之类的错位字符。
> 根因：**三层字符集错配**：容器/Podman 管道输出 bytes 永远 = UTF-8，而 Windows PowerShell 5 / Trae Sandbox 默认 chcp 936 (GBK) 在解码这些 bytes。
> 修复：`src/jpman_client/tasks/utils.py::_ensure_win32_stdout_transcode()` 已在 `run_cmd()` 入口自动执行以下双端修复（模块级单例只初始化一次）：
>
> 1. **B 端捕获修复（源头不乱码）：`invoke c.run(..., encoding='utf-8')` 强制 UTF-8 解码子进程 stdout bytes → `Result.stdout` 里的 str 就是正确中文。
> 2. **A 端打印修复：用 `kernel32.GetConsoleOutputCP()` 获取宿主真实代码页（通常 936），通过 `io.TextIOWrapper` 把 `sys.stdout` / `sys.stderr` 换壳编码成宿主实际解码端一致的 bytes（trae-sandbox 收到 cp936 解码 → 中文正确显示。
> 3. **逃生舱（如仍出现个别 `?` 字符）：这些字符大概率不在 GBK 字符集中（如某些异体字 / Unicode 私人区的 挙 ），属于文档 / 代码源文件中的字符串中使用全角标点；可改用 GB2312/GBK 可直接表示的常见简体中文即可。
> 4. 容器层加固：Containerfile.client ENV 追加 `PYTHONIOENCODING=UTF-8` + `PYTHONUTF8=1`，保证容器内 invoke 也永远输出 UTF-8 bytes。

## 叠加镜像内约定（由 Containerfile.client 保证）

| 约定 | 值 | 说明 |
|------|---|---|
| 默认用户 | `devuser`（固定 UID/GID 1000） | 与基础镜像一致，non-root；2026-09-11 起固定 1000（此前被基础镜像 ubuntu 账号挤到 1001） |
| Python 环境 | `conda main`（cp314t free-threading，`/opt/conda/envs/main/bin`） | 登录 shell 自动激活；PATH 顶端已生效 |
| 客户端安装路径 | `/opt/apps/containers/client/`（editable） | `_project_root()` 锚点完整 |
| WORKDIR | `/workspace` | `Path.cwd()` 与宿主期望一致 |
| SDK 策略 | `PODMAN_CLIENT_SDK_STRATEGY=legacy` | 容器内 pure-Linux，直接 `from_env()`，不走 Windows 多候选 |
| 容器内 SDK 前置条件 | `env.run-cmd` / `env.shell` 会先启动 `podman system service --time=0` | R1 修复：bootstrap 用 `--entrypoint /usr/bin/tini` 跳过 entrypoint、supervisord 只监督 Jupyter，容器内从无运行中 daemon；若未提前拉起 service，`from_env()` 会连不存在的默认 UDS socket `/run/user/<UID>/podman/podman.sock` 报 `FileNotFoundError`（被 urllib3 包装成 `APIError`） |
| 默认缓存目录 | `IMAGE_CACHE_DIR=/workspace/.image-cache` | 可被宿主挂载覆盖 |
| 自举容器 rootless | `/dev/fuse + label=disable + cgroupns=host` | 与 `ContainerConfig` 硬编码对齐，**不使用 `--privileged`** |
| 容器名（默认） | `jpman-client-env`（用完自动 `--rm` 删除） | 可通过 `--name` 覆盖 |

## 叠加层基底指纹防陈旧机制（`base-digest` 检测，2026-09-11）

**问题本质：镜像 tag 是移动指针，叠加层固化的是 digest（不可变指纹）。**

`localhost/jupyter-podman-client:latest` 是一个「叠加镜像」——基于 `localhost/jupyter-podman-rootless:latest`（基底）叠加 client 与 shared（命名构建上下文）两个源码树、按先 shared 后 client 顺序 `pip install -e` 构建。**`invoke run` 使用的不是基底 tag，而是叠加镜像构建那一刻固化的基底内容**。基底 tag 之后被更新（重建 / `invoke load`）不会传导给已构建的叠加层，导致「容器跑的还是旧基底」。

**解决机制闭环（三环节）**：

1. **构建时固化**（`invoke env.build-layer`）：构建前取基底当前 digest，经 `--build-arg BASE_DIGEST` 烤进叠加镜像 LABEL（`org.specweave.base-image` / `org.specweave.base-digest`，见 [Containerfile.client](../Containerfile.client) 末尾）。指纹保存在**构建时快照**，运行时不重算。
2. **启动前比对**（`invoke run` → [manage.py::_warn_if_layer_stale](../src/jpman_client/tasks/manage.py)）：读叠加层 LABEL 的固化 digest，与本地基底当前 digest 比较；不一致打印中文警告并给出重建指引。**只警告不阻断**（旧基底可能是有意选择）。
3. **一键恢复**（`invoke run --rebuild-layer`，B 档 2026-09-11 新增）：检测到陈旧时自动执行 `env.build-layer` 重建叠加层，随后继续正常启动；**重建失败自动回退旧基底启动**（不因重建失败而让容器起不来）。

```bash
# 启动前检测到「叠加层基底陈旧」警告时，两条路径任选：
invoke run --rebuild-layer          # 推荐：自动重建+重启（失败回退旧基底）
invoke run                          # 继续用旧基底（有意保持；警告仅提示）

# 手动重建（等价）
invoke env.build-layer && invoke stop && invoke run
# 确定有意使用旧基底 / 不想每次看到警告
# （.env 或 export）JPUMAN_SKIP_BASE_CHECK=1
```

**层级不变式**：LABEL 放在 Containerfile **末尾**（仅新增薄层），前置 COPY/pip 层缓存不受基底变化影响——重建叠加层通常 <1 分钟（见 [01-getting-started.md](01-getting-started.md)）。