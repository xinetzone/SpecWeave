---
okf_version: "0.2"
type: spec
title: "免费大模型API汇总博文→OKF知识包转化规划"
description: "将知乎博文《2026最新免费大模型API汇总》转化为OKF知识包，覆盖国内23平台+国际17平台的免费额度、有效期、代表模型、擅长场景等事实信息"
tags: [okf-bundle, blog-article, llm-api, free-tier, resource-roundup]
generated: { by: "seven-concepts-cmd", at: "2026-09-09T14:17:00+08:00" }
---

# 免费大模型API汇总 → OKF知识包 转化规划

## 1. 内容敏感度预检

| 项目 | 结论 | 依据 |
|------|------|------|
| 来源 | 知乎公开博文 | https://zhuanlan.zhihu.com/p/2050524686992380835 |
| 访问控制 | 无（公开可访问） | 无 share?code=/token=/邀请码参数 |
| 敏感度级别 | **公开内容** | 符合公开内容定义：公开发布的网页/博客 |
| 工作流模式 | **标准 Spec Mode** | 产出物入 `projects/awesome-okf-xs/doc/bundles/jishu/ai/free-llm-api-roundup/` |
| Spec 目录 | `.trae/specs/free-llm-api-roundup-okf-wiki/` | |

## 2. 骨架判定（操作可复现性两问）

| 问题 | 回答 | 理由 |
|------|------|------|
| Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **否** | 文章是表格型资源盘点，无操作步骤、无代码教程 |
| Q2：这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **不适用** | 无操作步骤 |

**判定：两问皆否 → 不设 examples/ 目录**

**内容性质**：资讯速报/资源盘点 → description 标注"非操作教程"

**骨架**：
```
free-llm-api-roundup/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-platform-overview.md    # 平台总览（国内外分区、总量统计）
│   ├── 01-domestic-platforms.md   # 国内平台清单（23家）
│   ├── 02-international-platforms.md # 国际平台清单（17家）
│   └── 03-selection-guide.md      # 选型指南（按场景推荐）
└── references/
    ├── index.md
    ├── article-source.md          # 博文事实清单（F编号双份登记之一）
    └── verification.md            # P0核验报告（含勘误）
```

## 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/domestic-model-token-export/` | ❌ 不选 | 已有 bundle（flagged），主题为"国产模型出口经济"，与本 bundle 主题（免费API资源盘点）完全不同 |
| `jishu/ai/deepseek-pricing/` | ❌ 不选 | 已有 bundle，仅覆盖 DeepSeek 一家，且本 bundle 覆盖40家平台，范围远超 |
| `jishu/ai/` 下新建 `free-llm-api-roundup/` | ✅ 选定 | 同域内唯一覆盖"多平台免费API资源盘点"的子目录，与 deepseek-pricing/context-optimization/token-economy-explosion 形成互补（付费定价↔免费资源↔成本优化↔宏观数据） |

**最终路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/free-llm-api-roundup/`

## 4. 时效性

| 项目 | 结论 |
|------|------|
| 博文发布时间 | 2026-06-17 |
| `stale_after` | **2026-08-17**（2个月，符合资讯速报1-2月标准） |
| 价格/额度变动风险 | **高**（厂商政策随时调整，各额度均为发布时点快照） |
| 已知边界声明 | 所有免费额度、有效期数据以博文发布时点（2026-06-17）为准，后续变动以官方最新公告为准 |

## 5. P0 必核验清单

以下声明默认标为 P0（数字/日期/定价/成效数字），需通过 WebSearch 权威交叉核验：

| F编号范围 | 声明类型 | 核验策略 |
|----------|---------|---------|
| F-001~F-067 | 各平台免费额度数字（Token数、有效期天数） | WebSearch 查各平台官方文档/公告页核对 |
| F-068~F-075 | 发布日期（中国移动MoMA 2026-05、商汤2026-05-08、小米2026-05-12、讯飞星辰2026-03） | 官网/新闻稿验证 |
| F-021 | "可降低30%成本"（中国移动MoMA自宣成效数字） | **厂商自宣，默认P0必核验** |
| F-025 | "推理成本极低"（火山方舟自宣） | 厂商自宣成效，P0核验或标"作者观点" |
| F-069 | Google Gemini 2.5 Flash 1500次/天 | 查 Google AI Studio 官方文档 |
| F-072 | NVIDIA NIM 无限制（已取消额度限制） | 查 NVIDIA Build 官方公告 |
| F-082 | OpenAI 新用户Free Tier | 查 OpenAI 官方 pricing 页面 |
| 选型指南中的表述 | 各推荐是否有权威支撑 | 区分"作者推荐"与客观事实 |

## 6. 信源距离预判

| 平台 | 信源距离 | 备注 |
|------|---------|------|
| 阿里云百炼、腾讯云TokenHub、百度千帆 | 第三方综述 | 博文作者整理汇总，非官方一手发布 |
| 中国移动MoMA、商汤日日新、小米MiMo | 第三方综述（含厂商新闻稿引用） | 有具体发布日期，需溯源新闻稿 |
| DeepSeek官方、智谱AI、Kimi | 部分可能含一手信息 | 博文作者可能参考官方公告 |
| Google AI Studio、NVIDIA Build、Groq、HuggingFace | 第三方综述 | 博文作者汇总，需对照官方文档核验 |
| 选型指南 | 作者观点 | 非官方事实，显式标注 |
| "降低30%成本"等成效数字 | **厂商自宣** | 必须 P0 核验或标"厂商/客户自述" |
