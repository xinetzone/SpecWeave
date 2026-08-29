# Checklist

## Bundle 结构与规范
- [ ] `agent-skills-spec` bundle 创建于 `doc/bundles/ai/ai-agent/` 下，含 index.md、log.md、concepts/、examples/、references/ 标准结构（AC-R1）
- [ ] 根 index.md 含 `okf_version: "0.2"` 声明（AC-R2）
- [ ] 各子目录 index.md 无 frontmatter 且含 `{toctree}` 块，收录本目录全部内容文档（AC-R2）
- [ ] 所有非保留 .md 文件含有效 YAML frontmatter，type 字段非空（AC-R3）

## 流程纪律
- [ ] references/ 信源文件先于 concepts/examples 生成（AC-R4 / 信源先行）
- [ ] concepts/ 分批生成，每批 ≤7 文件
- [ ] 各级 index.md 在所有内容文档定稿后最后生成（AC-R4 / Index 最后写）
- [ ] facts.md 全部事实编号 F-xxx 且无推断性表述（G1 门）

## 内容质量
- [ ] 文档引用的函数名/类名/CLI 命令经 Grep 验证存在于 skills-ref 源码（AC-R5 / 无虚构 API）
- [ ] 格式规范类声明与 specification.mdx 原文一致
- [ ] 内部交叉链接使用 `/` 开头 bundle-relative 路径，无断链（AC-R6）
- [ ] 正文中文、代码块标注语言、概念/示例文档结尾含"## 相关概念"章节

## 验证与索引
- [ ] `invoke gates.all` 通过（UTF-8 + toctrees）（AC-R8）
- [ ] `ai/ai-agent/index.md` 已更新（total_bundles 30→31、表格行、toctree）（AC-R7）
- [ ] `bundles/index.md` 总索引统计已更新（AC-R7）

## 提交与边界
- [ ] external/ 目录零变更（AC-R9）
- [ ] 子模块 awesome-okf-xs 完成一次原子提交（AC-R9）
- [ ] 主仓库 SpecWeave 完成一次原子提交（spec 同步 + 子模块指针）（AC-R9）
- [ ] 与既有 anthropics-skills / official-skills 知识束无内容重复（定位差异化：开放标准+参考实现）
