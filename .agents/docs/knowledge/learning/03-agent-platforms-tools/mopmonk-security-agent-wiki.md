---
id: "mopmonk-security-agent-wiki"
title: "MopMonk 安全 Agent Wiki 教程"
source: "https://mp.weixin.qq.com/s/Y_8DYQGuxgHdiw-a74ZN0w"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/mopmonk-security-agent-wiki.toml"
---
# MopMonk 安全 Agent Wiki 教程

> **原文来源**: [微信公众号文章](https://mp.weixin.qq.com/s/Y_8DYQGuxgHdiw-a74ZN0w)

---

## 概述

2026年6月底，一个名为 **MopMonk**（中文代号"扫地僧"）的神秘AI Agent突然出现在全球AI安全领域最权威的评测榜单——CyberGym上，以 **73.1%** 的漏洞复现成功率一举夺得 **全球第七名、中国第一名** 的成绩。本教程系统解析MopMonk的核心技术架构和设计思想，帮助读者理解AI安全Agent的前沿实践。

**核心认知**：模型能力只是入场券，Agent执行力（Harness+记忆+流程）才决定胜负。

---

## 目录导航

| 序号 | 章节 | 文件 | 内容概要 |
|---|---|---|---|
| 00 | 教程概述与学习目标 | [mopmonk-security-agent-wiki/00-overview.md](mopmonk-security-agent-wiki/00-overview.md) | MopMonk背景介绍、学习目标、前置知识要求 |
| 01 | 核心概念解析（一） | [mopmonk-security-agent-wiki/01-core-concepts.md](mopmonk-security-agent-wiki/01-core-concepts.md) | CyberGym基准、Harness协调层、PoC差分验证 |
| 02 | MiniMax M3基座 | [mopmonk-security-agent-wiki/02-minimax-m3.md](mopmonk-security-agent-wiki/02-minimax-m3.md) | 国产开源六边形战士的能力特点与基准成绩 |
| 03 | 三大核心技术 | [mopmonk-security-agent-wiki/03-core-technologies.md](mopmonk-security-agent-wiki/03-core-technologies.md) | 结构化记忆、记忆驱动挖掘、多Agent并行探索 |
| 04 | 步骤式学习导读 | [mopmonk-security-agent-wiki/04-learning-guide.md](mopmonk-security-agent-wiki/04-learning-guide.md) | 入门/进阶/深入三层学习路径 |
| 05 | 常见问题解答 | [mopmonk-security-agent-wiki/05-faq.md](mopmonk-security-agent-wiki/05-faq.md) | 6个高频FAQ问题 |
| 06 | 相关资源链接 | [mopmonk-security-agent-wiki/06-resources.md](mopmonk-security-agent-wiki/06-resources.md) | 论文、代码仓库、媒体报道等资源 |

---

> **最后更新**：2026年7月
>
> 本教程基于MopMonk GitHub技术报告和公开媒体报道编写，所有数据均来自公开可验证的来源。
