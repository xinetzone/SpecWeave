# Tasks
- [x] Task 1: 设计联合创始角色数据模型字段
  - [x] SubTask 1.1: 在 TOML frontmatter 中定义 `tier` 字段（取值 `co-founder` / `standard`，`standard` 为默认可省略）
  - [x] SubTask 1.2: 在 TOML frontmatter 中定义 `[permissions]` 表结构（含 `view` 与 `manage` 字段）
- [x] Task 2: 创建联合创始角色定义文件 `.agents/roles/co-founder.md`
  - [x] SubTask 2.1: 编写 TOML frontmatter（id、domain、layer、tier、permissions、bindings）
  - [x] SubTask 2.2: 编写 Markdown 正文（Description、Responsibilities、Non-Goals）
- [x] Task 3: 更新 `.agents/roles/README.md` 角色索引
  - [x] SubTask 3.1: 在角色职责矩阵中新增"层级"列，为联合创始角色显示 🏛️ 联合创始，普通角色显示"标准"
  - [x] SubTask 3.2: 在矩阵中追加联合创始角色行
  - [x] SubTask 3.3: 更新文件结构说明，加入 `co-founder.md`
  - [x] SubTask 3.4: 新增"权限控制"章节，说明联合创始角色的查看与管理权限要求
- [x] Task 4: 同步 `AGENTS.md` 角色定义索引表
  - [x] SubTask 4.1: 在 AGENTS.md 角色定义索引表中追加联合创始角色行
- [x] Task 5: 验证标记一致性与权限声明完整性
  - [x] SubTask 5.1: 校验联合创始角色在 README.md 索引与详情文件中视觉标记一致（🏛️ + [联合创始]）
  - [x] SubTask 5.2: 校验 `[permissions]` 表在联合创始角色文件中存在且字段完整
  - [x] SubTask 5.3: 运行 check-links.py 验证新增文件无断链

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 2]
- [Task 5] depends on [Task 3] 与 [Task 4]
