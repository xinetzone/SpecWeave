---
id: tasks
title: Firecrawl 博文转化任务清单（R→I→E→V→C）
created: 2026-09-16
---

# 任务清单

## R 事实采集与核验

- [x] 阶段0 敏感度预检：公开内容，标准工作流
- [x] browser_use 提取微信全文（mp.weixin.qq.com 反爬，直接浏览器提取 #js_content，4303 字）
- [x] F 编号事实采集：[facts.md](facts.md) F-001~F-034（博文）
- [x] 信源距离预判：第三方编译推介 → 官方 README/API/官网交叉核验；成效数字识别为厂商自述
- [x] 第一轮 P0 核验（19 项）：GitHub API + README + v2.5 发布文（F-035~F-048）
- [x] 第二轮独立深核（两路子代理，F-049~F-063）：commits API/npm/PyPI/官网/SEC
- [x] 勘误捕获与误判修订：F-008 提交日 ❌、F-007 样本限定 ❌；F-038 第一轮 ❌ 经深核改判 ⚠️；合计 26 簇 20✅/5⚠️/2❌

## I 骨架与拆分

- [x] 操作可复现性两问：①是 ②否 → 技术综述骨架，无 examples/
- [x] 归属：`jishu/ai/firecrawl/`（wigolo/browseract 同品类先例，单篇不新建分组）
- [x] 三层知识拆分：事实层/机制层/边界层 → 3 篇 concepts

## E Bundle 生成（信源先行）

- [x] references/article-source.md（F 双份登记 F-001~F-063）
- [x] references/verification.md（核验报告+勘误四清单+误判修订记录）
- [x] references/index.md
- [x] concepts/00-project-and-endpoints.md
- [x] concepts/01-agent-data-workflow.md
- [x] concepts/02-access-license-boundaries.md
- [x] concepts/index.md
- [x] log.md
- [x] index.md（最后写）

## V 对抗审查与收尾

- [x] 四视角审查（事实溯源/结构规范/读者可用/时效边界，另加老板视角）
- [x] 双份 F 编号集合正则比对（spec facts.md ↔ article-source.md：各 63、集合相等、连续）
- [x] 三级 toctree 门禁（check-toctrees.py 通过：引用有效、内容可达）
- [x] 相对链接全可达（含 concepts→兄弟束两级上跳修正）+ 零绝对本地链接/零家目录路径
- [x] UTF-8 strict（check-utf8.py：10412 文件通过）
- [x] frontmatter 完整（博文 + GitHub API + README + 官网 + SEC 多信源）
- [x] 组 index 接入：ai/index.md 表格行 + toctree（修复并行写入拼接损伤与重复行）
- [x] 总索引对账（check-bundles-index.py：555 束/59 组/9 域五面一致；修复并行会话造成的 549/416 二次计数漂移）
- [x] review.md 审查记录

## C 原子提交（待用户确认）

- [ ] 子模块 awesome-okf-xs 内提交（bundle 9 文件 + jishu/ai/index.md + bundles/index.md，显式文件列表）
- [ ] 主仓库提交 spec（.trae/specs/okf-wiki-ecosystem/firecrawl-blog-okf-wiki/）
- [ ] 主仓库更新子模块指针（不 push）
