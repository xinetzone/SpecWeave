# Coze 开发平台生态 OKF Wiki 教程生成 - Implementation Plan

## Task 1: R阶段 - coze-py 源码事实采集
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 深度阅读 coze-py 源码核心模块：coze.py（主客户端）、auth/（认证模块）、chat/（对话）、bots/（Bot管理）、workflows/（工作流）、conversations/（会话）、websockets/（WebSocket实时通信）、audio/（语音）、datasets/（数据集）、files/（文件）、model.py（数据模型）、request.py（HTTP请求）、config.py（配置）
  - 提取可验证事实（类名、方法签名、参数、数据流、继承关系），编号 F-cp-001~F-cp-xxx
  - 事实写入 `.trae/specs/okf-wiki-ecosystem/coze-dev-okf-wiki/coze-py/facts.md`
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-1.1: 事实清单中无推断性表述（"用于"/"目的是"等），每个事实指向具体源码文件和行号；核心模块全覆盖（auth/chat/bots/workflows/websockets/audio/model/request）
  - `rule` TR-1.2: 事实数量 ≥ 60条，覆盖SDK主要API面
- **Notes**: 关注同步/异步双接口设计、Stream/AsyncStream流式对象、Page分页器、WebSocket事件处理器模式

## Task 2: I阶段 - coze-py 架构洞察与知识地图设计
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于事实清单提炼3-5个核心架构洞察（陈述+证据+反常识+行动四元组）
  - 设计知识地图：文档分组（入门/核心/高级）、依赖关系、学习路径
  - 确定每个概念文档覆盖哪些 F-cp-xxx 事实
  - 洞察写入 `.trae/specs/okf-wiki-ecosystem/coze-dev-okf-wiki/coze-py/insights.md`
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `rule` TR-2.1: 洞察四元组完整（陈述/证据/反常识/行动），每个洞察引用具体事实编号
  - `rubric` TR-2.2: 知识地图设计合理性；scale 1-5；anchors 1=无学习路径/3=基本线性/5=分层递进+多路径；threshold >= 4；evidence 知识地图文档

## Task 3: E阶段 - coze-py 知识束生成（信源先行+分批）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `bundles/coze/coze-py/` 目录结构（concepts/examples/references）
  - 批次3a：生成 references/ 信源登记（≥4篇：coze-client/auth-module/chat-workflow/websockets-audio 等核心模块信源）
  - 批次3b：生成 concepts/ 第一批（入门篇：整体架构、认证体系、客户端初始化，3-4篇）
  - 批次3c：生成 concepts/ 第二批（核心篇：对话与流式、Bot管理、工作流，3-4篇）
  - 批次3d：生成 concepts/ 第三批（高级篇：WebSocket实时通信、音频处理、分页与会话，3-4篇）
  - 批次3e：生成 examples/ 实战示例（≥3篇：基础对话/工作流调用/WebSocket语音对话）
  - 批次3f：生成各级 index.md（子目录索引→根索引）和 log.md
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-7
- **Test Requirements**:
  - `rule` TR-3.1: references/ 先于 concepts/ 生成；每批≤7文件；index最后生成
  - `rule` TR-3.2: concepts/ ≥8篇、examples/ ≥3篇、references/ ≥4篇；含index.md和log.md
  - `rule` TR-3.3: 所有文档frontmatter字段完整（type/title/description/sources/generated/verified/status/stale_after）

## Task 4: V阶段 - coze-py 独立验证与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 结构检查：目录结构完整性、frontmatter合规性
  - 链接检查：所有交叉链接无断链
  - Grep验证：对文档中引用的关键类名（Coze/AsyncCoze/TokenAuth/ChatEventType/Stream/Page等）和方法名在源码中验证存在性
  - 代码示例检查：API调用与源码一致
  - 修复发现的问题
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-4.1: Grep验证关键API存在性通过率100%，零虚构
  - `rule` TR-4.2: 内部交叉链接0断链
  - `rule` TR-4.3: frontmatter检查全部通过

## Task 5: R阶段 - coze-studio 源码事实采集
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 阅读后端Go源码核心模块：api/（handler/middleware/router）、application/（应用服务）、domain/（领域实体）、infra/（基础设施：cache/es/orm/rdb/sse/storage）、pkg/（工具包）、types/（常量/错误码）、main.go入口
  - 阅读前端架构关键文件：rush.json（monorepo配置）、frontend/目录结构、package.json依赖关系
  - 阅读IDL定义（idl/目录Thrift文件）：api.thrift、base.thrift、app/、conversation/、workflow/等核心接口
  - 阅读部署配置：docker-compose.yml、Dockerfile、Helm Chart
  - 提取架构级事实（分层结构、依赖注入、接口定义、数据流），编号 F-cs-001~F-cs-xxx
  - 事实写入 `.trae/specs/okf-wiki-ecosystem/coze-dev-okf-wiki/coze-studio/facts.md`
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 事实覆盖后端DDD四层（api/application/domain/infra）、前端monorepo架构、IDL接口定义、Docker部署
  - `rule` TR-5.2: 事实数量 ≥ 70条，后端Go架构为主，前端和部署为架构级覆盖
- **Notes**: coze-studio是大型全栈项目，采用分层采样策略：后端聚焦DDD架构和核心接口，前端聚焦monorepo包分层和架构模式，不逐包分析135+前端包

## Task 6: I阶段 - coze-studio 架构洞察与知识地图设计
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 提炼3-5个核心架构洞察（DDD分层、Go微服务架构、Rush.js monorepo、Thrift IDL代码生成、Docker+Helm部署）
  - 设计知识地图：后端架构篇→前端架构篇→IDL与API篇→部署运维篇
  - 洞察写入 `.trae/specs/okf-wiki-ecosystem/coze-dev-okf-wiki/coze-studio/insights.md`
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: 洞察四元组完整，引用具体事实编号
  - `rubric` TR-6.2: 知识地图对大型全栈项目的分层覆盖合理性；scale 1-5；anchors 1=只有代码罗列/3=后端或前端偏科/5=全栈架构均衡覆盖+学习路径清晰；threshold >= 4

## Task 7: E阶段 - coze-studio 知识束生成（信源先行+分批）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 创建 `bundles/coze/coze-studio/` 目录结构
  - 批次7a：生成 references/ 信源登记（≥4篇：backend-arch/frontend-arch/idl-defs/deployment-config）
  - 批次7b：生成 concepts/ 第一批（入门篇：项目概览与整体架构、技术栈概览，2篇）
  - 批次7c：生成 concepts/ 第二批（后端篇：DDD分层架构、API层与路由、Domain领域层、Infra基础设施层，4篇）
  - 批次7d：生成 concepts/ 第三批（前端与IDL篇：Rush.js monorepo架构、Thrift IDL与代码生成，2篇）
  - 批次7e：生成 concepts/ 第四批（部署篇：Docker Compose部署、Helm Chart配置，2篇）
  - 批次7f：生成 examples/ 实战示例（≥2篇：本地Docker部署、自定义后端API开发示例）
  - 批次7g：生成各级 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: references/ 先于 concepts/ 生成；每批≤7文件
  - `rule` TR-7.2: concepts/ ≥8篇、examples/ ≥2篇、references/ ≥4篇
  - `rule` TR-7.3: frontmatter字段完整

## Task 8: V阶段 - coze-studio 独立验证与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 结构检查、frontmatter检查、链接检查
  - Grep验证：对文档中引用的Go类型/函数名、React组件名、Thrift定义在源码中验证存在性
  - 修复发现的问题
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-8.1: Grep验证关键类型/函数/接口存在性通过率100%
  - `rule` TR-8.2: 链接0断链、frontmatter全部合规

## Task 9: R阶段 - cozeloop-python（含cozeloop-examples）源码事实采集
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 阅读 cozeloop-python 源码核心模块：client.py（客户端）、_client.py（底层实现）、trace.py（追踪）、span.py（Span）、prompt.py（Prompt管理）、logger.py（日志）、entities/（实体定义）、decorator/（装饰器）、spec/（规范）
  - 阅读 cozeloop-examples 示例代码：python/native/、python/tool/、go/native/ptaas/
  - 提取可验证事实，编号 F-cl-001~F-cl-xxx
  - 事实写入 `.trae/specs/okf-wiki-ecosystem/coze-dev-okf-wiki/cozeloop-python/facts.md`
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-9.1: 事实覆盖客户端初始化、Trace/Span、Prompt管理、PTaaS、日志等核心模块
  - `rule` TR-9.2: 事实数量 ≥ 40条；cozeloop-examples内容整合进事实清单

## Task 10: I阶段 - cozeloop-python 架构洞察与知识地图设计
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 提炼2-3个核心架构洞察（Span追踪模型、Prompt即服务、Noop客户端设计）
  - 设计知识地图
  - 洞察写入 `.trae/specs/okf-wiki-ecosystem/coze-dev-okf-wiki/cozeloop-python/insights.md`
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `rule` TR-10.1: 洞察四元组完整
  - `rubric` TR-10.2: 对小型SDK的架构洞察深度适当；scale 1-5；anchors 1=API罗列/3=基本使用说明/5=架构模式洞察+可观测性最佳实践；threshold >= 4

## Task 11: E阶段 - cozeloop-python 知识束生成（信源先行+分批）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 创建 `bundles/coze/cozeloop-python/` 目录结构
  - 批次11a：生成 references/ 信源登记（≥3篇：client-arch/trace-span/prompt-ptaas）
  - 批次11b：生成 concepts/（≥5篇：整体架构、客户端初始化与认证、Trace与Span追踪、Prompt管理与PTaaS、装饰器与集成）
  - 批次11c：生成 examples/（≥2篇：基础Trace上报、Prompt获取与格式化，整合cozeloop-examples代码）
  - 批次11d：生成各级 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-7
- **Test Requirements**:
  - `rule` TR-11.1: references/ 先于 concepts/；每批≤7文件
  - `rule` TR-11.2: concepts/ ≥5篇、examples/ ≥2篇、references/ ≥3篇；cozeloop-examples内容已整合
  - `rule` TR-11.3: frontmatter完整

## Task 12: V阶段 - cozeloop-python 独立验证与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 结构检查、frontmatter检查、链接检查
  - Grep验证关键类名/方法名存在性
  - 修复问题
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-12.1: Grep验证通过率100%
  - `rule` TR-12.2: 链接0断链、frontmatter合规

## Task 13: 分组索引与总导航更新
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4, Task 8, Task 12
- **Description**:
  - 创建 `bundles/coze/index.md` 分组索引，列出3个知识束及其简介、知识束概览表、推荐学习路径、生态关系图
  - 更新 `bundles/index.md` 总索引：添加coze分组条目、更新生态关系图、更新推荐入门路径、更新分组导航表和分组详情
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-13.1: bundles/coze/index.md 存在且正确列出3个知识束（coze-py/coze-studio/cozeloop-python）
  - `rule` TR-13.2: bundles/index.md 包含coze分组，total_bundles和groups计数正确更新
  - `rule` TR-13.3: 生态关系图和推荐路径正确反映coze分组的位置

## Task 14: 最终全局验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 全局frontmatter检查（所有.md文件）
  - 全局链接检查（跨知识束链接）
  - 统计总文件数、内容文档数
  - 确认log.md记录了生成历史
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-14.1: 所有.md文件frontmatter合规
  - `rule` TR-14.2: 全局0断链
  - `rule` TR-14.3: 文件统计与索引中声明的数量一致
  - `rubric` TR-14.4: 整体产出质量评估；scale 1-5；anchors 1=格式错误多/内容不准/3=基本可用但有瑕疵/5=与onnx束质量相当、可直接作为学习资源；threshold >= 4
