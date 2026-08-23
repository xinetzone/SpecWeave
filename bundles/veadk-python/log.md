# 变更日志

## 2026-08-23

- 初始生成 OKF v0.2 文档 bundle
- 基于 R 阶段事实清单（131 条 veadk-python 源码事实）与 I 阶段 5 个架构洞察生成
- 创建 12 篇概念文档，分入门组（00-05）和进阶组（06-11）：
  - 入门组：概览、Agent 生命周期、AgentBuilder、Agent 类型、配置系统、Runner
  - 进阶组：记忆系统、LLM 模型抽象、知识库、评估系统、CLI 工具集、高级特性
- 创建 1 篇示例文档：快速开始
- 创建 2 篇信源登记文件：源码登记、架构洞察
- 执行 V 阶段验证：结构检查、Frontmatter 检查、链接检查、Grep API 验证、代码示例检查、Index 完整性检查、内容质量检查
- V 阶段验证结果：7 项检查全部通过，25+ 核心 API 在源码中验证存在，64 条内部链接无断链
- V 阶段修复 3 个问题：
  - 03-agent-types.md：F-0128 → F-128（事实编号前导零）
  - 10-cli-tools.md：rl_group → rl（Click group name 修正）
  - 10-cli-tools.md：studio 源文件名 — → cli_frontend.py
- 创建 references/verification-report.md 验证报告
