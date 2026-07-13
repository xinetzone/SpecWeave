# Agent Workspace Hub - 验证清单

## 根工作区自举验证（零安装核心）
- [ ] 工作区发现协议文档完整定义了5步识别流程和优先级规则
- [ ] 提示词自举协议文档完整定义了一句话装载的环境检测→路径确认→路径选择→获取→完整性验证→自举流程
- [ ] 通用引导提示词（Universal Bootstrap Prompt）文本已定稿，内置8条安全规则（S1-S8）
- [ ] AGENTS.md格式规范明确了"最小可行子集"包含的必要区块（含快速开始/引导提示词）
- [ ] AGENTS.md中包含可复制的引导提示词
- [ ] README.md中包含"一句话装载"章节
- [ ] SpecWeave根目录AGENTS.md满足最小可行子集要求
- [ ] 模拟全新环境验证：只git clone SpecWeave，不运行任何安装命令
- [ ] 智能体进入克隆目录后能自动发现AGENTS.md
- [ ] 智能体能按AGENTS.md启动协议正确加载核心规范
- [ ] 根目录.agents/roles/下所有标准角色立即可识别和@召唤
- [ ] 根目录.agents/skills/下所有技能立即可使用
- [ ] 全程不需要运行任何CLI安装命令，git clone完成即就绪
- [ ] 模拟零接触场景：将引导提示词发给全新环境智能体，自动完成检测→确认→获取→验证→自举→报告就绪
- [ ] **安全规则验证S1**：引导提示词硬编码官方仓库URL，不接受URL替换
- [ ] **安全规则验证S2**：执行git clone前必须向用户确认目标路径
- [ ] **安全规则验证S3**：提示词明确禁止在用户主目录/系统目录/根目录自动创建文件夹
- [ ] **安全规则验证S4**：自举过程只读文件，不自动执行hooks脚本、不自动pip install
- [ ] **安全规则验证S5**：clone后验证AGENTS.md存在且包含"启动协议"关键词
- [ ] **安全规则验证S6**：遇到错误（网络/权限/磁盘）明确报告，不静默失败
- [ ] 引导提示词幂等：已在有效SpecWeave目录内收到提示词跳过clone直接报告就绪
- [ ] 目录冲突处理：目标已存在且是非空非SpecWeave目录时停止并询问用户
- [ ] Git不可用时降级为zip下载指引
- [ ] 跨平台兼容：提示词中避免使用bash/PowerShell特定语法
- [ ] `workspace bootstrap`命令可生成最简可工作的项目（含AGENTS.md和最小目录结构）
- [ ] 经bootstrap生成的项目git clone后即可被智能体识别使用
- [ ] `workspace discover`命令可正确识别当前目录的工作区类型
- [ ] 引导提示词在5种环境分支下都能正确选择路径（已在目录内/Trae/git+确认/A2A/手动指引）

## Trae Skill门面验证
- [ ] Skill位于`.agents/skills/agent-workspace-hub/`目录，结构遵循README.md + SKILL.md + .agents/分离设计
- [ ] SKILL.md在根目录作为AI入口，包含完整frontmatter（name/description/version/author），遵循五要素模型
- [ ] README.md在根目录作为人类入口，包含Skill说明、开发指南
- [ ] `.agents/`子目录存在，所有辅助资源（提示词、参考、示例、脚本）均在此目录下
- [ ] `.agents/agents/openai.yaml`包含完整的系统提示词模板，指导智能体使用Workspace管理能力
- [ ] `.agents/references/`包含快速参考卡片，列出核心概念和常用操作
- [ ] Skill通过import调用核心Python库API，不重复实现业务逻辑
- [ ] 智能体加载此Skill后，无需额外安装CLI即可使用Workspace管理能力
- [ ] Skill可正确调用bootstrap/pack/install/activate/list等所有核心操作
- [ ] `.agents/assets/examples/`包含示例Workspace模板可供参考

## A2A协议v1.0验证
- [ ] A2A Agent Card生成器工作正常，输出符合A2A v1.0规范JSON
- [ ] activate工作区时自动生成`.a2a/agent-card.json`
- [ ] Agent Card正确列出工作区名称、描述、URL、能力（暴露的角色/技能）
- [ ] 根工作区Agent Card聚合列出所有已激活子Workspace
- [ ] 未标记a2aExported=true的角色/技能不出现在Agent Card中
- [ ] deactivate工作区时Agent Card被移除
- [ ] 本地A2A注册表工作正常：activate注册、deactivate注销
- [ ] A2A JSON-RPC HTTP服务可通过`workspace a2a serve`启动
- [ ] `tasks/send`端点正常工作：接收任务并桥接到@角色调用
- [ ] `tasks/get`端点正常工作：返回任务当前状态和结果
- [ ] `tasks/cancel`端点正常工作：取消正在运行的任务
- [ ] SSE流正确推送任务状态更新到客户端
- [ ] 传入A2A Message正确映射到工作区角色输入
- [ ] 工作区执行结果正确封装为A2A Artifact返回（支持文本/文件/结构化数据）
- [ ] A2A权限控制生效：非导出角色无法通过A2A访问
- [ ] `/.well-known/agent-card.json`端点在HTTP服务中正确暴露
- [ ] 首期A2A HTTP服务使用Python标准库实现，无重型依赖
- [ ] 外部A2A兼容客户端可发现并成功调用工作区能力

## 包格式与规范验证
- [ ] workspace.yaml manifest JSON Schema 定义完整且自洽，可通过 jsonschema 库自检
- [ ] manifest 所有必填字段（元数据/roles/skills/exports/platforms/a2a等）都有明确定义
- [ ] 角色定义中的a2aExported布尔字段正确实现
- [ ] Workspace目录结构严格遵循AGENTS.md + README.md + .agents/分离原则：根目录仅workspace.yaml/README.md/AGENTS.md/.a2a/，所有AI资源在.agents/下
- [ ] 有效 manifest 示例验证通过，无效 manifest 被正确拒绝并给出清晰错误信息
- [ ] Workspace角色文件格式 100% 兼容现有 `.agents/roles/` 格式（TOML frontmatter + Description/Responsibilities/Non-Goals）
- [ ] 虚拟团队yaml格式 100% 兼容现有 `.agents/teams/data/*.yaml` 格式
- [ ] SemVer 版本号比较和范围匹配逻辑正确（支持 ^/~/>=/< 等）
- [ ] `.agentworkspace` 格式支持可重现构建（同一份源打包出相同哈希）
- [ ] 包格式向前兼容设计合理

## 生命周期管理验证
- [ ] `workspace init` 可交互式创建标准Workspace脚手架
- [ ] `workspace validate` 正确验证Workspace目录格式
- [ ] `workspace pack` 正确生成 `.agentworkspace` 文件
- [ ] `workspace install` 支持本地文件安装
- [ ] `workspace install` 支持从 registry 安装
- [ ] `workspace install` 支持从git仓库安装
- [ ] `workspace install` 幂等：重复安装同一版本不报错
- [ ] `workspace install` 后状态为installed但不自动激活
- [ ] `workspace activate` 正确执行完整激活流程
- [ ] `workspace deactivate` 正确执行完整休眠流程
- [ ] `workspace uninstall` 正确执行完整卸载流程
- [ ] `workspace uninstall` 幂等：重复卸载不报错，无残留
- [ ] `workspace upgrade` 正确检测新版本并升级
- [ ] `workspace upgrade` 失败自动回滚到旧版本
- [ ] `workspace list` 正确列出所有已安装Workspace及其状态
- [ ] `workspace info` 正确展示Workspace详细信息
- [ ] `workspace search` 在 registry 中正确搜索Workspace
- [ ] 工作区状态机校验正确：非法状态转换被拦截

## 角色自动注册与@机制验证（核心）
- [ ] activate后Workspace角色文件正确出现在 `.agents/roles/`
- [ ] 角色ID命名空间规则正确（`<ws-id>-<role-id>.md`）
- [ ] 角色frontmatter中的bindings路径正确调整指向工作区安装目录
- [ ] 角色文件标记来源Workspace徽章
- [ ] `.agents/roles/README.md` 索引正确追加工作区角色条目
- [ ] deactivate后角色文件从 `.agents/roles/` 完全移除
- [ ] deactivate后角色索引README正确移除对应条目
- [ ] 同名角色通过命名空间正确区分，无@冲突
- [ ] 注册后的角色文件格式完全合规，可被现有角色加载器读取
- [ ] 根工作区角色天然可用，不需要激活流程

## 团队治理集成验证
- [ ] activate后在 `.agents/teams/data/` 正确生成 `ws-<id>.yaml` 虚拟团队文件
- [ ] 虚拟团队yaml格式完全兼容现有团队数据格式
- [ ] 虚拟团队状态与Workspace状态正确同步（active/suspended/dissolved）
- [ ] deactivate后虚拟团队状态标记为suspended（保留文件不删除）
- [ ] uninstall后虚拟团队状态标记为dissolved（归档留存）
- [ ] 生命周期操作预留V3验证/操作令牌接口
- [ ] 跨工作区协作预留权限控制接口

## 隔离与安全验证
- [ ] 每个Workspace安装在独立目录下
- [ ] Workspace默认文件系统隔离
- [ ] 接口显式导出：exports字段外的模块默认私有
- [ ] 所有关键操作有结构化日志
- [ ] 100%向后兼容：安装Workspace不破坏现有roles/teams，卸载后完全恢复原状

## 性能与可靠性验证
- [ ] 单个Workspace activate/deactivate 操作在5秒内完成
- [ ] 所有操作幂等，异常中断后可安全重试
- [ ] 跨平台全局安装路径在Windows/macOS/Linux上都正确
- [ ] 损坏的包文件被正确识别并拒绝安装
- [ ] 依赖循环被正确检测并报错

## Registry与团队共享验证
- [ ] 本地 registry 初始化成功
- [ ] `workspace registry add/remove/list` 正确管理registry源
- [ ] `workspace publish` 正确发布包到registry
- [ ] 发布到registry的包可被其他用户搜索和安装
- [ ] 版本范围解析正确（^1.0.0、~1.2.0等）

## 平台适配器验证
- [ ] PlatformAdapter 抽象基类接口定义清晰合理
- [ ] Trae适配器：现有 `.agents/skills/` + roles可成功打包为Workspace
- [ ] Trae适配器：Workspace activate后功能与原生一致
- [ ] Trae双向转换：原生→Workspace→原生后功能无差异
- [ ] MCP适配器骨架结构完整，明确映射规则
- [ ] 豆包适配器骨架结构完整，明确标注待补充API部分
- [ ] 适配器注册机制工作正常，可通过名称查找适配器

## 示例工作区验证
- [ ] 竹简悟道工作区可成功pack + install + activate
- [ ] 竹简悟道激活后philosopher角色可@，行为符合预期
- [ ] WeasyPrint文档工坊工作区可成功pack + install + activate
- [ ] 复盘方法论工作区可成功pack + install + activate
- [ ] 三个工作区可同时激活，互不干扰
- [ ] 每个示例工作区都有清晰的README使用说明
- [ ] apps/下的现有应用（竹简悟道、ai-code-assistant等）都可被识别为Workspace

## 自主进化框架验证
- [ ] 进化引擎接口定义完整
- [ ] 知识沉淀框架可运行（人工审批模式）
- [ ] 角色创建触发框架对接现有role-auto-creation四条件
- [ ] `workspace evolve` 命令框架工作正常
- [ ] 进化历史记录留存

## CLI体验验证
- [ ] bootstrap和discover命令正常工作
- [ ] a2a命令（start/stop/status/serve）正常工作
- [ ] 所有命令参数解析正确
- [ ] `--help` 文档完整清晰
- [ ] 错误场景给出用户友好信息，不暴露原始stack trace
- [ ] CLI输出美观易读，颜色/表格/进度提示合理
- [ ] 配置文件管理正常工作

## 文档与开发者体验验证
- [ ] 快速开始指南包含两种路径：零安装路径（git clone即用）和CLI增强路径
- [ ] 工作区发现协议文档完整清晰
- [ ] AGENTS.md最小可行子集有示例模板
- [ ] 包格式规范文档详细，每个字段有说明和示例
- [ ] CLI命令参考完整，每个命令有参数说明和示例
- [ ] 开发者指南涵盖：从零创建智能体友好项目、创建Workspace包、发布、开发适配器
- [ ] 架构说明文档清晰解释核心概念：三种工作区形态、发现协议、状态机、隔离机制
- [ ] 新开发者按文档可在45分钟内完成：bootstrap一个项目 → git clone验证可用 → 添加角色技能 → 打包
- [ ] 所有文档中的示例命令可实际执行成功
- [ ] 项目README.md清晰说明定位、两种使用方式（零安装/CLI增强）
- [ ] 项目AGENTS.md完整，为AI协作者提供路由索引
- [ ] apps/README.md应用清单已更新

## 测试覆盖率验证
- [ ] 核心模块（发现协议/验证器/角色注册/生命周期）测试覆盖率≥95%
- [ ] 整体项目测试覆盖率≥85%
- [ ] 所有单元测试通过无失败
- [ ] 端到端集成测试覆盖：零安装自举 + 完整生命周期管理
- [ ] 多Workspace隔离集成测试通过
- [ ] 跨平台测试（Windows + 至少一个类Unix系统）

## 项目规范合规验证
- [ ] 目录结构符合 apps/ 应用规范
- [ ] 代码风格与现有项目一致
- [ ] 遵循 Conventional Commits 提交规范
- [ ] 复用现有 `.agents/scripts/lib/` 共享函数，无重复实现
- [ ] Markdown链接使用相对路径，无 file:/// 绝对路径
- [ ] 所有新增脚本通过重复代码检测
