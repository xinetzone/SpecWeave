# 将 knowledge-catalog 移动到 vendor 作为 git 子模块 - 验证清单

- [x] 预检查完成：knowledge-catalog 工作区干净，commit hash 确认为 930b65fc3f5619d5d0591f88c72ebae8b848d60d
- [x] .gitmodules 备份已创建（.gitmodules.backup）
- [x] 子模块添加成功：.gitmodules 包含 vendor/knowledge-catalog 条目，URL 正确为 git@github.com:GoogleCloudPlatform/knowledge-catalog.git
- [x] vendor/knowledge-catalog 目录存在，是有效的 git 子模块（.git 文件指向主仓库 gitdir）
- [x] 子模块初始化成功：克隆完成，文件完整
- [x] 子模块版本正确：HEAD 指向 930b65f，与原目录一致
- [x] 子模块工作区干净，无本地修改
- [x] vendor/AGENTS.md 路由表已更新，在子模块路由表和边界声明表中添加了 knowledge-catalog 条目，格式与 ark-cli 一致
- [x] 全库搜索完成，确认所有 .chaos/libs/knowledge-catalog 引用均位于规划文档中，无代码/配置文件需要更新
- [x] 现有子模块状态正常（flexloop、awesome-okf、knowledge-catalog 正常；ark-cli 未初始化、xuanspace 有新提交为迁移前已有状态，未受影响）
- [x] 主仓库 git status 显示预期变更：.gitmodules 修改、vendor/AGENTS.md 修改、vendor/knowledge-catalog 新gitlink
- [x] 原始目录 `.chaos/libs/knowledge-catalog` 保留，等待用户确认后删除
- [x] 未修改 knowledge-catalog 内部任何文件，符合第三方依赖只读原则
