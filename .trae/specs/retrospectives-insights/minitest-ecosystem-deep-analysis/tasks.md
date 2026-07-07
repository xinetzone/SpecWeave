# Minitest AI QA 测试平台生态系统深度研究与洞察报告 - The Implementation Plan

## [x] Task 1: 官方文档深度解析与产品概念梳理
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 获取并解析 https://www.minitap.ai/docs/minitest 及其关键子页面内容
  - 梳理产品定位、核心价值主张、Mini AI Agent能力
  - 提取用户故事（User Story）与验收标准（Acceptance Criteria）模型
  - 分析测试执行流程：构建上传→虚拟设备执行→结果交付
  - 理解测试结果类型（Passed/Failed/Warning）与交付物（视频、复现步骤、设备日志、修复提示）
  - 整理Quickstart流程与应用套件结构
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 产品定位描述准确完整，清晰说明"零脚本QA Agent"核心价值
  - `human-judgement` TR-1.2: 用户故事模型与验收标准规则阐述清晰，包含类型枚举、依赖关系、Profile绑定等
  - `human-judgement` TR-1.3: 测试流程从构建上传到结果报告的完整链路描述准确
  - `human-judgement` TR-1.4: 失败时交付物（视频、repro、日志、fix prompt）说明完整
- **Notes**: 文档首页内容较少，需关注子页面链接；可使用defuddle获取更多子页面内容

## [x] Task 2: minitest-cli Python CLI 架构深度分析
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 分析项目分层结构：commands/、core/、api/、models/、utils/
  - 研究Typer命令体系注册机制与15+命令组功能
  - 深入分析配置管理（pydantic-settings）、环境变量加载、.env自动加载
  - 解析ApiClient异步HTTP客户端设计：自动auth注入、X-Minitest-Channel头、超时策略、文件上传
  - 分析认证体系：OAuth登录流程、API Key（mtk_前缀）、MINITEST_TOKEN、三种凭证优先级
  - 研究输出约定：--json模式stdout/stderr分离、Rich表格渲染、退出码定义（0-5）
  - 分析关键命令实现：init onboarding playbook、run执行与watch模式、batch管理、app-knowledge版本化更新
  - 读取core/目录关键模块：auth.py、config.py、app_context.py、credentials.py、oauth.py
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 分层架构图清晰展示commands/core/api/models/utils职责划分
  - `human-judgement` TR-2.2: 命令体系表格完整列出所有命令组及其功能
  - `human-judgement` TR-2.3: ApiClient设计分析包含自动认证、channel header、超时、文件上传等关键细节，有代码引用
  - `human-judgement` TR-2.4: 认证机制三种凭证源优先级与Key rotation流程说明准确
  - `human-judgement` TR-2.5: 输出约定与退出码规范完整，引用代码位置
  - `human-judgement` TR-2.6: 关键命令（init/run/batch/app-knowledge）流程分析有代码引用支撑
- **Notes**: 需读取多个核心文件，注意AGENTS.md中的开发规范也是重要分析对象

## [x] Task 3: minitest-trigger GitHub Action CI/CD集成分析
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 分析action.yml输入输出参数定义与默认值
  - 深入研究GitHub OIDC认证流程：getIDToken、audience设置、claims解析
  - 分析构建验证逻辑：iOS .app/.ipa检测与.app自动打包为.ipa、Android x86_64 ABI验证
  - 研究Web测试支持：web-targets解析（browser:viewport组合）、web-url覆盖
  - 分析CI元数据提取：commit title自动检测、PR number/title、baseRef/headRef
  - 深入分析PR头SHA覆盖逻辑：pull_request事件使用pull_request.head.sha而非OIDC merge SHA
  - 研究cancel-previous-runs机制：release branch pattern匹配、同分支CI批次取消
  - 分析发布流程：Release workflow构建dist/、ncc打包、v1标签自动更新
  - 读取src/api.ts、validate.ts、ci-metadata.ts、commit-sha.ts、commit-title.ts、web-targets.ts辅助模块
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-3.1: OIDC认证流程完整说明，包含token获取、claims解析、PR SHA特殊处理
  - `human-judgement` TR-3.2: 构建验证表格清晰列出iOS/Android/Web各平台要求与验证逻辑
  - `human-judgement` TR-3.3: PR SHA覆盖问题的原因与解决方案分析深入，引用代码位置
  - `human-judgement` TR-3.4: Web测试目标组合表完整列出所有有效browser:viewport组合
  - `human-judgement` TR-3.5: 取消之前运行的机制与作用域说明准确
  - `human-judgement` TR-3.6: 发布流程（semver tag→dist构建→v1更新）描述完整
- **Notes**: dist/目录不提交源码，由CI自动构建；注意form字段用snake_case而JSON用camelCase的约定

## [ ] Task 4: agent-skills Skill定义与AI Agent协作模式分析
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 分析SKILL.md frontmatter格式：name、description触发词设计
  - 研究onboarding playbook设计（minitest init输出）：认证→App→Profile→Journey→Scenario→Build→Run全流程
  - 深入分析测试Profile与Persona设计：@qa.minitap.ai共享收件箱OTP自动读取、BYO账户、特定状态账户预配置
  - 研究用户故事创建最佳实践：验收标准编写规则（视觉可验证、具体、单断言、时间顺序）、story types枚举、依赖声明
  - 分析CI/自动化使用模式：JSON输出管道、env set/--yes安全机制、--dry-run预览、test-file上传与绑定
  - 研究CLI-Skill同步机制：AGENTS.md明确要求的配对PR同步、Quick Reference表维护
  - 读取metadata.json了解Skill元数据
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-4.1: SKILL.md结构分析完整，触发词description设计原则说明清晰
  - `human-judgement` TR-4.2: @qa.minitap.ai共享收件箱模式设计巧妙点分析深入
  - `human-judgement` TR-4.3: 验收标准编写规则四条原则与离线测试、文件seeding等约定完整
  - `human-judgement` TR-4.4: CLI-Skill同步机制说明准确，强调"必须配对PR"的关键要求
  - `human-judgement` TR-4.5: CI自动化最佳实践（JSON管道、--yes、--dry-run、secret stdin）总结完整
- **Notes**: 这是理解AI Agent如何使用CLI工具的关键文档，注意conventions部分

## [ ] Task 5: 工程基础设施与DevOps实践分析
- **Priority**: medium
- **Depends On**: Task 3
- **Description**: 
  - 分析renovate-config统一依赖更新策略：
    - extends配置（best-practices、monorepos、recommended）
    - prConcurrentLimit: 5、minimumReleaseAge: 14天
    - schedule：周二/三/四上午开窗
    - 自动合并规则：patch/pin/digest、devDeps minor/patch、GitHub Actions
    - 安全漏洞告警：高优先级、无冷却期、security标签
    - major更新：不自动合并、breaking-change-review标签
  - 分析devops-common共享GitHub Actions库：
    - setup-go-private：Go私有模块配置
    - gcp-docker-build-push：GCP Artifact Registry镜像构建推送，分支/标签tagging策略
    - affected-pytest：基于pytest-impacted的选择性测试（PR跑受影响用例、main跑全量）
    - 其他Actions（aws-codeartifact、argocd-deploy、python-migrate等）概览
  - 总结minitest-cli开发规范（ruff+pyright+pytest、绝对导入、文件<150行、X | None语法、Annotated Typer参数、无交互提示）
  - 总结minitest-trigger开发规范（TypeScript严格模式、ESLint flat config、Prettier无分号单引号、@vercel/ncc单文件打包、dist不提交）
  - 分析跨仓库协同模式
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-5.1: renovate-config配置表格完整列出所有关键规则及其理由
  - `human-judgement` TR-5.2: devops-common Actions库每个Action的用途、输入、使用场景说明清晰
  - `human-judgement` TR-5.3: minitest-cli Python代码规范总结完整，引用AGENTS.md
  - `human-judgement` TR-5.4: minitest-trigger TypeScript代码规范总结完整，引用AGENTS.md
  - `human-judgement` TR-5.5: affected-pytest选择性测试策略分析深入（diff vs base-ref、依赖文件触发全量）
- **Notes**: renovate-config的14天冷却期和schedule策略是很好的工程实践；注意每个仓库都有自己的renovate.json继承共享配置

## [ ] Task 6: 示例应用与数据模式分析
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 分析demo-app Flutter扫雷游戏：
    - 项目结构（MVC模式：models/controllers/widgets/screens）
    - 状态管理（Provider）
    - 三个难度级别（Beginner/Intermediate/Expert）
    - 游戏机制（首次点击安全、长按标记、自动展开）
    - 跨平台支持（Android/iOS/Web/Windows/macOS/Linux）
    - 测试目录结构（unit tests + widget tests）
  - 分析minisweeper Sweep游戏问题数据集：
    - minisweeper_issues.csv内容概览
    - 作为Minitest测试训练/验证数据的用途
  - 深入分析测试Profile设计模式：
    - email-OTP personas默认方案（@qa.minitap.ai无密码→共享收件箱读OTP）
    - Bring-your-own account（stdin传入密码）
    - 特定状态账户预配置（<state>@qa.minitap.ai + password + 用户后端预配）
    - 无Profile绑定→匿名→自注册→读OTP流程
    - 第三方auth共享账户池
  - 分析环境变量安全管理机制：
    - 默认masked显示（********）
    - env get单值reveal（安全脚本赋值）
    - 写操作read-merge-write（不覆盖其他key）
    - mutating命令强制--yes确认
    - --dry-run预览变更（+/-/~标记）
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-6.1: demo-app架构分析清晰说明MVC分层和Provider状态管理
  - `human-judgement` TR-6.2: minisweeper用途说明准确
  - `human-judgement` TR-6.3: 测试Profile四种场景（OTP/BYO/特定状态/无绑定）设计模式分析完整
  - `human-judgement` TR-6.4: 环境变量安全管理五重保护机制（mask/get单值/merge-write/--yes/--dry-run）分析深入
- **Notes**: 可读取关键Dart文件（game_controller.dart、cell.dart等）了解具体实现

## [ ] Task 7: 系统架构图绘制与跨仓库关系分析
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**: 
  - 绘制Minitest生态系统整体架构图（Mermaid flowchart）：
    - 用户层：开发者CLI、CI/CD GitHub Action、Web UI、Slack集成
    - 工具层：minitest-cli、minitest-trigger、agent-skills
    - 平台层：testing-service（后端）、apps-manager、minihands-integrations、Supabase OAuth
    - 执行层：iOS Simulator、Android Emulator、Web浏览器
    - 基础设施层：devops-common、renovate-config
  - 绘制7个仓库职责与依赖关系图
  - 绘制CLI命令执行流转图（命令解析→配置加载→认证→API调用→输出渲染）
  - 绘制CI触发完整流程图（push/tag→OIDC→构建验证→上传→触发→Check Runs）
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 整体架构图清晰展示从用户到设备执行的完整链路
  - `human-judgement` TR-7.2: 仓库关系图明确每个仓库的角色和依赖方向
  - `human-judgement` TR-7.3: CLI执行流程图展示Typer回调→全局flag→子命令→ApiClient调用链
  - `human-judgement` TR-7.4: CI流程图包含OIDC认证、构建上传、触发、状态回传全链路
  - `human-judgement` TR-7.5: 所有Mermaid图表语法正确，可正常渲染
- **Notes**: Mermaid图表遵循安全编码六规则

## [ ] Task 8: 设计决策、可复用模式与最佳实践提炼
- **Priority**: high
- **Depends On**: Task 7
- **Description**: 
  - 提炼核心设计决策与权衡：
    - 为什么选择Typer而非Click/argparse
    - 为什么OIDC而非静态API Key作为CI默认认证
    - 为什么stdout/stderr分离设计（JSON data / diagnostics）
    - 为什么@qa.minitap.ai共享收件箱模式而非要求用户提供测试账户
    - 为什么退出码0-5细粒度分类而非0/1通用
    - 为什么.app自动打包为.ipa而非要求用户提供.ipa
    - 为什么PR head SHA需要覆盖OIDC SHA
  - 提取可复用工程模式：
    - CLI--json模式设计模式（stdout数据/stderr诊断，管道友好）
    - CI OIDC无密钥认证模式
    - 凭证多源优先级模式（env var→api key→oauth）
    - 环境变量安全管理五重保护模式
    - 依赖更新风险控制模式（冷却期+开窗+分级自动合并）
    - CLI-Agent Skill双向同步模式
    - 选择性测试策略（受影响用例/全量用例分流）
    - Playbook引导式onboarding模式
  - 总结安全最佳实践：
    - 凭证管理（token存储~/.minitest/credentials.json、API Key mint/revoke/list、stdin传密码）
    - 密钥处理（env masked显示、单值reveal、--dry-run、--yes确认）
    - OIDC安全（audience限定、PR SHA覆盖）
    - 构建安全（ABI验证、平台架构检查）
  - 总结开发者体验（DX）设计亮点：
    - 一行安装脚本（curl/irm + uv自动安装）
    - init引导式onboarding
    - apps dependencies Mermaid图可视化
    - --watch轮询模式
    - Rich表格输出
    - 非阻塞更新检查
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 设计决策分析包含"为什么"而非仅"是什么"，体现权衡思考
  - `human-judgement` TR-8.2: 可复用模式每个模式有清晰的问题-方案-适用场景描述
  - `human-judgement` TR-8.3: 安全最佳实践分类清晰（凭证/密钥/OIDC/构建）
  - `human-judgement` TR-8.4: DX亮点总结体现用户体验思考
- **Notes**: 这是报告最有价值的部分，需体现深度洞察而非表面描述

## [ ] Task 9: 洞察报告整合与格式规范检查
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 将所有分析内容整合为一份结构化的洞察报告Markdown文件
  - 报告结构建议：
    1. 执行摘要
    2. 产品概述与核心概念
    3. 生态系统架构总览（含架构图）
    4. minitest-cli深度分析
    5. minitest-trigger CI/CD集成分析
    6. agent-skills AI协作模式分析
    7. 工程基础设施与DevOps实践
    8. 示例应用与数据模式
    9. 核心设计决策与权衡
    10. 可复用工程模式
    11. 安全最佳实践
    12. 技术栈总览与版本信息
    13. 关键洞察与启示
  - 确保所有文件/代码引用使用可点击file:///绝对路径格式，关键代码段标注行号
  - 检查Mermaid图表语法正确性
  - 审查内容准确性与一致性
  - 添加frontmatter（id、title、date、category、tags、source）
- **Acceptance Criteria Addressed**: [AC-6, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 报告结构完整，13个章节逻辑连贯
  - `human-judgement` TR-9.2: 所有代码引用使用file:///格式，关键位置标注行号范围
  - `human-judgement` TR-9.3: Mermaid图表可正常渲染，无语法错误
  - `human-judgement` TR-9.4: frontmatter完整，符合YAML格式规范
  - `human-judgement` TR-9.5: 报告内容有深度洞察，不仅是事实罗列
  - `human-judgement` TR-9.6: 文件命名符合kebab-case规范
- **Notes**: 报告保存到 docs/knowledge/learning/ 或 docs/retrospective/ 对应目录；根据"格式一致性优先原则"，参考同目录现有报告的实际格式
