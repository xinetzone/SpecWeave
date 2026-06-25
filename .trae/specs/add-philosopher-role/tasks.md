# Tasks

> 以下所有路径均以竹简悟道项目根目录（`zhujian-wudao/`）为基准。

- [x] Task 1: 创建角色目录结构与核心参考文件
  - [x] SubTask 1.1: 创建 `.agents/roles/` 目录
  - [x] SubTask 1.2: 创建 `.agents/roles/references/insight-writing-guide.md`，摘录项目核心概念词典（体道四法、体道链、玄同、恒德、微明、概念解缚、Open Questioning）和洞察撰写标准结构（七节完整操作手册 / 基本结构）
  - [x] SubTask 1.3: 创建 `.agents/roles/references/constraints-cheatsheet.md`，摘录哲思引导者须遵循的核心约束（三不原则、产品层禁令 C-01~C-06、哲学立场约束 C-21~C-23）

- [x] Task 2: 创建哲思引导者角色定义文件
  - [x] SubTask 2.1: 编写 `.agents/roles/philosopher.md`，包含 TOML frontmatter（`id = "philosopher"`, `domain = "content"`, `layer = "generation"`, `tier = "standard"`, `[bindings]` 含规则、参考、工作流声明）
  - [x] SubTask 2.2: 编写 Markdown 正文：`# 哲思引导者（Philosopher）` → `## 核心定位` → `## 职责`（洞察撰写与编号、交叉引用维护、统计更新、复盘同步、三不原则遵循）→ `## 非目标`
  - [x] SubTask 2.3: 确保所有项目文件引用使用相对路径（遵循 `conventions.md` 交叉引用格式规范）

- [x] Task 3: 创建角色索引文件
  - [x] SubTask 3.1: 编写 `.agents/roles/README.md`，参照根项目 `.agents/roles/README.md` 的结构（角色概述 + 文件结构说明 + 职责矩阵）

- [x] Task 4: 更新项目 AGENTS.md 路由索引
  - [x] SubTask 4.1: 在文件地图中添加 `.agents/roles/` 目录及其子文件
  - [x] SubTask 4.2: 在路由索引表中添加角色相关条目

- [x] Task 5: 功能验证
  - [x] SubTask 5.1: 验证所有新增文件路径正确、文件存在
  - [x] SubTask 5.2: 验证 TOML frontmatter 语法正确（键值对完整、嵌套结构正确）
  - [x] SubTask 5.3: 验证所有交叉引用路径可解析（指向的文件存在）
  - [x] SubTask 5.4: 验证角色职责与项目工作流对齐

# Task Dependencies

- Task 2（角色定义文件）依赖 Task 1（目录与参考文件），因为角色定义需在职责中引用 `references/` 路径
- Task 3（角色索引）依赖 Task 2（角色定义），因为索引文件需引用 `philosopher.md`
- Task 4（路由索引更新）依赖 Task 2 和 Task 3（文件路径已确定）
- Task 5（验证）依赖 Task 1-4 全部完成
