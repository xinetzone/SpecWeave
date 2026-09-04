# Checklist

- [ ] `think/yangsheng/index.md` 分组索引存在，toctree 引用全部知识包 index
- [ ] `think/index.md` 域导航表与 toctree 已更新养生分组
- [ ] `doc/bundles/index.md` 统计（束数/分组数/总数）与条目已更新且数字准确
- [ ] `yangsheng-classics-reading` 知识包含根 index、facts.md、insights.md、concepts/、examples/、references/（各子目录含 index.md）
- [ ] 所有新增 Markdown 文件 frontmatter 含 `type`（必填）且溯源（sources）/信任（generated/verified）/生命周期（status/stale_after）字段族齐备
- [ ] `facts.md` 全部条目零推测、无因果推断词（G1）
- [ ] `insights.md` 条目含现象+根因+影响+建议四元组（G2）
- [ ] 概念文档覆盖：总览 1 篇 + 经典要义 ≥5 篇 + 谱系 1 篇 + 选读方法 1 篇
- [ ] 示例文档含原文选读对照 ≥1 篇、阅读计划 ≥1 篇
- [ ] references 登记权威版本与整理本，标注出处类型
- [ ] 正文中文、文件名 kebab-case 纯英文、交叉引用全部为相对路径（无 `file:///`）
- [ ] `python scripts/check-toctrees.py` 退出码 0（零断链/零孤立）
- [ ] `python scripts/check-utf8.py` 退出码 0（UTF-8 无 BOM）
- [ ] 未修改 conf.py 等构建配置；变更仅限 spec 范围内文件
- [ ] 原子提交仅在用户确认后执行，每 commit 显式列文件、单一职责、UTF-8 无乱码
