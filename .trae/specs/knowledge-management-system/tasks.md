# Tasks

- [x] Task 0: 知识库目录与模板搭建
  - [x] 创建 `docs/knowledge/` 及各分类子目录（operations/、platform/、troubleshooting/、decisions/、best-practices/、scripts/）
  - [x] 创建 `docs/knowledge/template.md` 知识条目标准模板（YAML frontmatter + 正文结构）
  - [x] 创建各分类目录的 `.gitkeep` 文件

- [x] Task 1: 索引自动生成脚本
  - [x] 实现 `docs/knowledge/scripts/generate_index.py`：
    - 递归扫描 `docs/knowledge/` 下所有 `.md` 文件（排除 template.md 和 README.md）
    - 使用正则手动解析每个文件的 frontmatter 元数据
    - 生成 README.md，包含：统计摘要、按类别分组的条目列表（表格）、标签索引、最近更新（TOP 10）、自动生成时间戳、相关资源链接（复盘报告、任务总结）
    - 缺失元数据时输出警告并继续
    - 空知识库时生成占位提示

- [x] Task 2: 知识库 README.md 初始生成
  - [x] 运行 `generate_index.py` 生成初始 README.md
  - [x] README.md 包含"使用指南"章节（如何添加知识条目、如何检索、如何维护）

- [x] Task 3: 示例知识条目
  - [x] 创建 `docs/knowledge/operations/windows-powershell-heredoc.md`：记录 Windows PowerShell 不支持 heredoc 的经验及替代方案
  - [x] 创建 `docs/knowledge/troubleshooting/move-item-access-denied.md`：记录 Move-Item 目录重命名报 Access Denied 的解决方案
  - [x] 创建 `docs/knowledge/decisions/libs-rename-to-vendor.md`：记录 libs/ 重命名为 vendor/ 的架构决策

- [x] Task 4: AGENTS.md 与角色定义集成
  - [x] 修改 `AGENTS.md` 全局核心规则，增加"查阅知识库"条款，引用 `docs/knowledge/README.md`
  - [x] 修改 `.agents/roles/developer.md`，增加"遇到问题时查阅 knowledge/troubleshooting/"条款
  - [x] 修改 `.agents/roles/architect.md`，增加"做技术决策时查阅 knowledge/decisions/"条款
  - [x] 修改 `.agents/roles/reviewer.md`，增加"审查代码时参考 knowledge/best-practices/"条款

- [x] Task 5: 重新生成索引并验证
  - [x] 运行 `generate_index.py` 重新生成完整的 README.md（含示例条目）
  - [x] 验证 README.md 内容完整性（统计、分类、标签、相关资源）

# Task Dependencies
- Task 1 依赖 Task 0（脚本需要目录结构和模板存在）
- Task 2 依赖 Task 1（运行脚本生成 README）
- Task 3 依赖 Task 0（示例条目需要目录结构存在）
- Task 4 独立于 Task 1-3（修改现有文件，不依赖知识库内容）
- Task 5 依赖 Task 1, 3（重新生成包含示例条目的完整索引）
- Task 0, 4 可并行执行