---
id: "containers-group-agents-readme"
title: "apps/containers 组级 AI 资产容器"
source: "../AGENTS.md#嵌套路由关系"
---
# apps/containers - .agents 目录

本目录是 `apps/containers` 容器分组（Podman rootless 生态）的**组级** AI 协作者资产容器。
组层只承载**跨成员事实**（离开任一成员视角才成立的信息）；成员特有规则存放在各成员自己的
`.agents/` 中，本目录不复制、不搬迁（组层反双写纪律 G4）。

## 目录结构

```
.agents/
├── README.md              ← 本文件（组级资产容器索引）
├── CHANGELOG.md           ← 组级治理变更日志
├── rules/                 ← 组级规则（每个主题必须跨 ≥2 成员成立且无现有归属者）
│   └── shared-package.md  ← jpman_common 共享包治理（唯一事实源边界/安装顺序/双向回归）
├── roles/                 ← （预留占位；未定义 → 回退 apps/ 与 SpecWeave 根角色）
├── skills/                ← （预留占位；未定义 → 回退根 skills/，如 compose-overlay-ops/client-overlay-scaffold）
├── scripts/               ← （预留占位；未定义 → 回退根 .agents/scripts/）
├── workflows/             ← （预留占位；未定义 → 回退根 workflows/）
├── templates/             ← （预留占位；未定义 → 回退根 templates/）
└── docs/                  ← （预留占位；⚠️ 不写任何产出物；组级人类文档在 ../docs/，公开知识在根 docs/）
```

**关于 `docs/` 占位目录**：遵循 SpecWeave 文档边界声明——对外可读文档一律入 `docs/`
（组级为 `../docs/`，成员级为各成员 `docs/`）或根 `docs/`，**禁止**在本 `.agents/docs/`
下写入任何报告/复盘/Wiki/教程。

## 组级核心资产（AI 协作者必读）

| 资产 | 路径 | 说明 |
|------|------|------|
| 组级路由入口 | [../AGENTS.md](../AGENTS.md) | 三成员路由表、G1-G4 组级约束、上下文路由 |
| 共享包（唯一被组层代管的成员） | [../shared/](../shared/pyproject.toml) | jpman-common 0.1.0：`connection.py`（连接层唯一事实源，podman import 唯一允许处）、`platform_paths.py`（to_posix_path 等）、`proc.py`（run_cmd/detect_runtime）、`containers.py`（只读探测）、`_win32_transcode.py`；测试在 ../../shared/tests/ |
| 构建端 AI 资产 | [../jupyter-podman-rootless/.agents/](../jupyter-podman-rootless/.agents/README.md) | 7 rules：containerfile/entrypoint/services/compose/invoke-tasks/ml-models/build-test |
| 消费端 AI 资产 | [../client/.agents/](../client/.agents/README.md) | 6 rules：invoke-tasks/sdk-connection/windows-wsl/quant-overlay/xmnn-overlay/monetize-overlay；C1-C14 P0 约束在 ../client/AGENTS.md |
| 三栈 compose 公共段 | [../client/overlays/_shared/base-rootless.yaml](../client/overlays/_shared/base-rootless.yaml) | rootless-base：三必需 + 凭证四变量 + network_mode bridge（extends 单一事实源） |
| 组级人类文档 | [../docs/](../docs/README.md) | 00-overview（组全景）+ 01-getting-started（跨成员端到端） |

## 新增组级规则的标准流程

`.agents/rules/` 下新增主题文件前必须同时满足：

1. **跨成员成立**：规则约束的行为同时涉及 ≥2 个成员（纯成员内规则回成员自己的 `.agents/rules/`）
2. **无现有归属者**：该主题在成员 rules、根 `.agents/` 中均无权威定义
3. 走七概念方法论（至少 I→F→V）：给出跨成员反例 → 一句话概括单一职责 → 对抗双写漂移风险
4. 落盘后同步三处索引：本文件目录结构段、`../AGENTS.md` 上下文路由表与 G 约束速览、
   必要时在 `../docs/` 对应文档加双向锚点

## 父级继承（所有未定义一律回退）

| 层级 | 入口路径 | 提供的资产 |
|------|---------|-----------|
| L1 apps 应用区 | [../../AGENTS.md](../../AGENTS.md) | apps 总入口、应用路由表 |
| L2 SpecWeave 根 | [../../../AGENTS.md](../../../AGENTS.md) | 全局启动协议、沟通语言、提交规范、修复闭环、路径引用 |
| 根核心规则 | [../../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md) | 内容敏感度预检、嵌套路由回退链 |
| 根 Skill | [../../../.agents/skills/README.md](../../../.agents/skills/README.md) | seven-concepts-cmd / compose-overlay-ops / client-overlay-scaffold / jpman-podman-ops / atomic-commit-cmd 等 |
| 根命令 | [../../../.agents/commands/README.md](../../../.agents/commands/README.md) | 七概念 R/I/E/C/A/F/V 子命令 |
| 根脚本共享库 | [../../../.agents/scripts/lib/README.md](../../../.agents/scripts/lib/README.md) | Python 共享函数（新增脚本前必先查重，禁止重复实现） |

## 变更日志

完整条目见 [CHANGELOG.md](CHANGELOG.md)。
