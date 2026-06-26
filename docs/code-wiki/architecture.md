# 整体架构

## 架构总览

本仓库采用“入口路由 + 规范容器 + 可执行子系统 + 知识沉淀 + 自动化验证”的组合架构。

```mermaid
flowchart TB
    User["用户或 AI 编码工具"] --> Entry["AGENTS.md 全局入口"]
    Entry --> Router["上下文路由表"]
    Router --> Agents[".agents 规范容器"]
    Router --> Docs["docs 文档与知识库"]
    Router --> Specs[".trae/specs 规格文档"]
    Router --> Prompt["prompt_extraction 提示词萃取系统"]
    Agents --> Roles["角色定义"]
    Agents --> Prompts["系统提示词"]
    Agents --> Protocols["协作协议"]
    Agents --> Workflows["标准工作流"]
    Agents --> Rules["治理规则"]
    Agents --> Scripts["自动化脚本"]
    Prompt --> Pipeline["Pipeline 流水线"]
    Pipeline --> Input["input 输入解析"]
    Pipeline --> Pre["preprocessing 预处理"]
    Pipeline --> Extract["extraction 特征提取"]
    Pipeline --> Assess["assessment 质量评估"]
    Pipeline --> Optimize["optimization 优化生成"]
    Prompt --> UI[Streamlit UI]
    Prompt --> Tests["pytest 测试"]
```

## 入口路由架构

`AGENTS.md` 是仓库的最高优先级入口，承担三个职责：

1. **定义全局规则**：沟通语言、按需读取、Mermaid 优先、代码修改约束、临时依赖管理、知识库查阅等。
2. **建立索引**：角色、协议、规则、工具、工作流、模板、提示词、自我演进模块、团队模块等。
3. **提供上下文路由表**：根据任务类型指向相关规范文件或目录。

```mermaid
flowchart LR
    A["任务输入"] --> B["读取 AGENTS.md"]
    B --> C{判断任务类型}
    C -->|"角色/协作"| D[.agents/roles]
    C -->|"工具使用"| E[.agents/tools]
    C -->|"协议/流程"| F[".agents/protocols 或 workflows"]
    C -->|"代码实现"| G["prompt_extraction 或 apps"]
    C -->|"知识复用"| H["docs/knowledge 或 retrospective"]
    C -->|"验证检查"| I[.agents/scripts]
```

## `.agents/` 规范体系架构

`.agents/` 是具体规范容器，内部以职责域拆分子目录。

```mermaid
flowchart TB
    Agents[.agents]
    Agents --> Roles["roles 角色定义"]
    Agents --> Modules["modules 自我演进模块"]
    Agents --> Prompts["prompts 系统提示词"]
    Agents --> Tools["tools 工具调用规范"]
    Agents --> Protocols["protocols 协作协议"]
    Agents --> Workflows["workflows 标准工作流"]
    Agents --> Templates["templates 模板"]
    Agents --> Scripts["scripts 验证脚本"]
    Agents --> Teams["teams 团队管理"]
    Agents --> Worlds["worlds 协作执行与环境管理"]
    Agents --> Rules["rules 硬编码治理规则"]
```

该架构的核心优势是“入口与细节分离”：

- `AGENTS.md` 保持轻量但具备完整路由能力。
- `.agents/` 承载所有可扩展的角色、协议、规则与工作流细节。
- 新增能力时优先增加或调整 `.agents/` 子模块，再同步入口索引。

## 自我演进四层闭环

项目定义了感知、认知、执行、治理四层闭环，用于描述规范体系如何持续演进。

```mermaid
flowchart TB
    subgraph P["感知层"]
        P1["自我洞察"]
        P2["自我复盘"]
    end
    subgraph C["认知层"]
        C1["自我萃取"]
        C2["自我进化"]
    end
    subgraph E["执行层"]
        E1["自我迭代"]
        E2["自我验证"]
    end
    subgraph G["治理层"]
        G1["自我管理"]
        G2["自我发展"]
    end
    P --> C
    C --> E
    E --> G
    G -.反馈.-> P
```

## 提示词萃取系统架构

`prompt_extraction/` 采用典型流水线架构，核心编排器为 `Pipeline`，核心数据载体为 `PromptRecord`。

```mermaid
flowchart LR
    A["输入文本或文件"] --> B["input 输入处理"]
    B --> C[PromptRecord]
    C --> D["preprocessing 清洗与标准化"]
    D --> E["extraction 特征提取"]
    E --> F["assessment 质量评估"]
    F --> G{overall < QUALITY_THRESHOLD}
    G -->|"是"| H["optimization 优化生成"]
    G -->|"否"| I["保留原结果"]
    H --> J["导出或 UI 展示"]
    I --> J
```

### 流水线步骤

| 步骤 | 模块 | 输入 | 输出 |
|---|---|---|---|
| 1 | `input` | 单条文本或批量文件 | `PromptRecord` 或 `list[PromptRecord]` |
| 2 | `preprocessing.cleaner` | 原始文本 | 清洗文本、Markdown 结构、元数据 |
| 3 | `preprocessing.normalizer` | 清洗文本 | 标准化文本 |
| 4 | `extraction.extractor` | 标准化文本、Markdown 结构 | `FeatureSet` |
| 5 | `assessment.evaluator` | 文本、`FeatureSet` | `QualityScore` |
| 6 | `optimization.optimizer` | `PromptRecord` | `OptimizationResult` |
| 7 | `pipeline.export_results` 或 UI | 处理结果 | CSV、可视化结果 |

## UI 架构

Streamlit UI 是 `Pipeline` 的前端封装，提供两种输入方式：

- 文件上传：支持 CSV、JSON、TXT、Markdown。
- 手动输入：处理单条提示词。

```mermaid
flowchart TB
    UI[ui/app.py] --> InputMode{输入方式}
    InputMode --> File["文件上传"]
    InputMode --> Manual["手动输入"]
    File --> Temp["临时文件"]
    Temp --> Batch[Pipeline.run_batch]
    Manual --> Single[Pipeline.run_single]
    Batch --> Result["结果展示"]
    Single --> Result
    Result --> Score["评分卡"]
    Result --> Radar["雷达图"]
    Result --> Diff["优化差异"]
    Result --> Export["导出按钮"]
```

## 验证架构

项目验证体系分为规范层验证和代码层验证。

```mermaid
flowchart LR
    A["验证入口"] --> B["规范层验证"]
    A --> C["代码层验证"]
    B --> B1[check-gitignore]
    B --> B2[check-links]
    B --> B3[check-spec-consistency]
    B --> B4[check-source-traceability]
    B --> B5[check-role-permissions]
    B --> B6[generate-nav]
    C --> C1["pytest 单元测试"]
    C --> C2["pytest 集成测试"]
    C --> C3["Streamlit 手动验收"]
```
