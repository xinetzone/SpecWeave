# offline-delivery 变更日志（原子提交汇总）

> 本文件只记录 `apps/containers/offline-delivery` 特有改动；SpecWeave 工作区根级、
> apps/containers 组级、其它成员（jupyter-podman-rootless / client / shared）的改动不在范围内。
> 格式：`日期 | type | 摘要`（type 遵循 Conventional Commits）；每条须可追溯（关联规格或 commit）、
> 关联七概念场景、说明验收点。

## [Unreleased]

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