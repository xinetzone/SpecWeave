# Checklist — 《医心方》阅读教程 OKF Wiki

## 结构与导航

- [ ] `doc/bundles/think/medicine/index.md` 分组索引存在，toctree 覆盖新包
- [ ] `think/index.md` 分组导航表与 toctree 含 medicine 条目，域描述文案已更新
- [ ] `doc/bundles/index.md` 统计数字（bundle 数/分组数）与 think 域条目已更新
- [ ] 知识包目录结构齐备：根 index、facts、insights、concepts/、examples/、references/、log.md

## Frontmatter 与格式

- [ ] 全部新增文件携带合规 OKF v0.2 frontmatter（type 必填 + sources/generated/verified/status/stale_after）
- [ ] 文件名全部 kebab-case 纯英文，中文行文
- [ ] 交叉引用使用相对路径，无 `file:///` 绝对路径

## 内容质量（G1/G2）

- [ ] facts.md 零推测、无因果推断词（因为/导致/所以），条目编号且内嵌信源 URL
- [ ] insights.md ≥4 条四元组洞察（现象+根因+影响+建议）
- [ ] 概念文档覆盖：总览、成书与结构、亡佚引书辑佚、版本流传、研究史、选读方法
- [ ] 示例文档含 ≥1 篇辑佚文选读对照与 1 篇阅读计划
- [ ] references 登记写本/刊本/影印本/现代整理本/研究论著，出处类型标注清晰
- [ ] 史实表述（丹波康赖、成书年代、卷数、引书数量）逐条有信源支撑，存疑项已标注

## 交叉引用与回归

- [ ] sexology/classics-reading 仅追加交叉链接，既有文字无删改
- [ ] sexology 包范围无新增断链

## 质量门

- [ ] `check-utf8.py` 退出码 0
- [ ] `check-toctrees.py` medicine 范围零断链零孤立
- [ ] `.temp/` 中间产物已清理

## 提交（用户确认后）

- [ ] 子模块原子提交：显式列文件、UTF-8 无乱码（`git cat-file -p` 验证）
- [ ] 根仓库 gitlink 更新提交
