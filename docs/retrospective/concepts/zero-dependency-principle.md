> **来源**：从 `docs/retrospective/knowledge-extraction.md` 六、可复用知识概念 拆分

# 零依赖原则（Zero-Dependency Principle）

## 定义
工具脚本仅依赖语言标准库，不引入任何第三方包。

## 适用场景
- 需要频繁执行的 CI 脚本
- 需要在多种环境运行的验证工具
- 项目基础设施级脚本

## 代价
某些功能（如语义匹配、Markdown AST 解析）需自行实现，精度可能不如专用库。

> **关联模块**：
> - `patterns/code-patterns/three-tier-check-tool.md`