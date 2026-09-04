# Checklist — create-eastern-western-classics-wiki

## R/I 阶段质量门
- [ ] 事实 ≥60 条且每条带信源（URL 或书目条目）
- [ ] G1 通过：facts.md 事实描述无因果推断词
- [ ] 争议条目（成书年代/署名/伯顿参与者/出版年/放逐原因/中译信息）均保留【待核验】标注
- [ ] G2 通过：≥4 条洞察均含四元组（现象+根因+影响+建议）

## Bundle 结构
- [ ] bundle 根 index.md frontmatter 符合 OKF v0.2（type OKF/generated/verified/status/stale_after/okf_version）
- [ ] concepts/ 8 篇 + examples/ 3 篇 + references/ 4 篇全部就位，各级 index.md 含 hidden toctree
- [ ] 文件名 kebab-case 英文，正文全部中文，路径引用为相对路径（无 file:/// 绝对路径）
- [ ] 概念/信源文档 frontmatter 带 sources 归因

## 内容质量
- [ ] 基准事实无偏离（3-5 世纪区间/三目的/1883 伯顿私人订阅/Doniger & Kakar 2002/约前 2 年出版/公元 8 年放逐）
- [ ] 年代与署名均采用区间性/存疑性表述，无确定性转录
- [ ] 原文引用遵守学术引介尺度：公版古典少量片段、现代著作仅提要、无露骨描写
- [ ] 与 classics-reading 通览教程定位分工清晰、无大段重复
- [ ] 02-eastern-western-classics.md 《欲经》《爱经》两节交叉引用链接有效

## 索引与质量门
- [ ] bundles/index.md 计数按磁盘实际值 +1、think 域束数 +1（组数不变）、sexology 行更新，三者一致
- [ ] sexology/index.md 导航表与 toctree 已更新
- [ ] `invoke gates.toctrees` 零断链零孤立
- [ ] `invoke gates.utf8` 通过
- [ ] `invoke build` 构建成功（警告仅来自其他既有 bundle）

## V 阶段
- [ ] 独立评审（新鲜上下文只读）完成，结果记录于 review.md
- [ ] fail 项全部修复并复跑质量门
- [ ] `.temp/eastern-western-classics-research/` 中间产物已清理
- [ ] 未执行 git commit（除非用户明确要求）
