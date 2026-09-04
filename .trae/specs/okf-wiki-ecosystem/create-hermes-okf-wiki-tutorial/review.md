# Hermes OKF Wiki 教程 - 验收检查清单

> **方法论**：seven-concepts 知识沉淀场景（R→I→E→V→C）。本清单对应用户场景的可用性检查与质量门。

## 目录与格式检查

- [ ] AC-1: `hermes-okf-wiki/` 目录存在，包含 README.md 和 00-07 编号章节文件
- [ ] AC-2: 所有章节 frontmatter 使用 YAML 格式，字段与现有原子化 wiki 一致（id/title/source/description/tags/category/date/status）
- [ ] 文件命名符合 kebab-case 规范（无中文字符）

## 内容覆盖检查

- [ ] AC-3: 项目定位与 OKF 生态背景阐述清晰（与 throughline/okf-harness/echoes-vault 对比）
- [ ] AC-4: 核心特性覆盖完整（10 项：Agent Memory/Knowledge Graph/Filesystem-First/Zero-DB/Hermes Plugin/Hermes-Ready/Resume/Portable/Config Validator/Git History）
- [ ] AC-5: 五层架构阐述清晰（Human Interface/Hermes Plugin/Universal Provider/Core OKF/Persistence）
- [ ] AC-6: 快速上手可实操（pip install → install-plugin → validate-config → memory setup → 卸载）
- [ ] AC-7: Hermes 插件 CLI 命令完整（hermes okf search/list/show/snapshot/restore）
- [ ] AC-8: 独立 CLI 命令完整（init/validate/list/show/search/log/diff/revert/log-append/graph/snapshot/context/sessions/plans/tools）
- [ ] AC-9: Agent 集成代码示例正确（HermesMemoryMixin/@memorize_decision/@memorize_tool/with_context）
- [ ] AC-10: RAG 集成代码示例正确（LangChain + Chroma，标注 `pip install hermes-okf[rag]`）
- [ ] AC-11: 故障排查覆盖 5 个问题（install-plugin 失败/memory setup 不显示/show 错误模型/bundle 未找到/Windows 文件名）
- [ ] AC-12: Roadmap 15 项特性状态清晰 + 术语表覆盖核心术语

## 图表与链接检查

- [ ] AC-13: Mermaid 架构图语法正确、可正常渲染
- [ ] AC-14: 文件间相对链接有效、无断链；okf-wiki/README.md 已添加 hermes-okf-wiki 入口

## 质量门（seven-concepts）

- [ ] G3（模式可迁移）：教程含触发场景、核心步骤、反模式（如插件 vs 装饰器选错）、迁移验证
- [ ] G4（行动项原子化）：每个章节单一职责、可独立验证、有明确验收标准
- [ ] 版本提示明确：hermes-okf v0.5.9，OKF 生态早期，API 可能演进
- [ ] 内容基于官方公开资料，无虚构未公开特性，命令与版本号有据可查

## 验证命令

- [ ] `python .agents/scripts/check-links.py` 通过（无断链）
- [ ] `python .agents/scripts/check-filename-convention.py` 通过（命名规范）