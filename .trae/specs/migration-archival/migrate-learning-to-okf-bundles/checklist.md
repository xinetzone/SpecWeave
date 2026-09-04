# Checklist

## 台账与调研（R）
- [x] facts-ledger.md 生成，条目数等于 learning/ 实测 md 文件数（2124），每条目有处置类型与目标位置
- [x] 10 对重复主题与 5 项部分重叠的处置决定已在台账中登记（执行期另新增 9 组重复登记，veadk 三重重复改判合并）
- [x] 非 md 资源处置已登记（22 项：随迁 13 + 舍弃 9）

## 迁移完整性
- [x] okf-bundles/chaos 10 个已成型包全部重定位，内容零改写，toctree 接线完成（veadk-python 按台账 A2 改判合并回填）
- [x] 10 对重复主题完成合并回填（8 对有独有内容回填、codewhale 空壳登记、agent-skills 并入核验）或确认重复删除，无影子束产生
- [x] 00-10 全部分类主题按映射表迁移完成，无遗漏主题（对抗审查 2124 md 全对账，28 目录文件数守恒 28/28）
- [x] 每个新建/合并束含合规 frontmatter（type 必填、派生物 sources 溯源）、index.md（toctree）、log.md（抽查 15/15 合规）

## 时效性
- [x] 时效敏感束均完成 2026-09 WebSearch 核验，核验记录写入 log.md 或过时标注（deepseek-pricing：官方平价制与束内峰谷表述冲突留痕待复核；onnx：官方 Latest v1.22.0/Opset 27，束内 1.23.0/opset 28 未能确认留痕）

## 洞察（I）
- [x] insights.md 产出，含重复率、时效衰减、分布分析、治理建议四部分

## 隐私脱敏
- [x] 台账已标记全部工作流元数据文件（12 retrospective + 10 seven-concepts-report + 37 log.md = 59 文件）处置方式
- [x] 工作流元数据文件未迁入 bundles，迁入束的 log.md 已重置为迁移事件日志
- [x] 对抗审查阶段隐私复扫零残留（2 处 major 个人路径残留当场修复，复扫 CLEAN）

## 对抗审查（V）
- [x] 独立子代理完成台账对账与内容保真抽查，问题修复并复验（review.md 总判定 PASS 可删源）

## 凭据扫描
- [x] 真实凭据格式扫描零命中（6 组正则 60+ 命中逐一核实，全部为占位符/官方示例/公开默认凭据）

## 源目录删除与上游修复
- [x] docs/knowledge/learning/ 已删除（含 .meta/toml 孤儿元数据与 categories/learning 孤儿分片）
- [x] 主仓库指向 learning/ 的引用全部修复（6360 处改链/文本化），check-links.py learning 断链清零，主仓库 sphinx-build 零新增错误

## 门控与提交（C）
- [x] 子模块门控：utf8 exit 0；bundles exit 0（9 域/56 组/497 束五面一致，门控重算）；toctrees 本迁移范围零新增错误（剩余 12 处均为并行会话 agent-platform-notes/yishu-vocal 遗留，已逐条核实归属）；sphinx reading 100% 且全部警告与本迁移文件交集为 0
- [x] bundles/index.md 计数与目录树三角一致（以门控重算为准，禁止手填）
- [x] 子模块原子提交完成（c57848410：add 与 commit 分离，暂存集逐文件核对 VIOLATIONS=0，并行会话文件零混入）
- [x] 主仓库提交完成：4a3a04e48（删除+上游修复）+ 0f93fb4c2（子模块指针 bump 2b716df7c→c57848410）；未 push
