# 将 SpecWeave 工作区集成到 Hermes Agent 的技术指导文档 - 检查清单

> 依据 `spec.md` 的 10 个验收标准（AC-1 ~ AC-10）逐项核对。

## 文档结构
- [x] AC-1: `hermes-agent-integration/` 目录存在，包含 README.md 和编号章节文件（00-06 左右），命名 kebab-case
- [x] AC-2: 每个章节 frontmatter 为 YAML 格式，符合项目当前标准（含 x-toml-ref，category/date/tags/version 迁移至 .meta/toml/）

## 内容覆盖
- [x] AC-3: Hermes 插件接口规范章节清晰阐述插件三类（General/Memory Provider/Context Engine）、发现路径、启用机制、plugin.yaml 字段、register(ctx) 与 tool schema
- [x] AC-4: SpecWeave 能力映射矩阵覆盖 skills/commands/scripts/roles/AGENTS.md/knowledge/vendor，并给出到 Hermes 各类能力的映射
- [x] AC-5: 配置文件设置章节覆盖 `~/.hermes/config.yaml`（plugins.enabled/disabled、memory.provider、context_engine）、HERMES_HOME、project 级 `./.hermes/plugins`
- [x] AC-6: 数据格式转换章节说明 AGENTS.md → plugin.yaml + register(ctx)、知识库 markdown → OKF concept/bundle、tool schema 的转换路径
- [x] AC-7: 权限认证章节覆盖插件 name 消毒/路径安全、manifest_version、HERMES_HOME、API key 环境变量、project 插件权限开启
- [x] AC-8: 调用方式示例章节包含 `hermes plugins install`、`hermes okf ...`、Hermes 会话内工具调用、`with_context` 召回示例
- [x] AC-9: 常见问题章节覆盖插件未发现/未启用/schema 不匹配/provider 单实例/Windows 路径/name 冲突/restart 要求

## 质量合规
- [x] AC-10: 文件间相对链接路径正确；与 hermes-okf-wiki / okf-wiki 的交叉引用指向存在文件
- [x] NFR-2: 单章节 <300 行（原子化）
- [x] NFR-3: 代码/CLI 示例完整可复制，标注预期输出或"示例"
- [x] NFR-4: 版本提示明确（hermes-agent 插件体系、hermes-okf v0.5.9）
- [x] NFR-6: 三级标题使用 x.y 编号格式（1.1、2.3 等）
- [x] NFR-7: 不虚构未公开特性；示例命令明确标注"需验证"
