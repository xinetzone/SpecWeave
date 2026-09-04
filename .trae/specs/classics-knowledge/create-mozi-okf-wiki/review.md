# Checklist — 《墨子》OKF 知识包

## 内容正确性
- [x] 《兼爱上》《非攻上》《公输》三篇原文全录与至少 2 个独立权威信源逐字一致
- [x] 全书 53 篇篇目表全覆盖，每篇标注分类（卷首杂论/十论/墨经/言行录/城守）与存亡状态，一句话提要
- [x] 十论"上中下"三篇差异与《韩非子·显学》"墨离为三"三派（相里氏/相夫氏/邓陵氏）对应关系明确
- [x] 墨经六篇、城守十一篇的"后期墨家/归属争议"属性已明确标注，未作墨子本人手笔史实陈述
- [x] 注家谱系（毕沅/孙诒让/梁启超/吴毓江/高亨/谭戒甫）立场标注、出处可溯
- [x] 核心概念解读呈现 ≥2 种注家立场且出处可溯

## 方法论质量门
- [x] G1：facts.md ≥30 条编号事实，纯客观描述（无"因为/导致/所以"），每条带信源 URL
- [x] G2：insights.md ≥3 条四元组洞察（现象+根因+影响+建议）
- [x] G3：≥2 个可复用阅读模式，各含触发场景/核心步骤/反模式/迁移示例
- [x] V：原文抽查 10 处 + 事实抽查 10 条全部通过

## OKF 格式与结构
- [x] 全部新增文档 frontmatter 符合 OKF v0.2（type/source 或 sources/generated/verified/status/stale_after）
- [x] bundle 根 index.md 及各子目录 index.md 均含 toctree 且引用全部文档
- [x] 文件名 kebab-case 纯英文；正文中文；交叉引用为相对路径无断链、无 file:///
- [x] `bundles/think/mozi/` 分组 index 与 toctree 完整
- [x] `bundles/think/index.md` 与 `bundles/index.md` 统计数字、分组表行、toctree、mermaid 节点已同步更新

## 交付验证
- [x] `invoke gates.all`（在 projects/awesome-okf-xs）全部通过（toctrees + utf8）
- [x] 原子提交完成且符合 Conventional Commits；主仓 gitlink 同步处理妥当

## 增量扩展：十论通读计划（Task 10）
- [x] `examples/04-ten-doctrines-reading-plan.md` 已由「上篇 8 篇」扩展为「十论现存 23 篇」通读路径（23 篇篇目总表 + 四阶段顺序 + 亡佚 7 篇提示 + 墨离为三文本分层提示）
- [x] 所据篇目/存佚/主张均回溯 facts.md F-030~F-046，无补造事实；「通读向导非逐字总录」边界已显式标注