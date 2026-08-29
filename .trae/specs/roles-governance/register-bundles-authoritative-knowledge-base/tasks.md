# Tasks

- [x] Task 1: 更新根 AGENTS.md 知识库登记：在「知识库与复盘」表中新增 bundles 条目，标注其为项目最高可信度知识库，入口指向 `projects/awesome-okf-xs/doc/bundles/index.md`
- [x] Task 2: 在 `.agents/global-core-rules.md` 新增「知识可信度分级」规则：定义一级（bundles）/二级（docs/knowledge/ 与 retrospective）分级、冲突裁决（以 bundles 为准）、未覆盖回退、只读约束四条内容
- [x] Task 3: 在 `.agents/context-routing.md` 常规任务路由表新增「概念查阅/知识检索（最高可信度源）」条目，必读入口指向 bundles 根索引，注明优先级高于 `docs/knowledge/`
- [x] Task 4: 在 `projects/AGENTS.md` awesome-okf-xs「可用资产索引」表中新增 bundles 资产行（路径 `awesome-okf-xs/doc/bundles/index.md` + 最高可信度知识库说明）
- [x] Task 5: 在 `docs/knowledge/README.md` 相关资源区添加最高可信度源说明，指向 bundles 根索引
- [x] Task 6: 验证与原子提交：运行链接检查确认新增引用有效，确认 `projects/awesome-okf-xs/` 子项目内部文件零修改（git status 验证），按 Conventional Commits 规范提交（docs 类型，中文描述，显式逐文件 git add）

# Task Dependencies

- Task 6 依赖 Task 1-5 全部完成
- Task 1-5 相互独立，可并行执行
