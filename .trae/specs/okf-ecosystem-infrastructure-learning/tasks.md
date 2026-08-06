---
id: okf-ecosystem-infrastructure-learning-tasks
title: OKF 生态基建系统学习 - 实施计划
type: Tasks
timestamp: 2026-08-06
updated: 2026-08-06
status: proposed
---

# OKF 生态基建系统学习 - 实施计划

> 方法论：知识沉淀场景（R→I→E→V→C）。R阶段（四文件夹事实采集）已在 Spec 阶段完成。

## [x] Task 0: 前置阅读 - 熟悉 okf-wiki 现有覆盖边界
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 阅读 okf-wiki 的 README.md、07-resources-and-glossary.md，确认已覆盖内容（OKF v0.2 规范、官方工具链、awesome-okf-analysis）
  - 确认 okf-wiki 现有 frontmatter 风格、子目录组织方式（参考 awesome-okf-analysis 与 knowledge-catalog-wiki）
  - 明确本次补充的"生态基建层"边界，避免与现有文档重复
- **Acceptance Criteria Addressed**: R1（学习覆盖完整性）

## [x] Task 1: 生态资源图谱文档 - awesome-okf 上游生态
- **Priority**: high
- **Depends On**: Task 0
- **Description**:
  - 基于 `.chaos\libs\awesome-okf\README.md` 与 `bundle\index.md`，整理 OKF 生态九大分类（OKF总览/规范/官方工具/示例bundle/社区工具/指南文章/背景起源/LLM-wiki模式/相关格式/社区）
  - 记录 `scripts\build-okf-bundle.mjs` 批转实现原理：README `##` 章节→概念 type 映射表、slug 规则、frontmatter 生成（type/title/description/resource/tags/generated）、保留 index.md/log.md、validate 校验
  - 列出社区工具清单（okft/okf-gem/okf-skills/knowledge-mcp 等）及其用途
- **Acceptance Criteria Addressed**: R1, R2
- **产出**: `okf-ecosystem-wiki/01-ecosystem-map.md`

## [x] Task 2: Bundle 分发注册机制文档 - awesome-okf-kit
- **Priority**: high
- **Depends On**: Task 0
- **Description**:
  - 解析 `registry.yaml` 字段 Schema：name/source_url/description/license/download/category/publisher/repo/okf_version/pages/tags
  - 记录 `okf get <name>` 消费流程（下载 release zip → 校验 → 安装到 `~/.okf/bundles/`）
  - 记录 `scripts\validate_registry.py` 校验规则（必填字段/name kebab-case 正则/download https zip/source_url URL/唯一性）
  - 记录发布流程（okf build → release zip → PR 添加 registry 条目 → CI 校验）
  - 许可证政策（LICENSING.md/TAKEDOWN.md）
- **Acceptance Criteria Addressed**: R1, R2
- **产出**: `okf-ecosystem-wiki/02-bundle-registry.md`

## [x] Task 3: Bundle 工程化模板文档 - okf-bundle-template
- **Priority**: high
- **Depends On**: Task 0
- **Description**:
  - 记录 `build.yml` 工作流：手动触发参数（url/name/max_depth/max_pages/js/path_prefix/all_paths）、`okf build` 命令、README 生成、commit、`okf zip` + `gh release`
  - 记录 `sync.yml` 工作流：每周 cron 同步、state.json 检测、`okf sync` 增量重写、commit + 重打包 release
  - 整理 okf-kit CLI 命令速查（build/sync/zip/get/chat/visualize）
  - 记录 NOTICE.md 许可署名要求与 registry 接入流程
- **Acceptance Criteria Addressed**: R1, R2
- **产出**: `okf-ecosystem-wiki/03-bundle-template.md`

## [x] Task 4: 生态基建导航 README
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 编写 `okf-ecosystem-wiki/README.md`，作为生态基建知识的统一入口
  - 导航表：链接到 01/02/03 主题文档，说明各自定位与阅读路径
  - 与 okf-wiki 通用教程、awesome-okf-analysis 建立互链（相对路径）
- **Acceptance Criteria Addressed**: R2, R3
- **产出**: `okf-ecosystem-wiki/README.md`

## [x] Task 5: 更新 okf-wiki 索引与双向链接
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 在 okf-wiki/README.md 文档索引表中新增 "OKF 生态基建" 入口
  - 在 okf-wiki/07-resources-and-glossary.md 的 7.5 交叉引用表新增条目
  - 在 okf-ecosystem-wiki 各文档中通过相对路径链接 okf-wiki 对应章节
- **Acceptance Criteria Addressed**: R3
- **产出**: okf-wiki/README.md、07-resources-and-glossary.md 更新

## [x] Task 6: 合规与链接验证
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 运行文件名规范检查（kebab-case、纯英文、数字前缀）
  - 运行链接检查脚本验证所有新增链接可达
  - 检查 frontmatter 字段风格与 okf-wiki 一致、相对路径无 file:///
  - 内容非重复性检查（不重复 okf-wiki 已有规范教程/官方工具链/awesome-okf-analysis）
- **Acceptance Criteria Addressed**: R2, R3
- **产出**: 验证报告（通过/修复记录）

# Task Dependencies
- Task 1/2/3 相互独立，可并行（均依赖 Task 0）
- Task 4 依赖 Task 1/2/3
- Task 5 依赖 Task 4
- Task 6 依赖 Task 5