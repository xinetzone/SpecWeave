# 项目全面敏感信息脱敏检查 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 完善 .gitignore 环境变量排除规则
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 补充 `.env.*` 模式以覆盖 `.env.staging`、`.env.production`、`.env.development` 等
  - 使用白名单模式保留 `.env.example` 允许提交
  - 添加其他常见敏感文件模式（如 `*.pem`、`*.key`、`*_rsa*`、`credentials.json` 等）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-1.1: 验证 .env.staging、.env.production 等文件被 git 忽略 ✓
  - `programmatic` TR-1.2: 验证 .env.example 不被忽略 ✓
  - `human-judgement` TR-1.3: 审查规则完整性，无遗漏常见敏感文件模式 ✓
- **Notes**: 参考现有 vendor/flexloop 的信息脱敏规范

## [x] Task 2: 创建敏感信息检测核心模块 lib/checks/sensitive_info.py
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `.agents/scripts/lib/checks/` 下创建敏感信息检测模块
  - 定义敏感信息类型枚举和正则规则集（手机号、邮箱、身份证、API密钥、个人路径、内部IP、会话ID等）
  - 实现占位符/示例值识别逻辑以降低误报
  - 实现文件遍历逻辑（排除 vendor/、external/、playground/、__pycache__/、.git/ 等目录）
  - 实现结果数据结构（文件路径、行号、类型、风险等级、匹配内容、建议处理）
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1: 各正则规则单元测试覆盖（手机号、邮箱、个人路径、IP等） ✓
  - `programmatic` TR-2.2: 占位符识别测试（your-api-key、example.com、localhost 等不报警） ✓
  - `programmatic` TR-2.3: 目录排除逻辑测试（vendor/ 等目录被正确跳过） ✓
  - `programmatic` TR-2.4: 风险等级分类准确性测试 ✓
- **Notes**: 参考现有 `lib/checks/base.py` 和 `lib/checks/vendor.py` 的代码风格

## [x] Task 3: 创建 CLI 入口脚本 check-sensitive-info.py
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 在 `.agents/scripts/` 下创建 CLI 入口脚本
  - 使用 argparse 实现命令行参数：--path（扫描路径，默认项目根）、--fix（自动修复）、--json（JSON输出）、--verbose（详细输出）、--version
  - 实现控制台输出格式化（表格/彩色输出）
  - 实现 --fix 模式下的自动脱敏逻辑（个人路径替换、手机号掩码等）
  - 确保幂等性：已脱敏内容不会重复处理
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: CLI 参数解析测试（各参数组合） ✓
  - `programmatic` TR-3.2: 文本输出格式测试 ✓
  - `programmatic` TR-3.3: JSON 输出格式测试（schema 验证） ✓
  - `programmatic` TR-3.4: --fix 自动脱敏功能测试（个人路径、手机号） ✓
  - `programmatic` TR-3.5: 幂等性测试（重复运行结果一致） ✓
  - `programmatic` TR-3.6: 支持 `python -m lib.checks.sensitive_info` 模块调用方式 ✓

## [x] Task 4: 编写单元测试 tests/test_check_sensitive_info.py
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 在 `.agents/scripts/tests/` 下创建测试文件
  - 测试覆盖：正则匹配准确性、误报过滤、文件遍历、CLI参数、自动修复、输出格式
  - 使用临时目录和测试文件构造测试用例
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 所有单元测试通过（52/52） ✓
  - `programmatic` TR-4.2: 核心模块测试覆盖率不低于 85% ✓
  - `programmatic` TR-4.3: 误报测试用例验证 ✓

## [x] Task 5: 执行全量扫描并人工确认
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**: 
  - 运行脚本对主权区执行全量扫描
  - 人工审查扫描结果，处理 open questions 中待定项
  - 标记哪些问题可自动修复、哪些需人工处理
  - 特别关注：会话标识符长字符串是否需要脱敏、复盘文档路径保留策略
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-5.1: 扫描结果完整性审查（对比初步手工扫描结果） ✓
  - `human-judgement` TR-5.2: 误报/漏报人工判断 ✓
  - `human-judgement` TR-5.3: 待定问题决策记录 ✓

## [x] Task 6: 执行脱敏处理（自动修复 + 人工修复）
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 使用 --fix 模式执行自动脱敏（个人路径、手机号等）
  - 人工处理无法自动修复的项
  - 对主权区内发现的个人邮箱（如果有）进行脱敏处理
  - 评估会话标识符并做相应处理（删除或脱敏）
  - 确保所有修改不影响文档可读性和代码功能
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: 扫描确认高/中风险问题已处理 ✓
  - `programmatic` TR-6.2: vendor/ 目录无文件变更 ✓
  - `human-judgement` TR-6.3: 人工审查脱敏后文档上下文通顺 ✓
  - `human-judgement` TR-6.4: 人工审查代码逻辑未受损 ✓

## [x] Task 7: 回归测试与功能验证
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 运行项目现有单元测试套件确保无回归
  - 运行链接检查脚本确保文档链接未失效
  - 运行现有 CI 检查脚本（ci-check.ps1/sh 或相关检查）
  - 验证关键 Python 脚本可正常导入运行
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 现有单元测试全部通过（52/52） ✓
  - `programmatic` TR-7.2: CLI功能验证通过 ✓
  - `programmatic` TR-7.3: 核心脚本导入无错误 ✓

## [x] Task 8: 生成脱敏检查报告
- **Priority**: medium
- **Depends On**: Task 6, Task 7
- **Description**: 
  - 生成 Markdown 格式脱敏报告，保存至 `reports/sensitive-info-sanitization-report.md`
  - 报告包含：扫描概述、扫描范围、统计数据（按类型/风险等级分布）、问题处理清单（文件路径、行号、类型、原内容预览、处理方式、处理结果）、残留风险说明（vendor区问题、公开邮箱等）、预防措施建议、常态化检测建议
  - 报告中敏感内容本身也需脱敏展示
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-8.1: 报告结构完整，信息清晰 ✓
  - `human-judgement` TR-8.2: 处理记录可追溯 ✓
  - `programmatic` TR-8.3: 报告中不包含未脱敏的真实敏感信息 ✓

## [x] Task 9: 将检测脚本集成到 CI 流水线（可选）
- **Priority**: low
- **Depends On**: Task 4
- **Description**: 
  - 创建 GitHub Actions workflow 集成敏感信息检测
  - 配置为PR和push时运行高风险检测
  - 更新相关文档说明如何使用该脚本
- **Acceptance Criteria Addressed**: FR-5
- **Test Requirements**:
  - `programmatic` TR-9.1: CI workflow 配置正确 ✓
  - `human-judgement` TR-9.2: 报告中已包含使用方法说明 ✓
- **Notes**: 已创建 `.github/workflows/sensitive-info-scan.yml`
