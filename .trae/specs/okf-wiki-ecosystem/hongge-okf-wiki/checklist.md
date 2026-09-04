---
title: 红歌教学知识包 OKF wiki - 验证清单
session: sc-20260902-hongge-okf-wiki
created: 2026-09-02
---

# 红歌教学知识包 OKF wiki - Verification Checklist

## 结构与规范
- [x] CP-1: `doc/bundles/yishu/hongge/index.md` 与 `doc/bundles/yishu/hongge/hongge-pedagogy/` 束目录存在，束含 concepts/examples/references 三子目录
- [x] CP-2: 束根 index.md 的 frontmatter 含 `type: OKF` 与 `okf_version: "0.2"`；分组 index.md 为 `type: group`；其余文件均有非空 type 且无 okf_version
- [x] CP-3: 全部 .md 为 UTF-8 无 BOM、frontmatter YAML 可解析、双引号字段内无 ASCII 双引号
- [x] CP-4: 文件名 kebab-case、正文中文、交叉引用全部为相对路径且无 file:/// 链接
- [x] CP-5: toctree 只链接已存在文件，无"待补"挂空链接

## 内容完整性
- [x] CP-6: concepts/ 含 00-09 共 10 篇 + index.md；examples/ 含 3 篇 + index.md；references/ 含 3 篇 + index.md；facts.md、insights.md 齐备
- [x] CP-7: facts.md 事实 ≥60 条、编号连续、每条含信源 URL 与信源层级标注；P0 双源核验表 ≥15 行覆盖曲目/课标/法条/柯尔文史实
- [x] CP-8: insights.md 洞察 ≥5 条，每条含现象/根因/影响/建议四要素并回指 F 编号
- [x] CP-9: 四大需求全覆盖——曲谱库（02/09 + examples/02）、教学型赏析（03/04/05/06）、歌谱（02/09/references/02 + 教案谱例指引）、手势×声乐（07/08 + examples/01 练声环节）
- [x] CP-10: 与 vocal/meitong-yanyin-pedagogy 束的交叉引用链接有效且语义相关

## 事实与合规（人审）
- [x] CP-11: 抽审 10 条事实 URL 可访问、信源为权威站点；曲目词曲作者/年份/出处无差错
- [x] CP-12: 无保护期内完整曲谱/歌词转录；examples/02 含版权自查表；曲谱获取全部指向正版/公版渠道
- [x] CP-13: 柯尔文七音手势描述（手型/空间位置）与柯达伊体系权威资料一致；无 AI 生成手势示意图
- [x] CP-14: 全束无个人姓名、无聊天原文、无政治表述差错

## 教学可用性（人审）
- [x] CP-15: examples/01 教案 45 分钟环节闭环（手势练声→赏析→视唱→演唱处理→作业），可直接打印备课
- [x] CP-16: 零基础读者从 concepts/00 入门地图出发路径清晰，术语首现均有解释

## 配图
- [x] CP-17: `doc/_static/bundles/yishu/hongge/images/` 下 hongge-group-hero.jpg 与 hongge-pedagogy-cover.jpg 存在且被索引页正确引用
- [x] CP-18: 图片无文字乱码、无真实政治人物肖像、风格与 gui 先例装饰定位一致

## 对抗审查
- [x] CP-19: V 阶段四视角审查意见 ≥5 条（含文件定位），≥2 条修正已落盘并复验无断链

## 门控与构建（programmatic）
- [x] CP-20: `conda run --no-capture-output -n py314 invoke gates.utf8` 全绿
- [x] CP-21: `conda run --no-capture-output -n py314 invoke gates.toctrees` 全绿（无断链/孤立文档）
- [x] CP-22: `conda run --no-capture-output -n py314 invoke gates.bundles` 全绿（束/组/域计数一致；hongge 组与 hongge-pedagogy 束被识别）
- [x] CP-23: `bundles/index.md` 与 `yishu/index.md` 五面对账一致（frontmatter/域节/分组表/toctree/mermaid）
- [x] CP-24: 定向 sphinx dummy 构建 0 error、无与新增文件相关警告
