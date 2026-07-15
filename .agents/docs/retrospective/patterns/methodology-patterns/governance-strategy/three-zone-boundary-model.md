---
id: "three-zone-boundary-model"
title: "三区域边界模型"
source: "../../../reports/spec-system/retrospective-vendor-submodule-collaboration-20260629/insight-extraction.md + SpecWeave 13天全生命周期复盘验证"
maturity: "L2"
tags: ["governance", "external-dependency", "boundary", "vendor", "submodule"]
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/three-zone-boundary-model.toml"
---
# 三区域边界模型：外部代码依赖的主权划分

## 模式类型
治理策略模式

## 成熟度
L2 已验证（flexloop vendor集成 + SpecWeave四不原则+零依赖原则落地验证）

## 模型概述

管理外部代码依赖（git submodule、vendored library 等）时，将文件系统划分为三个主权区域，每个区域有明确的权责和操作规则，确保主项目与外部代码库在保持独立的前提下高效协同。

## 区域划分

### 架构总览

```mermaid
flowchart TB
    subgraph PROJECT["🏠 主项目主权区（SpecWeave）—— 完全控制·无限制操作"]
        direction TB
        P1[".agents/    智能体规范体系"]
        P2["docs/      文档与知识库"]
        P3[".trae/     Spec 任务管理"]
        P4["apps/      应用开发空间"]
        P5["pytest.ini 测试配置"]
        P6["...        项目根配置文件"]
    end
    subgraph INTERFACE["🔌 接口层（主项目维护）—— 定义交互规则"]
        direction TB
        I1["📋 vendor/README.md<br/>依赖总览·用途说明"]
        I2["🏷️ vendor/VERSION.md<br/>版本清单·commit锁定·许可证"]
        I3["🔍 repo-check vendor --deep<br/>集成验证脚本（5项检查）"]
        I4["📜 dependency-management.md<br/>子模块管理协议"]
        I5["📖 VENDOR-INTEGRATION.md<br/>协同操作指南"]
    end
    subgraph EXTERNAL["📦 外部依赖主权区（flexloop）—— 只读引用·禁止侵入"]
        direction TB
        E1["vendor/flexloop/<br/>├── src/<br/>├── tests/<br/>├── pyproject.toml<br/>├── LICENSE (Apache-2.0)<br/>└── .git ← gitdir 指针<br/>（git submodule · 固定 commit d618849a）"]
    end
    PROJECT -->|"① 模式萃取<br/>复制代码并标注来源"| INTERFACE
    INTERFACE -->|"② 只读引用<br/>gitlink 指针"| EXTERNAL
    INTERFACE -->|"③ 元数据记录<br/>用途·版本·许可证"| EXTERNAL
    INTERFACE -->|"④ 违规检测<br/>--deep 自动化检查"| EXTERNAL
    style PROJECT fill:#d4edda,stroke:#28a745,stroke-width:3px,color:#155724
    style INTERFACE fill:#fff3cd,stroke:#ffc107,stroke-width:3px,color:#856404
    style EXTERNAL fill:#f8d7da,stroke:#dc3545,stroke-width:3px,color:#721c24
    style P1 fill:#e8f5e9,stroke:#4caf50
    style P2 fill:#e8f5e9,stroke:#4caf50
    style P3 fill:#e8f5e9,stroke:#4caf50
    style P4 fill:#e8f5e9,stroke:#4caf50
    style P5 fill:#e8f5e9,stroke:#4caf50
    style P6 fill:#e8f5e9,stroke:#4caf50
    style I1 fill:#fff8e1,stroke:#ffb300
    style I2 fill:#fff8e1,stroke:#ffb300
    style I3 fill:#fff8e1,stroke:#ffb300
    style I4 fill:#fff8e1,stroke:#ffb300
    style I5 fill:#fff8e1,stroke:#ffb300
    style E1 fill:#ffebee,stroke:#e53935
```

### 权限边界矩阵

```mermaid
flowchart LR
    subgraph "允许操作 ✅"
        direction TB
        A1["git submodule update<br/>更新指向的 commit"]
        A2["读取外部代码<br/>参考实现·学习模式"]
        A3["模式萃取后复制<br/>到主项目（标注来源）"]
        A4["向 flexloop 上游<br/>提交 PR（外部流程）"]
    end
    subgraph "禁止操作 ❌"
        direction TB
        B1["在 vendor/flexloop/<br/>内创建/修改/删除文件"]
        B2["import vendor.flexloop<br/>直接导入运行时"]
        B3["sys.path.insert<br/>指向 vendor/"]
        B4["让 pytest 递归收集<br/>vendor/ 下的测试"]
    end
    style A1 fill:#d4edda,stroke:#28a745
    style A2 fill:#d4edda,stroke:#28a745
    style A3 fill:#d4edda,stroke:#28a745
    style A4 fill:#d4edda,stroke:#28a745
    style B1 fill:#f8d7da,stroke:#dc3545
    style B2 fill:#f8d7da,stroke:#dc3545
    style B3 fill:#f8d7da,stroke:#dc3545
    style B4 fill:#f8d7da,stroke:#dc3545
```

### 代码流向与数据流

```mermaid
sequenceDiagram
    participant Dev as "开发者"
    participant Main as "🏠 主项目主权区"
    participant API as "🔌 接口层"
    participant Ext as "📦 外部依赖区"
    participant Git as "Git 版本控制"
    Note over Dev,Git: 场景1：参考外部实现模式
    Dev->>Ext: 阅读 flexloop 源码
    Ext-->>Dev: 返回代码模式参考
    Dev->>Main: 在主项目中实现适配版
    Dev->>API: 标注 source 来源
    Note over Dev,Git: 场景2：更新外部依赖版本
    Dev->>Git: git submodule update
    Git->>Ext: 更新 working tree 到新 commit
    Dev->>API: 更新 VERSION.md 记录新版本
    Dev->>API: 运行 --deep 验证
    API->>Ext: 检查初始化/清洁度/一致性
    API-->>Dev: ✅ 验证通过
    Dev->>Git: 原子提交（gitlink + VERSION.md）
    Note over Dev,Git: 场景3：检测违规（自动化）
    loop 每次 CI/pre-commit
        API->>Ext: 检查 submodule 状态
        API->>Main: 扫描非法 vendor 引用
        API->>Main: 检查 pytest 隔离配置
        API-->>Dev: 报告违规项
    end
```

### 区域 1：主项目主权区（🏠 完全控制）
- **范围**：`.agents/`、`docs/`、`.trae/`、`apps/`、项目根配置文件等
- **规则**：完全自主控制，可以任意创建、修改、删除
- **操作权限**：无限制

### 区域 2：接口层（🔌 主项目维护）
- **范围**：`vendor/README.md`、`vendor/VERSION.md`、验证脚本、协议文档、测试配置
- **规则**：由主项目维护，定义主项目如何与外部依赖交互
- **关键约束**：接口层文件必须**位于外部依赖目录之外**
- **操作权限**：可以创建、修改，但必须记录变更原因

### 区域 3：外部依赖主权区（📦 只读引用）
- **范围**：`vendor/flexloop/` 等 git submodule 目录、手动管理库的 vendor 子目录
- **规则**：视为只读，不做任何侵入式创建或修改
- **关键约束**：
  - 不在外部目录内创建主项目维护的文件
  - 不直接 import 外部代码到运行时
  - 不手动修改外部目录内容（修改应通过 submodule update 或上游 PR）
- **操作权限**：仅通过 git submodule 命令更新指向的 commit

## 交互规则

| 交互类型 | 正确做法 | 错误做法 |
|---------|---------|---------|
| 引用代码 | 通过模式萃取复制到主项目，标注来源 | `import vendor.flexloop.xxx` 或 `sys.path.insert` |
| 更新版本 | `git submodule update` 后更新 VERSION.md | 手动修改外部目录文件 |
| 元数据管理 | 在 vendor/ 根级 README.md/VERSION.md 记录 | 在外部目录内创建 README.md |
| 测试隔离 | pytest.ini norecursedirs 排除 vendor/ | 让 pytest 递归收集 vendor/ 下的测试 |
| 添加元信息 | 接口层文档记录用途、许可证、来源 | 修改外部仓库的 LICENSE 或元数据文件 |

## 实施检查清单

- [ ] 外部依赖通过 git submodule（gitlink）或明确协议管理
- [ ] 主项目元数据（版本、用途、许可证）存放在外部目录之外
- [ ] 验证脚本覆盖：初始化状态、工作树清洁度、元数据一致性、非法引用
- [ ] 测试配置排除外部依赖目录
- [ ] 项目中无 `sys.path.insert/append` 指向 vendor/ 的代码
- [ ] 项目中无 `import vendor.` 或 `from vendor.` 的 import 语句

## 适用场景

- Git submodule 管理外部框架/参考实现
- Vendored library（复制到 vendor/ 但不修改的第三方库）
- 多个独立代码库之间的引用协同

> 来源：establish-vendor-collaboration-framework spec 实践
> 关联：[VENDOR-INTEGRATION.md](../../../../knowledge/VENDOR-INTEGRATION.md)、[外部依赖四不原则](four-negatives-external-dependency.md)
