---
title: "jupyter-podman-rootless 嵌入 containers 上游工具（podman-compose/podman-py/toolbox）"
status: "draft"
source: "github.com/containers/{podman-compose,podman-py,toolbox} 官方上游（经 vendor/ 子模块引入）"
---

# Jupyter Podman Rootless：嵌入 containers 上游工具 Spec

## Why

当前 `apps/containers/jupyter-podman-rootless` 镜像**只内嵌 podman CLI（apt）**，而 podman-compose / podman-py 仅以 PyPI pip 包存在于**宿主编排侧**（`pyproject.toml` extras），toolbox 只做了"可被宿主 Toolbx 识别"的兼容标记（R5），未内嵌工具本体。用户希望把镜像升级为**开箱即用的 Podman 平台开发箱（DinP 平台化）**：进入容器即可使用 `podman-compose`、`podman-py` SDK、`toolbox` 做容器化开发。为满足"来源与 `containers` 上游同步、跨机可复现"，三个上游仓库须以 **`vendor/` git 子模块（third_party 只读）** 方式纳入 SpecWeave 版本控制并 pin commit（现 `external/dao/action/Containers/` 下快照是 untracked 本地 clone，仅作 pin 依据，不入库）。

## What Changes

- **仓库层（SpecWeave vendor/ 区域）**：将三个仓库注册为 `third_party` 类型 git submodule，路径 `vendor/{podman-compose,podman-py,toolbox}`（URL `git@github.com:containers/<name>.git`），pin 当前已核实的上游 commit；同步更新 vendor 区域登记——`vendor/AGENTS.md`（子模块路由表 + 边界声明）新增三行，并按 check-vendor 规则再生成 `vendor/README.md`、`vendor/VERSION.md`。`external/dao/action/Containers/` 下历史 untracked 快照保持原样、不删除、不纳入版本控制。
- **镜像内预装（DinP 平台化）**：
  - `podman-compose`、`podman-py`：由固定 submodule 源树在 conda-builder 阶段 pip 安装进 `/opt/conda/envs/main`（经 COPY --from 进入 final），容器内 `podman-compose --version`、`python -c "import podman"` 直接可用。
  - `toolbox`：新增 Go builder 阶段（`FROM golang:<pin> AS toolbox-builder`），由固定 submodule 源树编译出 `toolbox` 二进制，final 阶段 COPY 至 `/usr/local/bin/toolbox`。
- **构建链路接驳**：`invoke build`、jpman `rebuild/build` 及 podman-compose 后端在构建前自动执行 "stage upstream"（从 `vendor/<name>` 子模块复制到应用内 git-ignored 的构建上下文目录 `<app>/upstream/<name>`）；submodule 未初始化时给出友好错误（提示 `git submodule update --init vendor/<name>`）。`Containerfile` 相应新增 COPY/安装逻辑。
- **规范与文档同步**：更新 `.agents/rules/containerfile.md`（层架构 + VALIDATE 清单 15→18 项）、`build-test.md`（前置条件 + 验证步骤）、`.agents/CHANGELOG.md`、AGENTS.md/`.agents/README.md` 描述；新增人类可读文档 `docs/17-upstream-tools.md` 并更新 `docs/README.md`、`docs/04-image-architecture.md` 等。

## Impact

- Affected specs：jupyter-podman-rootless 7 层架构规范、构建与测试规范（应用自治）；vendor 区域登记（主权区）。
- Affected code/config：
  - SpecWeave root/vendor：`.gitmodules`、`vendor/AGENTS.md`（子模块路由表/边界声明）、`vendor/README.md`、`vendor/VERSION.md`（check-vendor 再生成）。
  - 应用：`Containerfile`（新增 Go 阶段与安装层/校验）、`src/jpman_builder/tasks/build.py` 与 `tasks/utils.py`（stage 逻辑）、`bin/jpman`（bash 同功能）、`.containerignore`、`.gitignore`、`.agents/rules/{containerfile,build-test}.md`、`.agents/CHANGELOG.md`、`AGENTS.md`、`.agents/README.md`、`docs/04-image-architecture.md`、`docs/08-directory-structure.md`、`docs/README.md`、新增 `docs/17-upstream-tools.md`。
- 不涉及：宿主编排侧 PyPI 依赖方式（R1/R2 三层后端仍走 pip，本次不改）；宿主 Toolbx 透传语义（R5 保持）。

## 约束

- 工具本体来源必须是**已注册并 pin commit 的 `vendor/` submodule 源树**，禁止回退为"构建时 git clone 上游 main / PyPI latest"；`external/dao/action/Containers/` 快照仅作注册前 pin 依据，不参与运行时/构建路径。
- Python 3.14 cp314t（free-threading）兼容：podman-py / podman-compose 及运行时依赖需在 main 环境可导入/可执行；若某依赖无 cp314t wheel 导致 sdist 编译失败，采用"conda-forge 装运行时依赖 + `pip install --no-deps` 本地源"降级策略。
- 构建上下文保持应用根目录（context 精简原则），不得扩大为 SpecWeave root；`upstream/` 仅作为 git-ignored 的临时构建输入，不进最终镜像层（python 工具在 builder 阶段内 `rm`；toolbox 只 COPY 二进制）。
- `.containerignore` 的 `*.md` 黑名单需为 `upstream/*/README.md` 增加反白（setuptools readme 需 README 文件存在），避免本地 pip 安装构建失败。

## ADDED Requirements

### Requirement: 在 vendor/ 注册 containers 上游三仓库为 git submodule（third_party）

系统（SpecWeave 超级仓库）SHALL 将以下三个仓库注册为 `third_party` 类型 git submodule 并固定到当前已核实的上游 commit：

| 子模块路径 | URL | 固定 commit |
|---|---|---|
| `vendor/podman-compose` | `git@github.com:containers/podman-compose.git` | `e3df10472e194ab6d547b5ad25542c5c79e1a5fb` |
| `vendor/podman-py` | `git@github.com:containers/podman-py.git` | `5dd81b49f35733a27b8051c47e23d3b4c85ea716` |
| `vendor/toolbox` | `git@github.com:containers/toolbox.git` | `81401f64b3865129ea66f2a5e02a7eb40edd4fb8` |

注册 SHALL 遵循 vendor 区域约定（只读、gitlink pin、禁止修改子模块内容），并同步更新 `vendor/AGENTS.md` 子模块路由表与边界声明、经 `python .agents/scripts/check-vendor.py` 再生成 `vendor/README.md`/`vendor/VERSION.md`。现有 `external/dao/action/Containers/` 历史快照 SHALL 保持 untracked 原样。

#### Scenario: 注册成功且 pin 生效

- **WHEN** 在 SpecWeave 根执行 `git submodule status`
- **THEN** 三行输出均以 `<40位commit>` 开头（无前缀 `-`），对应 commit 与上表一致；`git status` 无 `vendor/<name>` 下散落文件被误报为 untracked。

#### Scenario: vendor 登记一致且无泄漏

- **WHEN** 在 SpecWeave 根执行 `python .agents/scripts/check-vendor.py` 与 `git status --short`
- **THEN** vendor 登记检查通过（`vendor/README.md`、`vendor/VERSION.md` 已再生成），不出现未登记孤儿目录；`external/dao/action/Containers/` 下历史快照（conmon/qm 等）不产生任何 untracked 条目。

### Requirement: 镜像内嵌 podman-compose 与 podman-py（本地固定源安装）

镜像最终层 SHALL 内嵌 podman-compose 与 podman-py，二者由 pin commit 的 `vendor/` submodule 源树安装进 `/opt/conda/envs/main`，随 `COPY --from=conda-builder` 进入 final；安装完成后 builder 阶段的源树 SHALL 被清理（不进 final 镜像）。版本 SHALL 以 `podman-compose --version` 与 `python -c "import podman"` 的元数据方式可回显，纳入 Containerfile VALIDATE 清单。

#### Scenario: 容器内工具可用

- **WHEN** 镜像构建成功并以 `devuser` 在容器内执行 `/opt/conda/envs/main/bin/podman-compose --version`
- **THEN** 命令退出码 0，输出版本号。

- **WHEN** 容器内执行 `/opt/conda/envs/main/bin/python -c "import podman; print(podman.__version__ if hasattr(podman,'__version__') else 'ok')"`
- **THEN** 导入成功且退出码 0。

### Requirement: 镜像内嵌 toolbox 二进制（本地固定源编译）

最终镜像 SHALL 提供可执行文件 `/usr/local/bin/toolbox`，来源为 pin commit 的 `vendor/toolbox` submodule 源树，经 Go builder 阶段（`FROM golang`）编译产出后 COPY 进 final；Go 模块代理 SHALL 可通过 build-arg（如 `GO_PROXY`）切换，默认与容器构建其它下载一致可配置。builder 阶段与工具源码不进入 final。

#### Scenario: toolbox 可执行

- **WHEN** 容器内以任意用户执行 `command -v toolbox` 与 `toolbox --help`
- **THEN** 前者输出 `/usr/local/bin/toolbox`，后者退出码 0。

（注：`toolbox create/enter` 属 DinP 运行时能力，受 WSL2 用户命名空间等环境限制，列入 runtime-conditional 冒烟验证，不阻塞镜像构建验收。）

### Requirement: 构建链路自动 stage 上游源树

应用构建入口（invoke `build`、jpman `build/rebuild/rebuild-all`、podman-compose 后端）SHALL 在发起 `podman build` 前自动执行一次 "stage upstream"：从三个已注册 `vendor/` submodule 路径（相对 SpecWeave root）复制构建所需内容到 `<project_root>/upstream/{podman-compose,podman-py,toolbox}`（git-ignored）。任一 submodule 缺失/未初始化时 SHALL 中止构建并输出修复提示（`git submodule update --init vendor/<name>`）。跨平台路径转换（Windows → WSL）SHALL 复用既有规则。

#### Scenario: stage 后正常构建

- **WHEN** 三个 submodule 均已初始化，执行 `invoke build`（或 jpman 对应命令）
- **THEN** 构建日志出现 upstream stage 成功信息，镜像构建走通且含三个工具。

#### Scenario: submodule 缺失

- **WHEN** 某 submodule 未初始化，执行任一构建命令
- **THEN** 命令以非 0 退出，错误信息包含具体的 `git submodule update --init vendor/<name>` 修复命令。

### Requirement: 规则与文档同步

`.agents/rules/containerfile.md` SHALL 更新层架构（记录新增 Go builder 阶段、python 工具安装位置、VALIDATE 15→18 项）；`.agents/rules/build-test.md` SHALL 增加 submodule 前置条件与三项内嵌工具验证；`.agents/CHANGELOG.md`、`AGENTS.md`、`.agents/README.md`、`docs/04-image-architecture.md`、`docs/08-directory-structure.md`、`docs/README.md` SHALL 同步；新增 `docs/17-upstream-tools.md` 说明三个上游仓库的来源（vendor/ third_party）、固定 commit、升级流程与容器内用法。

#### Scenario: 文档一致

- **WHEN** 按 `docs/README.md` 索引逐文档抽查与镜像实际行为
- **THEN** 无过期描述（不出现"podman-compose 仅宿主机"等与新行为冲突的表述）；`check-links` 类相对路径检查通过。

## MODIFIED Requirements

### Requirement: Containerfile 7 层架构规范（containerfile.md）

**修改**：原"Layer 3 main 环境仅含 Jupyter + omlmd/olot、Layer 6 VALIDATE 15 项"的规范扩展为：main 环境增加 podman-py/podman-compose（本地源），镜像增加 toolbox Go builder 阶段产物 COPY，VALIDATE 清单扩至 18 项（新增 podman-compose / python-podman / toolbox）。层变化频率标注同步更新，保持"builder 产物 COPY、配置变更低层缓存"原则。

### Requirement: vendor 区域子模块登记（vendor/AGENTS.md 与 check-vendor 产物）

**修改**：`vendor/AGENTS.md` 的「子模块路由表」与「边界声明」新增 podman-compose / podman-py / toolbox 三个 `third_party` 条目（说明：containers 官方容器编排工具链，只读依赖，gitlink pin commit）；`vendor/README.md`、`vendor/VERSION.md` 由 `check-vendor.py` 再生成。禁止修改子模块内部内容；`external/` 根 .gitignore 策略**不改变**（保持 external 整目录忽略）。

### Requirement: 构建测试规范（build-test.md）

**修改**：构建前置条件增加"三 submodule（`vendor/<name>`）已注册并 pin"；构建后 7 步验证清单增加内嵌工具可用性检查项（见 ADDED Requirements 对应 Scenario）。

## REMOVED Requirements

（无）

## 验证策略

- 静态：`git submodule status`、`python .agents/scripts/check-vendor.py`、Containerfile/RUN 语法（`bash -n`、`podman build` dry-run）、docs 链接检查。
- 动态（环境条件）：在 WSL/Podman 环境执行真实构建与容器内工具验证（参考 `.agents/rules/build-test.md` 既有流程）；本机无法构建时该部分标注"需用户在 WSL/Linux 环境验证"，与历史 spec 处理方式一致。

## Open Questions

- toolbox 官方以 meson 构建，内嵌方案选 Go builder 阶段直编（`go build`）而非完整 meson 流程——影响：不产出 man page / completion / profile.d 集成。是否需要完整 meson 打包？（默认：Go 直编仅交付二进制，文档注明。）
- `GO_PROXY` 默认值：默认官方 `proxy.golang.org` 还是镜像 `goproxy.cn`？（建议默认官方、可 build-arg 覆盖，与既有 MIRROR 设计一致。）
