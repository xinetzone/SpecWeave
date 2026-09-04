# Checklist

- [x] 目标目录 `.agents/docs/retrospective/reports/task-reports/retrospective-caffe-proto-20260722/` 已创建
- [x] `README.md` 主报告已生成，含 YAML frontmatter 元数据
- [x] `README.md` 保留原有 10 章完整结构，内容不丢失
- [x] `README.md` 中无 `file:///` 绝对路径链接，所有链接使用相对路径
- [x] `insight-extraction.md` 已生成，含≥3 个方法论模式
- [x] 每个方法论模式含完整六要素：触发场景、核心做法、反模式（≥3个）、边界条件、检验标准、迁移示例（≥1个跨领域场景）
- [x] `insight-extraction.md` 含问题模式分析（环境兼容性、API 默认行为）
- [x] `export-suggestions.md` 已生成，含优先级排序表（P0-P4）
- [x] `export-suggestions.md` 含风险矩阵（概率、影响、缓解措施）
- [x] `export-suggestions.md` 含工具推荐列表
- [x] `export-suggestions.md` 含关键文件快速索引
- [x] 索引文件 `task-reports/README.md` 已更新，新增条目
- [x] 新增索引条目包含名称、日期、简要说明和链接
- [x] 链接验证通过：`python .agents/scripts/check-links.py --path .agents/docs/retrospective/reports/task-reports/retrospective-caffe-proto-20260722/` 无断链
- [x] 所有文件编码为 UTF-8，无乱码