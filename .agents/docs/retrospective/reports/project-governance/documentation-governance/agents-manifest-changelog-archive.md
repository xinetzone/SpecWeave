---
id: "agents-manifest-changelog-archive"
title: "AGENTS Manifest 历史变更归档"
source: "../../../../../../AGENTS.md#历史归档"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/agents-manifest-changelog-archive.toml"
---
# AGENTS Manifest 历史变更归档

## 归档说明

本文件归档原位于项目根 `AGENTS.md` 末尾的历史变更记录。

归档目的：

- 保持 `AGENTS.md` 作为启动入口与路由索引的单一职责
- 将历史演进记录下沉到 `.agents/docs/` 文档治理语境中统一维护
- 避免根入口持续膨胀为“规范入口 + 历史仓库”的混合文档

## 归档记录

- 2026-07-13 | feat | Task 0：工作区发现与提示词自举协议落地——新增工作区发现协议（五步发现流程、根工作区零安装自举、AGENTS.md最小可行子集规范）、提示词自举协议（一句话装载、8条安全规则、环境自适应路径选择、7个边界情况处理）；AGENTS.md新增「快速开始：一句话装载」章节，内嵌可复制通用引导提示词；核心规范入口表新增两个协议入口。来源：agent-app-marketplace spec Task 0
- 2026-07-13 | docs | 核心数据自动更新：提交数1313+、模式441+、脚本309+、Skill16个、规则133+、指令集10个、核心规范入口22项、GitCode Stars4、Forks2、Issues0、PRs0。来源：docgen.py stats 自动统计
- 2026-07-12 | docs | 核心数据自动更新：提交数1311+、模式438+、脚本309+、Skill16个、规则133+、指令集10个、核心规范入口22项、GitCode Stars4、Forks2、Issues0、PRs0。来源：docgen.py stats 自动统计
- 2026-07-12 | refactor | 第一性原理全面复盘更新：核心规范入口表从15项扩展至22项，补全 L0入门指南、L1能力注册中心、Skill门面、检查清单、工具配置、协作环境、系统架构、复用案例等新增模块；开发规范补充修复闭环、三阶段递进、简单任务验证、路径引用规范等关键规则；数据更新至1290+次提交节点。来源：第一性原理+全项目复盘
- 2026-07-11 | feat | AGENTS.md 启动协议新增步骤 2.3「内容敏感度预检」：判定公开/私域内容级别，私域内容跳过 `.trae/specs/` 公共规划区域直接进入 `playground/`；步骤 3.5 自检清单新增敏感度确认项；配套规则见 [.agents/rules/content-sensitivity-precheck.md](../../../../../rules/content-sensitivity-precheck.md)。来源：联想AI妙记私域网页分析复盘
- 2026-07-01 | refactor | AGENTS.md 原子化：将全局核心规则拆分为 .agents/global-core-rules.md，上下文路由表拆分为 .agents/context-routing.md，删除重复的能力边界/开发规范内容（已有独立文件），AGENTS.md 精简为入口索引（296行→约70行）；修复启动协议代码块嵌套导致Markdown链接不渲染的问题
