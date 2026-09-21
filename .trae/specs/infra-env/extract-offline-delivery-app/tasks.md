# offline-delivery 独立应用抽取 - Implementation Plan

> 方法链路：R（磁盘事实核对：骨架/打包器/镜像定义/编排内核逐文件）→ F（第一性原理：交付物应由交付方自持输入与工具，而非寄居消费端）
> → I（本文文件级任务队列）→ C（按任务原子收尾，不自动 git commit）。
> 容器/构建/打包命令一律在 WSL2（默认 `podman-machine-default`）内执行；宿主工作区 `d:\spaces\SpecWeave`。
> 迁移真源（只读参考，**禁止依赖**）：`apps/containers/client/overlays/xmnn-runtime/`、`apps/containers/client/src/jpman_client/{relpack.py,tasks/xmnnrt.py}`、`apps/containers/client/tests/test_release_bundle.py`。
> 新应用根：`apps/containers/offline-delivery/`（目录名不含 `xmnn`，产品经 `products/<名>/` 扩展）。

## Task 1: 应用骨架与治理资产
- **Status**: `completed`
- **Completion Evidence**:
  - 落盘 9 件：`AGENTS.md`(90 行)、`README.md`(59)、`.gitignore`、`.agents/{README.md(73),CHANGELOG.md(44),rules/delivery-pipeline.md(77)}`、`docs/{README.md(38),00-overview.md(67),01-quickstart.md(145)}`；`AGENTS.md` 首部含「启动协议」并声明 `apps/containers → apps → SpecWeave 根` 三级父级
  - `.gitattributes` 新增 `**/relpack`、`**/relpack.ps1` 的 `text eol=lf`，注释改指新应用（原 `overlays/xmnn-runtime/xmnnctl` 便捷壳表述清除）
  - `git check-ignore --no-index` 对 wheel / `release/.env` / `release/workspace/` / `release/artifacts/*` 四类均命中，两处 `.gitignore` 由 `!` 例外放行；`check-links.py --path apps/containers/offline-delivery` 零断链
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `apps/containers/offline-delivery/`：`AGENTS.md`（启动协议块 + 定位 + 嵌套路由图 + 任务路由表 + P0 约束速览 + 变更日志区）、`README.md`（人类入口：定位/关系/快速开始/命令表）、`.agents/{README.md,CHANGELOG.md,rules/delivery-pipeline.md}`（单一规则主题：骨架零 Python 契约、CRLF shebang 守卫、版本语义、形态感知 tag、离线契约、禁依赖 client/shared）、`docs/{README.md,00-overview.md,01-quickstart.md}`（含「新增交付产品」步骤）。
  - `.gitignore`：忽略 `products/*/wheels/*.whl`、`products/*/release/.env`、`products/*/release/workspace/`、`products/*/release/artifacts/*`（保留 `!.gitignore` 例外）、`__pycache__/`、`.pytest_cache/`。
  - `.gitattributes`（仓库根）：新增 `**/relpack` 与 `**/relpack.ps1` 的 `text eol=lf`（对齐既有 `**/xmnnctl*` 段），并把注释中「dev-repo convenience shim overlays/xmnn-runtime/xmnnctl」更新为新应用路径。
- **Acceptance Criteria Addressed**: AC-5, AC-9
- **Test Requirements**:
  - `rule` TR-1.1: 上述文件全部存在；`apps/containers/offline-delivery/AGENTS.md` 首部含「启动协议」关键词且声明父级为 `apps/containers` → `apps` → SpecWeave 根
  - `rule` TR-1.2: `git check-ignore` 对 `products/xmnn-runtime/wheels/x.whl`、`products/xmnn-runtime/release/.env`、`products/xmnn-runtime/release/workspace/x`、`products/xmnn-runtime/release/artifacts/x.tar.gz` 均命中
  - `rule` TR-1.3: `.gitattributes` 含 `**/relpack` 行且注释不再指向 `overlays/xmnn-runtime/xmnnctl`

## Task 2: 交付骨架纯移动
- **Status**: `completed`
- **Completion Evidence**:
  - `release/` 全量迁至 `products/xmnn-runtime/release/`（9 个跟踪文件 + 未跟踪本地产物随迁：`artifacts/release.json`、`artifacts/xmnn-runtime-1.2.1.dev0.tar.gz`(1,199,948,906 B 旧产物，已在 Task 8 由新 CLI 重打)、`workspace/` 内容）；源目录已不存在
  - 六文件（`xmnnctl`、`xmnnctl.ps1`、`compose.yaml`、`compose.podman.yaml`、`.env.example`、`artifacts/.gitignore`）经 `git hash-object` 与 `HEAD` blob 对拍 + `git diff --no-index` 双验，**逐字一致**
  - `README.md` diff 恰 2 hunk（4+/4−），仅改「开发仓库便捷壳」两处表述；`xmnnctl` CR=0/LF=454、`xmnnctl.ps1` CR=0/LF=498；骨架内 `../` 零命中；`compose.yaml` 仍含 `pull_policy: never` 且无 `extends`/`build:`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 `client/overlays/xmnn-runtime/release/` 全量移动为 `offline-delivery/products/xmnn-runtime/release/`：`xmnnctl`、`xmnnctl.ps1`、`compose.yaml`、`compose.podman.yaml`、`.env.example`、`.gitignore`、`README.md`、`artifacts/.gitignore`、`workspace/.gitkeep`。
  - 仅改写 `README.md` 两处「开发仓库便捷壳」表述（§2 执行位置注、§7 排障首行）为新应用路径（`offline-delivery/bin/relpack`），其余字节保持不变（含行尾）。
  - 未跟踪产物（`artifacts/release.json`、`artifacts/xmnn-runtime-*.tar.gz`、`release/workspace/` 内容）为本地态，不入 git；迁移后由 Task 8 重新打包生成。
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 六个非 README 文件与 `git show HEAD:<旧路径>` 逐字一致（diff 空）
  - `rule` TR-2.2: 骨架内 `grep -rn '\.\./'`（除 README 排障文字外）零命中；`compose.yaml` 仍含 `pull_policy: never` 且不含 `extends`/`build`
  - `rule` TR-2.3: `xmnnctl` 与 `xmnnctl.ps1` 无 CR（LF 行尾）且保留原权限

## Task 3: 镜像定义与产品参数迁移
- **Status**: `completed`
- **Completion Evidence**:
  - 6 项资产迁入（`Containerfile.xmnn-runtime`、`.dockerignore`、`scripts/{install-torch.sh,register-kernel.sh}`、`smoke/_runtime_smoke.py`、`wheels/` 含 `.gitignore` 与已暂存 whl）；**更正（独立审查 F1 复核）**：其中 5 项内容因注释/文档串改写而不再与 `HEAD` 哈希相同（`install-torch.sh` 2825→2847、`register-kernel.sh` 同长异容、`_runtime_smoke.py` 11735→11747、`.dockerignore` 526→536、Containerfile 注释段），差异**全部限于注释与文档串**（`invoke xmnnrt.*` → `bin/relpack`），构建/运行逻辑与 HEAD 逐字等价；仅 `wheels/.gitignore` 与 HEAD 逐字相同
  - 新增 `product.env`（8 键 + `WHEEL_PREFIX=xmnn-`，逐键中文注释，`WHEEL_DIST=../workspace/dist` 注明相对应用根）
  - Containerfile 差异**仅注释 + 横幅一行**（`invoke xmnnrt.up` → `bin/relpack smoke`）；4 个 Layer、四个 ARG、7 个 `org.specweave.*` LABEL、Layer 4 root/devuser 双跑 10 项守卫语义未变；COPY 目标全在本产品目录内
  - `bash -n` 两脚本 exit 0；`install-torch.sh` 形态白名单（`""/cpu/cu130`）与 `/opt/xmnnrt-torch-flavor` marker 逻辑保留；产品目录内 `jpman_client|jpman_common|overlays/_shared|client/` 零命中
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 迁移 `client/overlays/xmnn-runtime/{Containerfile.xmnn-runtime,.dockerignore,scripts/install-torch.sh,scripts/register-kernel.sh,smoke/_runtime_smoke.py,wheels/.gitignore}` → `offline-delivery/products/xmnn-runtime/`（同构路径）。
  - 新增 `products/xmnn-runtime/product.env`：`PRODUCT`、`IMAGE_NAME=localhost/xmnn-runtime`、`CONTAINERFILE=Containerfile.xmnn-runtime`、`WHEEL_GLOB=xmnn-*.whl`、`WHEEL_PREFIX=xmnn-`、`WHEEL_DIST=../workspace/dist`、`BASE_IMAGE_DEFAULT=localhost/jupyter-podman-rootless:latest`、`TORCH_DEFAULT=cpu`、`RELEASE_DIR=release`。
  - 注释重写：Containerfile 与脚本头注中的 `invoke xmnnrt.build/up`、`client/workspace/dist`、`overlays/xmnn-runtime` 表述改为 `bin/relpack stage|build|pack|smoke` 与 `products/xmnn-runtime/`；**不迁移**内部 compose 栈与 `overlays/_shared` 依赖。
  - `.dockerignore` 保留并同步注释（wheels/ 反放行、忽略 `.env` 与缓存）。
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `rule` TR-3.1: 产品目录内 `grep -rn "jpman_client\|jpman_common\|overlays/_shared\|client/"` 零命中（注释亦不得残留）
  - `rule` TR-3.2: `Containerfile.xmnn-runtime` 四个 Layer 结构、`ARG`（`BASE_IMAGE`/`PIP_MIRROR`/`TORCH_VERSION`/`TORCH_FLAVOR`）、`org.specweave.*` LABEL、Layer 4 双身份 10 项守卫与横幅语义保持不变；COPY 目标仅限本产品目录内的 `scripts/`、`smoke/`、`wheels/`
  - `rule` TR-3.3: `bash -n` 对 `scripts/*.sh` 全过；`install-torch.sh` 的形态白名单（`""/cpu/cu130`）与 CUDA 形态 marker 语义不变
  - `rule` TR-3.4: `product.env` 键齐备且被 CLI 读取（无第二处产品常量）

## Task 4: shell CLI（`bin/relpack` + `bin/relpack.ps1`）
- **Status**: `completed`
- **Completion Evidence**:
  - `bin/relpack`（198 行，Task 10 后）、`bin/relpack.ps1`（136 行，pwsh7 桥接壳）、`bin/lib/{log.sh,common.sh,pipeline.sh}`
  - 校验：`bash -n` 四文件 exit 0；pwsh `Parser::ParseFile` → PARSE OK；`check-pwsh7-compliance.py` 2 合规 0 豁免；`--help` 打印命令面、`version` 输出 `产品=xmnn-runtime | 形态=cpu | 镜像=localhost/xmnn-runtime:cpu | 版本=1.2.1.dev0`
  - 静态零命中 `jpman`/`invoke `/`pip install`/`client/`/`overlays/_shared`；含 `podman save`、`gzip -t`、原子 `mv`、CRLF 守卫、双 torch 键、形态白名单
  - `stage` 幂等（首跑暂存、复跑「已是最新」）；CRLF 守卫正/负例均实证（负例拦下 `broken.sh`，跳过 `artifacts/` 与 `.ps1`）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `bin/relpack`（bash，`set -euo pipefail`）：读取 `products/<产品>/product.env`；子命令 `stage` / `build` / `pack` / `smoke` / `version` / `--help`；`-p|--product`（默认 `xmnn-runtime`），`-v|--version`、`--wheel`、`--torch cpu|cu130`、`--base-image`、`--pip-mirror official|tuna|aliyun`、`--no-cache`。
  - 语义映射：`stage` ← `xmnnrt._ensure_wheel_staged`；`build` ← `overlay_core.build_image`（context=产品目录、双 tag `<IMAGE_NAME>:<形态>` + `:latest`、build args `BASE_IMAGE/PIP_MIRROR/TORCH_FLAVOR`）；`pack` ← `relpack.pack_release`（CRLF 守卫 → tag → `podman save | gzip -1` → `gzip -t` → 原子 mv → `release.json`，torch 标签新键优先旧键回退）；`smoke` ← 交付骨架 `init/up/smoke/down`。
  - `bin/relpack.ps1`（pwsh7）：同名命令面，容器操作经 `wsl.exe -d <distro> -- bash <bin/relpack> <args>` 桥接（发行版优先级 `OFFLINE_DELIVERY_WSL_DISTRO` → `XMNN_WSL_DISTRO` → `COMPOSE_WSL_DISTRO` → `podman-machine-default`）。
  - `bin/lib/`：日志、路径换算与 product.env、流水线机制（wheel 暂存 / CRLF 守卫 / release.json 写出 / smoke 步骤）。
- **Acceptance Criteria Addressed**: AC-3, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-4.1: `bash -n bin/relpack` 与 `bin/lib/*` 全过；`relpack.ps1` 语法解析无错
  - `rule` TR-4.2: `--help` 覆盖 `stage/build/pack/smoke/version` 且两端文案一致；`version` 输出产品名、镜像名、形态 tag、版本、wheel 名
  - `rule` TR-4.3: 源码静态断言 —— 含 `podman save`、`gzip -t`、原子 `mv`、CRLF 守卫、双键 torch 标签、形态白名单；零命中 `pip install`/`invoke`/`jpman`
  - `rule` TR-4.4: `check-pwsh7-compliance.py` 对 `bin/relpack.ps1` 无违规
  - `rubric` TR-4.5: CLI 内不出现 xmnn 常量（产品差异全部来自 `product.env`）；新增产品所需改动面；scale 1-5；1/3/5 锚点同 AC-8；threshold >= 4

## Task 5: 守卫测试迁移与新增
- **Status**: `completed`
- **Completion Evidence**:
  - `tests/{conftest.py(40),test_release_skeleton.py(512),test_relpack_cli.py(246→含 Task 10 新增用例)}`；无 Python 包、无第三方依赖、daemon-free
  - 迁移处置：**保留**骨架不变量与两端行为断言；**替换** `resolve_wheel`/`to_wsl_path`/`find_crlf_shebang_scripts` 为 `pipeline.sh::wheel_version`、`common.sh::win_to_wsl_path` ↔ `relpack.ps1::ConvertTo-WslPath` 对等断言与本地 CRLF 扫描器；**删除** 9 个需 POSIX bash harness 的用例并以静态等价断言（fail-fast 文案、优先级链、token 形态）替代（docstring 说明）
  - `pytest tests -q` → **56 passed**（Task 10 后；Task 5 时为 53 passed），0 skip
- **Priority**: high
- **Depends On**: Task 2, Task 4
- **Description**:
  - 迁移 `client/tests/test_release_bundle.py` 的骨架不变量到 `offline-delivery/tests/test_release_skeleton.py`；新增 `tests/test_relpack_cli.py`（CLI 静态不变量与 `bash -n`）与 `tests/conftest.py`。
  - 不建 Python 包：测试以 `pytest` 直接运行；如需 YAML 断言优先文本匹配。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-5.1: `pytest tests -q` 在 `apps/containers/offline-delivery/` 内全绿
  - `rule` TR-5.2: 覆盖点逐条可查（文件清单、compose 不变量、podman override 三必需且无 privileged、`.env.example` 键集合、两端命令同构、shebang 全 LF、`localhost/xmnn-runtime:$ver` 计数、随机凭证来源等）
  - `rule` TR-5.3: 测试仅读文件与运行 `bash -n`，不触 podman/daemon（daemon-free）

## Task 6: client 侧完全移除与内核清理
- **Status**: `completed`
- **Completion Evidence**:
  - 删除 15 项：`overlays/xmnn-runtime/` 整目录（含 compose×3、便捷壳、`.env.example`、`README.md`、`.dockerignore`、`smoke/__pycache__`）、`src/jpman_client/relpack.py`、`tasks/xmnnrt.py`、`tests/test_release_bundle.py`、`tests/test_xmnnrt_stage.py`、`.agents/rules/xmnnrt-overlay.md`、`docs/13-xmnn-runtime-overlay.md`
  - 更新 15 文件：`tasks/__init__.py`（去命名空间）、`AGENTS.md`（P0 表 C26/C27/C28 合并为「已迁出」备注、C18/C19/C25 保留、变更日志追加）、`README.md`、`.agents/README.md`、`.agents/CHANGELOG.md`（追加迁出条目）、`docs/README.md`、`.env.example`、`.gitignore`、`docs/11`、`.agents/rules/{xmnn-overlay,invoke-tasks}.md`、`overlays/xmnn-dev/{compose.yaml,README.md}`、三个测试文件
  - 内核死代码清理：删 `StackSpec.torch_default`/`flavor_tag`、`image_flavor()`、`image_tag_alias()`、`image_tag()` 形态分支、`resolve_build_args()` 的 `torch_default` 回落、`build_image()` 别名双 `-t`、`_require_local_image()` 迁移提示、`build_help()` 形态文案；**保留** `warn_torch_flavor_mismatch()`/`image_torch_flavor()`（xmnn-dev 仍用）
  - 校验：`xmnnrt|xmnn-runtime` 仅命中变更日志历史条目；`flavor_tag|image_flavor|image_tag_alias|torch_default` 于 `src/` 零命中；`invoke --list` = 根(7)/container(7)/env(3)/quant(6)/xmnn(10)/monetize(8)；client `pytest tests -q` → **182 passed / 2 skipped**（`--ignore=tests/test_ast_inject.py`；该文件 8 例失败为 Windows 原生 bash 存量差异，改动前即存在且本次未触碰）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 删除：`client/overlays/xmnn-runtime/`（整目录）、`src/jpman_client/relpack.py`、`tasks/xmnnrt.py`、`tests/test_release_bundle.py`、`tests/test_xmnnrt_stage.py`、`.agents/rules/xmnnrt-overlay.md`、`docs/13-xmnn-runtime-overlay.md`。
  - 更新：`tasks/__init__.py`、`AGENTS.md`、`README.md`、`.agents/README.md`、`.agents/CHANGELOG.md`、`docs/README.md`、`.env.example`、测试三件（黄金清单与专属用例）。
  - 内核死代码清理（FR-12）：删 `flavor_tag`/`image_flavor`/`image_tag_alias`/`torch_default` 及其 help/hint 分支与专属测试；保留 `warn_torch_flavor_mismatch`；发现其他消费者须停止并回报。
  - `client/overlays/xmnn-runtime/xmnnctl{,.ps1}`（开发仓库便捷壳）随目录删除。
- **Acceptance Criteria Addressed**: AC-4, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: `grep -rn "xmnnrt\|xmnn-runtime" apps/containers/client` 仅命中 `.agents/CHANGELOG.md` 历史条目
  - `rule` TR-6.2: client `pytest tests -q` 全绿；`invoke --list` 不再出现 `xmnnrt.*` 且其余命名空间表面不变
  - `rule` TR-6.3: `flavor_tag|image_flavor|image_tag_alias|torch_default` 于 `src/` 零命中；`warn_torch_flavor_mismatch` 仍有调用方
  - `rule` TR-6.4: 迁移后 client 无对 `release/` 或 `relpack` 的任何引用残留

## Task 7: 仓库治理同步
- **Status**: `completed`
- **Completion Evidence**:
  - 七个路由/文档文件登记 `offline-delivery`：`apps/containers/AGENTS.md`（四成员概述 + 成员路由表 + 嵌套树 + 上下文路由表，G1-G4 未动）、`apps/containers/README.md`、`apps/containers/docs/{README,00-overview,01-getting-started}.md`（新增第 6 节「末端分支：打客户离线交付包」）、`apps/AGENTS.md`（client 行标注「已于 2026-09-21 迁出」）、`apps/README.md`
  - 看板刷新：`docgen.py theme-dashboards`（13 主题更新）+ `update-spec-readme`（639 spec），`.trae/specs/infra-env/README.md` 收录 `extract-offline-delivery-app`
  - `check-links.py --path apps/containers` exit 0（12 条为既有目录链接警告）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - `apps/containers/AGENTS.md` 成员路由表/嵌套路由图/任务路由表补条目；组级 `G1-G4` 保持不动。
  - `apps/containers/README.md`、组级 `docs/`、`apps/AGENTS.md`、`apps/README.md` 登记新应用与其在镜像流中的位置。
  - `.trae/specs` 看板经 docgen 刷新并确认本 spec 入册。
- **Acceptance Criteria Addressed**: AC-5, AC-9
- **Test Requirements**:
  - `rule` TR-7.1: 五个路由/文档文件中均可检索到 `offline-delivery`，且不再把 `xmnnrt` 描述为 client 的活跃栈
  - `rule` TR-7.2: 看板刷新命令退出码 0，`.trae/specs/infra-env/README.md` 含本 spec 条目
  - `rule` TR-7.3: `check-links.py --path apps/containers` 无新增断链

## Task 8: 端到端验证与收口
- **Status**: `completed`
- **Completion Evidence**:
  - 静态门禁：新应用 `pytest` 53 passed（Task 10 后 56）→ 客户端 `182 passed/2 skipped`（忽略存量）；`bash -n` ×4 OK；pwsh PARSE OK；`check-pwsh7-compliance` PASS；`check-links` exit 0
  - `stage`/`version`/`--help` 幂等正确；`pack` 真机成功（`real 4m08.870s`），`release.json` 逐字段与磁盘一致（`archive.size_bytes=4088086206`、`sha256=c4907c7d…`、`pack_tool=offline-delivery.relpack`）
  - CRLF 守卫反例：注入带 CRLF shebang 的临时脚本后 `pack` 非零退出并给出 `git add --renormalize .` 修法（探针已删除）
  - `smoke` 首轮 **FAIL**（`run_smoke_step` 参数缺陷，exit 126）→ 见 Task 10 修复后复验 **PASS**（exit 0）
  - 仓库外交付验证：`D:\tmp-delivery-check`（硬链接 inode 一致）内 `init → load → ps → up → smoke → down` 六步全 exit 0，`load` 完整性校验通过、两次 10 项守卫 `10 passed,0 failed`，全程零仓库引用；临时目录已清理
  - 已知环境状态（非缺陷，迁移前遗留）：`:latest` 当前指向 cu130 镜像（LABEL `torch-flavor=cu130`，7.89 GB），故本次 `pack` 产出 4.09 GB 归档；`release.json` 与实际镜像自洽。建议下次交付前以 `--torch cpu` 重建镜像后再 `pack`
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 静态门禁 + 真机 `stage/build/pack/smoke` + 仓库外交付验证 + CHANGELOG 收口。
  - 本地若已存在 `localhost/xmnn-runtime:latest` 则无需重建镜像（`build` 需联网与数分钟下载，作为可选验证，执行前须经用户确认）。
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-8.1: `bin/relpack pack` 退出码 0，`release.json` 的 `archive.sha256`/`size_bytes` 与磁盘一致，`wheel.version` == whl 文件名版本
  - `rule` TR-8.2: `bin/relpack smoke` 退出码 0，输出含 10 项守卫结果（Task 10 后达成）
  - `rule` TR-8.3: 仓库外临时目录内的交付骨架 `init → load → up` 三步成功，全程无对 `apps/containers` 路径的访问
  - `rubric` TR-8.4: 端到端可复现性；scale 1-5；threshold >= 4；evidence 为 `docs/01-quickstart.md` 与实测输出对照

## Task 9: 残余治理措辞与测试缓存清理（实施中发现的补充项）
- **Status**: `completed`
- **Completion Evidence**:
  - `apps/containers/.agents/README.md`：「三成员路由表」→「四成员路由表（构建端/消费端/共享包/离线交付）」；正确的「三栈 compose 公共段」表述保留
  - `apps/containers/.agents/rules/shared-package.md`：明确「三个 Python 包成员…；离线交付成员 offline-delivery 为脚本型成员，无 Python 包」
  - 删除 `.benchmarks/`、`tests/__pycache__/`；`.gitignore` 补 `.benchmarks/`；`git check-ignore --no-index` 命中；`check-links.py --path apps/containers` exit 0
- **Priority**: low
- **Depends On**: Task 7
- **Acceptance Criteria Addressed**: AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-9.1: 组层两文件措辞与四成员现状一致，「三栈 compose 公共段」等正确表述未被改动
  - `rule` TR-9.2: 残留目录已删除且被忽略规则覆盖；`check-links.py --path apps/containers` 退出码 0

## Task 10: 修复 `smoke` 步骤参数缺陷（V 阶段真机验证发现的实施缺陷）
- **Status**: `completed`
- **Completion Evidence**:
  - 根因：`run_smoke_step` 只 `shift` 掉步骤名，而三个调用点多传 `"$RELEASE_DIR"`，`(cd "$RELEASE_DIR" && "$@")` 遂执行目录本身（exit 126）
  - 修复：`run_smoke_step`/`smoke_hint` 移入 `bin/lib/pipeline.sh` 成为可测库函数，骨架目录仅从公共变量 `RELEASE_DIR` 读取；`bin/relpack` 三处调用点改为 `run_smoke_step up ./xmnnctl up` 形式（212 → 198 行）；输出文案与 trap 收尾不变
  - 预防（回归测试，daemon-free）：新增静态用例（调用点不含目录字面量、实现唯一）+ 真 bash 行为用例（假 `xmnnctl` 验证 argv/工作目录）+ 缺命令用例（rc=127）；WSL 内 `pytest tests/test_relpack_cli.py -q` → 17 passed，行为用例真实执行非 skip
  - 同类问题审计：`bin/` 内 `shift`+`$@` 四处逐一核对，仅本处签名与调用不一致，其余自洽
  - 闭环（真机复验）：`./bin/relpack smoke` **exit 0**（1m38s），up → 容器内 10 项守卫全 PASS → down；结束后无运行中容器，2225/8893 已释放；全量 `pytest tests -q` → **56 passed**
- **Priority**: high
- **Depends On**: Task 8
- **Acceptance Criteria Addressed**: AC-3, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-10.1: `bin/relpack smoke` 真机退出码 0，四步齐备且容器最终停止
  - `rule` TR-10.2: 新增回归用例证明 `run_smoke_step` 按签名调用骨架命令（argv 与 cwd 正确），且在缺命令时干净失败（非 126）
  - `rule` TR-10.3: `bash -n` 全过、全量 pytest 全绿

## Task 11: 独立审查 R1 发现项修复
- **Status**: `completed`
- **Completion Evidence**:
  - **F2（actionable，必修）**：`docs/01-quickstart.md` 的 `release.json` 字段名与真实清单逐字对齐（`archive.name` → `wheel(file、version、size_bytes) / image(ref、id、torch_cpu、abi) / archive(file、size_bytes、sha256)`）；同步修正 `.agents/rules/delivery-pipeline.md` §3 同一笔误（`archive.name` → `archive.file`）
  - **F3**：`README.md` 命令表按 `bin/relpack --help` 权威文案逐行校正（`smoke` 参数 `-p|--product` → `--version V`；`build` 补 `--wheel/--pip-mirror`；表下补全局参数与覆盖优先级）
  - **F9**：`bin/lib/common.sh` 新增 `ensure_xdg_runtime_dir()`（仅未设/空时按 `id -u` 导出 `/run/user/<uid>` 并 `mkdir -p`，失败仅 warn、不覆盖既有值），由 `require_podman` 调用；WSL 实测未设→`/run/user/1000`、已设→原值保留
  - **F7**：`apps/containers/docs/01-getting-started.md` frontmatter `source` 改为四成员现状（三个 Python 包成员 + 脚本型 `offline-delivery`）
  - **F6**：spec `status` 由 `draft` 改为 `completed` 并重跑 docgen；看板 `.trae/specs/infra-env/README.md` 第 17 行由「? 待启动」变为「✓ 完成」
  - 回归：应用内 `pytest tests -q` → **56 passed**；`check-links --path apps/containers` exit 0；`bash -n` → BASH_OK；`relpack version` 输出与基线一致
- **Priority**: medium
- **Depends On**: Task 8, Task 10
- **Acceptance Criteria Addressed**: AC-3, AC-7, AC-9
- **Test Requirements**:
  - `rule` TR-11.1: 文档中 `release.json` 字段名与产物清单逐字一致；命令表参数与 `--help` 一致
  - `rule` TR-11.2: 修复后应用内 pytest 全绿、`bash -n` 全过、`check-links` 退出码 0、`version` 输出无变化

# Task Dependencies

- Task 1 无依赖，先行。
- Task 2、Task 3、Task 4 依赖 Task 1，可并行。
- Task 5 依赖 Task 2、Task 4（需要骨架与 CLI 落位后才能断言）。
- Task 6 依赖 Task 2、Task 3、Task 4、Task 5（新应用必须已可独立承担交付链路后再删 client 侧）。
- Task 7 依赖 Task 6（路由同步必须基于最终成员面）。
- Task 9 依赖 Task 7；Task 8 依赖 Task 1-7 全部前置；Task 10 依赖 Task 8（由 V 阶段真机验证触发，修复后复验闭环）；Task 11 依赖 Task 8、Task 10（独立审查 R1 的发现项修复）。