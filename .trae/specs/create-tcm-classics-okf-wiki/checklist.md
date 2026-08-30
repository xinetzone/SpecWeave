# Checklist — 中医经典 OKF 知识包教程

对照 `spec.md` 的 ADDED Requirements 逐项验收。

## 落位与结构

- [ ] 新域 `bundles/tcm/`、分组 `bundles/tcm/classics/`、5 个束（tcm-overview/huangdi-neijing/nanjing/shanghan-zabinglun/shennong-bencaojing）目录结构与 spec 一致
- [ ] 每束含根 index.md（toctree 引用全部内容文档）、concepts/、examples/、references/ 三层结构及各自 index.md、log.md
- [ ] `bundles/index.md` 统计同步：total_bundles 291、groups 33、domains 14，mermaid 图含 tcm 节点，toctree 含 `tcm/index`
- [ ] `tcm/index.md` 与 `tcm/classics/index.md` 存在且导航完整

## 权威底本与原文忠实性

- [ ] 精读原文（内经选篇/难经选难/伤寒选条/本草经序录与代表药）均经 ctext.org + 维基文库双源逐字核对
- [ ] 异文处显式标注"某本作某"并给出信源出处，异文在 facts.md 有编号登记
- [ ] 存目清单完整：素问 81 + 灵枢 81 篇名全录、难经 81 难题名、伤寒论 398 条编号索引、本草经 365 药三品归属表
- [ ] 未精读篇目有存目标记与一句导读，无构拟补全

## 成书与文献学事实诚实呈现

- [ ] 内经/难经/本草经的托名性质与成书学说均并列 ≥2 种，标注依据文献
- [ ] 神农本草经的辑复性质显著标注（孙星衍/顾观光/森立之等辑本系统并列）
- [ ] 伤寒杂病论流变（王叔和整理→宋代校订→分成二书）与版本系统（宋本/成注本/桂林古本/康平本）如实呈现，不作单一"真本"裁决

## 解读多元性与立场标注

- [ ] 核心句解读至少 1 种传统注家 + 1 种现代校注对照，出处可溯
- [ ] 各束 references/ 含注本分级表（入门/进阶/研究级）
- [ ] 无受版权保护现代注本的整段转录（仅信源登记与结论性引用）

## 医学免责声明与合规

- [ ] 每束根 index.md 显著位置有"文献学习资料、非医疗建议"声明
- [ ] 方药剂量信息均伴随文献记录性质标注

## OKF 格式与质量门

- [ ] 所有新增文档有 OKF v0.2 YAML frontmatter（type: OKF、source、generated/verified、status、stale_after）
- [ ] 文件名 kebab-case 纯英文，正文中文，交叉引用相对路径带 .md 后缀
- [ ] 束自包含：本地链接目标均在 bundles/ 树内，无 file:/// 绝对路径
- [ ] `invoke gates.all` 在 projects/awesome-okf-xs 通过（utf8 + toctrees 无断链无孤立文档）

## 方法论闭环

- [ ] facts.md ≥60 条编号事实（OV/NGJ/NJ/SH/BC 前缀），无因果推断词，每条带信源 URL（G1）
- [ ] insights.md ≥3 条四元组洞察（G2）
- [ ] ≥2 个可复用阅读模式含触发场景/核心步骤/≥3 反模式/迁移示例（G3，沉淀于 tcm-overview 束）
- [ ] V 对抗审查完成：原文抽查 ≥10 处双源复核、事实抽查 10 条、分层表述与合规审查均有记录
- [ ] C 原子提交完成：每束一提交 + 索引一提交（Conventional Commits，中文描述"为什么"），主仓 gitlink 同步
