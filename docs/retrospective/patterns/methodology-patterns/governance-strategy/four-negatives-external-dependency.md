---
id: "four-negatives-external-dependency"
title: "外部依赖四不原则"
source: "../../../reports/spec-system/retrospective-vendor-submodule-collaboration-20260629/insight-extraction.md + SpecWeave 13天全生命周期复盘量化验证"
maturity: "L3"
tags: ["governance", "external-dependency", "vendor", "submodule", "boundary"]
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/four-negatives-external-dependency.toml"
---
# 外部依赖四不原则：submodule/vendored code 管理铁律

## 模式类型
治理策略模式

## 成熟度
**L3 标准化**（flexloop vendor集成验证 + SpecWeave 13天793次提交实践，150+脚本全部零第三方依赖验证）

## 量化验证结论
- **零依赖验证**：SpecWeave项目150+ Python自动化脚本全部零第三方依赖，仅使用Python标准库
- **跨平台验证**：Windows/macOS/Linux三平台即用，无需pip install、无需虚拟环境配置
- **边界清晰验证**：vendor目录管理遵循四不原则，主项目与外部依赖边界清晰
- **故障隔离验证**：外部依赖问题不影响主项目运行，环境一致性得到保障

## 待跨场景验证项
- [ ] 是否存在必须引入第三方依赖的场景（如复杂YAML/JSON Schema处理、加密算法）
- [ ] 在依赖数量>50个的大型项目中验证边界维护成本
- [ ] 在二进制依赖（C扩展、Rust扩展）场景中验证四不原则适用性
- [ ] 验证零依赖原则与"不要重复造轮子"的平衡边界

## 原则概述

管理外部代码依赖（git submodule、vendored library、第三方Python包）时必须遵循的四条铁律，每条原则对应一类常见错误模式，通过自动化验证脚本兜底执行。

零依赖原则是四不原则在主项目内部的延伸：主项目自身的工具脚本尽可能不引入第三方依赖，确保跨环境即用。

## 四不原则

### 纵深防御架构

四条原则形成四层防御体系，前三条是行为约束（禁止类），第四条是保障机制（检测类），共同构成纵深防御：

```mermaid
flowchart TB
    subgraph L1["❶ 第一层防御：文件系统边界"]
        N1["🚫 不侵入<br/>No Intrusion<br/>保护外部目录完整性"]
        N1_DET["检测：git submodule status<br/>不应有 +/U 前缀"]
    end
    subgraph L2["❷ 第二层防御：运行时边界"]
        N2["🚫 不直引<br/>No Direct Import<br/>防止运行时耦合"]
        N2_DET["检测：静态扫描<br/>import vendor. / sys.path vendor"]
    end
    subgraph L3["❸ 第三层防御：版本边界"]
        N3["🚫 不跟版<br/>No Auto-Tracking<br/>防止上游变动自动传导"]
        N3_DET["检测：.gitmodules 无 branch<br/>VERSION.md 有固定 commit"]
    end
    subgraph L4["❹ 第四层防御：自动化兜底"]
        N4["🔍 不裸考<br/>No Bare Reliance<br/>自动化验证兜底执行"]
        N4_DET["repo-check vendor --deep<br/>5 项检查 · <10s · 0 误报"]
    end
    subgraph L5["❺ 零依赖原则（主项目内部）"]
        N5["🚫 不滥引<br/>No Unnecessary Dependency<br/>脚本尽量零第三方依赖"]
        N5_DET["检测：requirements.txt<br/>仅标准库→零依赖认证"]
    end
    N1 -->|"违反"| C1["⚠️ submodule dirty<br/>版本控制混乱"]
    N2 -->|"违反"| C2["⚠️ 运行时耦合<br/>更新时 break"]
    N3 -->|"违反"| C3["⚠️ 构建不稳定<br/>意外 break"]
    N5 -->|"违反"| C5["⚠️ 环境依赖<br/>部署困难"]
    N1_DET --> N4
    N2_DET --> N4
    N3_DET --> N4
    N4 -->|"全部通过"| R["✅ 零冲突 · 零混乱 · 可维护"]
    N5_DET --> R
    style L1 fill:#ffebee,stroke:#e53935,stroke-width:2px
    style L2 fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style L3 fill:#fff8e1,stroke:#fdd835,stroke-width:2px
    style L4 fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style L5 fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style N1 fill:#ffcdd2,stroke:#e53935
    style N2 fill:#ffe0b2,stroke:#ff9800
    style N3 fill:#ffecb3,stroke:#fdd835
    style N4 fill:#c8e6c9,stroke:#4caf50
    style N5 fill:#bbdefb,stroke:#2196f3
    style R fill:#d1ecf1,stroke:#17a2b8,stroke-width:2px
    style C1 fill:#f8d7da,stroke:#dc3545
    style C2 fill:#f8d7da,stroke:#dc3545
    style C3 fill:#fff3cd,stroke:#ffc107
    style C5 fill:#d1ecf1,stroke:#17a2b8
```

### 每条原则的因果链

```mermaid
flowchart LR
    subgraph P1["❶ 不侵入"]
        direction TB
        W1["❌ 错误：在 vendor/flexloop/<br/>创建主项目文件"]
        E1["💥 后果：submodule<br/>permanent dirty"]
        R1["✅ 正确：元数据外置<br/>vendor/README.md + VERSION.md"]
        V1["🔍 验证：git status clean<br/>git submodule status 前缀为空格"]
        W1 --> E1 --> R1 --> V1
    end
    subgraph P2["❷ 不直引"]
        direction TB
        W2["❌ 错误：sys.path.insert<br/>或 import vendor.flexloop"]
        E2["💥 后果：运行时强耦合<br/>更新即 break"]
        R2["✅ 正确：模式萃取6步法<br/>评估→理解→适配→标注→验证→登记"]
        V2["🔍 验证：grep -r 'import vendor\\.'<br/>无匹配"]
        W2 --> E2 --> R2 --> V2
    end
    subgraph P3["❸ 不跟版"]
        direction TB
        W3["❌ 错误：branch = main<br/>submodule update --remote"]
        E3["💥 后果：上游 breaking<br/>change 自动传导"]
        R3["✅ 正确：固定 commit<br/>手动评估后更新"]
        V3["🔍 验证：.gitmodules 无 branch<br/>VERSION.md 有具体哈希"]
        W3 --> E3 --> R3 --> V3
    end
    subgraph P5["❺ 不滥引（零依赖）"]
        direction TB
        W5["❌ 错误：每个小功能都pip install<br/>requests/numpy/pyyaml"]
        E5["💥 后果：环境依赖爆炸<br/>新机器部署要装半小时"]
        R5["✅ 正确：优先用标准库<br/>必须引入时评估ROI"]
        V5["🔍 验证：脚本可直接运行<br/>无需pip install任何包"]
        W5 --> E5 --> R5 --> V5
    end
    P1 --> P4["❹ 不裸考：repo-check vendor --deep<br/>一键检测以上所有约束"]
    P2 --> P4
    P3 --> P4
    P5 --> P4
    style W1 fill:#f8d7da,stroke:#dc3545
    style W2 fill:#f8d7da,stroke:#dc3545
    style W3 fill:#f8d7da,stroke:#dc3545
    style W5 fill:#f8d7da,stroke:#dc3545
    style E1 fill:#fff3cd,stroke:#ffc107
    style E2 fill:#fff3cd,stroke:#ffc107
    style E3 fill:#fff3cd,stroke:#ffc107
    style E5 fill:#fff3cd,stroke:#ffc107
    style R1 fill:#d4edda,stroke:#28a745
    style R2 fill:#d4edda,stroke:#28a745
    style R3 fill:#d4edda,stroke:#28a745
    style R5 fill:#d4edda,stroke:#28a745
    style V1 fill:#d1ecf1,stroke:#17a2b8
    style V2 fill:#d1ecf1,stroke:#17a2b8
    style V3 fill:#d1ecf1,stroke:#17a2b8
    style V5 fill:#d1ecf1,stroke:#17a2b8
    style P4 fill:#c8e6c9,stroke:#4caf50,stroke-width:2px
```

### 与三区域模型的映射关系

```mermaid
flowchart TB
    subgraph THREE["三区域边界模型"]
        direction LR
        Z1["🏠 主项目区"]
        Z2["🔌 接口层"]
        Z3["📦 外部依赖区"]
        Z1 --> Z2 --> Z3
    end
    subgraph FOUR["四不原则+零依赖"]
        direction TB
        N1["❶ 不侵入"]
        N2["❷ 不直引"]
        N3["❸ 不跟版"]
        N4["❹ 不裸考"]
        N5["❺ 不滥引（零依赖）"]
    end
    N1 -.->|"保护"| Z3
    N2 -.->|"定义"| Z2
    N3 -.->|"保障"| Z1
    N4 -.->|"执行"| Z2
    N5 -.->|"约束"| Z1
    style THREE fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px
    style Z1 fill:#d4edda,stroke:#28a745
    style Z2 fill:#fff3cd,stroke:#ffc107
    style Z3 fill:#f8d7da,stroke:#dc3545
    style N1 fill:#ffcdd2,stroke:#e53935
    style N2 fill:#ffe0b2,stroke:#ff9800
    style N3 fill:#ffecb3,stroke:#fdd835
    style N4 fill:#c8e6c9,stroke:#4caf50
    style N5 fill:#bbdefb,stroke:#2196f3
```

### 违规状态迁移

```mermaid
stateDiagram-v2
    [*] --> Clean: "初始状态<br/>(0违规)"
    Clean --> Intrusion: "侵入外部目录<br/>(创建文件)"
    Clean --> DirectImport: "直引外部代码<br/>(import vendor.)"
    Clean --> AutoTrack: "开启分支跟踪<br/>(branch=main)"
    Clean --> UnnecessaryDep: "滥引第三方包<br/>(可不用却pip install)"
    Intrusion --> Dirty: "submodule modified content"
    DirectImport --> Coupled: 运行时耦合
    AutoTrack --> Unstable: 构建不稳定
    UnnecessaryDep --> EnvBloat: 环境依赖膨胀
    Dirty --> Detected: "--deep 检测到"
    Coupled --> Detected: "--deep 检测到"
    Unstable --> Detected: "--deep 检测到"
    EnvBloat --> Detected: "零依赖审计发现"
    Detected --> Fixing: "删除非法文件<br/>移除直引<br/>关闭跟踪<br/>替换为标准库方案"
    Fixing --> Clean: "验证通过<br/>(git submodule update)"
```

### ❶ 不侵入（No Intrusion）
- **含义**：外部依赖目录视为只读，不在其中创建或修改主项目维护的文件
- **反面典型**：在 `vendor/flexloop/` 内创建 README.md 记录元数据 → submodule 标记为"modified content"
- **正确做法**：所有元数据（README、VERSION、用途说明）放在接口层（vendor/ 根级或 docs/ 目录）
- **验证手段**：`git submodule status` 前缀检测（不应有 `+`/`U` 标记）；`git status --porcelain <submodule_dir>` 应无输出

### ❷ 不直引（No Direct Import）
- **含义**：不通过 `import`、`sys.path.insert/append` 等方式将外部代码直接引入主项目运行时
- **反面典型**：`sys.path.insert(0, "vendor/flexloop/src")` 然后 `from flexloop import xxx`
- **正确做法**：通过模式萃取流程（评估→理解→适配→标注→验证→登记）将需要的模式复制到主项目并标注来源
- **验证手段**：静态扫描 Python 文件中的 `sys.path.*vendor` 和 `(import|from) vendor\.` 模式

### ❸ 不跟版（No Auto-Tracking）
- **含义**：不自动跟踪上游分支的最新版本，采用固定 commit 锁定策略
- **反面典型**：submodule 配置为跟踪 main 分支，`git submodule update --remote` 自动拉取最新代码
- **正确做法**：
  - VERSION.md 记录具体 commit 哈希（非"见子模块"占位符）
  - 更新前评估兼容性（查看 CHANGELOG、检查 breaking changes）
  - 更新后运行完整验证（--deep 检查 + 测试）
- **验证手段**：检查 .gitmodules 中无 `branch = ` 配置；VERSION.md 包含完整 commit 哈希

### ❹ 不裸考（No Bare Reliance）
- **含义**：不依赖开发者记忆或人工约定来遵守上述三条原则，用自动化验证脚本兜底
- **反面典型**：在文档中写"请不要修改 vendor/ 目录"，但没有工具检测违规
- **正确做法**：
  - 深度集成验证脚本（`repo-check.py vendor --deep`）自动检测违规
  - pytest 配置自动排除 vendor/ 目录
  - CI/pre-commit hook 集成检查（可选）
- **验证手段**：脚本可一键运行，在 <10 秒内完成全部检查

### ❺ 不滥引（No Unnecessary Dependency，零依赖原则）
- **含义**：主项目自身的工具脚本优先使用Python标准库，不滥引第三方依赖；必须引入时严格评估ROI
- **反面典型**：为了读个JSON就引入pydantic，为了处理个路径就引入pathlib2（Python 3已内置）
- **正确做法**：
  - 150+脚本全部零第三方依赖验证通过
  - 标准库能实现的绝不引入第三方包
  - 必须引入时（如复杂加密、特定协议）记录原因和替代方案评估
- **价值**：跨Windows/macOS/Linux即用，无需pip install、无需虚拟环境、不存在版本冲突
- **验证手段**：脚本可直接 `python script.py` 运行，无ImportError

## 与三区域模型的关系

四不原则+零依赖原则是三区域边界模型的操作化规则。如上映射关系图所示：前三条原则分别保护三个区域的边界完整性，第四条"不裸考"通过接口层的自动化工具兜底执行，第五条"不滥引"保障主项目区的可移植性，形成完整的防御闭环。详细区域定义见 [三区域边界模型](three-zone-boundary-model.md)。

## 反模式与后果

| 违反原则 | 后果 | 严重程度 |
|---------|------|---------|
| 侵入外部目录 | submodule 永久 dirty，版本控制混乱 | 🔴 高 |
| 直接 import | 运行时耦合，更新外部依赖时 break | 🔴 高 |
| 跟踪分支 | 上游 breaking change 自动传导，构建不稳定 | 🟡 中 |
| 无自动化验证 | 规则形同虚设，依赖人工 review 容易遗漏 | 🟡 中 |
| 滥引第三方包 | 环境依赖膨胀，部署困难，版本冲突地狱 | 🟡 中 |

## 实施检查清单

- [ ] `repo-check.py vendor --deep` 0 错误 0 警告
- [ ] 项目中无 `sys.path` hack 指向 vendor/
- [ ] 项目中无 `import vendor.` 语句
- [ ] .gitmodules 无 branch 跟踪配置
- [ ] VERSION.md 包含具体 commit 哈希
- [ ] pytest 配置排除 vendor/
- [ ] 所有脚本可直接运行，无需pip install第三方包
- [ ] 新引入第三方包时有ROI评估记录

## 关联模式
- [three-zone-boundary-model.md](three-zone-boundary-model.md)：三区域边界模型是本原则的理论基础
- [shared-lib-gravity.md](../tools-automation/shared-lib-gravity.md)：共享库引力定律——什么时候应该提取共享库而非复制代码
- [tool-bootstrap-effect.md](../tools-automation/tool-bootstrap-effect.md)：工具自举效应与dogfooding
- [VENDOR-INTEGRATION.md](../../../../../.agents/VENDOR-INTEGRATION.md)：vendor子模块协同规范
