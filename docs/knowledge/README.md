---
type: Reference
title: "项目知识库"
---

# 项目知识库

项目知识库的统一入口页。详细分类条目与标签检索已拆分到独立索引，避免根 README 持续膨胀。

- **总条目数**：475
- **分类数**：25
- **标签数**：829

## 快速导航

| 顶层分类 | 条目数 | 入口 |
|----------|--------|------|
| architecture | 1 | [architecture](categories/architecture.md) |
| best-practices | 49 | [best-practices](best-practices/README.md) |
| cake-cutting-rule | 7 | [cake-cutting-rule](categories/cake-cutting-rule.md) |
| decisions | 6 | [decisions](decisions/README.md) |
| docs | 10 | [docs](categories/docs.md) |
| examples | 6 | [examples](categories/examples.md) |
| generative-media-pipeline | 6 | [generative-media-pipeline](categories/generative-media-pipeline.md) |
| knowledge | 20 | [knowledge](categories/knowledge.md) |
| mindfulness-positivity | 6 | [mindfulness-positivity](categories/mindfulness-positivity.md) |
| monetization-direction | 11 | [monetization-direction](categories/monetization-direction.md) |
| operations | 26 | [operations](operations/README.md) |
| platform | 1 | [platform](categories/platform.md) |
| research | 1 | [research](categories/research.md) |
| short-video-skills | 6 | [short-video-skills](categories/short-video-skills.md) |
| social-relations | 1 | [social-relations](categories/social-relations.md) |
| standards | 1 | [standards](categories/standards.md) |
| tech | 88 | [tech](tech/README.md) |
| troubleshooting | 4 | [troubleshooting](troubleshooting/README.md) |
| unknown | 218 | [unknown](categories/unknown.md) |
| what-is-life | 7 | [what-is-life](categories/what-is-life.md) |

## 辅助索引

- [分类总索引](category-index.md)：查看全部分类及条目摘要
- [标签索引](tags/README.md)：按关键词标签分片检索

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [openKylin 知识枢纽：官方文档导读、发行版对比与工程沉淀](tech/openkylin/index.md) | 2026-10-22 | tech |
| [openKylin WSL 开发工具包（okw）](tech/openkylin/references/wsl-devkit-guide.md) | 2026-10-22 | tech |
| [生成式媒体生产管线：从静帧到成片的六条工程做法](generative-media-pipeline/index.md) | 2026-10-20 | generative-media-pipeline |
| [首帧保真：图生视频链路里的锚点前置](generative-media-pipeline/concepts/01-anchor-frame-fidelity.md) | 2026-10-20 | generative-media-pipeline |
| [水印去除与编码兜底：让成片绕开平台标记与本机依赖缺失](generative-media-pipeline/concepts/02-watermark-and-codec.md) | 2026-10-20 | generative-media-pipeline |
| [文字渲染与限流降级：字幕字体的选型方法与 429 失败后的降级路径](generative-media-pipeline/concepts/03-text-rendering-and-fallback.md) | 2026-10-20 | generative-media-pipeline |
| [组装即代码：把时间轴写成段落表，让缺口显式、规格与产物可对读](generative-media-pipeline/concepts/04-assembly-as-code.md) | 2026-10-20 | generative-media-pipeline |
| [证据与成本基线](generative-media-pipeline/references/evidence-and-costs.md) | 2026-10-20 | generative-media-pipeline |
| [做短视频的 Skill 全景调研：从零到发布的多智能体流水线教程](short-video-skills/index.md) | 2026-10-20 | short-video-skills |
| [生态全景与 Agent Skills 规范](short-video-skills/concepts/01-landscape-and-spec.md) | 2026-10-20 | short-video-skills |
| [生产管线与选型：工序五段·双范式选型法](short-video-skills/concepts/02-pipeline-and-selection.md) | 2026-10-20 | short-video-skills |

## 相关资源

### 回溯报告

- [双体系引用收敛台账（ACT-5）](../retrospective/cross-reference-ledger.md)
- [🔄 复盘与模式库](../retrospective/index.md)
- [变更日志](../retrospective/log.md)

## 使用指南

### 如何添加知识条目

1. 在 `docs/knowledge/` 下选择对应的分类目录（如 `operations/`、`learning/` 等）
2. 复制 `template.md` 作为模板，创建新的 `.md` 文件
3. 填写 YAML frontmatter 元数据（标题、分类、标签、日期、摘要等）
4. 在正文中按照模板结构编写内容
5. 运行 `python scripts/generate_index.py` 重新生成入口页、分类索引与标签分片

### 如何检索

- **按分类入口**：优先使用上方「快速导航」进入各主题 README
- **按全部分类**：打开 [分类总索引](category-index.md) 查看所有分类及摘要
- **按标签检索**：打开 [标签索引](tags/README.md) 后进入对应分片页面
- **按时间排序**：查看本页「最近更新」章节，了解最新添加的知识条目
- **全文搜索**：在项目根目录使用 `rg "关键词" docs/knowledge/` 进行全文搜索

### 如何维护

- **定期整理**：每月检查一次知识条目，更新过时内容，补充遗漏信息
- **标签规范化**：使用统一的标签命名，避免同义词分散（如 `powershell` 和 `ps`）
- **及时归档**：完成任务或解决问题后，及时将经验沉淀为知识条目
- **索引更新**：每次添加、修改或删除知识条目后，运行本脚本重新生成全部索引

---

*索引自动生成于 2026-10-20 15:41:37*
