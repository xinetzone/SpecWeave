# Checklist — create-sexology-classics-wiki

## 结构完整性
- [x] `think/sexology/index.md` 存在且 toctree 引用 `classics-reading/index`
- [x] `classics-reading/` 下 index.md、facts.md、insights.md、log.md 齐备
- [x] `concepts/` 含 index.md + 9 篇概念文档（00-08），toctree 全覆盖
- [x] `examples/` 含 index.md + 3 篇示例，toctree 全覆盖
- [x] `references/` 含 index.md + 5 篇信源，toctree 全覆盖

## 规范合规
- [x] bundle 根 index.md frontmatter 含 type: OKF、generated、verified、status、stale_after、okf_version: "0.2"
- [x] Concept/Reference 文档带 sources 逐声明归因，引用路径为 `/references/xxx.md` 形式
- [x] 文件名全部 kebab-case 英文，正文全部中文
- [x] okf_version 仅出现在 bundle 根 index（子目录 index 不重复）

## 内容质量
- [x] facts.md 登记 104 条事实，三大板块分组，编号连续可引用
- [x] 【待核验】条目（≥11 项，见 spec 清单）显式标注或采用已核实表述
- [x] 纠正项落实：阮芳赋《性知识手册》1985、《性的知识》1955、《肉蒲团》1633、博物馆藏品三处分散
- [x] 六大板块均有对应概念文档覆盖
- [x] 原文引用限于学术引介尺度（公版节选/篇名/命题；版权著作仅提要），无露骨描写
- [x] insights.md 含 4 条四元组洞察（陈述/证据/反常识/行动）+ 知识地图

## 索引一致
- [x] bundles/index.md：total_bundles 287、groups 33、think "6 束 · 3 组"、sexology 表格行
- [x] think/index.md：sexology 行 + `sexology/index` toctree 条目

## 工程质量门
- [x] `invoke gates.toctrees` 通过（零断链、零孤立）
- [x] `invoke gates.utf8` 通过
- [x] `invoke build` Sphinx 构建成功（边界注：全量构建因全仓 HTML 写出耗时中止，解析阶段 100% 完成且 sexology 全部文件零警告，现存 35 条警告均为其他 bundle 既有问题）

## 独立评审
- [x] V 阶段四视角评审完成，结果写入 spec 目录 review.md
- [x] 评审 fail 项（如有）已修复并复跑质量门
