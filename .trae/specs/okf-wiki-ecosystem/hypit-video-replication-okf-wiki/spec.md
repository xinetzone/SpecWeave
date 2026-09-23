---
status: "draft"
version: "1.0"
---

# Hypit 视频复刻工作流 → OKF Wiki 教程 Spec

## Why

微信公众号文章《一条视频复刻 100 个版本，Hypit 开源了。》介绍 Hypit：让 Coding Agent 分析参考视频，将镜头、字幕、B-roll、特效和语义时间关系复制为可编辑工作流，再替换人物、产品、语言或内容生成多个版本。本任务按公开博文转 OKF Wiki 流程，结合 Hypit 官方仓库与 Skill 文档进行事实核验和三层知识拆分。

## 路由与归属

- 内容敏感度：公开微信公众号文章，无 `token`、`code` 或登录要求。
- 方法论链路：知识沉淀场景，执行 `R→I→E→V`。
- 目标位置：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ai-agent/hypit-video-replication/`。
- 归属理由：Hypit 是面向 Coding Agent 的开源视频工作流 Skill，主线是 Agent 生产工具；`jishu/ai/ai-agent/` 已有 `show-me-skill`、`wigolo`、`openviking` 等非纯源码教程先例。
- 不新建分组：单篇文章不足以支撑新分组。

## 骨架判定

1. 有可照做的安装命令、项目文件夹准备和 Agent 调用方式。
2. 官方仓库提供 Quickstart、示例源文件与运行说明，流程具备可复现性。

结论：两问皆为“是”，保留 `examples/`。

## 交付物

- bundle 根索引、3 篇 concepts、1 篇 example、事实登记、P0 核验报告、日志。
- 更新 `jishu/ai/ai-agent/index.md`、`jishu/ai/index.md` 与 `bundles/index.md` 导航和计数。

## 事实与边界

- 博文中的“1.1 万 Star”是 2026-09-21 页面时点数据，正文标注时效性。
- `$1.15` 是官方 GOAT DEBATE 示例的生产成本，不是 Hypit 普遍成本承诺。
- “100 个版本”“适合广告/TikTok Shop/联盟营销”等是官方定位或作者转述，正文保留信源口径，不扩写为效果保证。
- Seedance、GPT Image、WhisperX、Google Video Intelligence 等第三方服务费用不由 Hypit 本身决定。

