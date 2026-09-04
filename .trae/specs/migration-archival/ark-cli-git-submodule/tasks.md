# ark-cli Git 子模块集成 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 前置检查与环境准备
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 验证 Git 可用且 GitHub SSH 连接正常
  - 确认 `vendor/ark-cli` 目标路径不存在（或为空目录，如存在残留需清理）
  - 确认现有 flexloop 子模块状态正常，作为基线
  - 记录当前 git status 作为操作前快照
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-1.1: `git --version` 成功执行
  - `programmatic` TR-1.2: `Test-Path vendor/ark-cli` 返回 false（或目录为空）
  - `programmatic` TR-1.3: `git submodule status vendor/flexloop` 正常显示（无 `-` 前缀）
- **Notes**: 如果 vendor/ark-cli 已存在但不是子模块（如之前 npm 全局安装残留），需先删除该目录

## [x] Task 2: 添加 ark-cli 子模块
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 执行 `git submodule add git@github.com:volcengine/ark-cli.git vendor/ark-cli`
  - 如默认分支非 main，需添加 `-b <branch>` 参数
  - 等待克隆完成（可能需要几分钟）
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-2.1: 命令退出码为 0
  - `programmatic` TR-2.2: vendor/ark-cli 目录存在且包含 README.md 等源码文件
  - `programmatic` TR-2.3: .gitmodules 包含 vendor/ark-cli 条目
- **Notes**: 如遇 SSH 权限问题，可能需要检查 SSH 密钥配置；网络问题可重试

## [x] Task 3: 验证子模块初始化状态
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 执行 `git submodule status vendor/ark-cli` 确认状态
  - 记录子模块当前 commit hash 和默认分支
  - 检查子模块内是否有 LICENSE 文件以确认许可证类型
  - 验证 flexloop 子模块未受影响
- **Acceptance Criteria Addressed**: [AC-3, AC-8]
- **Test Requirements**:
  - `programmatic` TR-3.1: `git submodule status vendor/ark-cli` 输出以 commit hash 开头（无前缀 `-`）
  - `programmatic` TR-3.2: `git submodule status vendor/flexloop` 与操作前一致
  - `human-judgement` TR-3.3: 记录 commit hash、默认分支名、许可证类型（如 MIT/Apache-2.0 等）
- **Notes**: 输出前缀说明：` `(空格)=正常，`-`=未初始化，`+`=有改动，`U`=合并冲突

## [x] Task 4: 更新 vendor/AGENTS.md 路由表
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 在「子模块路由表」表格中添加 ark-cli 条目
  - 类型为 third_party（第三方只读）
  - 说明为火山引擎方舟大模型平台 CLI 工具
  - 标注无 AGENTS.md（第三方项目不设自有路由）
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 子模块路由表新增 ark-cli 行，类型标注为 third_party
  - `human-judgement` TR-4.2: 说明文字准确描述 ark-cli 用途
  - `programmatic` TR-4.3: Markdown 表格格式正确，列数与现有行一致
- **Notes**: 参考现有 flexloop 行的格式，保持一致性

## [x] Task 5: 更新 vendor/README.md 依赖清单
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 在「依赖清单」表格中添加 ark-cli 行
  - 版本格式为 `<branch>@<short-commit> (子模块)`
  - 类型为 third_party
  - 引入日期为 2026-07-07
  - 用途说明为火山引擎方舟大模型平台 CLI 工具（第三方只读依赖）
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 依赖清单表格新增 ark-cli 行，字段完整
  - `programmatic` TR-5.2: Markdown 表格列数与现有行一致
- **Notes**: 版本号使用短 commit hash（8位），与 flexloop 条目格式一致

## [x] Task 6: 更新 vendor/VERSION.md 版本记录
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 在版本表格中添加 ark-cli 行
  - 填写完整 commit hash、来源地址、引入日期 2026-07-07
  - 许可证字段：从子模块 LICENSE 文件读取，如无法确认填"待确认"
  - 类型为 third_party
  - 跟踪分支填写实际默认分支名
  - 在「更新记录」章节添加 2026-07-07 引入 ark-cli 子模块的条目
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 版本表格新增 ark-cli 行，字段完整准确
  - `human-judgement` TR-6.2: 更新记录章节有对应日期条目
  - `programmatic` TR-6.3: Markdown 表格列数与现有行一致
- **Notes**: 注意区分版本表格（| 库名称 | 版本号 | ...）和更新记录（- 日期 | 描述）两种格式

## [x] Task 7: 暂存所有变更并最终验证
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6
- **Description**: 
  - 暂存 .gitmodules 变更
  - 暂存 vendor/ark-cli gitlink（子模块目录）
  - 暂存 vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md 元数据更新
  - 执行最终验证：检查暂存区内容、子模块状态、无意外变更
  - 验证新克隆者可通过 `git submodule update --init` 初始化（dry-run 验证逻辑）
- **Acceptance Criteria Addressed**: [AC-7, AC-8]
- **Test Requirements**:
  - `programmatic` TR-7.1: `git diff --cached --name-only` 列出预期的 5 个变更路径（.gitmodules、vendor/ark-cli、vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md）
  - `programmatic` TR-7.2: `git submodule status` 两个子模块均显示正常（空格前缀）
  - `programmatic` TR-7.3: 工作区无意外的未暂存变更（除了已知的 docs/knowledge 文件）
  - `human-judgement` TR-7.4: 暂存的 diff 内容审查无误
- **Notes**: 不执行 commit，仅暂存；最终提交由用户确认后执行
