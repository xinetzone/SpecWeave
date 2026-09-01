# Checklist

## G0 信源稳定性
- [ ] `source-versions.md` 记录全部 12 个仓库的 commit hash + 分支 + 盘点日期
- [ ] 文档与 facts 中信源路径全部指向 `external/dao/action/Textualize/<repo>`（无临时段、无 file:///）
- [ ] 任务期间信源未被 pull/切换分支

## G1 事实采集（R）
- [ ] rich/textual 深度仓库核心模块全覆盖，中度仓库架构+核心用法覆盖
- [ ] 事实全部编号 F-xxx，无"用于/目的是/设计为"等推断性表述
- [ ] 每个事实指向具体源码文件路径

## G2 架构洞察（I）
- [ ] 3-5 个洞察四元组完整（陈述/证据/反常识/行动）
- [ ] 知识地图含分组学习路径，每篇概念文档标注覆盖的 F-xxx 编号

## G3 批量生成（E）
- [ ] references/ 12 个信源登记先于 concepts/ 生成，含 commit hash
- [ ] 分批生成，每批≤7文件
- [ ] 根/子目录 index 最后生成；每个 index.md 含 `{toctree}` 块且收录本目录全部内容文档
- [ ] 仅根 index.md 含 okf_version frontmatter；子目录 index 无 frontmatter
- [ ] frontmatter 必填字段完整（type/title/description/tags/generated/verified/status/stale_after/sources）
- [ ] 交叉链接统一 `/` 开头 bundle-relative 路径；代码块标注语言

## G4 独立验证（V）
- [ ] 文档引用的每个类名/方法名经 Grep 信源验证存在（无虚构 API）
- [ ] 全部"X个/Y份"计数断言经 Glob/Grep 独立复核一致
- [ ] 链接无断裂、toctree 导航链完整
- [ ] `check-source-path-stability.py` audit rc=0（或命中项经"历史记录 vs 活动引用"分流）
- [ ] 验证报告已产出，问题逐一修复并复验

## 覆盖度
- [ ] rich 概念文档 5-6 篇 + 示例 2-3 篇
- [ ] textual 概念文档 5-6 篇 + 示例 2-3 篇
- [ ] 7 个中度仓库各 2 篇概念文档
- [ ] 3 个轻度仓库并入生态总览文档
- [ ] log.md 记录变更

## C 阶段
- [ ] 回顾记录（顺利点/问题点/反模式）写入 `<spec-dir>/retrospective.md`
