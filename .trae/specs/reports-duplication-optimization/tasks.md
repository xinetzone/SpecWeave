# Tasks

## 任务：复盘报告体系重复内容优化

### Phase 1：重复内容分析

- [x] Task 1.1: 扫描 `docs/retrospective/reports/` 下所有子文件夹，识别所有包含"关联模块引用块"的文档
- [x] Task 1.2: 统计 README.md 中"关联报告"部分的数量和内容
- [x] Task 1.3: 生成重复内容分析报告

### Phase 2：子模块文档优化

- [x] Task 2.1: 批量移除子模块文档末尾的关联模块引用块
  - 目标文档：`export-suggestions.md`、`insight-extraction.md`、`project-overview.md`、`execution-retrospective.md`
  - 移除内容：`> **关联模块**：[project-overview.md]...` 引用块
- [x] Task 2.2: 验证 frontmatter source 字段完整性

### Phase 3：README.md 优化

- [x] Task 3.1: 精简所有 README.md，保留核心"子模块导航"表格
- [x] Task 3.2: 评估并移除冗余的"关联报告"部分（如该信息已可通过导航表访问）

### Phase 4：汇总文件处理

- [x] Task 4.1: 分析汇总 `.md` 文件与子模块的内容重复度
- [x] Task 4.2: 优化汇总文件，保留结构化索引，内容引用子模块

### Phase 5：验证

- [x] Task 5.1: 运行链接检查器验证文档完整性
- [x] Task 5.2: 生成优化前后对比报告

# Task Dependencies

- Task 2.1 依赖 Task 1.1 的分析结果
- Task 3.1 依赖 Task 1.2 的分析结果
- Task 4.1 依赖 Task 1.3 的分析结果
- Task 5.1 依赖 Task 2.1、3.1、4.1 的完成
