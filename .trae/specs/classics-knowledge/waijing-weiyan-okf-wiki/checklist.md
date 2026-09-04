# Checklist — 《黄帝外经》（外经微言）OKF 知识包教程

对照 `spec.md` 的 ADDED Requirements 逐项验收。

## 落位与结构

- [ ] 新域骨架 `bundles/tcm/index.md`、`bundles/tcm/classics/index.md` 存在，导航完整并注明与 create-tcm-classics-okf-wiki 的衔接（classics 组当前 1 束、未来 6 束）
- [ ] 束 `bundles/tcm/classics/waijing-weiyan/` 含根 index.md（toctree 引用全部内容文档）、facts.md、insights.md、log.md、concepts/（9 篇 + index）、examples/（5 篇 + index）、references/（3 篇 + index）
- [ ] `bundles/index.md` 统计同步：total_bundles 287、groups 33、domains 14；mermaid 图含 tcm 节点；toctree 含 `tcm/index`
- [ ] 文件名 kebab-case 纯英文，正文中文，交叉引用相对路径带 .md 后缀，无 file:/// 绝对路径

## 权威原文与双源核对

- [ ] 13 篇精读原文（卷一 9 篇 + 命门真火篇 + 命门经主篇 + 小心真主篇 + 善养篇）均经维基文库 + 古诗文网/古书网双源逐字核对
- [ ] 异文处显式标注"某本作某"，facts.md 有 WJ-TEX 编号登记与信源 URL
- [ ] 81 篇存目完整：9 卷 × 9 篇篇名与维基文库逐字一致；68 篇非精读各有一句提要与全文链接；精读 13 篇有标记
- [ ] 无构拟补全（存目篇目不虚构原文）

## 文献学事实诚实呈现

- [ ] 汉志《外经》三十七卷已佚（著录层）与今本《外经微言》清抄本（文本层）分层陈述，无混淆
- [ ] 发现史完整：1980 天津发现、清精抄本形态、卷首题署、1984 中医古籍出版社影印 5500 册、嘉庆八年《山阴县志》著录、"嘉庆二十年静乐堂书"朱题（疑后人加）
- [ ] 陈士铎生平与成书年代诸说并列（约 1689–1707 / 1698–1707 / 1698），标注出处
- [ ] 真伪两派并列且各 ≥2 条文献依据（托名派：影印前言、周益新/张芙蓉研究；传承派：梅自强等；余瀛鳌序两说），无单向裁决措辞
- [ ] 傅山传授说标注"何高民考证、学界有异议"

## 解读多元性与立场标注

- [ ] 每篇精读四板块齐全：原文逐段 / 字词注解 / 白话大意 / 学术解读
- [ ] 学术解读含传统视角（篇末"陈士铎曰"微言）与现代研究视角（浅释/林明欣/周益新等结论性引用）双对照，出处可溯
- [ ] 核心概念（颠倒之术、命门水火、顺逆探原）标注思想渊源（道家广成子/温补学派赵献可张景岳/《内经》）
- [ ] 无受版权保护现代注本的整段转录（仅信源登记与结论性引用）
- [ ] 红铅、古代方术等内容附文献性质与批判性说明

## 医学免责声明与合规

- [ ] 束根 index.md 首屏显著位置有"古籍文献学习资料、非医疗建议"声明
- [ ] examples 涉养生/方药处有文献性质标注

## OKF 格式与质量门

- [ ] 所有新增文档有 OKF v0.2 YAML frontmatter（type、source、generated/verified、status、stale_after；束根 index 含 okf_version: "0.2"）
- [ ] 束自包含：本地链接目标均在 bundles/ 树内
- [ ] `invoke gates.all` 在 projects/awesome-okf-xs 通过（utf8 + toctrees 无断链无孤立）
- [ ] `invoke build` 构建成功无警告级错误

## 方法论闭环（G1–G4）

- [ ] facts.md ≥60 条编号事实（WJ-BIB/WJ-TEX/WJ-RES/WJ-SRC 分类），无因果推断词，每条带信源（G1）
- [ ] insights.md ≥3 条四元组洞察（陈述/证据/反常识/行动）+ 知识地图（G2）
- [ ] ≥2 个可复用阅读模式含触发场景/核心步骤/≥3 反模式/迁移示例（G3，沉淀于 08-reading-method.md）
- [ ] V 对抗审查留痕：原文抽查 ≥10 处双源复核、事实抽查 10 条、分层/合规审查记录入 log.md
- [ ] C 原子提交完成：束内容一提交 + 域骨架/索引一提交（子模块内 Conventional Commits 中文主体）+ 主仓 gitlink 同步一提交（G4）