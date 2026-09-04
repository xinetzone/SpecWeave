# Specs 全局执行看板

> 本目录是 SpecWeave 项目所有规格文档（spec）的指挥中心，按 13 大主题分类组织。本文档由 docgen（C-6）于 **2026-09-04** 自动生成；详细 spec 列表见各主题 README。

---

## 📊 全局状态总览

| 分区 | Spec 数 | 已完成 | 进行中 | 待启动 | 看板 |
|---|---|---|---|---|---|
| [core-foundation](./core-foundation/README.md) | 20 | 18 | 1 | 1 | 🔧 [查看](./core-foundation/README.md) |
| [roles-governance](./roles-governance/README.md) | 9 | 9 | 0 | 0 | ✅ [查看](./roles-governance/README.md) |
| [standards-tools](./standards-tools/README.md) | 48 | 38 | 3 | 7 | 🔧 [查看](./standards-tools/README.md) |
| [readme-branding](./readme-branding/README.md) | 4 | 4 | 0 | 0 | ✅ [查看](./readme-branding/README.md) |
| [docs-restructure](./docs-restructure/README.md) | 16 | 9 | 4 | 3 | 🔧 [查看](./docs-restructure/README.md) |
| [retrospectives-insights](./retrospectives-insights/README.md) | 171 | 140 | 15 | 16 | 🔧 [查看](./retrospectives-insights/README.md) |
| [migration-archival](./migration-archival/README.md) | 15 | 13 | 1 | 1 | 🔧 [查看](./migration-archival/README.md) |
| [okf-wiki-ecosystem](./okf-wiki-ecosystem/README.md) | 116 | 69 | 6 | 41 | 🔧 [查看](./okf-wiki-ecosystem/README.md) |
| [classics-knowledge](./classics-knowledge/README.md) | 45 | 25 | 1 | 19 | 🔧 [查看](./classics-knowledge/README.md) |
| [caffe-framework](./caffe-framework/README.md) | 44 | 33 | 6 | 5 | 🔧 [查看](./caffe-framework/README.md) |
| [xmnn-packaging](./xmnn-packaging/README.md) | 40 | 22 | 9 | 9 | 🔧 [查看](./xmnn-packaging/README.md) |
| [workspace-governance](./workspace-governance/README.md) | 29 | 19 | 2 | 8 | 🔧 [查看](./workspace-governance/README.md) |
| [infra-env](./infra-env/README.md) | 21 | 12 | 2 | 7 | 🔧 [查看](./infra-env/README.md) |
| **合计** | **578** | **411** | **50** | **117** | &mdash; |

**状态**：✓ 已完成 ｜ ! 进行中 ｜ ? 待启动 ｜ — 无 metadata

---

## 📁 主题索引

> 各主题执行看板详见对应 README，按编号进入查看完整 spec 列表。

1. [core-foundation](./core-foundation/README.md) — 20 spec：项目核心基础设施、系统架构、核心功能模块的创建与配置类 spec
2. [roles-governance](./roles-governance/README.md) — 9 spec：智能体角色定义扩展、权限标记、治理规则体系、索引同步相关 spec
3. [standards-tools](./standards-tools/README.md) — 48 spec：文档编写标准、命名规范、自动化检查/验证工具、IDE 适配优化相关 spec
4. [readme-branding](./readme-branding/README.md) — 4 spec：对外展示窗口演进、品牌定位词选型、蓝图与场景展示相关 spec
5. [docs-restructure](./docs-restructure/README.md) — 16 spec：已有文档原子化拆分、主题分类、目录重构、重复消除、命名统一等结构性整理 spec
6. [retrospectives-insights](./retrospectives-insights/README.md) — 171 spec：已完成任务/项目系统性复盘、问题诊断、经验萃取、方法论分析的 spec
7. [migration-archival](./migration-archival/README.md) — 15 spec：外部内容引入、沙箱治理、历史项目迁移、归档体系建立相关 spec
8. [okf-wiki-ecosystem](./okf-wiki-ecosystem/README.md) — 116 spec：外部源码、官方文档、博客文章的知识化转译（OKF 知识包/Wiki 教程）spec
9. [classics-knowledge](./classics-knowledge/README.md) — 45 spec：中西方典籍、道家/中医/数理经典的知识化工程 spec
10. [caffe-framework](./caffe-framework/README.md) — 44 spec：Caffe FFI、pycaffe、算子实现、Docker 镜像与性能优化 spec
11. [xmnn-packaging](./xmnn-packaging/README.md) — 40 spec：wheel 构建、Nuitka 打包、运行时镜像、模型精度验证 spec
12. [workspace-governance](./workspace-governance/README.md) — 29 spec：目录重组、规范整合、子项目管理、工作区模板萃取 spec
13. [infra-env](./infra-env/README.md) — 21 spec：Docker/devcontainer/conda/Jupyter 环境搭建与运维 spec

## 📆 新增 Spec 指南

1. **选择主题**：判断归属 13 大主题之一；跨主题的优先归入最相关主题。
2. **查重**：在对应主题目录下检索是否已有相近 spec，避免近名重复（见 C-5 查重脚本）。
3. **命名**：kebab-case，语义化描述，参考现有命名（如 create-*-wiki-tutorial）。
4. **创建三件套**：spec.md（YAML frontmatter 含 status/title）+ tasks.md + checklist.md。
5. **更新看板**：运行 `python .agents/scripts/docgen.py theme-dashboards` 刷新主题看板，运行 `python .agents/scripts/docgen.py update-spec-readme` 刷新全局总览。

*本看板由 docgen（C-6）于 2026-09-04 生成，后续自动维护。*
