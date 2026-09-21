# offline-delivery - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文（含首部「启动协议」四个字）
> 步骤 2：确认父级工作区 — 本应用是 SpecWeave apps/containers/ 下的独立交付应用：
>         ../AGENTS.md（组级路由）、../../AGENTS.md（apps 应用区入口）、
>         ../../../AGENTS.md（SpecWeave 根契约）、../../.agents/（组级 AI 资产容器）
> 步骤 3：文档边界 — 对外人类可读文档唯一入本应用 docs/（docs/README.md 为索引入口）；
>         .agents/ 只放 AI 资产；禁止向 .agents/docs/ 写入任何产出物（该路径已废止）
> 步骤 3.5：自检 — 逐项勾选：
>   □ 已完成内容敏感度预检（本应用=公开开源代码；产出物落本应用 docs/ 或应用目录内，
>     禁止向 .agents/docs/ 写入任何产出物）
>   □ 父级 AGENTS.md 已回读磁盘原文（启动协议步骤 1.1），与系统注入一致
>   □ 改动涉及客户交付骨架（release/）时已加载 .agents/rules/delivery-pipeline.md §1
>   □ 未把本应用规则/文档复制到父级组层（组层反双写纪律 G4）
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 **apps/containers/offline-delivery（厂商侧离线交付链路）** 的应用级路由入口，
> 只承载本应用特有事实；未覆盖的规则逐级回退父级（见「上下文路由表」末两行）。

## 项目概述

- **应用性质**：厂商侧**离线交付链路**——把预构建 wheel 装入运行时镜像，再打包成客户可自持的离线交付物
- **能力面**：`stage`（暂存 wheel）→ `build`（构建运行时镜像）→ `pack`（导出离线归档 + 校验清单）→ `smoke`（经交付骨架端到端验证）；日常运行与排障直接使用交付骨架自带的 `xmnnctl` / `xmnnctl.ps1`
- **产物**：① 客户 `release/` 交付骨架（零 Python、零仓库外引用）；② `release/artifacts/xmnn-runtime-<版本>.tar.gz` + 同目录 `release.json`
- **外部输入（仅两项）**：`../workspace/dist/xmnn-*.whl`（预构建 wheel）与基镜像 `localhost/jupyter-podman-rootless:latest`
- **工具链**：`bin/relpack`（bash，WSL/Linux/macOS）+ `bin/relpack.ps1`（pwsh7，Windows 原生经 `wsl.exe` 桥接）；**零 Python**，不引入 pip / invoke / podman-py
- **产品分层**：应用工具（`bin/`）+ 多产品（`products/<产品名>/`）；首个产品 `products/xmnn-runtime/`，产品参数单一事实源为 `products/<产品>/product.env`
- **禁止依赖**：`apps/containers/client/` 与 `apps/containers/shared/` 的任何路径或代码
- **父级工作区**：[../AGENTS.md](../AGENTS.md)（组级）→ [../../AGENTS.md](../../AGENTS.md)（apps 区）→ [../../../AGENTS.md](../../../AGENTS.md)（根契约）
- **AI 资产容器**：[.agents/](.agents/README.md)（仅一个规则主题 `rules/delivery-pipeline.md`）
- **人类文档**：[docs/](docs/README.md)（索引 + 概述 + 快速开始）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、七概念指令）
  └─ apps/AGENTS.md（应用区入口路由）
       └─ apps/containers/AGENTS.md（组级路由入口，仅承载跨成员事实）
            └─ apps/containers/offline-delivery/AGENTS.md（本文件 = 应用级路由入口）
                 ├─ README.md                        ← 人类入口：定位、快速开始、命令表
                 ├─ docs/                            ← 人类可读文档（索引 + 2 篇）
                 │    ├─ README.md                   ← 文档索引
                 │    ├─ 00-overview.md              ← 定位 / 制品流 / 与组内其它应用边界 / 目录结构
                 │    └─ 01-quickstart.md            ← 前置条件 + 逐命令 + 失败处置 + 新增第二个产品
                 ├─ .agents/                         ← 本应用 AI 资产容器
                 │    ├─ README.md                   ← 资产索引 + 父级回退链
                 │    ├─ CHANGELOG.md                ← 应用变更日志（原子提交汇总）
                 │    └─ rules/delivery-pipeline.md  ← 唯一规则主题：离线交付流水线硬约束（8 节）
                 ├─ bin/                             ← relpack（bash）+ relpack.ps1（pwsh7）工具链入口
                 ├─ products/<产品名>/               ← 单产品全部资产；product.env 为参数单一事实源
                 │    └─ xmnn-runtime/               ← 首个产品：product.env + Containerfile + scripts/ + smoke/ + wheels/ + release/
                 └─ tests/                           ← 交付骨架与 CLI 静态守卫测试（pytest，不建 Python 包）
```

**嵌套优先原则**：进入 `products/<产品>/` 后仍以本文件为最近入口；未覆盖规则按 本应用 → apps/containers → apps → SpecWeave 根 逐级回退。

## 上下文路由表（任务类型 → 入口）

| 任务类型 | 必读入口 |
|---------|---------|
| 新增第二个交付产品 | [docs/01-quickstart.md](docs/01-quickstart.md)（「新增第二个交付产品」）+ [.agents/rules/delivery-pipeline.md](.agents/rules/delivery-pipeline.md) §7 |
| 改镜像定义与 Containerfile | `products/xmnn-runtime/product.env` + `products/xmnn-runtime/Containerfile.xmnn-runtime` + 本文件「P0 约束速览」 |
| 改打包 CLI（`bin/relpack*`） | [.agents/rules/delivery-pipeline.md](.agents/rules/delivery-pipeline.md) §2-§6（CRLF 守卫/版本语义/形态 tag/归档原子性/release.json） |
| 改交付骨架（客户契约，`release/`） | [.agents/rules/delivery-pipeline.md](.agents/rules/delivery-pipeline.md) §1（纯移动与零 `../` 契约）+ 骨架内 `README.md` |
| 失败排障（缺 wheel/镜像/podman/podman-compose/端口占用） | [docs/01-quickstart.md](docs/01-quickstart.md)（「常见失败与处置」） |
| 全局提交与代码规范 | [../../../AGENTS.md](../../../AGENTS.md) → [../../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md) |
| Skill 与七概念指令 | [../../../.agents/skills/README.md](../../../.agents/skills/README.md) / [../../../.agents/commands/README.md](../../../.agents/commands/README.md) |

## P0 约束速览（违反 = 打回）

| # | 约束 | 权威事实源 |
|---|------|-----------|
| 1 | **交付骨架纯移动 + 零 `../`**：`release/` 内文件逐字不变（仅「开发仓库便捷壳」表述例外），不得出现指向仓库其他文件的相对路径 | [delivery-pipeline.md](.agents/rules/delivery-pipeline.md) §1 |
| 2 | **CRLF shebang 守卫**：`pack` 前扫描骨架内 shebang 脚本，命中 CR 即 fail-fast，绝不产出坏字节 | 同上 §2 |
| 3 | **归档原子性**：`podman save \| gzip -1` → `gzip -t` → 原子 `mv`，不在交付目录留截断归档 | 同上 §5 |
| 4 | **版本语义**：默认取暂存 wheel 版本；GA 交付用 `--version` 显式指定 | 同上 §3 |
| 5 | **形态感知 tag**：`<IMAGE_NAME>:<形态>` + `:latest` 别名；形态白名单 `cpu\|cu130`，缺省来自 `product.env` 的 `TORCH_DEFAULT` | 同上 §4 |
| 6 | **零 Python 与禁依赖**：CLI 仅需 bash 4+ / pwsh 7.4+ / podman；禁止依赖 `client/`、`shared/`；外部输入仅 `workspace/dist` wheel 与基镜像 | 同上 §7 |
| 7 | **Windows 一律 pwsh7**：禁止 Windows PowerShell 5.1；容器命令统一经 `wsl.exe` 桥接 | 同上 §8 |
| 8 | **wheel 与归档不入 git**：`products/*/wheels/*.whl`、`release/artifacts/*` 由 `.gitignore` 守卫（仅放行 `.gitignore` 例外） | [.gitignore](.gitignore) |

## 变更日志

完整条目见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)。

- 2026-09-21 | feat | 应用抽取：客户离线交付链路迁出 `apps/containers/client/overlays/xmnn-runtime/`，落为完全自包含应用 `offline-delivery/`（目录名不含 `xmnn`，多产品经 `products/<名>/` 扩展）；工具链改为 bash + pwsh7 双入口零 Python CLI（`bin/relpack*`）。规格：[.trae/specs/infra-env/extract-offline-delivery-app/spec.md](../../../.trae/specs/infra-env/extract-offline-delivery-app/spec.md)