---
id: tasks
title: 《ARM败在哪？RISC-V上车》博文转化任务清单（R→I→E→V→C）
created: 2026-11-04
---

# 任务清单

## R 事实采集与核验

- [x] 阶段0 敏感度预检：公开内容，标准工作流
- [x] WebFetch 提取微信全文（`mp.weixin.qq.com` 反爬常规拦截，本次首次即返回全文，属例外；正文五节+结语已获取）
- [x] F 编号事实采集：[facts.md](facts.md) F-001~F-028（博文）
- [x] 信源距离预判：芯片垂直自媒体产业评论 → 权威产业源交叉核验；识别为"第三方综述/评论转述"，无成效数字可核
- [x] P0/P1 核验（10 项 V1~V10）：RISC-V International 官方站 + 官方 ISA 规范库 + Gasgoo/Hengsen/EEWorld/EET-China/EDN + RISC-V Summit 2023 + AUTOSAR 适配公告（F-029~F-041）
- [x] 勘误与口径核定：0 ❌；3 ⚠️（量产元年媒体框架、换供应商上限非现状、ARM 短期待主流为定性判断）

## I 骨架与拆分

- [x] 操作可复现性两问：①否 ②否 → 产业评论骨架，无 examples/
- [x] 归属：`jishu/iot/riscv-automotive/`（jishu/iot 已有博文核验先例 embedded-weekly-03/xingchen-300-edge-ai/rtx-spark，单篇不新建分组）
- [x] 三层知识拆分：现象层/机制路径层/工程判断层 → 3 篇 concepts

## E Bundle 生成（信源先行）

- [x] references/article-source.md（F 双份登记 F-001~F-041）
- [x] references/verification.md（核验报告 V1~V10 + 口径四清单 + 残余不确定性）
- [x] references/index.md
- [x] concepts/00-supply-chain-autonomy.md
- [x] concepts/01-adoption-path-and-ecosystem.md
- [x] concepts/02-four-industry-realities.md
- [x] concepts/index.md
- [x] log.md
- [x] index.md（最后写）

## V 对抗审查与收尾

- [x] 四视角审查（事实溯源/结构规范/读者可用/时效边界，另加老板视角）
- [x] 双份 F 编号集合正则比对（spec facts.md ↔ article-source.md：各 41、集合相等、F-001~F-041 连续）
- [x] 三级 toctree 门禁（check-toctrees.py：本包 3 级全可达；4 处缺口均为他人在途 WIP，只报不改）
- [x] 相对链接全可达（bundle 9 文件 / 30 链接 0 断链）+ 零绝对本地链接/零家目录路径
- [x] UTF-8 strict（check-utf8.py：12769 文件通过）
- [x] frontmatter 完整（博文 URL + riscv.org + 官方 ISA 规范库三信源）
- [x] 组 index 接入：jishu/iot/index.md 表行 + toctree
- [x] 总索引对账（check-bundles-index.py：9 域/64 组/705 束 五面一致；并发会话先改至 704，本包仅补 +1 未回滚）
- [x] review.md 审查记录

## C 原子提交（待用户确认）

- [ ] 子模块 awesome-okf-xs 内提交（bundle 9 文件 + jishu/iot/index.md + bundles/index.md，显式文件列表）
- [ ] 主仓库提交 spec（.trae/specs/okf-wiki-ecosystem/riscv-automotive-blog-okf-wiki/）
- [ ] 主仓库更新子模块指针（不 push）
