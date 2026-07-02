---
id: mdi-technical-architecture
title: MDI研究报告 - 技术架构深度解析
source: "mdi-research-report.md#4-技术架构深度解析"
x-toml-ref: "../../../.meta/toml/docs/knowledge/mdi-research/03-technical-architecture.toml"
---

# 技术架构深度解析

## 完整系统架构

```mermaid
flowchart TB
    subgraph External["外部输入"]
        FS["文件系统<br/>(.md文件)"]
        STR["字符串内容<br/>(API调用)"]
        GIT["Git版本库<br/>(diff对比)"]
    end

    subgraph Core["MDI Core (mdi包)"]
        direction TB
        subgraph Parser["Parser层"]
            P1["markdown-it-py<br/>Block Tokenizer"]
            P2["Frontmatter解析<br/>(YAML + TOML引用)"]
            P3["Section树构建<br/>(H1-H6层级)"]
            P4["Table智能分类<br/>(关键词匹配)"]
            P5["Code Block识别<br/>(language+meta)"]
            P6["List解析<br/>(checkbox/ordered/unordered)"]
            P7["MyST Directive解析<br/>({endpoint}/{command})"]
        end

        subgraph Model["模型层"]
            MD["MDIDocument"]
            IF["Interface[]"]
            PA["Parameter[]"]
            RS["Response[]"]
            ER["ErrorCode[]"]
        end

        subgraph Validator["Validator层"]
            V1["Profile自动检测"]
            V2["通用规则验证<br/>(E001-E003/W001-W008)"]
            V3["Skill Profile规则"]
            V4["WebAPI Profile规则"]
            V5["CLI Profile规则"]
            V6["评分系统<br/>(0-100分)"]
        end

        subgraph Generator["Generator层"]
            G1["Python TypedDict"]
            G2["TypeScript interface"]
            G3["OpenAPI 3.0 JSON"]
            G4["MCP Tool定义"]
            G5["Markdown文档"]
            G6["Python Click CLI"]
            G7["pytest测试骨架"]
            G8["Jest测试骨架"]
        end

        subgraph Versioning["版本管理层"]
            VC1["结构化Diff"]
            VC2["影响分析"]
            VC3["版本升级建议"]
        end
    end

    subgraph Testing["测试工具层"]
        T1["Mock数据生成"]
        T2["示例提取"]
        T3["检查清单转换"]
    end

    subgraph Output["输出产物"]
        O1["类型定义文件"]
        O2["API规范文件"]
        O3["测试骨架"]
        O4["验证报告"]
        O5["变更报告"]
    end

    FS --> P1
    STR --> P1
    GIT --> VC1
    P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> P7 --> MD
    MD --> IF --> PA
    MD --> RS
    MD --> ER
    MD --> V1 --> V2 --> V3 --> V4 --> V5 --> V6
    MD --> G1 & G2 & G3 & G4 & G5 & G6 & G7 & G8
    MD --> T1 & T2 & T3
    MD --> VC1 --> VC2 --> VC3
    G1 & G2 --> O1
    G3 & G4 --> O2
    G7 & G8 --> O3
    V6 --> O4
    VC3 --> O5
    style Core fill:#e8f5e9
    style Parser fill:#e3f2fd
    style Validator fill:#fff3e0
    style Generator fill:#f3e5f5
    style Versioning fill:#fce4ec
```

## 核心数据流

```mermaid
sequenceDiagram
    participant User as 用户
    participant CLI as CLI (mdi命令)
    participant Parser as MDIParser
    participant Validator as MDIValidator
    participant Gen as MDIGenerator
    participant FS as 文件系统

    User->>CLI: mdi validate api.md
    CLI->>Parser: parse_file("api.md")
    Parser->>FS: 读取.md文件内容
    FS-->>Parser: Markdown文本
    Parser->>Parser: 解析Frontmatter+Block
    Parser-->>CLI: MDIDocument对象
    CLI->>Validator: validate(doc)
    Validator->>Validator: Profile检测+规则验证
    Validator-->>CLI: ValidationReport
    CLI-->>User: 验证报告(分数+错误+警告)

    User->>CLI: mdi gen api.md -l pytest
    CLI->>Parser: parse_file("api.md")
    Parser-->>CLI: MDIDocument对象
    CLI->>Gen: generate(doc, output_dir)
    Gen->>Gen: 选择pytest生成器
    Gen->>Gen: 提取示例+检查清单
    Gen->>Gen: 生成Mock数据
    Gen->>Gen: 生成测试用例
    Gen->>FS: 写入test_*.py文件
    Gen-->>CLI: 生成文件列表
    CLI-->>User: 生成结果摘要
```

## 模块依赖关系

```mermaid
flowchart BT
    subgraph 基础层["基础层 (无内部依赖)"]
        M["models.py<br/>数据类定义"]
        U["generators/utils.py<br/>工具函数"]
    end

    subgraph 核心层["核心层 (依赖基础层)"]
        P["parser.py<br/>Markdown解析"]
        V["validator.py<br/>规范验证"]
        MD["mock_data.py<br/>Mock数据生成"]
        EE["example_extractor.py<br/>示例提取"]
        CC["checklist_converter.py<br/>检查清单转换"]
    end

    subgraph 生成器层["生成器层 (依赖核心层)"]
        BG["generators/base.py"]
        PG["generators/python_gen.py"]
        TG["generators/typescript_gen.py"]
        OG["generators/openapi_gen.py"]
        MG["generators/mcp_gen.py"]
        MK["generators/markdown_gen.py"]
        CG["generators/cli_gen.py"]
        PT["generators/pytest_gen.py"]
        JG["generators/jest_gen.py"]
    end

    subgraph 门面层["门面层"]
        GN["generator.py<br/>MDIGenerator门面"]
        VR["versioning.py<br/>版本管理"]
        MC["mcp_domain.py<br/>MCP领域模型"]
        MS["mcp_server.py<br/>FastMCP构建"]
    end

    subgraph 入口层
        INIT["__init__.py<br/>公共API"]
        MAIN["__main__.py<br/>CLI入口"]
    end

    M --> P & V & MD & EE & CC
    U --> BG & PG & TG & OG & MG & MK & CG & PT & JG
    P --> V & GN & VR & MC
    V --> GN
    MD & EE & CC --> PT & JG
    BG --> PG & TG & OG & MG & MK & CG & PT & JG
    PG & TG & OG & MG & MK & CG & PT & JG --> GN
    GN --> INIT
    VR --> INIT
    MC --> MS --> INIT
    INIT --> MAIN
    style 基础层 fill:#e8f5e9
    style 核心层 fill:#e3f2fd
    style 生成器层 fill:#f3e5f5
    style 门面层 fill:#fff3e0
    style 入口层 fill:#fce4ec
```

---

**下一步阅读**：
- [工具链使用指南](04-toolchain-guide.md) - CLI命令参考、Python API、三种Profile使用指南
- [返回生态对比分析](02-ecosystem-comparison.md)
- [返回索引](../mdi-research-report.md)
