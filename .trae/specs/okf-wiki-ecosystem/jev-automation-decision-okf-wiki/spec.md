---
title: "Jev 自动化决策引擎 OKF Wiki"
status: "completed"
date: "2026-09-20"
methodology: "seven-concepts-cmd: R -> I -> E -> V"
content-sensitivity: "public"
source: "https://mp.weixin.qq.com/s/40nRaVYdYljYCbwkPCZo7g"
---

# Jev 自动化决策引擎 OKF Wiki

## 范围

将微信公众号《快200倍、输出直接免费！全新AI模型Jev爆火，正在血洗大模型自动化》转化为可溯源的中文 OKF v0.2 知识包，重点解释 Jev 的类型化决策接口、四类应用叙述和工程边界。

## 内容判定

- URL 为公开微信公众号文章，无 `code`、`token` 或登录要求，按公开工作流执行。
- 原文没有完整安装、版本、输入输出和可复现测量流程；不创建 `examples/`。
- 现有 `jev/` bundle 对应另一篇文章，本次新建独立 bundle，避免混淆信源。

## 事实与核验

- F-001～F-024 登记文章元信息、四类场景、文章数字、官方入口及官方机制补充。
- 官方文档确认 System One、三种问题原语、文本状态、Quick Start 和 API 形态。
- 文章的速度、成本、幻觉、候补名单和案例效果均按厂商/文章口径处理；核心宣传结论无法独立复现，bundle 使用 `flagged`。

## 知识地图

1. `concepts/00-system-one-and-jev.md`：从聊天生成到类型化决策。
2. `concepts/01-four-application-patterns.md`：四类场景的状态、判断与外围执行分工。
3. `concepts/02-engineering-boundaries.md`：置信度、回退、端到端成本和证据边界。

## 验收

- 事实双表 F 编号连续且一致。
- 所有数字、模型名和能力声明带事实编号或明确归属。
- `flagged` 警示、四类勘误表和单源边界均写入正文。
- bundle、AI 分组索引和总索引的 toctree 与计数完成同步。
- 未声称运行 API、复现游戏或验证厂商性能。

## 执行记录

- `scripts/check-toctrees.py`：通过。
- `scripts/check-utf8.py`：通过（全子项目快照）。
- 新 bundle 局部链接检查：9 个 Markdown、27 个本地引用，全部通过。
- `scripts/check-bundles-index.py`：本次 bundle 接入后，AI 分组与总数已对齐；全库仍被并发工作树中的 `sheke/` 计数漂移拦截。
- 全 AI 分组扫描未作为本次通过依据：发现其他并发 bundle 的历史断链，不改动无关文件。
