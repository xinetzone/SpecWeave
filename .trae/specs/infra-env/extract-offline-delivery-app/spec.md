---
title: "offline-delivery 独立应用抽取（xmnn-runtime 离线交付链路迁出 client）"
status: "completed"
---

# offline-delivery 独立应用抽取 - Product Requirements Document

## Overview

- **Summary**: 把当前寄居在 `apps/containers/client/overlays/xmnn-runtime/` 的客户离线交付链路（镜像定义 + 打包器 + `release/` 交付骨架）整体迁出，在 `apps/containers/` 下新建**完全自包含**的独立应用 `offline-delivery/`，其构建/打包工具链改为**零 Python 的 shell CLI**（bash + pwsh7 双入口），并同步从 client 侧删除原实现。
- **Purpose**: 客户交付物目前与消费端 client 的镜像消费栈强耦合——`relpack.py` 位于 `jpman_client` 包内并硬编码 client 根路径，镜像定义依赖 client 的 `overlays/_shared/base-rootless.yaml` 与 invoke 编排内核，导致「一份客户交付物要拖着整个 client 与 shared 两个应用才能构建」。交付物本质上应独立演进（有自己的产品参数、版本语义、发布节奏），不应被消费端的重构连带影响。
- **Target Users**: 厂商侧交付工程师（打包/发布离线镜像）、客户侧安装人员（接收 `release/` 交付骨架）、后续新增交付产品的维护者。

## Goals

- 在 `apps/containers/offline-delivery/` 建立独立应用：目录名**不含 `xmnn`**，以 `products/<产品名>/` 承载多产品，便于后续扩展第二个交付产品。
- 交付链路只依赖两项外部输入：① `apps/containers/workspace/dist/xmnn-*.whl`（预构建 wheel）；② 构建基底镜像 `localhost/jupyter-podman-rootless:latest`（由 `jupyter-podman-rootless` 应用产出）。
- 构建/打包工具改为 **bash + pwsh7 双入口 CLI**（`bin/relpack` / `bin/relpack.ps1`），不再需要 `pip install`、不引入 `jpman_client` / `jpman_common` / invoke。
- 能力面收敛为 **stage（暂存 wheel）→ build（构建镜像，含 `--torch` 形态与形态感知 tag）→ pack（导出 tar.gz + release.json）→ smoke（经交付骨架端到端 10 项守卫）**；日常运行与排障直接使用交付骨架自带的 `xmnnctl` / `xmnnctl.ps1`。
- client 侧原 `xmnnrt.*` 栈（overlays/xmnn-runtime + tasks/xmnnrt.py + relpack.py + 相关测试/规则/文档）**完全移除**，IC 侧文档与路由改为指向新应用，杜绝两份镜像定义漂移。

## Non-Goals

- 不改 `jupyter-podman-rootless`（基镜像）任何内容；不做基镜像重建。
- 不改交付骨架的对外契约：客户可见的 `xmnnctl` / `xmnnctl.ps1` 命令面、`compose*.yaml`、`.env` 键、`release.json` 字段、README 使用流程保持等价。
- 不保留内部开发栈：原 `xmnnrt.up/down/ps/logs` 与 GPU 运行期透传（`compose.gpu*.yaml`、`up --gpu`）随栈一并取消；GPU/形态化交付如需重启，另立提案。
- 不为新应用建立可安装的 Python 包（无 pyproject、无 scikit-build-core、无 invoke 任务）。
- 不动 `apps/docker-images/xmnn-runtime/`（历史 Docker 骨架应用，与本次无关）。

## Background & Context

- 现状事实（磁盘核对）：
  - 交付骨架在 `apps/containers/client/overlays/xmnn-runtime/release/`：`xmnnctl`(bash, 454 行) + `xmnnctl.ps1`(pwsh7, 498 行) + `compose.yaml` + `compose.podman.yaml` + `.env.example` + `README.md` + `artifacts/.gitignore` + `workspace/.gitkeep`；**骨架本身零 Python、零 `../` 引用**（`compose.yaml` 已自述「不依赖仓库内任何其他文件」）。
  - 厂商侧打包器 `client/src/jpman_client/relpack.py`：硬编码 `CLIENT_ROOT`/`OVERLAY_DIR`/`RELEASE_DIR`，经 `wsl.exe` 在 WSL 内执行 `podman tag → podman save | gzip -1 → gzip -t → 原子 mv`，产出 `artifacts/release.json`（schema_version/product/version/wheel/image/archive/built_at/source_commit/pack_tool）。
  - 镜像定义 `client/overlays/xmnn-runtime/Containerfile.xmnn-runtime`：`ARG BASE_IMAGE=localhost/jupyter-podman-rootless:latest`；Layer 1 内置 torch（`scripts/install-torch.sh`，形态 cpu|cu130）、Layer 2 装 whl 到 `/opt/conda`(cp314 GIL)、Layer 3 内核注册 + 运行时守卫、Layer 4 构建期 root/devuser 双跑 10 项硬验证（`smoke/_runtime_smoke.py`）；构建上下文仅需本目录的 `scripts/`、`smoke/`、`wheels/`。
  - 编排在 client 内核：`tasks/xmnnrt.py` 的 `XMNNRT_SPEC` 经 `make_stack_tasks` 生成七任务，`up` 依赖 `overlays/_shared/base-rootless.yaml`（client 侧 `extends` 单一事实源）与 podman-compose 子进程层。
  - 形态感知 tag（C28）：`localhost/xmnn-runtime:<形态>` + `:latest` 通用别名；`relpack._PACK_SCRIPT` 硬编码 `SRC="localhost/xmnn-runtime:latest"`。
  - wheel 现落 `apps/containers/workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（177 MB，`apps/containers/.gitignore` 已忽略 `workspace/`）。
- 用户决策（本次澄清）：目录名不复用 `xmnn`（为后续扩展预留）；client 侧完全迁移；工具链用 shell CLI + 独立单测；能力面收敛为构建+打包+冒烟。

## Functional Requirements

- **FR-1**: 新建应用根 `apps/containers/offline-delivery/`，含治理资产（`AGENTS.md`、`README.md`、`.agents/{README.md,CHANGELOG.md,rules/}`、`docs/`）与工具链（`bin/`、`tests/`）。
- **FR-2**: 目录布局按「应用工具 + 多产品」分层：`products/<产品名>/` 承载单产品全部资产（产品参数、Containerfile、构建脚本、冒烟、wheel 暂存区、`release/` 交付骨架）；首个产品为 `products/xmnn-runtime/`。
- **FR-3**: `release/` 交付骨架**纯移动**：内容除「开发仓库便捷壳」两处表述外逐字保持不变；骨架内不得出现指向新应用或仓库其他文件的相对路径。
- **FR-4**: `bin/relpack`（bash，WSL/Linux/macOS）与 `bin/relpack.ps1`（pwsh7，Windows 原生经 `wsl.exe` 桥接）提供等价命令面：`stage` / `build` / `pack` / `smoke` / `version` / `--help`；产品经 `-p|--product` 选择，默认 `xmnn-runtime`。
- **FR-5**: `stage` 语义与现版 `_ensure_wheel_staged` 等价：`--wheel` 显式 > `WHEEL_DIST`（默认 `../workspace/dist`，即 `apps/containers/workspace/dist`）最新 mtime > 复用已暂存 > 非零退出并给出上游指引；同名同 size 同 mtime 时跳过拷贝；暂存区同时只保留一个 whl。
- **FR-6**: `build` 语义与现版等价：构建上下文 = 产品目录；build args 为 `BASE_IMAGE` / `PIP_MIRROR` / `TORCH_FLAVOR`（形态白名单 `cpu|cu130`，缺省 `cpu`）；产出双 tag —— `localhost/xmnn-runtime:<形态>`（形态感知）与 `localhost/xmnn-runtime:latest`（通用别名）；支持 `--no-cache`；构建期 10 项硬验证由 Containerfile 自带，任一失败即构建失败。
- **FR-7**: `pack` 语义与现版等价：① 交付骨架 CRLF shebang 守卫（命中即 fail-fast，不产出坏字节）；② 镜像 tag 为 `localhost/xmnn-runtime:<版本>`；③ `podman save | gzip -1` + `gzip -t` + 原子 `mv`（不在交付目录留截断归档）；④ 写 `release/artifacts/release.json`，字段与 `.pack_tool` 之外的现版逐字一致（`pack_tool` 改为新应用标识），torch 标签读取保留「新键 `org.specweave.torch-version` 优先、旧键 `org.specweave.torch-cpu` 回退」；⑤ 版本默认取暂存 whl 版本，`--version` 可显式覆盖。
- **FR-8**: `smoke` 以**交付骨架自身为唯一入口**做端到端验证：把本地镜像改挂到交付版本 tag → `release/` 内 `./xmnnctl init`（缺 `.env` 时）→ `up` → `smoke`（容器内 `/opt/xmnnrt-smoke/_runtime_smoke.py` 10 项）→ `down`；任一步失败即非零退出并打印可执行指引。
- **FR-9**: 产品参数单一事实源 `products/<产品名>/product.env`（镜像名、Containerfile 名、wheel glob、wheel 源目录、基镜像默认、torch 缺省、骨架目录名）；CLI 只读该文件，不内嵌产品常量。
- **FR-10**: 迁移包 `tests/` 守卫测试（pytest，纯文件/文本断言，不建 Python 包）：覆盖交付骨架不变量（文件清单、compose 无 `../`、`image/pull_policy/ports/volumes/env` 四键与 `pull_policy: never`、podman override 三必需且无 privileged、`.env.example` 无 CR、两端命令同构、shebang 全 LF、`localhost/xmnn-runtime:$ver` 计数、随机凭证来源等）与 CLI 静态不变量（`bash -n`、形态 tag 规则、CRLF 守卫存在）。
- **FR-11**: client 侧完全移除：删 `overlays/xmnn-runtime/`（整目录）、`src/jpman_client/relpack.py`、`src/jpman_client/tasks/xmnnrt.py`、`tests/test_release_bundle.py`、`tests/test_xmnnrt_stage.py`、`.agents/rules/xmnnrt-overlay.md`、`docs/13-xmnn-runtime-overlay.md`；同步更新 `tasks/__init__.py`、`AGENTS.md`、`README.md`、`.agents/README.md`、`.agents/CHANGELOG.md`（追加历史条目）、`docs/README.md`、`.env.example`、`tests/{test_tasks_surface,test_compose_merge,test_overlay_core}.py`。
- **FR-12**: 内核死代码清理：`flavor_tag` / `image_flavor` / `image_tag_alias` / `torch_default` 在 xmnnrt 迁出后不再有声明者，删除其实现、专属测试与 help/hint 分支；`warn_torch_flavor_mismatch` 保留（`xmnn` 开发栈仍在用）。
- **FR-13**: 仓库治理同步：`apps/containers/AGENTS.md`（成员路由表、嵌套路由图、任务路由表）、`apps/containers/README.md`、组级 `docs/`、`apps/AGENTS.md`、`apps/README.md` 登记新应用；`.gitattributes` 增加 `**/relpack` 的 `text eol=lf` 并把「便捷壳」注释更新为新应用路径；`.trae/specs` 看板经 docgen 刷新。

## Non-Functional Requirements

- **NFR-1**: 零 Python 运行时依赖——CLI 仅需 bash 4+ / pwsh 7.4+ 与 `podman`（`smoke` 另需 `podman-compose`）；不使用 podman-py SDK。
- **NFR-2**: 交付骨架保持「零 Python、零网络、零仓库外引用」的客户交付契约不变。
- **NFR-3**: Windows 原生一律走 `bin/relpack.ps1`（pwsh7），不得依赖 Windows PowerShell 5.1；跨平台差异集中在「容器命令在何处执行」一处，不做逻辑分叉。
- **NFR-4**: 所有失败路径必须给出中文、可执行、指向下一步的指引（缺 wheel / 缺镜像 / 缺 podman / 缺 podman-compose / CRLF 骨架 / 端口占用）。
- **NFR-5**: 脚本单一职责、单文件不超过 ~200 行；公共逻辑（日志、路径换算、podman 调用）抽出为 `bin/lib/` 共享片段，禁止在 bash 与 pwsh 之间重复实现同一语义。

## Constraints

- **Technical**: 新应用**禁止**引用 `apps/containers/client/` 与 `apps/containers/shared/` 的任何路径或代码；外部输入仅 `apps/containers/workspace/dist/*.whl` 与 `localhost/jupyter-podman-rootless:latest`；wheel 与镜像归档不入 git。
- **Business**: 交付骨架是客户可见契约，除开发仓库便捷壳表述外不得顺手改动（含不得新增 GPU 覆盖、不得改端口/凭证键）。
- **Dependencies**: 验证依赖本机 WSL 发行版（默认 `podman-machine-default`，可经环境变量覆盖）与其中可用的 podman / podman-compose。

## Assumptions

- 本机已存在 `localhost/jupyter-podman-rootless:latest` 与 `localhost/xmnn-runtime:latest` 镜像（真机 `pack` / `smoke` 验证前提；`build` 重建需联网，作为可选验证）。
- `apps/containers/workspace/dist` 内 whl 版本号可作为交付版本默认值（`1.2.1.dev0`）。
- 交付骨架 8893/2225 端口在做 `smoke` 时可用（若被占用，报错指引由 CLI 输出）。

## Acceptance Criteria

### AC-1: 新应用完全自包含
- **Type**: `rule`
- **Given**: `apps/containers/offline-delivery/` 全量文件
- **When**: 静态检查（`grep -rn` 命中 `jpman_client`、`jpman_common`、`invoke `、`client/`、`shared/`、`overlays/_shared`；并检查 `release/` 内 `../` 引用）
- **Then**: 除文档中「不得依赖」类说明文字外零命中；Containerfile 只 COPY 产品目录内文件
- **Pass Condition**: 检查命令输出为空（或仅命中文档说明行，且逐行确认非真实依赖）
- **Evidence**: 检查命令与原始输出

### AC-2: 交付骨架纯移动
- **Type**: `rule`
- **Given**: 迁移前后同名文件（`xmnnctl`、`xmnnctl.ps1`、`compose.yaml`、`compose.podman.yaml`、`.env.example`、`artifacts/.gitignore`）
- **When**: 逐文件 `git show HEAD:<旧路径>` 与新路径 diff
- **Then**: 上述文件逐字一致（README.md 例外，仅「开发仓库便捷壳」两处表述更新为新应用路径）
- **Pass Condition**: diff 为空（README 仅限声明范围内的段落差异）
- **Evidence**: diff / sha256 对照输出

### AC-3: CLI 与现版语义等价
- **Type**: `rule`
- **Given**: `bin/relpack`（及 `bin/relpack.ps1`）
- **When**: 执行 `stage/build/pack/smoke/version` 并核对产物
- **Then**: 暂存选择顺序、双 tag 规则、CRLF 守卫、归档原子性、`release.json` 字段与 torch 标签回退均与现版一致；`--torch cu130` 时 tag 为 `…:cu130` 且 `:latest` 别名同时存在
- **Pass Condition**: 真机输出与 `release.json` 内容逐字段核对通过
- **Evidence**: 命令输出、`release.json` 内容

### AC-4: client 侧零残留
- **Type**: `rule`
- **Given**: `apps/containers/client/`
- **When**: `grep -rn "xmnnrt\|xmnn-runtime" apps/containers/client` 与 `pytest`（client 全量）
- **Then**: 除 `.agents/CHANGELOG.md` 历史条目外零命中；client 测试全绿，无 `xmnnrt` 相关失败/跳过
- **Pass Condition**: grep 结果符合上述限定，pytest 退出码 0
- **Evidence**: grep 输出、pytest 汇总行

### AC-5: 治理资产同步
- **Type**: `rule`
- **Given**: 组级与应用区路由文件
- **When**: 检查 `apps/containers/AGENTS.md`、`apps/containers/README.md`、`apps/AGENTS.md`、`apps/README.md`、组级 `docs/`、`.gitattributes`
- **Then**: 新应用被登记为成员并出现在路由图/任务路由表；`.gitattributes` 含 `**/relpack` 的 `eol=lf` 且注释不再指向已删除的便捷壳
- **Pass Condition**: 逐文件核对通过；`.trae/specs` 看板刷新后包含本 spec
- **Evidence**: 文件片段、看板条目

### AC-6: 真机端到端可用
- **Type**: `rule`
- **Given**: WSL 内已存在 `localhost/xmnn-runtime:latest`
- **When**: 执行 `bin/relpack pack` 与 `bin/relpack smoke`
- **Then**: `pack` 产出 `release/artifacts/xmnn-runtime-<版本>.tar.gz` 与 `release.json`（sha256/size 与实际一致）；`smoke` 经交付骨架完成 init/up/10 项守卫/down 且退出码 0
- **Pass Condition**: 两条命令退出码均为 0，产物存在且自洽
- **Evidence**: 命令输出、`ls -l` 与 sha256 核对

### AC-7: 静态质量与回归
- **Type**: `rule`
- **Given**: 新应用 `tests/`、`bin/`；client 全量测试
- **When**: 运行新应用 pytest、`bash -n`（所有 shell 脚本）、`.agents/scripts/check-pwsh7-compliance.py`、client pytest
- **Then**: 全部通过；pwsh7 合规检查无新增违规
- **Pass Condition**: 各命令退出码 0
- **Evidence**: 各命令汇总输出

### AC-8: 可扩展性（多产品）
- **Type**: `rubric`
- **Dimension**: 新增第二个交付产品所需改动面
- **Scale**: 1-5
- **Anchors**: 1 = 需要改 CLI 逻辑与多处硬编码；3 = 需要改 CLI 若干处 + 新增文件；5 = 仅新增 `products/<名>/`（含 `product.env`）并在文档中登记，CLI 代码零改动
- **Pass Threshold**: >= 4
- **Evidence**: 「新增产品」步骤文档 + 结构核对（CLI 内不出现 xmnn 常量）

### AC-9: 文档可执行
- **Type**: `rubric`
- **Dimension**: 新应用文档能否让未参与本次迁移的人从零跑通 stage→build→pack→smoke
- **Scale**: 1-5
- **Anchors**: 1 = 只有文件清单；3 = 有命令但缺前置条件/失败处置；5 = 快速开始含前置条件、逐命令预期输出、常见失败与处置，且与 CLI `--help` 一致
- **Pass Threshold**: >= 4
- **Evidence**: `docs/` + `README.md` 内容与 CLI help 对照

## Open Questions

- [ ] 交付骨架 `compose.yaml` 未显式声明 `logging: driver: k8s-file`（内部栈侧曾因宿主默认 journald 导致 `podman logs` 空读）——是否纳入客户契约，本次不改，留作后续提案。
- [ ] 是否把 `--torch cu130` 形态纳入客户交付（C26 结论为「GPU 交付属后续提案」）；GPU 运行期透传随内部栈取消后如何重启。
- [ ] `apps/containers/workspace/dist` 与 `client/workspace/dist` 双目录并存的历史成因需在实现时确认（本 spec 以用户指定的 `apps/containers/workspace/dist` 为唯一 wheel 源）。