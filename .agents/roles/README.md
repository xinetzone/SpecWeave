---
id: "roles"
title: "角色定义索引"
source: "AGENTS.md#角色定义"
x-toml-ref: "../../.meta/toml/.agents/roles/README.toml"
---
# 角色定义索引

本目录包含多智能体协作系统中所有角色定义文件。每个角色通过 YAML frontmatter 声明其绑定关系，完整元数据通过 x-toml-ref 引用外部 TOML 文件，并通过 Markdown 正文描述职责边界。

## 角色职责矩阵

| 角色 | ID | 领域 | 层级 | 层级标记 | 核心职责 |
|---|---|---|---|---|---|
| 编排协调者 | orchestrator | coordination | orchestration | 标准 | 任务分配、流程协调 |
| 架构师 | architect | engineering | design | 标准 | 方案设计、架构决策 |
| 开发者 | developer | engineering | implementation | 标准 | 代码实现、重构 |
| 代码审查者 | reviewer | quality | assurance | 标准 | 质量审查、规范校验 |
| 测试工程师 | tester | quality | verification | 标准 | 测试编写、覆盖率 |
| 联合创始者 | co-founder | governance | founding | 🏛️ 联合创始 | 愿景确立、协作契约奠基 |

## 协作场景

| 文档 | ID | 说明 |
|---|---|---|
| [角色协作场景](collaboration-scenarios.md) | collaboration-scenarios | 中心化与去中心化两种协作模式、角色相互 @ 机制、任务分配方式与预期交付物 |

## 文件结构说明

```
.agents/roles/
├── README.md                    # 本文件，角色索引
├── collaboration-scenarios.md   # 角色协作场景
├── co-founder.md                # 🏛️ 联合创始者
├── orchestrator.md              # 编排协调者
├── architect.md                 # 架构师
├── developer.md                 # 开发者
├── reviewer.md                  # 代码审查者
└── tester.md                    # 测试工程师
```

## 使用方法

1. 每个角色文件包含 YAML frontmatter，用于声明绑定的规则、引用与技能；完整元数据通过 x-toml-ref 引用外部 TOML 文件。
2. Markdown 正文分为 Description、Responsibilities、Non-Goals 三部分，明确角色定位与边界。
3. 在工作流编排时，通过 `id` 字段引用对应角色。
4. 角色之间通过 Non-Goals 明确职责边界，避免职责重叠。

## 权限控制

联合创始角色（`tier = "co-founder"`）具有特殊权限边界，其查看与管理受以下约束：

| 权限操作 | 允许范围 | 说明 |
|---|---|---|
| 查看 (view) | core-team | 核心团队成员可查看联合创始角色定义 |
| 管理 (manage) | co-founders | 仅联合创始者可修改联合创始角色定义 |

普通角色（`tier = "standard"`，默认）无额外权限约束，遵循常规角色管理流程。

联合创始角色在索引与详情页中通过 🏛️ 徽章与 `[联合创始]` 文字前缀标识，确保在所有相关界面中保持高辨识度。

### 环境兼容性说明

联合创始角色的视觉标记采用 🏛️ 徽章与 `[联合创始]` 文字前缀双要素设计。在支持 emoji 渲染的环境中（如 GitHub、VS Code 预览），两要素同时呈现；在不支持 emoji 的环境中（如部分终端、纯文本编辑器），标记退化为仅 `[联合创始]` 文字前缀，仍可正常识别。文字前缀作为 emoji 的降级方案，确保所有环境下联合创始角色均可辨识。
