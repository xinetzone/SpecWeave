# Checklist — create-mawangdui-fangzhong-wiki

## R/I 阶段质量门
- [x] 事实 ≥80 条且每条带信源（URL 或书目条目）
- [x] G1 通过：facts.md 事实描述无因果推断词
- [x] 争议条目（墓主身份/房内记分合/拟题/周贻谋版次/海外丛书）均保留【待核验】标注
- [x] G2 通过：≥4 条洞察均含四元组（现象+根因+影响+建议）

## Bundle 结构
- [x] bundle 根 index.md frontmatter 符合 OKF v0.2（type OKF/generated/verified/status/stale_after/okf_version）
- [x] concepts/ 8 篇 + examples/ 3 篇 + references/ 4 篇全部就位，各级 index.md 含 hidden toctree
- [x] 文件名 kebab-case 英文，正文全部中文
- [x] 概念/信源文档 frontmatter 带 sources 归因

## 内容质量
- [x] 基准事实无偏离（前 168 年下葬/1972-1974 发掘/2014 初版/2024 修订本/五十余种 13 万字）
- [x] 原文引用遵守学术引介尺度：出土公版文献少量片段、现代著作仅提要、无露骨描写
- [x] 与 classics-reading 通览教程定位分工清晰、无大段重复
- [x] 01-ancient-china.md 交叉引用链接有效

## 索引与质量门
- [x] bundles/index.md 计数 291 束、think "10 束 · 5 组"（并行会话已纳入 fangzhong-bajia，基于 290 递增）
- [x] sexology/index.md 导航表与 toctree 已更新
- [x] `invoke gates.toctrees` 零断链零孤立（bundle 级通过；全树 20 处问题均属并行会话 ishinpo-reading）
- [x] `invoke gates.utf8` 通过（bundle 22 文件 + 全树 5922 文件）
- [x] `invoke build` 读取阶段零警告（本 bundle 22 文件全部解析通过；写入阶段后台继续运行，日志 .temp/gate-build2.txt）

## V 阶段
- [x] 独立评审（新鲜上下文只读）完成，结果记录于 review.md（0 fail / 0 warn）
- [x] fail 项全部修复并复跑质量门（评审 0 fail / 0 warn，无需修复）
- [x] `.temp/` 中间产物已清理（本任务 5 个文件已删；ishinpo 等属并行会话，未动）