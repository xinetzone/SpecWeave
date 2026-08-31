# Checklist — 中医经典 OKF 知识包教程

对照 `spec.md` 的 ADDED Requirements 逐项验收。

> 执行说明：《黄帝内经》束按执行决议改为交叉引用 think 域已有教程（think/huangdi-neijing/neijing-reading），tcm 域实际 5 束为 tcm-overview/nanjing/shanghan-zabinglun/shennong-bencaojing/waijing-weiyan；内经文献学事实沉淀进总览束。验收以实际决议口径执行。

## 落位与结构

- [x] 新域 `bundles/tcm/`、分组 `bundles/tcm/classics/`、5 个束（tcm-overview/nanjing/shanghan-zabinglun/shennong-bencaojing/waijing-weiyan，内经交叉引用）目录结构与 spec 决议一致
- [x] 每束含根 index.md（toctree 引用全部内容文档）、concepts/、examples/、references/ 三层结构及各自 index.md、log.md
- [x] `bundles/index.md` 统计同步：total_bundles 300、groups 39、domains 14（frontmatter 与正文一致），mermaid 图含 tcm 节点，toctree 含 `tcm/index`
- [x] `tcm/index.md` 与 `tcm/classics/index.md` 存在且导航完整（含内经交叉引用与推荐阅读路径）

## 权威底本与原文忠实性

- [x] 精读原文（难经选难/伤寒选条/本草经序录与代表药）均经双信源逐字核对（texts/*.md 验证文本，V 审查 10.1 实抽 13 处复核通过）
- [x] 异文处显式标注"某本作某"并给出信源出处，异文在 facts.md 有编号登记（nj/sh/bc 异文均落位束内 references 与精读文档）
- [x] 存目清单完整：难经 81 难题名（正则验证恰好 81 行）、伤寒论 398 条编号索引+金匮 25 篇、本草经三品归属表（V 审查更正为实计 363 条并登记 353/365 口径差异；素问/灵枢 162 篇存目在 think 域内经束，经交叉引用贯通）
- [x] 未精读篇目有存目标记与一句导读，无构拟补全

## 成书与文献学事实诚实呈现

- [x] 内经/难经/本草经的托名性质与成书学说均并列 ≥2 种，标注依据文献（难经成书五说并列）
- [x] 神农本草经的辑复性质显著标注（卢复/孙星衍/顾观光/森立之辑本系统并列，六类差异成体系覆盖）
- [x] 伤寒杂病论流变（王叔和整理→宋代校订→分成二书）与版本系统（宋本/成注本/桂林古本/康平本）如实呈现，不作单一"真本"裁决

## 解读多元性与立场标注

- [x] 核心句解读至少 1 种传统注家 + 1 种现代校注对照，出处可溯（V 审查 10.3 抽查通过；无虚构注文）
- [x] 各束 references/ 含注本分级表（入门/进阶/研究级）
- [x] 无受版权保护现代注本的整段转录（V 审查 10.4 通过，注家对照采用谱系立场登记）

## 医学免责声明与合规

- [x] 每束根 index.md 显著位置有"文献学习资料、非医疗建议"声明（V 审查逐字核对）
- [x] 方药剂量信息均伴随文献记录性质标注（伤寒束声明含"不构成用药指导"）

## OKF 格式与质量门

- [x] 所有新增文档有 OKF v0.2 YAML frontmatter（type 必填、source/generated/verified/status/stale_after 齐备；okf_version 仅束根）
- [x] 文件名 kebab-case 纯英文，正文中文，交叉引用相对路径带 .md 后缀
- [x] 束自包含：本地链接目标均在 bundles/ 树内，无 file:/// 绝对路径（Grep 零命中 + V 审查链接扫描断链 0）
- [x] `invoke gates.all`：UTF-8 检查 6245 文件全过、tcm 4 束 toctree 零错误；gate 拦截的 16 处问题全部来自并行会话 think/buddhism、think/confucian/four-books 中间态文件（非本次变更，不干预）

## 方法论闭环

- [x] facts.md 264 条编号事实（OV/NGJ/NJ/SH/BC 前缀），无因果推断词，每条带信源 URL（G1；V 审查抽 10 条 URL 全部核验通过）
- [x] insights.md 5 条四元组洞察（G2）
- [x] 3 个可复用阅读模式含触发场景/核心步骤/≥3 反模式/迁移示例（G3，完整落入 tcm-overview 束 concepts/05）
- [x] V 对抗审查完成：原文抽查 13 处双源复核、事实抽查 10 条、分层表述与合规审查均有记录（adversarial-review.md；1 BLOCKER 修复：本草经存目 363 条口径更正）
- [x] C 原子提交完成：子模块 6 提交（5 束各一 + 索引一）+ 主仓 2 提交（spec 记录 + gitlink 同步），Conventional Commits 中文描述，UTF-8 存储验证通过
