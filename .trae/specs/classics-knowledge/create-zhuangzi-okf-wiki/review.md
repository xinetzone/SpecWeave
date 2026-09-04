# Checklist — 《庄子》OKF 知识包教程

## 忠实性检查（原文与作者分层）

- [x] 内篇 7 篇全文逐字经双信源（郭象本系统 + ctext.org）核对，关键异文显式标注"某本作某"并给出处
- [x] 外篇 15、杂篇 11 结构清单完整，名篇精选段落出处可溯
- [x] 教程显式区分"庄子自著内篇 / 门人后学外杂篇 / 注家层"三层，不将传统托名/归属当史实陈述
- [x] 郭象删定 33 篇作为版本源流起点的事实登记准确

## 解读质量检查（多元性与立场标注）

- [x] 覆盖郭象、成玄英、王先谦、郭庆藩、陈鼓应等 ≥5 位注家立场
- [x] 每处核心句解读标注注家与出处
- [x] 核心概念（道/逍遥/齐物/心斋/坐忘/无用之用等）解读不混淆本文与注家引申（尤其区分庄子本文与郭象玄学化注）

## OKF 格式与导航检查

- [x] 所有新增 .md 文件含可解析的 OKF v0.2 YAML frontmatter（`type` 非空）
- [x] bundle 根 `chuang-tzu/index.md` 含 `okf_version: "0.2"` 且以 `{toctree}` 引用全部内容文档
- [x] `think/index.md` 新增 `zhuangzi` 分组导航行 + toctree（已提交入 HEAD）；`bundles/index.md` 的 zhuangzi 行已写入工作区（因并发任务共改此文件，注册收尾由索引维护完成）
- [x] Markdown 交叉引用使用相对路径，无断链、无孤立文档、无 `file:///` 绝对路径
- [x] 文件名 kebab-case 纯英文，正文中文
- [x] scoped `check-toctrees.py` 与 `check-utf8.py`（限 zhuangzi）全通过；全量 `gates.all` 残留报错均在其他并发 bundle（confucian/yinyangjia/buddhism）

## 方法论闭环检查（G1–G4 + V）

- [x] facts.md 56 条编号事实、无因果推断词、每条带信源 URL（G1）
- [x] insights.md 4 条四元组洞察（现象+根因+影响+建议）（G2）
- [x] 4 个可复用阅读模式，各含触发场景/核心步骤/反模式/迁移示例（G3）
- [x] 对抗审查（V）完成原文双源核对与事实抽查，全部与信源一致
- [x] 原子提交（C）单一职责，提交信息符合 Conventional Commits（commit `3beccc7d`）

## 落位检查

- [x] 新增文件位于 `projects/awesome-okf-xs/doc/bundles/think/chuang-tzu/` 与 `think/zhuangzi/index.md`
- [x] 提交发生在 awesome-okf-xs 子模块仓库内（非 SpecWeave 主仓）
- [x] 未修改任何既有 bundle 内容；`doc/bundles/index.md` 的 zhuangzi 行系追加导航（非破坏既有导航）