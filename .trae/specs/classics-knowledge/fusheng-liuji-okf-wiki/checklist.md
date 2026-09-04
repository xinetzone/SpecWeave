# Checklist：《浮生六记》OKF wiki 教程知识包

## 结构完整性（AC-1）
- [x] bundle 目录下存在 index.md / facts.md / insights.md / log.md
- [x] concepts/ 存在 7 篇概念文档 + index.md
- [x] examples/ 存在 3 篇示例文档 + index.md
- [x] references/ 存在 4 篇信源文档 + index.md
- [x] think/classics/index.md 存在
- [x] 文件总数 ≥ 19（含三级 index）

## 导航与 toctree（AC-2）
- [x] think/classics/index.md 登记 fusheng-liuji-reading/index
- [x] think/index.md 分组表新增 classics 行且 toctree 含 classics/index
- [x] bundles/index.md 更新为 6 束 · 3 组且分组表含经典阅读行
- [x] 每个含子文档目录的 {toctree} 覆盖全部内容文档
- [x] gates.toctrees 通过或手动验证无断链/无孤立文档

## frontmatter 合规（AC-3）
- [x] 全部 .md 含 YAML frontmatter（type/title/description/tags/generated/status/stale_after）
- [x] 根 index 含 okf_version: "0.2"
- [x] 内容文档含 sources 字段溯源到 references
- [x] 无 file:/// 绝对路径链接
- [x] 全文件 UTF-8 无 BOM（gates.utf8 通过或等价检查）

## 事实零臆造（AC-4）
- [x] facts.md ≥ 40 条 F 编号事实，分域编号，无因果推断词
- [x] 关键事实与信源一致（1763 生 / 1808 使琉球 / 1877 初刻 / 俞平伯校本 / 1935 足本 / 1978 吴幅员 / 1989 黄楚香 / 2005 钱泳抄本）
- [x] 争议事实并列异说（沈复卒年、初刻年份、佚文真伪）
- [x] V 阶段对抗审查记录存在

## 内容质量（AC-5 rubric，阈值 ≥ 2.5）
- [x] 事实准确可溯源
- [x] 结构清晰、有读者向路径设计
- [x] 洞察有反常识点（伪书证据链 / 芸娘主体性 / 闲情文脉）
- [x] 精读片段有原文有赏析，版本推荐可操作

## 范式一致性（AC-6 rubric，阈值 ≥ 2.5）
- [x] 结构、frontmatter、叙事口吻、导航样式对齐 boshu-reading
- [x] 新读者可按"快速开始"路径无障碍进入
