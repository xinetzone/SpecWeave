---
id: awesome-okf-vendor-migration-tasks
---
# awesome-okf 迁移到 vendor/ 作为 Git 子模块 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 前置检查与基线记录
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 验证 Git 可用，网络可访问 GitHub
  - 记录根目录 awesome-okf 当前的完整 commit hash（`git -C awesome-okf rev-parse HEAD`）
  - 记录当前默认分支名
  - 检查 awesome-okf 内的 LICENSE 文件确认许可证类型
  - 记录现有三个子模块的状态基线：`git submodule status`
  - 记录 `git status` 快照
  - 统计需要更新路径引用的主权区文件列表（搜索 `file:///d:/AI/awesome-okf/`）
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-1.1: `git --version` 成功执行
  - `programmatic` TR-1.2: 获取到完整 commit hash（40位 SHA）
  - `programmatic` TR-1.3: `git submodule status` 记录三个现有子模块的正常状态（空格前缀）
  - `programmatic` TR-1.4: 列出所有包含旧路径引用的主权区文件路径清单
  - `human-judgement` TR-1.5: 确认 LICENSE 文件存在并记录许可证类型
- **Notes**: commit hash 必须精确记录，确保子模块检出到完全相同的版本

## [x] Task 2: 删除根目录旧 awesome-okf 目录
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 确认根目录 awesome-okf/ 确实是 untracked 状态（非子模块）
  - 删除根目录 awesome-okf/ 目录（Remove-Item -Recurse -Force）
  - 验证根目录不再有 awesome-okf/
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-2.1: 删除命令退出码为 0
  - `programmatic` TR-2.2: `Test-Path d:\AI\awesome-okf` 返回 false
  - `programmatic` TR-2.3: `git status` 显示 awesome-okf/ 不再在 untracked files 中
- **Notes**: 删除前务必备份 commit hash；如误删可从远程重新克隆

## [x] Task 3: 添加 awesome-okf 作为 vendor 子模块
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 执行 `git submodule add -b main https://github.com/yzfly/awesome-okf.git vendor/awesome-okf`（默认浅克隆）
  - 等待克隆完成
  - 进入子模块目录，checkout 到 Task 1 记录的精确 commit hash
  - 如子模块默认非浅克隆，配置 `git config -f .gitmodules submodule.vendor/awesome-okf.shallow true`
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: `git submodule add` 命令退出码为 0
  - `programmatic` TR-3.2: vendor/awesome-okf 目录存在且包含 README.md、LICENSE 等源码文件
  - `programmatic` TR-3.3: .gitmodules 包含 vendor/awesome-okf 条目
  - `programmatic` TR-3.4: `git -C vendor/awesome-okf rev-parse HEAD` 输出与 Task 1 记录的 commit hash 完全一致
  - `programmatic` TR-3.5: `git submodule status vendor/awesome-okf` 输出以空格开头（正常状态）
- **Notes**: 必须 checkout 到精确 commit 而非分支 tip，确保分析文档的行号引用有效

## [x] Task 4: 验证现有子模块未受影响
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 执行 `git submodule status` 检查所有子模块
  - 对比 Task 1 记录的三个现有子模块（flexloop、ark-cli、xuanspace）的 commit hash
  - 确认 .gitmodules 中这三个子模块的配置未被修改
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-4.1: vendor/flexloop 的 commit hash 与 Task 1 基线一致
  - `programmatic` TR-4.2: vendor/ark-cli 的 commit hash 与 Task 1 基线一致
  - `programmatic` TR-4.3: projects/xuanspace 的 commit hash 与 Task 1 基线一致
  - `programmatic` TR-4.4: .gitmodules 中三个旧子模块条目未变更
- **Notes**: 如发现现有子模块状态被意外修改，立即暂停并回滚

## [x] Task 5: 更新 vendor/AGENTS.md 路由表
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 读取当前 vendor/AGENTS.md 内容
  - 在「子模块路由表」表格中添加 awesome-okf 行：
    - 子模块: awesome-okf
    - 类型: third_party
    - AGENTS.md 入口: 无（第三方项目）
    - 说明: 中文 OKF 生态项目（开源知识格式工具链与插件集）
  - 在「边界声明」表格中添加 awesome-okf 行（归属: awesome-okf 子模块, 可修改: ❌ 否, 说明: 第三方只读依赖）
  - 保持 Markdown 表格格式一致
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 子模块路由表新增 awesome-okf 行，列数与现有行一致
  - `human-judgement` TR-5.2: 类型正确标注为 third_party
  - `human-judgement` TR-5.3: 边界声明表新增 awesome-okf 行
  - `programmatic` TR-5.4: Markdown 表格语法正确，无列数不匹配
- **Notes**: 参考现有 ark-cli 行的格式（同为 third_party 类型）

## [x] Task 6: 更新 vendor/README.md 依赖清单
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 读取当前 vendor/README.md
  - 在依赖清单表格中添加 awesome-okf 行：
    - 版本: `main@<short-commit> (子模块)`（short-commit 为 Task 1 commit hash 的前8位）
    - 类型: third_party
    - 引入日期: 2026-08-06
    - 用途: 中文 OKF（Open Knowledge Format）生态项目，含零依赖插件与 Skill 集
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 依赖清单表格新增 awesome-okf 行，字段完整
  - `programmatic` TR-6.2: Markdown 表格列数与现有行一致
- **Notes**: 版本格式与 flexloop/ark-cli 条目保持一致

## [x] Task 7: 更新 vendor/VERSION.md 版本记录
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 读取当前 vendor/VERSION.md
  - 在版本表格中添加 awesome-okf 行：
    - 库名称: awesome-okf
    - 版本号: main@<short-commit>
    - 完整 commit hash: Task 1 记录的40位 SHA
    - 来源地址: https://github.com/yzfly/awesome-okf.git
    - 引入日期: 2026-08-06
    - 许可证: MIT（或 Task 1 确认的实际许可证）
    - 类型: third_party
    - 跟踪分支: main
  - 在「更新记录」章节添加条目：`- 2026-08-06 | 引入 awesome-okf 子模块（从根目录迁移至 vendor/，修复架构边界）`
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 版本表格新增 awesome-okf 行，字段完整准确
  - `human-judgement` TR-7.2: 更新记录章节有 2026-08-06 对应条目
  - `programmatic` TR-7.3: Markdown 表格列数与现有行一致
- **Notes**: 注意版本表格和更新记录是两种不同格式

## [x] Task 8: 批量修复主权区文档的 file:/// 路径引用
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 基于 Task 1 收集的文件列表，逐个读取主权区文件（.agents/、.trae/specs/ 等，排除 vendor/）
  - 将所有 `file:///d:/AI/awesome-okf/` 精确替换为 `file:///d:/AI/vendor/awesome-okf/`
  - 注意：仅替换 `file:///` URL 中的路径，不替换正文中的文字提及（如 "awesome-okf 项目"）
  - 替换后验证每个文件的 Markdown 链接格式未被破坏
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-8.1: Grep 搜索主权区（排除 vendor/），`file:///d:/AI/awesome-okf/` 出现次数为 0
  - `programmatic` TR-8.2: Grep 搜索 `file:///d:/AI/vendor/awesome-okf/` 的出现次数与 Task 1 统计的旧路径次数一致
  - `human-judgement` TR-8.3: 抽样检查 2-3 个文件，确认链接格式正确、正文未被误替换
- **Notes**: 使用精确字符串替换，避免使用可能破坏内容的正则表达式

## [x] Task 9: 运行 check-vendor.py 合规检测
- **Priority**: high
- **Depends On**: Task 5, Task 6, Task 7, Task 8
- **Description**: 
  - 运行 `python .agents/scripts/check-vendor.py --deep` 进行深度合规检测
  - 如检测出问题，根据错误信息修复后重新运行
  - 记录检测结果
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `programmatic` TR-9.1: check-vendor.py --deep 退出码为 0
  - `programmatic` TR-9.2: 输出无 ERROR 级别的问题
  - `human-judgement` TR-9.3: 如有 WARNING 需评估是否可接受
- **Notes**: check-vendor.py 会验证子模块配置、元数据一致性、非法引用等

## [x] Task 10: 暂存所有变更并最终验证
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - 按三查暂存法逐个添加文件：
    1. 查修改：.gitmodules、vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md、路径更新的主权区文档
    2. 查新增：vendor/awesome-okf gitlink
    3. 查删除：确认无意外删除
  - 执行 `git add` 逐个添加（禁止 `git add .`）
  - 验证暂存区内容：`git diff --cached --name-only`
  - 验证最终状态：`git status`、`git submodule status`
  - 执行链接检查（至少检查更新过的主权区文档中的链接）
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-10.1: `git diff --cached --name-only` 列出所有预期变更文件，无意外
  - `programmatic` TR-10.2: `git submodule status` 四个子模块（flexloop、ark-cli、xuanspace、awesome-okf）均显示正常（空格前缀）
  - `programmatic` TR-10.3: 暂存的 awesome-okf 条目 mode 为 160000（gitlink）
  - `programmatic` TR-10.4: 根目录无 awesome-okf/ 的残留
  - `human-judgement` TR-10.5: `git diff --cached` 审查暂存内容无误
- **Notes**: 不执行 git commit，仅暂存；最终提交由用户确认后执行
