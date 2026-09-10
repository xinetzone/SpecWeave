---
id: "jupyter-upstream-tools"
title: "容器编排上游工具（vendor 内嵌）"
source: "Containerfile#构建阶段 + src/jpman_builder/tasks/stage_upstream.py + bin/jpman"
---
# 容器编排上游工具（vendor 内嵌）

## 概述

自 2026-09 起，本镜像将三个容器编排上游工具**直接内嵌进镜像**：

- `podman-compose`（声明式编排 CLI）与 `podman-py`（podman SDK）装入 `main` conda 环境（`/opt/conda/envs/main/bin`）；
- `toolbox`（Toolbx 容器管理 CLI）以 Go（cgo，glibc）编译的剥离二进制装入 `/usr/local/bin/toolbox`。

三者的源树都以 **git submodule（third_party，固定 commit）** 形式注册在 SpecWeave 根工作区的 `vendor/` 下，随镜像构建以「本地源」方式安装/编译，而非在容器内联网 `pip install`/`go install` 最新版——保证镜像内工具版本**可复现、可审计**，且与网络波动解耦。

## 三个上游工具

| 工具 | 上游来源 | 镜像内落点 | 引入形态 | pin commit |
|------|---------|-----------|---------|-----------|
| podman-compose | github.com/containers/podman-compose | `/opt/conda/envs/main/bin/podman-compose` | conda-builder 阶段本地源 `pip install ./upstream-podman-compose` | `e3df10472` |
| podman-py | github.com/containers/podman-py | `main` env site-packages（`import podman`） | conda-builder 阶段本地源 `pip install ./upstream-podman-py` | `5dd81b49` |
| toolbox | github.com/containers/toolbox | `/usr/local/bin/toolbox` | toolbox-builder aux 阶段 `go build`（golang:1.26-bookworm） | `81401f64` |

三个子模块已在根工作区 [vendor/AGENTS.md](../../../../vendor/AGENTS.md) 登记为 third_party 只读依赖（gitlink pin commit，禁止本地修改），与 [.gitmodules](../../../../.gitmodules) 中的 `vendor/podman-compose`、`vendor/podman-py`、`vendor/toolbox` 条目对应。

## 构建 stage 机制（upstream/ 临时目录）

三份源树位于 SpecWeave 根 `vendor/`，**在镜像构建上下文之外**。容器镜像构建需要在上下文中以 `upstream/<name>` 引用它们（`COPY upstream/podman-py`、`COPY upstream/podman-compose`、`COPY upstream/toolbox/src`），因此引入了「构建前 stage」机制：

1. 构建入口（`invoke build`，或 `jpman rebuild` / `jpman rebuild-all`）先调用 `stage_upstream_sources`；
2. 脚本自应用根向上查找含 `.gitmodules` 的工作区根，读取 `vendor/{podman-compose,podman-py,toolbox}` 的工作树内容；
3. 复制到 `<应用根>/upstream/<name>`（跳过 `.git`、`__pycache__`、`*.pyc` 等）；目录已存在则先清空（幂等）。

`upstream/` 的语义要点：

- **仅构建上下文临时目录**：由 stage 机制在每次构建前生成，不随应用提交；已被应用根 `.gitignore` 忽略；
- **源来自 vendor/ 子模块**：不要手动向 `upstream/` 添加或修改文件，任何改动都会在下次构建前被覆盖；
- **.containerignore 反白 README**：`.containerignore` 的 `*.md` 通用规则会排除上游源树的 Markdown，但本地 pip 构建需要根 `README.md` 作为 `long_description` 元数据，因此显式放行 `upstream/podman-compose/README.md` 与 `upstream/podman-py/README.md`——这两条反白规则不可删除。

实现见 [src/jpman_builder/tasks/stage_upstream.py](../src/jpman_builder/tasks/stage_upstream.py)（bash 侧等价实现内联于 [bin/jpman](../bin/jpman) 的 `stage_upstream_sources`）。

## 固定 commit 与升级流程

升级某个上游工具时，按以下顺序操作：

1. **初始化**（首次）：在 SpecWeave 根目录执行

   ```bash
   git submodule update --init vendor/podman-compose vendor/podman-py vendor/toolbox
   ```

2. **更新 submodule pin**：在 `vendor/<name>/` 内拉取上游并检出目标 commit/tag（third_party 子模块只读，仅在本仓库 gitlink 层记录变更）：

   ```bash
   cd vendor/<name>
   git fetch origin
   git checkout <目标tag或commit>
   cd <SpecWeave根>
   git add vendor/<name>          # 记录新的 gitlink commit
   ```

3. **同步版本标注**：若新版本涉及镜像内版本声明（如 toolbox `-X` 注入的版本、注释中的 pin commit），同步更新 `Containerfile`（该文件不在本同步范围，改前须遵循 [.agents/rules/containerfile.md](../.agents/rules/containerfile.md)）；
4. **重新 stage**：stage 在构建前自动执行，无需手动调用；直接进入下一步即可（调试时可运行 `jpman rebuild` 观察 `[INFO][stage]` 日志确认已复制最新源树）；
5. **重建镜像**：`invoke build`（或 `bash bin/jpman rebuild-all`）全量重建；
6. **验证**：重跑下方「验证」三项内嵌工具检查，确认版本已更新且三项 [OK] 通过。

## 容器内用法

进入容器（`jpman shell` / `invoke shell` / `ssh -p 2222 devuser@localhost`）后，devuser 可在容器内直接使用下列工具（conda `main` env 与 `/usr/local/bin` 均已在 PATH）；其中 `toolbox` 例外——其容器创建/进入能力属宿主侧，容器内仅可验证二进制活性（见下方注意块）：

```bash
# podman-compose：容器内声明式编排（示例：/workspace 下使用 Compose 文件）
podman-compose --version
podman-compose -f compose.yaml up -d

# podman SDK（podman-py）：以 Python 方式驱动容器内 rootless Podman
python -c "import podman; print('[OK] podman SDK importable')"

# toolbox：仅二进制随镜像内嵌（/usr/local/bin/toolbox）；容器的创建/进入由宿主侧发起
toolbox --version                                    # 活性检查：确认二进制可执行
# 宿主侧（非容器内）创建/进入 Toolbx 容器：
#   toolbox create -i jupyter-podman-rootless:latest -c jupyter-dev
#   toolbox enter jupyter-dev
```

> **注意（toolbox 的能力边界）**：`toolbox` 二进制虽内嵌于镜像，但其**容器创建/进入能力由宿主侧 Toolbx 启动器提供**——启动器注入 `TOOLBOX_PATH`，容器内二进制再经 `flatpak-spawn --host` 转发回宿主执行。本镜像内嵌的 marker（`/run/.toolboxenv`、`/run/.containerenv`）使镜像**可被**宿主 Toolbx 识别与进入；但在**普通 `podman run` / `podman-compose` 会话**中并无宿主启动器，裸跑 `toolbox`（及任何子命令）会按上游设计报 `Error: TOOLBOX_PATH not set`（退出码 1），而 `toolbox --version` 等 cobra 短路型 flag 不受影响。故镜像内对 toolbox 的验证仅声明为**二进制活性（liveness）**，不声明为「容器内可用」。

容器内 Podman 本身为 rootless 模式（fuse-overlayfs + crun，见 [05-rootless-podman.md](05-rootless-podman.md)），这些内嵌工具面向在容器内继续做嵌套容器/编排的开发场景；在 WSL2 导出场景（[15-wsl-export.md](15-wsl-export.md)）下，导出的发行版也天然自带以上编排能力。

## 与宿主侧 pip 依赖的关系

- **宿主侧（invoke 三层后端）不变**：`invoke build/run/...` 仍依赖宿主机 pip 安装的 `podman-compose`/`podman`（`pip install -e ".[compose]"` / `".[full]"`），作为宿主机操作容器镜像的编排后端（见 [09-three-tier-backend.md](09-three-tier-backend.md)）；
- **本次内嵌是镜像内能力**：进入容器后无需再 pip 安装即可使用 podman-compose 与 podman SDK；宿主侧与镜像内同名工具**版本相互独立**——宿主侧跟随 pip extras 解析，镜像内跟随 `vendor/` 子模块 pin commit，互不影响；
- 两个 `omlmd`/`olot` 亦与此同理（容器内预装，宿主机可选安装，见 [06-ml-model-management.md](06-ml-model-management.md)）。

## 验证

容器内执行三项内嵌工具检查（容器外亦对应镜像构建最终验证块的 23 项 [OK] 检查）：

```bash
podman-compose --version                                   # [OK] podman-compose available (main env)
python -c "import podman; print('[OK] podman SDK importable')"
toolbox --version                                          # [OK] toolbox binary present (/usr/local/bin; 活性检查)
```

排障与 `upstream/`/子模块相关问题见 [.agents/rules/build-test.md](../.agents/rules/build-test.md) 的常见问题排查。
