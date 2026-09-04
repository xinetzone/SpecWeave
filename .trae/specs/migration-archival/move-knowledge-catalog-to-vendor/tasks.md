# 将 knowledge-catalog 移动到 vendor 作为 git 子模块 - 实施计划

## [x] Task 1: 预检查与备份准备
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 再次确认 knowledge-catalog 工作区干净，无未提交修改
  - 记录当前 commit hash（930b65f）
  - 备份当前 .gitmodules 文件
  - 检查是否有进程正在使用 knowledge-catalog 目录
- **Acceptance Criteria Addressed**: [AC-3, AC-5]
- **Test Requirements**:
  - `programmatic` TR-1.1: `git -C .chaos/libs/knowledge-catalog status` 显示 "working tree clean"
  - `programmatic` TR-1.2: `git -C .chaos/libs/knowledge-catalog rev-parse HEAD` 输出 930b65f 开头的 commit hash
  - `programmatic` TR-1.3: 备份 .gitmodules 文件存在且内容完整
- **Notes**: 确保操作前状态安全，可随时回滚

## [x] Task 2: 临时移除原始目录的 git 跟踪（如果已被跟踪）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 检查 `.chaos/libs/knowledge-catalog` 是否被主仓库 git 跟踪
  - 如果已被跟踪，从 git 索引中移除（不删除物理文件）
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-2.1: 运行 `git ls-files .chaos/libs/knowledge-catalog` 检查是否有跟踪文件
  - `programmatic` TR-2.2: 如果有跟踪文件，`git rm --cached` 执行成功
- **Notes**: 注意：.chaos 目录可能在 .gitignore 中，需验证

## [x] Task 3: 添加 git 子模块到 vendor/knowledge-catalog
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 使用 `git submodule add` 将 knowledge-catalog 添加为子模块，路径为 vendor/knowledge-catalog
  - 确保子模块 URL 为 `git@github.com:GoogleCloudPlatform/knowledge-catalog.git`
  - 子模块默认不跟踪分支（固定在当前 commit）
- **Acceptance Criteria Addressed**: [AC-1, AC-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: `git submodule add` 命令成功执行，无错误
  - `programmatic` TR-3.2: .gitmodules 文件新增 [submodule "vendor/knowledge-catalog"] 段
  - `programmatic` TR-3.3: vendor/knowledge-catalog 目录存在且包含 .git 文件（或gitlink）
- **Notes**: 如果 vendor/knowledge-catalog 目录已存在，需要先删除（确保是新目录）

## [x] Task 4: 验证子模块状态并固定到正确 commit
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 初始化并更新子模块
  - 验证子模块 HEAD 指向 930b65f
  - 确认子模块工作区干净
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-4.1: `git submodule update --init vendor/knowledge-catalog` 成功
  - `programmatic` TR-4.2: `git -C vendor/knowledge-catalog rev-parse HEAD` 输出 930b65f
  - `programmatic` TR-4.3: `git -C vendor/knowledge-catalog status` 显示 "working tree clean"
- **Notes**: 确保子模块版本与原目录完全一致

## [x] Task 5: 更新 vendor/AGENTS.md 子模块路由表
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 在 vendor/AGENTS.md 的「子模块路由表」中添加 knowledge-catalog 条目
  - 类型标记为 third_party，AGENTS.md 入口标注"无（第三方项目）"
  - 保持与 ark-cli 条目格式一致
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 子模块路由表包含 knowledge-catalog 条目，格式正确
  - `human-judgement` TR-5.2: 条目信息准确（类型为 third_party，说明正确）
- **Notes**: 说明文字：Google Cloud Knowledge Catalog 元数据管理平台（第三方只读依赖）

## [x] Task 6: 检查并更新旧路径引用（如有）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 搜索代码库中对 `.chaos/libs/knowledge-catalog` 路径的引用
  - 如果存在引用，评估是否需要更新
  - 文档中对 knowledge-catalog 项目的引用（如 knowledge-catalog-wiki）是项目名称引用，不需要修改路径
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-6.1: 使用 grep 搜索全库，列出所有匹配 `.chaos/libs/knowledge-catalog` 的文件
  - `human-judgement` TR-6.2: 评估每个引用，确定是否需要更新，如需要则更新
- **Notes**: 注意：文档中提到的 "knowledge-catalog-wiki" 是文档目录名，不是路径引用，无需修改

## [x] Task 7: 完整性验证
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 运行 `git status` 检查主仓库状态
  - 验证所有现有子模块状态正常
  - 对比原始目录和新子模块目录的文件列表一致性
  - 运行 check-vendor 脚本（如果适用）验证 vendor 状态
- **Acceptance Criteria Addressed**: [AC-1, AC-3, AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-7.1: `git submodule status` 显示所有子模块状态正常（包括 knowledge-catalog）
  - `programmatic` TR-7.2: 两个目录（原位置和新位置）的文件列表一致（排除 .git 目录）
  - `programmatic` TR-7.3: `git status` 显示预期的变更（.gitmodules 修改、新 gitlink、vendor/AGENTS.md 修改）
- **Notes**: 保留原始目录直到用户确认后删除

## [x] Task 8: （可选）清理原始目录
- **Priority**: low
- **Depends On**: Task 7
- **Description**: 
  - 在用户确认验证通过后，删除原始目录 `.chaos/libs/knowledge-catalog`
  - 提交所有变更（遵循 Conventional Commits）
- **Acceptance Criteria Addressed**: []
- **Test Requirements**:
  - `human-judgement` TR-8.1: 用户确认后执行删除
  - `programmatic` TR-8.2: 提交信息符合规范，例如 `chore(vendor): add knowledge-catalog as third-party submodule`
- **Notes**: 此任务需等待用户明确确认后执行，默认先保留原始目录
