# Agent Workspace Hub - 智能体工作区枢纽系统 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 0: 定义工作区发现协议与SpecWeave根工作区自验证
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 正式定义**工作区发现协议（Workspace Discovery Protocol）**文档：智能体进入目录后的5步识别流程（AGENTS.md → workspace.yaml → .agents/ → 向上递归 → 用户确认）
  - 正式定义**一句话提示词自举协议（Prompt Bootstrap Protocol）**：设计通用引导提示词，支持环境自适应路径选择
  - 标准化AGENTS.md格式规范：明确"最小可行AGENTS.md"需要包含哪些区块（启动协议、路由表、自检清单、快速开始/引导提示词）
  - 撰写通用引导提示词（Universal Bootstrap Prompt），包含环境检测→路径选择→获取→自举→就绪验证完整指令链
  - 引导提示词需支持5种环境分支：已在目录内→Trae Skill→git clone→A2A连接→手动指引
  - 在AGENTS.md和README.md中嵌入可复制的引导提示词
  - 对当前SpecWeave根目录做一次**自举合规性审计**：验证现有AGENTS.md是否满足零安装自举要求，识别缺失项
  - 修复发现的问题，确保SpecWeave本身git clone到全新环境后，智能体只读AGENTS.md即可正确加载所有规范并开始工作
  - 编写《工作区发现协议规范》文档
- **Acceptance Criteria Addressed**: [AC-0, AC-0b, AC-0b2, FR-0 ~ FR-0n]
- **Test Requirements**:
  - `programmatic` TR-0.1: 发现协议文档完整，包含5步识别流程和优先级规则
  - `programmatic` TR-0.2: 提示词自举协议文档完整，通用引导提示词文本已定稿且内置8条安全规则
  - `human-judgement` TR-0.3: 模拟全新环境：只git clone SpecWeave，不运行任何安装命令，验证智能体能按AGENTS.md启动协议正确加载规范（角色、技能、规则立即可用）
  - `human-judgement` TR-0.4: 模拟零接触场景：将引导提示词发给全新环境中的智能体，验证智能体自动完成检测→路径确认→获取→完整性验证→自举→报告就绪
  - `programmatic` TR-0.5: 现有AGENTS.md满足"最小可行子集"要求且包含引导提示词
  - `programmatic` TR-0.6: 根目录.agents/roles/下的角色不需要安装/激活即可被识别
  - `programmatic` TR-0.7: 引导提示词幂等：已在有效SpecWeave目录内收到提示词跳过clone直接就绪
  - `human-judgement` TR-0.8: 安全规则验证：目录冲突时不盲目覆盖、敏感目录防护生效、clone后验证AGENTS.md完整性、错误明确报告不静默
  - `human-judgement` TR-0.9: 边界场景验证：Git不可用时给出zip指引、网络故障时给出手动方案、跨平台无bash/PowerShell特定语法
- **Notes**: 这是零安装可用的核心，优先级最高。CLI工具是后续增强，先保证"项目本身就是自描述的"，且"一句话就能装载"。

## [ ] Task 0A: 创建Trae Skill门面
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在`.agents/skills/agent-workspace-hub/`下创建标准Skill目录，严格遵循README.md + SKILL.md + .agents/分离设计
  - 编写`SKILL.md`（AI入口，含标准frontmatter：name/description/version/author，遵循五要素模型）
  - 编写`README.md`（人类入口，包含Skill说明、开发指南）
  - 创建`.agents/agents/openai.yaml`：智能体使用Workspace管理能力的系统提示词模板
  - 创建`.agents/references/`：快速参考卡片，列出核心概念和常用操作
  - 创建`.agents/assets/examples/`：示例Workspace模板
  - 创建`.agents/scripts/`：辅助脚本（如有）
  - Skill通过import调用apps/agent-workspace-hub下的Python核心库，不重复实现逻辑
  - 确保智能体加载此Skill后无需额外安装即可使用完整Workspace管理能力
- **Acceptance Criteria Addressed**: [AC-0c, FR-A1~FR-A8]
- **Test Requirements**:
  - `programmatic` TR-0A.1: Skill目录结构遵循分离原则：SKILL.md（AI入口）+ README.md（人类入口）+ .agents/（资源容器）
  - `programmatic` TR-0A.2: SKILL.md frontmatter完整合规，遵循五要素模型
  - `programmatic` TR-0A.3: README.md存在且面向人类读者
  - `programmatic` TR-0A.4: 所有辅助资源均在`.agents/`子目录下
  - `human-judgement` TR-0A.5: 智能体加载Skill后可正确理解并使用Workspace管理能力
  - `programmatic` TR-0A.6: Skill可成功调用核心Python库API

## [ ] Task 0B: 实现A2A v1.0协议支持
- **Priority**: high
- **Depends On**: Task 7（activate/deactivate生命周期）
- **Description**: 
  - 设计A2A Agent Card生成器：根据workspace.yaml和角色定义自动生成标准A2A Agent Card JSON
  - 激活工作区时自动生成`.a2a/agent-card.json`
  - 根工作区生成聚合Agent Card，列出所有已激活子Workspace作为Skills
  - 实现A2A JSON-RPC over HTTP服务（使用Python标准库http.server）：
    - tasks/send端点：接收任务，桥接到@角色调用
    - tasks/get端点：查询任务状态
    - tasks/cancel端点：取消任务
    - SSE流式推送任务状态
  - 实现A2A Message → @角色输入的桥接
  - 实现@角色执行结果 → A2A Artifact的封装
  - 实现A2A权限控制：只有a2aExported=true的角色/技能可通过A2A访问
  - 实现本地A2A注册表：激活工作区时注册，deactivate时注销
- **Acceptance Criteria Addressed**: [AC-0d, AC-0e, FR-B0~FR-B4]
- **Test Requirements**:
  - `programmatic` TR-0B.1: Agent Card生成符合A2A v1.0 JSON Schema
  - `programmatic` TR-0B.2: 未标记a2aExported的角色不出现在Agent Card中
  - `programmatic` TR-0B.3: A2A tasks/send/get/cancel端点正常工作
  - `programmatic` TR-0B.4: 任务结果正确封装为A2A Artifact
  - `programmatic` TR-0B.5: SSE流正确推送状态更新
  - `human-judgement` TR-0B.6: 外部A2A客户端可发现并调用工作区
  - `programmatic` TR-0B.7: 测试覆盖率≥85%

## [ ] Task 1: 项目初始化与核心架构搭建
- **Priority**: high
- **Depends On**: Task 0
- **Description**: 
  - 在`apps/agent-workspace-hub/`下创建标准项目结构
  - 初始化pyproject.toml（遵循项目YAML偏好）
  - 创建核心目录：src/agent_workspace_hub/、schemas/、examples/、tests/、docs/
  - 定义核心数据模型（WorkspaceManifest、RoleDeclaration、WorkspaceStatus等）
  - 设计平台路径抽象（跨平台获取全局存储位置）
  - 编写项目README.md和AGENTS.md路由索引
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构符合apps/规范
  - `programmatic` TR-1.2: 核心数据模型可序列化/反序列化
  - `human-judgement` TR-1.3: 架构分层清晰，模块职责单一
- **Notes**: 项目名称：agent-workspace-hub，CLI命令名：`workspace`或`awsh`

## [ ] Task 2: 定义Workspace包格式规范与JSON Schema
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 设计`workspace.yaml` manifest完整字段（参考PRD FR-1，含A2A配置a2a字段和角色a2aExported标记）
  - 编写正式JSON Schema（schemas/agent-workspace.schema.json）
  - 定义标准目录结构规范（严格遵循AGENTS.md + README.md + .agents/分离原则：根目录只放workspace.yaml/README.md/AGENTS.md/.a2a/，所有AI资源在.agents/下：roles/skills/workflows/knowledge/config/hooks）
  - 定义`.agentworkspace`打包格式（zip结构、可重现构建规则）
  - 定义Workspace角色文件格式（100%兼容现有.agents/roles/格式：TOML frontmatter + Description/Responsibilities/Non-Goals）
  - 定义虚拟团队yaml格式（100%兼容现有.agents/teams/data/*.yaml格式）
  - 定义A2A Agent Card格式（100%兼容A2A v1.0规范）
  - 编写格式规范文档
- **Acceptance Criteria Addressed**: [AC-1, AC-0d, NFR-6]
- **Test Requirements**:
  - `programmatic` TR-2.1: JSON Schema通过jsonschema自检（包括a2a字段）
  - `programmatic` TR-2.2: 有效manifest通过验证，无效manifest被拒绝且错误信息清晰
  - `programmatic` TR-2.3: 角色文件格式与现有角色文件完全兼容（能被现有角色加载器读取）
  - `programmatic` TR-2.4: A2A Agent Card JSON通过A2A v1.0 Schema验证
  - `programmatic` TR-2.5: Workspace目录结构严格遵循分离原则：根目录仅workspace.yaml/README.md/AGENTS.md/.a2a/，AI资源均在.agents/下
  - `human-judgement` TR-2.6: 格式设计可扩展，兼容MCP和A2A

## [ ] Task 3: 实现manifest验证器与核心模型逻辑
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 实现manifest加载与验证（JSON Schema验证 + 语义验证）
  - 实现SemVer版本解析与比较逻辑
  - 实现依赖解析与版本范围匹配
  - 实现校验和计算与包完整性验证
  - 实现Workspace状态持久化（installed.json记录已安装工作区）
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-3.1: 合法manifest加载正确，所有字段解析无误
  - `programmatic` TR-3.2: 各类无效manifest被正确拒绝
  - `programmatic` TR-3.3: 版本比较和范围匹配逻辑正确
  - `programmatic` TR-3.4: 测试覆盖率≥95%

## [ ] Task 4: 实现文件系统隔离与安装存储层
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 实现跨平台全局安装路径（Windows %APPDATA%、macOS ~/Library/Application Support、Linux ~/.local/share）
  - 实现Workspace解压安装逻辑
  - 实现卸载清理逻辑
  - 实现文件系统隔离机制（工作区根目录沙箱）
  - 实现幂等安装/卸载
- **Acceptance Criteria Addressed**: [AC-2, AC-4, NFR-3, NFR-8]
- **Test Requirements**:
  - `programmatic` TR-4.1: 安装/卸载幂等（重复操作不报错/不残留）
  - `programmatic` TR-4.2: 安装后文件完整，卸载后完全清理
  - `programmatic` TR-4.3: 跨平台路径正确
  - `programmatic` TR-4.4: 测试覆盖率≥95%

## [ ] Task 5: 实现角色自动注册/注销机制（核心功能）
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 实现角色注册逻辑：将Workspace内`.agents/roles/*.md`转换为宿主.agents/roles/下的命名空间角色文件
    - 命名空间规则：`<ws-id>-<role-id>.md`（如zhujian-wudao-philosopher.md）
    - 自动调整frontmatter中的bindings路径（相对路径→指向工作区安装目录）
    - 添加来源标记徽章到角色描述
  - 实现角色注销逻辑：deactivate时从.agents/roles/移除对应文件
  - 实现.agents/roles/README.md索引自动更新：
    - 解析现有README格式
    - 在角色职责矩阵中追加工作区角色（标记来源）
    - 注销时从索引中移除
  - 实现@冲突检测与命名空间隔离
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-4, AC-6]
- **Test Requirements**:
  - `programmatic` TR-5.1: 激活后角色文件正确出现在.agents/roles/
  - `programmatic` TR-5.2: 角色文件格式正确，frontmatter和正文符合现有规范
  - `programmatic` TR-5.3: 索引README正确更新，追加/移除工作区角色条目
  - `programmatic` TR-5.4: deactivate后角色文件和索引条目完全清理
  - `programmatic` TR-5.5: 同名角色通过命名空间正确区分
  - `programmatic` TR-5.6: 测试覆盖率≥95%

## [ ] Task 6: 实现团队治理集成（虚拟团队注册）
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 实现虚拟团队配置生成：激活时在.agents/teams/data/生成`ws-<ws-id>.yaml`
    - 团队ID：`ws-<workspace-id>`
    - 团队名称：`<workspace-name> 工作区`
    - 团队成员：Workspace导出的角色
    - 状态与Workspace同步（active/suspended/dissolved）
    - 完全兼容现有team yaml格式
  - 实现虚拟团队状态同步（activate→active, deactivate→suspended, uninstall→dissolved）
  - 集成权限校验框架：生命周期操作作为L3操作，预留V3验证/操作令牌接口
  - 预留跨工作区协作权限控制接口
- **Acceptance Criteria Addressed**: [AC-2, AC-4, AC-7]
- **Test Requirements**:
  - `programmatic` TR-6.1: 激活后虚拟团队yaml正确创建在.agents/teams/data/
  - `programmatic` TR-6.2: 团队yaml格式与现有格式完全兼容
  - `programmatic` TR-6.3: deactivate时团队状态标记为suspended
  - `programmatic` TR-6.4: uninstall时团队状态标记为dissolved（保留归档，不物理删除）
  - `programmatic` TR-6.5: 测试覆盖率≥90%

## [ ] Task 7: 实现activate/deactivate生命周期
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 实现activate完整流程：验证状态→注册角色→注册虚拟团队→（若启用A2A）生成Agent Card→注册到A2A本地注册表→更新状态→执行post-activate钩子
  - 实现deactivate完整流程：验证状态→注销角色→标记团队suspended→（若启用A2A）从A2A注册表注销→更新状态→执行pre-deactivate钩子
  - 实现状态机校验（非法状态转换报错，如deactivate一个未激活的工作区）
  - 实现技能注册/注销（预留接口，与现有技能体系集成）
  - 集成A2A Agent Card生成器：activate时自动生成`.a2a/agent-card.json`，只包含a2aExported=true的角色/技能
  - 根工作区activate时生成聚合Agent Card
- **Acceptance Criteria Addressed**: [AC-2, AC-4, AC-0d]
- **Test Requirements**:
  - `programmatic` TR-7.1: activate流程完整执行，所有注册动作正确完成（角色、团队、A2A）
  - `programmatic` TR-7.2: deactivate流程完整执行，所有注销动作正确完成
  - `programmatic` TR-7.3: 非法状态转换被正确拦截
  - `programmatic` TR-7.4: activate后`.a2a/agent-card.json`存在且内容正确
  - `programmatic` TR-7.5: 未启用A2A的工作区不生成Agent Card
  - `programmatic` TR-7.6: 单个activate/deactivate在5秒内完成
  - `programmatic` TR-7.7: 测试覆盖率≥90%

## [ ] Task 8: 实现pack打包与upgrade升级逻辑
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 实现pack命令：验证源目录→生成manifest校验和→按规范排序打包为.agentworkspace（zip）→可重现构建
  - 实现upgrade逻辑：检测新版本→备份旧版本→执行升级→重新注册角色/团队→升级失败自动回滚
  - 实现版本兼容性检查（manifest中的engines/platforms字段）
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-8.1: 打包生成的文件可正常install+activate
  - `programmatic` TR-8.2: 同一份源重复pack生成相同哈希
  - `programmatic` TR-8.3: 升级成功后角色/团队正确更新
  - `programmatic` TR-8.4: 升级失败自动回滚到原版本
  - `programmatic` TR-8.5: 测试覆盖率≥90%

## [ ] Task 9: 实现CLI命令行界面
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 使用typer实现CLI框架
  - 实现所有核心命令：bootstrap（生成最简AGENTS.md脚手架）、discover（发现当前目录工作区类型）、init、validate、pack、install、uninstall、activate、deactivate、list、info、upgrade、search、publish、registry、a2a（A2A网关控制：start/stop/status/serve）
  - 实现友好的命令行输出：颜色、进度条、格式化表格、清晰错误信息
  - 实现配置文件管理（config.yaml）
  - 添加完整--help文档和示例
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-4, AC-11, AC-0e]
- **Test Requirements**:
  - `programmatic` TR-9.1: 所有命令参数解析正确（包括a2a命令）
  - `programmatic` TR-9.2: 错误场景给出用户友好信息（无原始stack trace）
  - `human-judgement` TR-9.3: CLI输出美观易读
  - `programmatic` TR-9.4: `workspace a2a serve`可启动HTTP网关
  - `programmatic` TR-9.5: 测试覆盖率≥85%

## [ ] Task 10: 实现本地Registry与发布/搜索
- **Priority**: medium
- **Depends On**: Task 9
- **Description**: 
  - 设计registry格式：文件系统结构、index.json索引
  - 实现registry管理：add/remove/list
  - 实现publish逻辑：验证→复制包到registry→更新索引
  - 实现search逻辑：在registry索引中搜索
  - 实现从registry安装（含版本范围解析）
  - 预留git仓库安装接口
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-10.1: registry初始化正确
  - `programmatic` TR-10.2: publish的包可被search发现
  - `programmatic` TR-10.3: 从registry安装功能正确
  - `programmatic` TR-10.4: 版本范围解析正确
  - `programmatic` TR-10.5: 测试覆盖率≥90%

## [ ] Task 11: 实现Trae平台双向适配器
- **Priority**: high
- **Depends On**: Task 10
- **Description**: 
  - 实现现有Trae资产→Workspace导出：将.agents/skills/下的Skill + 相关角色打包为Workspace
  - 实现Workspace→Trae资产导入：激活流程本质就是此功能（已在Task5-7实现）
  - 端到端验证：竹简悟道现有.agents/ → Workspace → pack → install → activate → @哲学家可用
- **Acceptance Criteria Addressed**: [AC-8, AC-10]
- **Test Requirements**:
  - `programmatic` TR-11.1: 现有Skill+角色可成功打包为Workspace
  - `human-judgement` TR-11.2: 激活后的角色行为与原生角色一致
  - `programmatic` TR-11.3: 测试覆盖率≥85%

## [ ] Task 12: 创建三个参考示例工作区
- **Priority**: medium
- **Depends On**: Task 11
- **Description**: 
  - 示例1：竹简悟道工作区（从现有apps/zhujian-wudao提取打包）
  - 示例2：WeasyPrint文档工坊（基于WeasyPrint学习成果创建：doc-architect角色 + pdf-generator技能 + 文档生成工作流）
  - 示例3：复盘方法论工作区（retrospective-facilitator角色 + 复盘SOP + 模式库访问）
  - 每个示例包含：workspace.yaml、AGENTS.md、README.md、.agents/（内含roles/、skills/等）
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `programmatic` TR-12.1: 三个示例都通过validate验证
  - `programmatic` TR-12.2: 三个示例都可pack + install + activate成功
  - `human-judgement` TR-12.3: 示例README清晰，开发者可参照创建自己的Workspace

## [ ] Task 13: 实现外部平台适配器抽象层与豆包/MCP适配器骨架
- **Priority**: medium
- **Depends On**: Task 11
- **Description**: 
  - 定义PlatformAdapter抽象基类：export_to_platform()、import_from_platform()、is_compatible()
  - 实现TraeAdapter（封装Task11逻辑）
  - 实现MCPAdapter骨架：将Workspace导出的工具/资源/Prompt映射为MCP Server格式
  - 实现DoubaoAdapter骨架：定义映射规则（角色→人设、技能→工具、知识库→文档），注释说明待补充API部分
  - 实现适配器注册机制
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-13.1: 抽象基类接口完整
  - `programmatic` TR-13.2: TraeAdapter正确实现接口
  - `human-judgement` TR-13.3: MCP和豆包适配器骨架结构清晰
  - `programmatic` TR-13.4: 适配器注册机制工作正常
  - `programmatic` TR-13.5: 测试覆盖率≥80%

## [ ] Task 14: 自主进化引擎框架
- **Priority**: low
- **Depends On**: Task 12
- **Description**: 
  - 定义进化引擎接口和钩子
  - 实现知识沉淀框架：使用日志记录→提取洞察→追加到knowledge/目录（预留人工审批点）
  - 实现进化触发检测框架（对接role-auto-creation四条件）
  - 实现`workspace evolve`命令框架（分析→建议→审批→应用流程）
  - 实现进化历史记录和版本对比
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-14.1: 进化引擎框架可运行
  - `programmatic` TR-14.2: 角色创建触发遵循现有role-auto-creation流程框架
  - `human-judgement` TR-14.3: 首期进化以人工审批为主，不做完全自动
  - `programmatic` TR-14.4: 测试覆盖率≥75%

## [ ] Task 15: 编写完整文档与开发者指南
- **Priority**: medium
- **Depends On**: Task 14
- **Description**: 
  - 快速开始指南：安装CLI→创建Workspace→添加角色→打包→安装激活→@测试
  - Workspace包格式规范文档：manifest字段、目录结构、最佳实践
  - CLI命令参考：每个命令的参数、选项、示例
  - 开发者指南：创建Workspace、发布到团队registry、开发平台适配器
  - 架构说明文档：核心概念、状态机、隔离机制、治理集成
  - 核心模块API docstring
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `human-judgement` TR-15.1: 新开发者按文档可在45分钟内完成全流程
  - `programmatic` TR-15.2: 文档中所有示例命令可实际执行成功
  - `human-judgement` TR-15.3: 文档结构清晰，中文为主

## [ ] Task 16: 测试完善与项目收尾
- **Priority**: high
- **Depends On**: Task 15
- **Description**: 
  - 补充端到端集成测试：init→create→validate→pack→publish→search→install→activate→@→deactivate→uninstall完整流程
  - 多Workspace隔离测试：同时激活3个示例工作区，验证互不干扰
  - 运行覆盖率检查，确保核心≥95%，整体≥85%
  - 更新apps/README.md应用清单
  - 完成项目AGENTS.md
  - 全流程手工验证一遍
  - 修复发现的问题
- **Acceptance Criteria Addressed**: [AC-12, NFR-7]
- **Test Requirements**:
  - `programmatic` TR-16.1: 所有单元测试通过
  - `programmatic` TR-16.2: 所有集成测试通过
  - `programmatic` TR-16.3: 覆盖率达标
  - `programmatic` TR-16.4: apps/README.md已更新
  - `human-judgement` TR-16.5: 手工端到端流程顺畅，3个示例工作区可同时激活并@使用
