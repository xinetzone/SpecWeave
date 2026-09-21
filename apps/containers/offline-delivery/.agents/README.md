---
id: "offline-delivery-agents-readme"
title: "offline-delivery AI 资产容器"
source: "AGENTS.md#嵌套路由关系"
---
# offline-delivery - .agents 目录

本目录是 `apps/containers/offline-delivery`（厂商侧离线交付链路）的 AI 协作者资产容器。
本应用**完全自包含**：禁止依赖 `apps/containers/client/` 与 `apps/containers/shared/`，
外部输入仅 `../workspace/dist/xmnn-*.whl` 与基镜像 `localhost/jupyter-podman-rootless:latest`。

## 目录结构

```
.agents/
├── README.md                          ← 本文件（资产容器索引）
├── CHANGELOG.md                       ← 应用变更日志（原子提交汇总）
└── rules/
    └── delivery-pipeline.md           ← 唯一规则主题：离线交付流水线硬约束（8 节）
```

父级已有的资产不在本应用重复：`roles/`、`skills/`、`scripts/`、`workflows/`、`templates/`、
`docs/` 均**未在本应用定义**（不存在对应目录），相关需求一律回退父级（见下方回退链）。

**特别说明**：`apps/containers/offline-delivery/.agents/docs/` **未创建且不得创建**——
遵循 SpecWeave 根 AGENTS 文档边界声明，对外可读文档一律入本应用 `../docs/`（原子文档集）
或根 `docs/`，禁止写入任何报告/复盘/Wiki。

## 唯一规则主题

| 文件 | 覆盖内容 |
|------|---------|
| [rules/delivery-pipeline.md](rules/delivery-pipeline.md) | ①交付骨架零 Python/零 `../` 契约与纯移动纪律 ②CRLF shebang 守卫 ③版本语义 ④形态感知 tag ⑤归档原子性 ⑥`release.json` 字段与 torch 双键回退 ⑦禁依赖 `client`/`shared` ⑧Windows 一律 pwsh7 |

**单一职责原则**：新增规则只能新增文件，不得把上述主题拆散或复制到父级组层
（组层反双写纪律 G4）；新增前先走 I→F→V（明确现有文件为何覆盖不了、新文件标题能否被一句话概括、
父级是否已有同名规则），并同步 AGENTS.md「上下文路由表」与「P0 约束速览」。

## 核心资产真源（AI 协作者必读，文档与代码冲突时以代码为准）

| 资产 | 路径 | 说明 |
|------|------|------|
| 工具链入口（POSIX） | `../bin/relpack` | bash CLI：`stage`/`build`/`pack`/`smoke`/`version`；唯一产品常量来源是 `product.env` |
| 工具链入口（Windows） | `../bin/relpack.ps1` | pwsh7 同名命令面，容器命令经 `wsl.exe` 桥接 bash 版 |
| 产品参数单一事实源 | [../products/xmnn-runtime/product.env](../products/xmnn-runtime/product.env) | `PRODUCT`/`IMAGE_NAME`/`CONTAINERFILE`/`WHEEL_GLOB`/`WHEEL_DIST`/`BASE_IMAGE_DEFAULT`/`TORCH_DEFAULT`/`RELEASE_DIR` |
| 镜像定义 | [../products/xmnn-runtime/Containerfile.xmnn-runtime](../products/xmnn-runtime/Containerfile.xmnn-runtime) | 四 Layer：torch 形态层 + whl 安装层 + 内核注册与运行时守卫 + 构建期双身份 10 项硬验证 |
| 客户交付骨架 | [../products/xmnn-runtime/release/](../products/xmnn-runtime/release/README.md) | 客户可见契约：`xmnnctl` / `xmnnctl.ps1` + 自包含 compose + `.env.example` + `artifacts/` |

## 人类文档 ↔ AI 规则对应关系

| 人类文档章节 | 对应 AI 规则文件 | 同步锚点 |
|------------|----------------|---------|
| [docs/00-overview.md](../docs/00-overview.md)（定位与制品流） | [rules/delivery-pipeline.md](rules/delivery-pipeline.md) §1 §7 | 外部输入两项、禁依赖 `client`/`shared`、骨架零 `../` |
| [docs/01-quickstart.md](../docs/01-quickstart.md)（逐命令与失败处置） | 同上 §2-§6 §8 | CRLF 守卫、版本语义、形态 tag、归档原子性、`release.json` 字段、pwsh7 桥接 |
| [docs/01-quickstart.md](../docs/01-quickstart.md)（新增第二个交付产品） | 同上 §7 | 只需新增 `products/<名>/` 并在文档登记，CLI 代码零改动 |

## 父级继承（所有未定义一律回退）

| 层级 | 入口路径 | 提供的资产 |
|------|---------|-----------|
| L1 apps/containers 组 | [../../.agents/](../../.agents/README.md) | 组级资产容器：shared-package 规则 + G1-G4 组级契约 |
| L2 组级路由 | [../../AGENTS.md](../../AGENTS.md) | 容器分组路由、成员表、rootless 共同契约 |
| L3 apps 应用区 | [../../../AGENTS.md](../../../AGENTS.md) | 应用区入口、应用路由表 |
| L4 SpecWeave 根 | [../../../../AGENTS.md](../../../../AGENTS.md) | 全局启动协议、沟通语言、提交规范、路径引用、修复闭环 |
| （根规则） | [../../../../.agents/global-core-rules.md](../../../../.agents/global-core-rules.md) | 内容敏感度预检、嵌套路由回退链、按需读取 |
| （根 Skill） | [../../../../.agents/skills/README.md](../../../../.agents/skills/README.md) | ci-check / link-check / atomic-commit / seven-concepts 等 L1 门面 |
| （根命令） | [../../../../.agents/commands/README.md](../../../../.agents/commands/README.md) | 七概念、复盘、洞察、原子化、对抗性评审 |

## 变更日志

完整条目见 [CHANGELOG.md](CHANGELOG.md)。

- 2026-09-21 | feat | 初始化本应用 AI 资产容器：`.agents/README.md` + `CHANGELOG.md` + 唯一规则主题 `rules/delivery-pipeline.md`