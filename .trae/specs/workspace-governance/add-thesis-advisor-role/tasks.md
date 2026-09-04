# Tasks

- [x] Task 1: 创建角色元数据 TOML 文件
  - [x] SubTask 1.1: 创建 `.meta/toml/.agents/roles/thesis-advisor.toml`，字段包含 id="thesis-advisor"、domain="academic"、layer="guidance"、tier="standard"
  - [x] SubTask 1.2: 在 bindings 中声明相关 rules、references、skills（指向学术写作相关参考与工具规范）

- [x] Task 2: 创建角色定义 Markdown 文件
  - [x] SubTask 2.1: 创建 `.agents/roles/thesis-advisor.md`，写入 YAML frontmatter（id/title/x-toml-ref/source）
  - [x] SubTask 2.2: 编写 Description 段落，定位为面向语言学及应用语言学专业的毕业论文写作指导者
  - [x] SubTask 2.3: 编写 Responsibilities 段落，按六阶段（选题/文献/设计/收集分析/撰写/定稿）组织指导内容，每阶段包含实施步骤、注意事项、时间管理建议
  - [x] SubTask 2.4: 在 Responsibilities 中追加「语言学专业写作差异」「常见问题解决方案」「学术规范要求」「实用技巧与资源推荐」四个子模块
  - [x] SubTask 2.5: 编写 Non-Goals 段落，明确不代写论文、不负责非语言学专业、不替代导师最终决策等边界

- [x] Task 3: 更新角色索引 README
  - [x] SubTask 3.1: 在 `.agents/roles/README.md` 角色职责矩阵追加论文指导者行（id=thesis-advisor、领域=academic、层级=guidance、核心职责=论文写作流程指导）
  - [x] SubTask 3.2: 在文件结构说明中追加 `thesis-advisor.md` 条目

- [x] Task 4: 一致性校验
  - [x] SubTask 4.1: 校验 md 文件 x-toml-ref 路径与实际 toml 文件路径一致
  - [x] SubTask 4.2: 校验 frontmatter id 与 toml id 一致
  - [x] SubTask 4.3: 校验 README 矩阵条目与文件结构列表同步

# Task Dependencies
- [Task 2] 依赖 [Task 1]（md 文件需引用 toml 路径）
- [Task 3] 依赖 [Task 2]（索引引用已存在的文件）
- [Task 4] 依赖 [Task 1][Task 2][Task 3]
