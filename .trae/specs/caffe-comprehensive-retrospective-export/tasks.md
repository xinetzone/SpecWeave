# Tasks

- [x] Task 1: 创建目标目录并导出主报告（README.md）
  - 创建 `.agents/docs/retrospective/reports/task-reports/retrospective-caffe-proto-20260722/` 目录
  - 将 `task-summary-caffe-proto-20260722.md` 内容迁移为 `README.md`，补充 YAML frontmatter 元数据
  - 修复所有 `file:///` 绝对路径链接为相对路径
  - 保留原有 10 章结构，不删减内容
  - 验证：Grep 搜索确认无 `file:///` 残留，链接检查通过

- [x] Task 2: 生成洞察萃取文件（insight-extraction.md）
  - 从主报告第9章提炼 3 个方法论模式（双层架构、Agent 友好路由、自验证代码生成器）
  - 每个模式补充：反模式（≥3个）、边界条件、可迁移性验证（≥1个跨领域场景）
  - 从主报告第5章提炼问题模式分析（环境兼容性、API 默认行为）
  - 验证：每个模式含完整六要素（触发场景、核心做法、反模式、边界条件、检验标准、迁移示例）

- [x] Task 3: 生成导出建议文件（export-suggestions.md）
  - 从主报告第10章提炼优先级排序表（P0-P4）、风险矩阵、工具推荐
  - 补充关键文件快速索引
  - 验证：建议项含优先级、类型、预期收益三要素

- [x] Task 4: 更新索引文件
  - 读取 `.agents/docs/retrospective/reports/task-reports/README.md`
  - 添加 `retrospective-caffe-proto-20260722` 条目（含名称、日期、简要说明、链接）
  - 验证：新增条目链接指向存在的文件

- [x] Task 5: 链接验证与收尾
  - 运行 `python .agents/scripts/check-links.py --path .agents/docs/retrospective/reports/task-reports/retrospective-caffe-proto-20260722/` 验证所有链接
  - 修复所有断链
  - 验证：链接检查通过，无断链报告

# Task Dependencies

- Task 2 依赖 Task 1（需要主报告内容作为萃取来源）
- Task 3 依赖 Task 1（需要主报告第10章内容）
- Task 4 依赖 Task 1、2、3（需要所有文件就位后更新索引）
- Task 5 依赖 Task 1、2、3、4（全部文件就位后验证）
- Task 2 和 Task 3 可并行执行