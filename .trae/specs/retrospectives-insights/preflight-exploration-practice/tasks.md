# Pre-flight预探索模式实践任务 - The Implementation Plan

## 任务分组：infrastructure-config - 基建配置类

### 分组说明
renovate-config和devops-common同属基建配置类，输入源都是配置文件，输出可自然融合到同一报告章节，适合合并执行。

## [ ] Pre-flight预探索阶段
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 对6个分析对象执行Pre-flight预探索
  - 生成preflight-exploration.md，包含文档站点概览、代码仓库顶层目录结构、核心入口文件路径、跨仓库依赖关系、关键术语预识别
  - 将预探索结果作为共享上下文注入所有子代理prompt
- **Acceptance Criteria**:
  - [ ] preflight-exploration.md生成完整，包含5个预探索输出模块
  - [ ] 每个分析对象的目录结构和核心文件已识别
  - [ ] 跨仓库依赖关系已分析并以Mermaid图展示
  - [ ] 关键术语已预识别并记录

## [ ] Task 1: minitest-cli CLI工具架构分析
- **Priority**: high
- **Group ID**: N/A
- **Depends On**: Pre-flight预探索阶段
- **Description**: 
  - 分析项目分层结构：commands/、core/、api/、models/、utils/
  - 研究Typer命令体系注册机制与命令组功能
  - 分析配置管理（pydantic-settings）、环境变量加载
  - 解析ApiClient异步HTTP客户端设计
  - 分析认证体系：OAuth登录流程、API Key、MINITEST_TOKEN、三种凭证优先级
  - 研究输出约定：--json模式stdout/stderr分离、Rich表格渲染、退出码定义
- **Acceptance Criteria**:
  - [ ] 分层架构分析完整，包含核心模块职责划分
  - [ ] 命令体系分析完整，包含所有命令组及其功能
  - [ ] ApiClient设计分析包含自动认证、channel header、超时、文件上传等关键细节
  - [ ] 认证机制三种凭证源优先级说明准确
  - [ ] 输出约定与退出码规范完整

## [ ] Task 2: minitest-trigger CI/CD集成分析
- **Priority**: high
- **Group ID**: N/A
- **Depends On**: Pre-flight预探索阶段
- **Description**: 
  - 分析action.yml输入输出参数定义与默认值
  - 深入研究GitHub OIDC认证流程：getIDToken、audience设置、claims解析
  - 分析构建验证逻辑：iOS .app/.ipa检测与.app自动打包为.ipa、Android x86_64 ABI验证
  - 研究Web测试支持：web-targets解析、web-url覆盖
  - 分析CI元数据提取：commit title自动检测、PR number/title、baseRef/headRef
  - 深入分析PR头SHA覆盖逻辑
- **Acceptance Criteria**:
  - [ ] OIDC认证流程完整说明，包含token获取、claims解析、PR SHA特殊处理
  - [ ] 构建验证表格清晰列出iOS/Android/Web各平台要求与验证逻辑
  - [ ] PR SHA覆盖问题的原因与解决方案分析深入

## [ ] Task 3: agent-skills Skill定义与AI Agent协作模式分析
- **Priority**: high
- **Group ID**: N/A
- **Depends On**: Pre-flight预探索阶段
- **Description**: 
  - 分析SKILL.md frontmatter格式：name、description触发词设计
  - 研究onboarding playbook设计（minitest init输出）：认证→App→Profile→Journey→Scenario→Build→Run全流程
  - 深入分析测试Profile与Persona设计：@qa.minitap.ai共享收件箱OTP自动读取
  - 研究用户故事创建最佳实践：验收标准编写规则、story types枚举、依赖声明
  - 分析CI/自动化使用模式：JSON输出管道、env set/--yes安全机制、--dry-run预览
- **Acceptance Criteria**:
  - [ ] SKILL.md结构分析完整，触发词description设计原则说明清晰
  - [ ] @qa.minitap.ai共享收件箱模式设计巧妙点分析深入
  - [ ] 用户故事创建最佳实践分析完整

## [ ] Task 4: renovate-config依赖更新策略分析
- **Priority**: medium
- **Group ID**: infrastructure-config
- **Depends On**: Pre-flight预探索阶段
- **Description**: 
  - 分析default.json配置结构
  - 研究依赖更新风控策略：14天冷却期、周中开窗、风险分级自动合并
  - 分析并发限制配置
  - 识别安全更新特殊处理规则
- **Acceptance Criteria**:
  - [ ] 配置结构分析完整
  - [ ] 风控策略分析完整，包含冷却期、开窗、分级合并规则
  - [ ] 安全更新处理规则说明准确

## [ ] Task 5: devops-common CI流程分析
- **Priority**: medium
- **Group ID**: infrastructure-config
- **Depends On**: Pre-flight预探索阶段
- **Description**: 
  - 分析affected-pytest Action设计：git diff + AST导入图分析
  - 研究选择性测试策略：PR事件受影响测试、主分支全量测试、依赖变更强制全量
  - 分析其他共享Action（如build、deploy等）
- **Acceptance Criteria**:
  - [ ] affected-pytest Action设计分析完整
  - [ ] 选择性测试策略分析完整
  - [ ] 共享Action清单与功能说明完整

## [ ] Task 6: demo-app示例应用分析
- **Priority**: low
- **Group ID**: N/A
- **Depends On**: Pre-flight预探索阶段
- **Description**: 
  - 分析demo-app的项目结构
  - 研究与Minitest平台的集成方式
  - 识别演示的核心功能和测试模式
- **Acceptance Criteria**:
  - [ ] 项目结构分析完整
  - [ ] 集成方式说明清晰
  - [ ] 演示功能与测试模式分析完整

## [ ] 整合报告阶段
- **Priority**: high
- **Depends On**: Task 1-6
- **Description**: 
  - 整合6份子任务报告，生成insight-report.md
  - 执行三层抽象整合：事实层（子代理产出）→关系层（主控新增）→洞察层（主控判断）
  - 记录integration-notes.md，文档化信息取舍逻辑
  - 提炼可复用模式和核心洞察
  - Checklist分层验证（L0门禁项→L1质量项→L2优化项）
- **Acceptance Criteria**:
  - [ ] insight-report.md生成完整，包含跨模块关联分析
  - [ ] integration-notes.md记录完整，包含合并记录、降级省略、不确定性、洞察升级、术语对齐、关键实体标记
  - [ ] 可复用模式和核心洞察提炼完成

## [ ] 预探索效果评估阶段
- **Priority**: medium
- **Depends On**: 整合报告阶段
- **Description**: 
  - 生成preflight-effect-report.md
  - 记录预探索阶段耗时
  - 对比有无预探索情况下的子代理执行时间
  - 评估时间节省效果和分析质量提升
- **Acceptance Criteria**:
  - [ ] preflight-effect-report.md生成完整
  - [ ] 包含预探索耗时数据
  - [ ] 包含时间节省对比分析
  - [ ] 包含效果评估结论

---

[CMD-LOG] | level=INFO | cmd=tasks | step=S2 | event=TASKS_CREATED | session=spec-preflight-practice-20260708 | msg=Pre-flight预探索实践任务tasks.md创建完成，包含预探索阶段、6个子任务、整合阶段、效果评估阶段
