# Home Assistant 智能家居系统集成 - 实施计划

## [x] Task 1: 创建 Home Assistant 集成技能目录和 SKILL.md
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `.agents/skills/` 下创建 `home-assistant/` 目录
  - 编写 SKILL.md，包含完整触发词、决策树、操作步骤、安全检查清单
  - 遵循五要素模型，控制在 500 行以内
  - **可选模块设计**: SKILL.md 中明确说明本技能为可选集成，不影响核心系统
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgment` TR-1.1: SKILL.md 包含完整触发词列表和强制措辞（"必须使用此技能"）
  - `human-judgment` TR-1.2: SKILL.md 控制在 500 行以内
  - `human-judgment` TR-1.3: 关键规则有 Why 解释（`> **为什么？**` 格式）
  - `human-judgment` TR-1.4: 写操作有安全检查清单（dry-run/幂等/验证）
  - `human-judgment` TR-1.5: SKILL.md 中明确说明本技能为可选集成
- **Notes**: 参考现有 skill 模板和 forum-posting skill 的双方案模式
- **Status**: Completed ✓

## [x] Task 2: 开发 HA API 自动化脚本（可选模块设计）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 Python 脚本 `ha_api.py`，支持 REST API 调用
  - 实现设备状态查询、设备控制、服务调用等核心功能
  - 支持配置化参数（HA URL、API Token）
  - 实现错误处理和重试机制
  - **可选模块设计**: 采用条件导入和 try/except 保护，避免硬依赖；HA 连接不可用时提供友好的错误提示和降级方案
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 脚本可独立运行，支持 `--help` 参数 ✓
  - `programmatic` TR-2.2: 状态查询功能返回正确的 JSON 数据
  - `programmatic` TR-2.3: 设备控制功能正确发送 POST 请求
  - `programmatic` TR-2.4: 错误处理机制正常工作（无效 token 返回错误）
  - `programmatic` TR-2.5: 无 HA 连接时脚本优雅降级，不抛出致命错误
- **Notes**: 使用 requests 库，遵循项目代码风格，参考 `.agents/scripts/lib/` 共享库
- **Status**: Completed ✓

## [x] Task 3: 创建 HA 集成指令集文档（可选模块设计）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 在 `.agents/commands/` 目录下创建 `home-assistant.md`
  - 定义触发条件、执行步骤、输入输出规范
  - 编写 RACI 责任分配矩阵，遵循五层审批模型
  - 更新 commands/README.md 索引
  - **可选模块设计**: 指令集标记为可选，核心系统不强制依赖
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgment` TR-3.1: 指令集文档包含完整的触发条件和执行步骤 ✓
  - `human-judgment` TR-3.2: RACI 矩阵符合三大强制规则（A唯一性、R≠A分离、双列设计） ✓
  - `human-judgment` TR-3.3: commands/README.md 索引已更新 ✓
  - `human-judgment` TR-3.4: 指令集标记为可选模块 ✓
- **Notes**: 参考 retrospective.md 和 atomic-commit.md 的结构
- **Status**: Completed ✓

## [x] Task 4: 创建团队协作配置（可选模块设计）
- **Priority**: medium
- **Depends On**: Task 3
- **Description**: 
  - 在 `.agents/teams/` 目录下创建 `home-assistant-team.md`
  - 定义 HA 集成治理范围、团队职责矩阵
  - 创建工作流（设备配置、集成测试、问题排查）
  - 更新 teams/README.md 索引
  - **可选模块设计**: 团队配置标记为可选，不影响核心团队运作
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgment` TR-4.1: 团队配置包含清晰的治理范围和职责矩阵 ✓
  - `human-judgment` TR-4.2: 工作流定义完整，包含 Mermaid 流程图 ✓
  - `human-judgment` TR-4.3: teams/README.md 索引已更新 ✓
  - `human-judgment` TR-4.4: 团队配置标记为可选模块 ✓
- **Notes**: 参考 flexloop-team.md 的结构
- **Status**: Completed ✓

## [x] Task 5: 编写使用文档和测试用例
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 创建技能使用文档（references/ 目录）
  - 编写脚本测试用例（tests/ 目录）
  - 更新 AGENTS.md 上下文路由表，添加 HA 集成相关入口（标记为可选）
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 测试用例运行通过（`python -m pytest`）✓
  - `human-judgment` TR-5.2: 使用文档完整清晰，包含快速开始指南
  - `human-judgment` TR-5.3: AGENTS.md 路由表已更新（标记为可选）
- **Notes**: 测试用例使用 pytest 框架，文档遵循渐进式披露原则
- **Status**: Completed ✓

## [x] Task 6: 验证和提交
- **Priority**: high
- **Depends On**: Task 1-5
- **Description**: 
  - 运行 CI 检查（ci-check.ps1）
  - 检查链接有效性（check-links.py）
  - 验证可选模块设计：确认不集成本模块时核心系统正常运行
  - 执行原子提交，推送至远程仓库
- **Acceptance Criteria Addressed**: AC-1-5
- **Test Requirements**:
  - `programmatic` TR-6.1: CI 检查通过（ci-check.ps1 返回成功）✓
  - `programmatic` TR-6.2: 链接检查通过（check-links.py 无错误）✓ (注: 已有断链非本次引入)
  - `human-judgment` TR-6.3: 可选模块设计验证通过，核心系统不依赖本模块 ✓
  - `programmatic` TR-6.4: 原子提交成功，所有文件已推送 ✓
- **Notes**: 使用 atomic-commit-cmd 技能执行提交
- **Status**: Completed ✓