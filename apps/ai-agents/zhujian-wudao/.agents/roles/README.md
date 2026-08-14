# 角色定义索引

本目录包含竹简悟道项目多智能体协作系统中所有角色定义文件。每个角色通过 TOML frontmatter 声明其绑定关系，并通过 Markdown 正文描述职责边界。

## 角色职责矩阵

| 角色 | ID | 领域 | 层级 | 层级标记 | 核心职责 |
|---|---|---|---|---|---|
| 哲思引导者 | philosopher | content | generation | 标准 | 洞察撰写、内容审查、交叉引用维护、哲学一致性保证 |

## 文件结构说明

```
.agents/roles/
├── README.md                          # 本文件，角色索引
├── philosopher.md                     # 哲思引导者
└── references/
    ├── insight-writing-guide.md       # 洞察撰写速查手册
    └── constraints-cheatsheet.md      # 约束速查表
```

## 使用方法

1. 每个角色文件包含 TOML frontmatter，用于声明绑定的规则、引用与工作流。
2. Markdown 正文分为核心定位、职责、非目标三部分，明确角色定位与边界。
3. 在工作流编排时，通过 `id = "philosopher"` 引用本角色。
4. 角色之间通过非目标明确职责边界，避免职责重叠。

## 权限控制

哲思引导者角色（`tier = "standard"`）无额外权限约束，遵循常规角色管理流程。
