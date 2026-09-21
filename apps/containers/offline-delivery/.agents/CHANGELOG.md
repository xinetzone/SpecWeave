# offline-delivery 变更日志（原子提交汇总）

> 本文件只记录 `apps/containers/offline-delivery` 特有改动；SpecWeave 工作区根级、
> apps/containers 组级、其它成员（jupyter-podman-rootless / client / shared）的改动不在范围内。
> 格式：`日期 | type | 摘要`（type 遵循 Conventional Commits）；每条须可追溯（关联规格或 commit）、
> 关联七概念场景、说明验收点。

## [Unreleased]

### 2026-09-21 | refactor | 底座/载荷分离：xmnn wheel 安装从镜像构建期拆到交付阶段

**关联七概念场景**：场景3「重构优化」——把频繁变动的载荷与极慢变动的底座解耦，消除「换一个 whl 就要重打整镜像」的重复成本。

**背景与动机（I）**：载荷 wheel（约 177 MB）随每个交付版本变化，而底座依赖面（torch + 20 条运行时依赖）变化极慢；
原设计把 wheel 装入镜像构建期，导致每次换 whl 都要重跑 torch 与依赖安装（首轮联网约 3 分钟、数 GB 网络往返），
且交付包必须整包重发。此外，若把 wheel 安装改到交付期却**不做依赖闭包与守卫分段**，缺失依赖只会在客户运行期以
`ImportError` 暴露（`--no-deps` 会静默掩盖），故本次重构必须同时补齐依赖清单与两段守卫。

**本任务落地**：

- **底座镜像**：`localhost/xmnn-runtime:base-<形态>`（cpu|cu130，**无 `:latest`、不含 xmnn**）＝ cp314 GIL base env +
  torch + 依赖面（`products/xmnn-runtime/deps.txt`，20 条无条件依赖）+ ipykernel + 内核注册脚本 + 守卫脚本；
  构建上下文收敛为产品目录（`Containerfile.xmnn-runtime` + `deps.txt` + `scripts/` + `smoke/`），**`wheels/` 目录删除**。
- **底座守卫**：新增 `smoke/_base_guards.py`（Layer 4，root/devuser 双跑，6 项）：双 ABI / `deps.txt` 逐条核验 /
  `pip check`（放行基镜像既有的 conda×ruamel-yaml 单条冲突）/ torch 形态（marker vs `version.cuda`）/ 内核双可见 /
  **反断言 `import xmnn` 必须失败**。
- **交付侧派生构建**：交付包新增 `release/payload/{Dockerfile,.gitignore,.keep}` 与 `payload/xmnn-*.whl`
  （177 MB，不入 git）；客户 `xmnnctl load` 语义改为「幂等导入底座（按 `release.json.image.id` 比对，已在则跳过）→
  校验载荷 sha256 → 以 `payload/` 为上下文派生构建 `localhost/xmnn-runtime:<交付版本>`
  （`pip install --no-index --no-deps`，载荷守卫与 `pip check` 在 `RUN` 内执行，失败即无 tag）→ 校验 `.env` 版本与清单一致」；
  `smoke`/`version` 改用派生镜像与清单；**`compose.yaml` 逐字未变（对外契约稳定）**。
- **制品与清单**：`bin/relpack` 的 `stage` 目标改为 `release/payload/`；新增 `deps [--write]`（解析 whl
  `Requires-Dist` 无条件项并与 `deps.txt` 比对，**deps 变化必须重发底座**）；`build` 产 `:base-<形态>`；
  `pack` 产 `artifacts/<镜像名末段>-base-<形态>.tar.gz` + **schema v2 `release.json`**
  （`payload{file,version,size_bytes,sha256}` / `image{ref,id,torch_version,torch_flavor,abi}` /
  `archive{file,size_bytes,sha256}`）；`smoke` 改为走交付骨架 `load → up → smoke → down`。
- **文档与治理同步（本切片）**：`AGENTS.md`（项目概述 / 路由树 / P0 约束速览 8→12 条）、`README.md`（命令表 + 快速开始 + 收益口径）、
  `docs/00-overview.md`（双制品流）、`docs/01-quickstart.md`（`deps` 命令 + 失败处置 + 新增「更新交付（只换 whl）」）、
  `rules/delivery-pipeline.md`（§1 契约修订至契约冻结 + 新增 §9-§12）。

**影响（交付骨架契约变化点）**：`release/` 新增 `payload/`（载荷 wheel + 派生 `Dockerfile`）并纳入契约；
`xmnnctl load` 语义从「导入镜像」变为「导入底座 + 派生构建」；`release.json` 升 schema v2（顶层 `version` 为载荷版本，
新增 `payload` 块与双 `sha256`）；底座 tag 不再有 `:latest`；**`compose.yaml` / `xmnnctl` 命令面 / `.env` 键未变**。

**实测事实**：底座镜像 2.47 GB（首轮联网装依赖约 3 分钟）；底座校验 6 项全过、`deps.txt` 20 条逐条 `[OK]`；
载荷守卫 10/10；派生镜像增量约 +0.18 GB、构建 1-3 分钟。收益口径：换 whl 只需重发约 **177 MB 载荷**，
而非约 **1.1 GB 底座归档**（旧口径「4 GB」指 cu130 形态镜像，属误传，不沿用）。

**验收点**：底座守卫 6/6、载荷守卫 10/10、`deps` 一致性校验、`pack` schema v2 清单与归档原子性；
真机端到端结论见统一验证记录（后续统一验证回填实测输出与 `release.json` 核对结论）。

### 2026-09-21 | feat | 应用抽取：客户离线交付链路从 client 迁出为独立应用

**关联七概念场景**：场景3「重构优化」——把寄居在消费端的交付链路还给交付方自持。

**背景与动机（I）**：客户交付物（镜像定义 + 打包器 + `release/` 骨架）原寄居在
`apps/containers/client/overlays/xmnn-runtime/`，打包器 `relpack.py` 位于 `jpman_client`
包内并硬编码 client 根路径，镜像构建依赖 client 的 `overlays/_shared/base-rootless.yaml`
与 invoke 编排内核——「一份客户交付物要拖着整个 client 与 shared 才能构建」。
交付物应独立演进（自有产品参数、版本语义、发布节奏），不应被消费端重构连带影响。

**本任务（Task 1：应用骨架与治理资产）落地**：

- 新建应用根 `apps/containers/offline-delivery/`（目录名**不含 `xmnn`**，为多产品扩展预留）
- `AGENTS.md`：启动协议块（PRIORITY ZERO）+ 项目概述 + 嵌套路由图 + 上下文路由表 + P0 约束速览 8 条
- `README.md`：人类入口（定位、与 client / jupyter-podman-rootless 的关系、快速开始、命令表）
- `.gitignore`：wheel 与镜像归档不入 git（保留 `wheels/.gitignore` 与 `artifacts/.gitignore` 例外）
- `.agents/`：资产容器索引 + 本变更日志 + 唯一规则主题 `rules/delivery-pipeline.md`（8 节）
- `docs/`：`README.md`（索引）+ `00-overview.md`（定位/制品流/边界）+ `01-quickstart.md`（逐命令 + 失败处置 + 新增第二个产品）
- 仓库根 `.gitattributes`：新增 `**/relpack` 与 `**/relpack.ps1` 的 `text eol=lf`，注释由旧便捷壳指向本应用

**验收点**：AC-5（治理资产同步）、AC-9（文档可执行）；规格
[.trae/specs/infra-env/extract-offline-delivery-app/](../../../../.trae/specs/infra-env/extract-offline-delivery-app/spec.md)。

**未跟踪 / 待后续任务完成（本应用当前不可运行）**：

- `bin/relpack` 与 `bin/relpack.ps1`：尚未落盘（并行任务负责），故本次无 `bash -n` / pwsh 解析证据
- `products/xmnn-runtime/`：`product.env`、`Containerfile.xmnn-runtime`、`scripts/`、`smoke/`、
  `wheels/`、`release/` 交付骨架均待迁移（Task 2 / Task 3）
- `tests/`：交付骨架与 CLI 静态守卫测试待新增（Task 5）
- `client/` 侧原实现（`overlays/xmnn-runtime/`、`relpack.py`、`tasks/xmnnrt.py` 等）尚在（Task 6）；
  在此之前 `.gitattributes` 中 `**/xmnnctl` 旧规则仍被 client 侧文件需要，不得删除
- 看板刷新与全量门禁（Task 7 / Task 8）未执行

**待验证**：本文件所列路径在 Task 2/Task 3 落盘前，`docs/01-quickstart.md` 中命令示例不可执行；
Task 8 真机验证通过后须回填 `pack` / `smoke` 实测输出与 `release.json` 核对结论。