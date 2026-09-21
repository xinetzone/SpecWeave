---
id: "offline-delivery-delivery-pipeline"
title: "离线交付流水线硬约束"
source: "AGENTS.md#P0 约束速览"
---
# 离线交付流水线硬约束

> 唯一规则主题：`apps/containers/offline-delivery` 的交付流水线（stage → deps → build → pack → smoke）。
> 命令面与语义以 `bin/relpack` / `bin/relpack.ps1` 与 [AGENTS.md](../../AGENTS.md) 为准。

## §1 交付骨架对外契约冻结与零 `../` 纪律

- `products/<产品>/release/` 是**客户可见契约**：客户侧仅需 Podman/Docker + 骨架本身，零 Python、零联网、零仓库外引用。
- **契约面 = 逐字不变的三项**：`compose.yaml`（及 `compose.podman.yaml`）文件内容不变、`xmnnctl` 命令面不变、
  `.env` 键不变；不得在交付链路中顺带改端口、改凭证键或调整命令语义。
- **契约内新增的载荷目录**（2026-09-21 起）：`release/payload/`（`payload/Dockerfile` + 载荷 `*.whl` +
  `.gitignore`/`.keep`）属客户可见契约的一部分——`payload/Dockerfile` 决定客户侧派生构建行为，
  改动（含安装参数、守卫调用顺序）等同契约变更，须同步骨架 `README.md`、本文档与 `docs/`。
- **契约内新增的守卫脚本**：构建期底座守卫 `smoke/_base_guards.py`（6 项）与交付期载荷守卫
  `smoke/_runtime_smoke.py`（10 项）随底座镜像下发、由派生构建调用，同属交付行为契约；守卫项增删
  等同契约变更（同时影响客户文档中「10 项守卫」的对外口径）。
- 骨架内**禁止**出现指向仓库其他文件的相对路径（`../`）；`compose.yaml` 不得出现 `extends` 或 `build`
  （镜像一律来自本地归档与本地派生构建，`pull_policy: never`）。
- 历史沿革：骨架自 `client/overlays/xmnn-runtime/` 迁入时按「纯移动」纪律逐字搬运（仅允许改写「开发仓库便捷壳」
  表述）；本条纪律改为契约冻结后，仍需改骨架时按契约变更处理——同步骨架 `README.md`、本文档与 `docs/`，并补守卫测试。
- 违反后果：客户拿到包后无法在无仓库环境下启动。改骨架前先读骨架自身的 `README.md` 与上文契约。

## §2 CRLF shebang 守卫（`pack` 前置 fail-fast）

- 无扩展名的 shebang 脚本（`xmnnctl`、`bin/relpack`、`bin/lib/*`）一旦被 CRLF 检出，
  Linux/WSL 首行报 `'/usr/bin/env: bash\r': No such file or directory`；内核先解析 shebang，脚本内自救无效。
- 守卫位置：`pack` **在导出归档之前**扫描骨架与 CLI 内所有 shebang 脚本，命中 CR 立即非零退出，
  **不产出坏字节**（绝不先打包再报错）。
- 修法（唯一正确路径）：`git add --renormalize .`（依赖仓库根 `.gitattributes` 中
  `**/relpack`、`**/relpack.ps1`、`**/xmnnctl`、`**/xmnnctl.ps1` 的 `text eol=lf` 显式规则）。
- 新增无扩展名 CLI 时必须同步在根 `.gitattributes` 增一行 `text eol=lf`，否则 `text=auto` 会在
  Windows 检出时写回 CRLF。

## §3 版本语义

- 交付版本默认取**暂存载荷 wheel 的版本**（从 `xmnn-<版本>-cp314-...whl` 文件名解析，如 `1.2.1.dev0`），
  也是客户侧派生镜像的 tag（`<IMAGE_NAME>:<交付版本>`，与骨架 `.env` 的 `XMNN_VERSION` 同值）。
- GA/正式交付必须用 `pack --version V` **显式指定**，不依赖 wheel 名推断（避免 dev 后缀流入客户交付）。
- 同一载荷版本只能对应一份清单；归档属于**底座**、不以交付版本命名（固定
  `<镜像名末段>-base-<形态>.tar.gz`，底座可跨交付版本复用）；`release.json` 的 `version` /
  `payload.version` / `payload.file` 三者必须自洽，`archive.file` 必须与 `image.ref` 的形态一致。

## §4 形态感知 tag（底座 `<IMAGE_NAME>:base-<形态>`，无 `:latest`）

- `build` 只产出**单一形态感知 tag** `${IMAGE_NAME}:base-<形态>`（形态白名单仅 `cpu|cu130`，缺省来自
  `products/<产品>/product.env` 的 `TORCH_DEFAULT`；`--torch` 单次覆盖同时改变 tag）。
- **禁止给底座打 `:latest`**：cpu 与 cu130 是互斥形态，共用别名会让后构建者静默覆盖前者的语义；
  镜像 tag 的内容即身份。
- 交付镜像 tag `${IMAGE_NAME}:<交付版本>` 由**客户侧派生构建**时下发（`xmnnctl load`），与本应用的
  `build`/`pack` 无关；底座与交付镜像因此是两条独立 tag 线。
- 底座身份以 `release.json.image.id` 为准（客户 `load` 据此判断「本机已有同一底座」而跳过导入）。

## §5 归档原子性

- 导出链固定：`podman save <底座 tag>` → `gzip -1` → `gzip -t` 校验 → **原子 `mv`** 落盘到 `release/artifacts/`。
- 先写临时文件、校验通过再 `mv`：任何中断都只能留下临时文件，**绝不在交付目录留截断归档**。
- `release.json` 中的 `archive.sha256` / `archive.size_bytes` 必须取自校验后的最终文件；
  `payload.sha256` 取自暂存载荷 wheel（`pack` 时计算），二者共同构成客户 `load` 的双校验基线。

## §6 `release.json` 字段契约（schema v2）与 torch 标签双键回退

- 字段集：`schema_version`（`"2"`）/ `product` / `version`（顶层=**载荷版本**）/ `payload`
  （`file`、`version`、`size_bytes`、`sha256`）/ `image`（`ref`、`id`、`torch_version`、`torch_flavor`、`abi`）/
  `archive`（`file`、`size_bytes`、`sha256`）/ `built_at` / `source_commit` / `pack_tool`；
  `pack_tool` 为本应用标识 `offline-delivery.relpack`。
- schema v1 → v2 的变化：`wheel` 块更名并补齐 `sha256`（`payload`）、`image` 新增 `torch_flavor` 并
  以 `torch_version` 取代 `torch_cpu`；客户侧骨架按 schema v2 读取（旧清单缺 `payload` 块时直接拒绝，
  提示改用与交付包成套的新版 `xmnnctl`）。
- torch 版本读取顺序：镜像 LABEL `org.specweave.torch-version`（新键）**优先**，
  缺失时回退 `org.specweave.torch-cpu`（旧键）；两者皆缺时如实记 `null` 并告警，**不得臆测**。
  形态取 LABEL `org.specweave.torch-flavor`，缺失记 `null`。
- 改字段属客户契约变更：须同步骨架 `README.md`、本文档与 `docs/`，并补守卫测试。
  读取纪律见 §12。

## §7 禁依赖 `client` / `shared`；外部输入仅两项

- 本应用**禁止**引用 `apps/containers/client/` 与 `apps/containers/shared/` 的任何路径或代码
  （含 `overlays/_shared`、`jpman_client`、`jpman_common`、`invoke`）。
- 外部输入仅：① `../workspace/dist/<WHEEL_GLOB>`（预构建**载荷** wheel，`stage` 暂存进
  `release/payload/` 随交付包发出，**不进底座构建上下文**）；② 基镜像 `BASE_IMAGE_DEFAULT`
  （`localhost/jupyter-podman-rootless:latest`，由 `jupyter-podman-rootless` 应用产出，作为底座 `FROM`）。
- 产品差异（镜像名、Containerfile 名、wheel glob、wheel 源目录、基镜像默认、torch 缺省、骨架目录名）
  **只允许**写在 `products/<产品>/product.env`；CLI 内不得内嵌 `xmnn` 等产品常量。
- 新增第二个交付产品 = 只新增 `products/<名>/`（含 `product.env`、`deps.txt` 与
  Containerfile/脚本/冒烟/`release/`（含 `payload/`））并在文档登记，**CLI 代码零改动**。

## §8 Windows 一律 pwsh7，容器命令经 `wsl.exe` 桥接

- Windows 原生一律使用 `bin/relpack.ps1`（pwsh 7.4+）；**禁止** Windows PowerShell 5.1。
- 跨平台差异只在「容器命令在何处执行」一处：pwsh 版把容器子命令经
  `wsl.exe -d <发行版> -- bash <bin/relpack> <args>` 桥接给 bash 版，**不做逻辑分叉**。
- WSL 发行版优先级：`OFFLINE_DELIVERY_WSL_DISTRO` → `XMNN_WSL_DISTRO` → `COMPOSE_WSL_DISTRO` → `podman-machine-default`。
- 宿主侧参数校验、日志与失败指引须与 bash 版同形；`.ps1` 提交前须过 `.agents/scripts/check-pwsh7-compliance.py`。

## §9 底座与载荷分离

- **底座**（`<IMAGE_NAME>:base-<形态>`，厂商侧 `build` 产出）：cp314 GIL base env + torch +
  `deps.txt` 依赖面 + ipykernel + 内核注册 + 底座守卫；构建上下文 = 产品目录
  （`Containerfile.*` + `deps.txt` + `scripts/` + `smoke/`），**不再包含 wheel 输入**。
- **载荷**（xmnn wheel，约 177 MB）：由 `stage` 暂存进 `release/payload/`，随交付包发出；
  客户侧 `xmnnctl load` 用 `payload/Dockerfile` 派生构建 `<IMAGE_NAME>:<交付版本>` 装入。
- **分离的红线**：底座内**绝不安装 xmnn**——底座守卫以反断言（两个 env 的 `import xmnn` 必须失败、
  site-packages 无 `xmnn*` 残留）硬失败兜底；底座若混入载荷，「底座可跨交付版本复用」的定位即失效，
  且错版会被载荷安装的 `--no-deps` 静默掩盖。
- **为什么拆**：载荷随每个交付版本变化而依赖面变化极慢，拆开后同一底座可派生多个交付版本；
  代价是客户侧 `load` 需要镜像构建能力（本地派生，增量约 0.18 GB、约 1-3 分钟，全程离线）。
- **对外契约不变**：`compose.yaml` 逐字未变，`up` 仍以 `.env` 的 `XMNN_VERSION` 为镜像 tag
  （该 tag 现由客户侧派生而存在，语义与 `down`/`ps`/`logs` 一致）。

## §10 依赖闭包与 `deps.txt`

- `products/<产品>/deps.txt` 是**底座依赖面的唯一事实源**：内容为载荷 wheel `METADATA` 中
  `Requires-Dist` **不含分号**的条目（无环境 marker、无 extra 的无条件运行时依赖）；`torch` 不在清单内
  （由 Containerfile Layer 1 精确 pin）。
- 生成/校验命令：`bin/relpack deps --write`（重写清单，保留头部注释块）/ `bin/relpack deps`（只校验）；
  差异清单格式为 `<` 仅 `deps.txt`、`>` 仅载荷 whl。
- **改则重发底座**：依赖面变化（新增/升级/删除依赖）必须 `deps --write` → `build` → 重新 `pack`，
  否则产出的交付包只能在客户运行期以 `ImportError` 暴露问题。
- **fail-fast 位点**：`deps` 命令与 `pack` 前置守卫共用同一校验（不一致即非零退出，并打印
  「对齐依赖集 → 重建底座 → 重新 pack」三步修法）；`smoke` 亦经交付骨架的派生构建覆盖该面。
- **`--no-index --no-deps` 的前提**：派生构建不做任何依赖解析与补装，其正确性完全由「底座已按
  `deps.txt` 铺满依赖面」保证；该前提一旦被破坏，故障不在构建期而在客户运行期。
- 缺少 `unzip`/`bsdtar`（无法读 wheel 元数据）时**只告警并跳过校验**（`[WARN]`，返回码 2）：
  既不静默宣称一致，也不硬阻断流水线。

## §11 守卫分段（构建期底座守卫 / 交付期载荷守卫）

- **构建期（厂商侧）**：`smoke/_base_guards.py` 由 `build` 的 Layer 4 执行（root + devuser 双跑），
  6 项：双 ABI（base cp314 GIL / main cp314t）、`deps.txt` 逐条已装、`pip check` 无**新**冲突、
  torch 形态与实物一致（marker vs `version.cuda`）、内核双可见、**反断言载荷未安装**；任一失败即构建失败。
- **交付期（客户侧）**：`smoke/_runtime_smoke.py`（10 项）与 `pip check` 在 `payload/Dockerfile` 的
  **`RUN` 内**执行（root + devuser 双跑），任一不过即构建中止、**不产出 tag**——客户机上不会出现半成品镜像。
- `pip check` 判据必须**收窄到载荷相关冲突**（以 `xmnn` 开头的冲突行）：基镜像自带
  `conda`×`ruamel-yaml` 元数据冲突与载荷无关，若要求整体 exit 0，派生构建会在任何客户机上 100% 失败；
  该既有债务在底座守卫中同样按逐行模式放行。
- 分段职责：底座守卫拦「底座缺陷」（依赖面缺失、形态错配、载荷误入），载荷守卫拦「载荷缺陷」
  （装载后导入/ABI/内核侧行为）；两者不可互相替代，也不得合并到同一阶段。
- 守卫项增删属交付契约变更（见 §1）：须同步骨架 `README.md`、`docs/` 与守卫测试。

## §12 清单 schema v2 与双 `sha256` 解析纪律

- schema v2 的 `payload` 与 `archive` **两个块都含 `sha256` 键**：抓「全局第一个 sha256」的写法必然张冠李戴
  （把底座归档摘要当成载荷摘要，或反之）——读取方（客户骨架 `xmnnctl`、校验脚本、文档示例）必须
  **按块定向取值**（`payload.sha256` 校验 `payload/` 内 wheel，`archive.sha256` 校验 `artifacts/` 内底座归档）。
- 块序固定为 `payload` → `image` → `archive` 且缩进 2 空格：便于人工对拍，但**不得**据此把位置当契约
  （读取一律按块名）。
- `image.id` 是底座的幂等凭据：客户 `load` 比对本机镜像 Id，相同即跳过归档导入；归档与清单 Id 不配套时
  必须拒绝执行，不得静默继续。
- 顶层 `version` 是**载荷版本**（= 派生镜像 tag = `.env` 的 `XMNN_VERSION`），`payload.version` 应与之
  一致；`archive.file` 与 `image.ref` 描述底座形态，不承载交付版本。