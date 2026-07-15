---
id: mdi-versioning-best-practices
title: MDI研究报告 - 版本控制与变更管理最佳实践
source: "mdi-research-report.md#6-版本控制与变更管理最佳实践"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/mdi-research/05-versioning-best-practices.toml"
---

# 版本控制与变更管理最佳实践

## 语义化版本规范

MDI文档遵循SemVer 2.0语义化版本规范，版本号格式为`MAJOR.MINOR.PATCH`：

| 版本层级 | 触发条件 | 示例场景 |
|---------|---------|---------|
| **MAJOR** | 破坏性变更 | 删除接口、删除参数、参数类型不兼容变更、必填参数新增 |
| **MINOR** | 向后兼容功能新增 | 新增接口、新增可选参数、新增响应状态码、新增错误码 |
| **PATCH** | 向后兼容问题修复 | 描述文本修正、示例更新、错别字修复、文档格式调整 |

## 变更严重性判定规则

```mermaid
flowchart TD
    Change["接口变更"] --> DelInterface{"删除接口?"}
    DelInterface -->|"是"| MAJOR["MAJOR版本"]
    DelInterface -->|"否"| DelParam{"删除参数?"}
    DelParam -->|"是"| MAJOR
    DelParam -->|"否"| ParamTypeChange{"参数类型<br/>不兼容变更?"}
    ParamTypeChange -->|"是"| MAJOR
    ParamTypeChange -->|"否"| AddRequiredParam{"新增必填<br/>参数?"}
    AddRequiredParam -->|"是"| MAJOR
    AddRequiredParam -->|"否"| DelResponse{"删除响应<br/>状态码?"}
    DelResponse -->|"是"| MAJOR
    DelResponse -->|"否"| AddInterface{"新增接口?"}
    AddInterface -->|"是"| MINOR["MINOR版本"]
    AddInterface -->|"否"| AddOptionalParam{"新增可选<br/>参数?"}
    AddOptionalParam -->|"是"| MINOR
    AddOptionalParam -->|"否"| AddError{"新增错误码<br/>或响应?"}
    AddError -->|"是"| MINOR
    AddError -->|"否"| DescChange{"描述/文档<br/>变更?"}
    DescChange -->|"是"| PATCH["PATCH版本"]
    DescChange -->|"否"| NoChange["无版本变更"]
    style MAJOR fill:#ffcdd2
    style MINOR fill:#fff9c4
    style PATCH fill:#c8e6c9
```

## 推荐工作流

```mermaid
flowchart LR
    A["修改MDI文档"] --> B["运行validate<br/>确保无错误"]
    B --> C["运行diff<br/>对比变更"]
    C --> D{"根据建议<br/>更新版本号"}
    D --> E["重新生成<br/>所有下游产物"]
    E --> F["运行测试<br/>确保无回归"]
    F --> G["原子提交"]
    G --> H["更新Changelog"]
    style A fill:#e3f2fd
    style D fill:#fff9c4
    style F fill:#c8e6c9
```

## Commit Message规范

遵循Conventional Commits规范，结合MDI变更类型：

| Commit类型 | 对应版本变更 | 示例 |
|-----------|-------------|------|
| `feat(api):` | MINOR版本 | `feat(api): 添加用户搜索接口` |
| `fix(api):` | PATCH版本 | `fix(api): 修正用户名字段描述` |
| `refactor(api)!:` | MAJOR版本 | `refactor(api)!: 删除旧版认证接口` |
| `docs:` | PATCH版本 | `docs: 更新API使用示例` |
| `test:` | 无版本变更 | `test: 添加登录接口测试用例` |

## Changelog自动生成

使用`mdi diff --json`命令可以自动生成结构化的变更日志，建议在CI/CD流水线中集成：

```bash
# 生成当前版本与上一版本的diff报告
python -m mdi diff docs/api-v1.0.0.md docs/api-v1.1.0.md --json --bump > changelog/v1.1.0.json
```

---

**下一步阅读**：
- [未来演进方向](06-future-evolution.md) - 短期/中期/长期规划
- [返回工具链指南](04-toolchain-guide.md)
- [返回索引](../mdi-research-report.md)
