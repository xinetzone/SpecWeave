# Checklist — create-fangzhong-bajia-wiki

## R 阶段（事实采集）
- [x] 房中八家书名与卷数逐家与《汉书·艺文志·方技略》原文核对一致（ctext.org 或权威点校本）
- [x] 房中类小序原文已登记且与权威文本一致
- [x] 事实总数 ≥40 条，每条带信源（URL 或权威书目）
- [x] G1 门通过：事实无因果推断词、无主观评价、关键数据完整
- [x] 争议条目（卷数/亡佚时代/佚文归属）已标【待核验】或采用已核实表述

## I 阶段（洞察）
- [x] 洞察 ≥3 条，每条含完整四元组（陈述/证据引事实编号/反常识/行动）
- [x] G2 门通过：洞察不重叠、有反常识性、行动建议可执行

## E 阶段（bundle 产出）
- [x] bundle 根 index.md 含快速导航/分读者路径/定位对比表/学习路径，frontmatter 合法（OKF v0.2）
- [x] facts.md 按四条线分组登记全部事实，编号与信源对应
- [x] insights.md 含洞察与知识地图
- [x] concepts/ 8 篇齐全（00 方技略/01 总表/02 容成务成/03 黄帝系/04 三阳班及其他/05 辑佚链条/06 出土互证/07 现代解读）
- [x] examples/ 3 篇齐全（首次研读/佚文对照/研读计划）
- [x] references/ ≥4 篇信源文档，均带 URL
- [x] 每级 index.md 的 hidden toctree 覆盖全部内容文档
- [x] 文件名 kebab-case 英文、正文中文、路径引用为相对路径（无 file:/// 绝对路径）
- [x] 内容得体：无超出学术引介尺度的摘录或露骨描写（V 阶段通读确认）
- [x] 与 classics-reading 通论无重复冗余（定位对比表明确分工）

## 索引与计数
- [x] sexology/index.md 导航表与 toctree 已加新 bundle
- [x] bundles/index.md 计数 290 束/36 组、think "9 束 · 6 组"、sexology 行更新，三者一致
- [x] classics-reading 两处交叉引用已加（未改既有事实与结论）
- [x] .trae/specs/README.md 与 standards-tools/README.md 看板已登记

## 质量门与收尾
- [x] invoke gates.toctrees 零断链零孤立（退出码 0）
- [x] invoke gates.utf8 通过
- [x] invoke build 本 bundle 不新增警告
- [x] .temp/fangzhong-bajia-research/ 中间产物已清理
- [x] V 阶段独立评审完成，结果记录于 review.md，fail 项已修复并复跑质量门
- [x] 未执行 git commit（除非用户明确要求）
