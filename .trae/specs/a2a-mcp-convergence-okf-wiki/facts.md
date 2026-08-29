# 博文事实采集（R 阶段，F-001~F-048）

> 信源：《A2A 与 MCP：Agent 互操作协议栈的合流时刻》，微信公众号"AI干活我偷懒"，2026-08-26 07:00，无作者bio
> URL：https://mp.weixin.qq.com/s/rhw4xEncNH-t7xcwrj_Hfw
> 内容性质：技术分析/架构战略类（协议合流事件+协议分工+技术架构+治理缺口+选型建议）

## 元信息

- **F-001**: 文章标题《A2A 与 MCP：Agent 互操作协议栈的合流时刻》，公众号"AI干活我偷懒"，2026-08-26 07:00，无作者bio，无免责声明

## 汇合事件（F-002 ~ F-010）

- **F-002**: 2026-08-20 Google将A2A协议捐赠给Linux Foundation旗下AAIF，与MCP同属一个中立治理机构
- **F-003**: A2A官方文档首页写明"MCP和A2A不是竞品"，A2A是agent-to-agent通信标准，让独立Agent（包括用MCP的Agent）互相发现、委派任务、共享结果
- **F-004**: AAIF 2025年12月成立，由Linux Foundation托管，白金成员8家：AWS、Anthropic、Block、Bloomberg、Cloudflare、Google、Microsoft、OpenAI
- **F-005**: AAIF成员数从成立时不到40家涨到2026年8月的250家以上
- **F-006**: AAIF原本已托管Anthropic的MCP、Block的goose、OpenAI的AGENTS.md，A2A并列其中
- **F-007**: AAIF执行总监Mazin Gilbert说："Companies don't want just one protocol; they want the whole stack to be open."
- **F-008**: lmunck博客点评：OpenAI、Google、Anthropic、Microsoft正在标准化Agent栈，恰恰是为了在更上层更激烈地竞争；当对手愿意把协议交给中立机构，说明真正的竞争已经不在这层
- **F-009**: 博文核心问题：A2A与MCP到底是什么关系？合流之后Agent生态竞争会移到哪里？
- **F-010**: 博文称"直接竞争对手共治同一套标准，在行业治理里极其罕见"

## MCP与A2A分工（F-011 ~ F-019）

- **F-011**: MCP是开源标准，把AI应用连到数据源、工具和工作流，官方类比是AI应用的USB-C接口
- **F-012**: A2A是Agent与Agent之间的开放标准，官方定位是"互操作的通用语言"
- **F-013**: 两者不是上下级，是两根轴线——MCP垂直（应用到资源），A2A水平（Agent到Agent）
- **F-014**: MCP交互对象是数据源、工具、工作流；A2A交互对象是其他独立Agent
- **F-015**: MCP是请求-响应；A2A是多轮协商、长时程任务
- **F-016**: MCP典型场景是查数据库、调API、读文件；A2A典型场景是跨组织协作、任务委派
- **F-017**: 开发者视角分工正交：MCP解决"资源侧标准化"（写一次server任何客户端都能连），A2A解决"Agent侧标准化"（任何框架构建的Agent都能互相对话）
- **F-018**: 官方推荐Agent栈：用ADK（或任意框架）构建，用MCP装备工具，用A2A与其他Agent通信——一个管"手"，一个管"对话"
- **F-019**: 博文引用A2A官方："A2A is for agent-to-agent communication... A2A lets independent agents — including those using MCP — discover each other, delegate tasks, and share results."以及"A2A不是MCP的替代品"

## 为什么不能用一个协议（F-020 ~ F-024）

- **F-020**: 工具是无状态、预定义函数的原语，调用一次返回一个结果；Agent有状态，会推理规划，能多轮协商
- **F-021**: 把Agent包装成工具暴露给别的Agent会砍掉协商能力，Agent天生应该直接对话
- **F-022**: 没有A2A时的连锁反应：点对点写死集成→每个新集成都要定制→系统难扩展→互操作低→临时通信缺一致安全措施
- **F-023**: A2A明确不做什么：不是Agent开发框架（LangGraph/CrewAI/ADK是那层）、不是子Agent或工具调用协议、不是即时消息应用而是机器对机器通信层
- **F-024**: 官方决策框架：简单调用直接用函数或API就行，上协议属于过度设计；工具调用表达不了"谈判与澄清"，这就是A2A存在的原因

## A2A技术架构（F-025 ~ F-033）

- **F-025**: A2A三个角色：User发起请求，A2A Client代表用户行动，A2A Server是暴露HTTP端点的远程Agent
- **F-026**: Server对客户端是不透明黑盒，内部记忆与工具一概不暴露——刻意设计，对方只需知道交付什么，不需要知道如何思考
- **F-027**: Agent Card：JSON"数字名片"，声明身份、端点、能力、认证、技能
- **F-028**: Task：有状态工单，唯一ID加定义的生命周期
- **F-029**: Message + Part：单轮通信，Part是内容容器，支持text、raw、url、data四种类型
- **F-030**: Context：用contextId把多个相关Task逻辑分组，追踪一次会话的来龙去脉
- **F-031**: 传输：HTTP(S)加JSON-RPC 2.0，认证要求声明在Agent Card里，凭证走HTTP头
- **F-032**: Agent Response只有两种形态：新Task（长时程操作）或即时Message
- **F-033**: 三种交互模式：短任务请求-响应轮询，长任务SSE流，更长或断连场景webhook推送

## 协同场景：汽车修理店（F-034 ~ F-037）

- **F-034**: 官方汽车修理店案例：用户描述车辆异响，Shop Manager Agent用A2A多轮追问细节（"能发个视频吗？"），再委派给Mechanic Agent
- **F-035**: Mechanic用MCP调诊断扫描仪、维修手册、平台升降机
- **F-036**: 需要备件时Mechanic用A2A跨组织询问Parts Supplier库存
- **F-037**: 流程四步：诊断（A2A多轮澄清）→委派（Manager交Mechanic说明约束）→工具调用（MCP驱动设备资料）→跨组织协作（A2A查供应商库存）。A2A只出现在Agent间打交道的两处，设备资料全走MCP

## 共享治理与采纳（F-038 ~ F-043）

- **F-038**: AAIF把Agent栈抽象成三层：模型层推理规划，MCP层工具集成，A2A层Agent协调
- **F-039**: 生产环境Agent栈通常同时需要两层：MCP连公司内部工单/CRM，A2A在Agent到达能力边界时路由到其他供应商专门Agent
- **F-040**: 共享治理保护两套协议区别：一套安全审查、一条合规轨道、一个解决重叠问题的统一场所；分散治理风险是两协议各自演变彼此偏离，逼每个框架做自定义桥接
- **F-041**: 采纳数字（据neuralcoretech博客）：MCP月度SDK下载超1.1亿，公共服务器超1万个（截至2026-04）；A2A采纳组织超150家
- **F-042**: AAIF四大工作流持续推进到2027年：MCP v2规范（流式支持与认证改进）、A2A治理规范（目标2026 Q3完成RFC）、AGENTS.md v1.0、安全一致性认证
- **F-043**: 企业端跟进（据neuralcoretech博客）：AWS Bedrock AgentCore于2026-08-21进入GA；Google在Cloud Next 2026发布Gemini Enterprise Agent Platform，把A2A作为协调层

## 三个缺口与建议（F-044 ~ F-048）

- **F-044**: 标准合流把风险转移而非消除，协议覆盖"怎么通信"但三个缺口协议层解决不了：归因（多Agent链没有"作者"，日志不是问责模型）、授权（协议描述可以请求什么，政策才描述被允许做什么）、追索（补救是合同性的不是技术性的）
- **F-045**: 买方下订单前五个问题：Agent无需人批能做什么？调用外部Agent保留什么记录？重大错误输出合同承诺什么？如何版本化与测试？合作伙伴Agent中途离线怎么办？
- **F-046**: EU AI Act Digital Omnibus 2026-07-27生效，Annex III高风险义务推迟到2027-12-02（据momoadvisors博客）
- **F-047**: 博文判断：互操作从差异化变成入场券；廉价互操作对买家是好消息对薄软件是坏消息；持久优势是结果质量、问责清晰度、出事时是否有人信任你
- **F-048**: 年底悬念：如果A2A与MCP采纳真正产出跨供应商Agent，共享栈就是真的；如果只是各玩各的，那只是一次branding

## P0 核验记录（2026-08-28）

12项P0声明核验：6✅ + 5⚠️ + 1❌

1. **F-002 A2A捐赠事件** ⚠️ — A2A早在2025-06-23已由Google捐赠给Linux Foundation；2026年8月是从LF独立项目**转入AAIF子基金会**，非首次捐赠。日期有分歧：AAIF官方博客为8月17日，Google Cloud公告为8月20日。→ **F-049勘误**
2. **F-004/F-005 AAIF成立与成员** ✅ — 2025-12-09成立，8家白金成员完全一致，成员从<40增至250+（Axios确认）
3. **F-006 AAIF托管项目** ✅ — MCP/goose/AGENTS.md为三大创始捐赠项目，完全正确
4. **F-007 Mazin Gilbert引语** ⚠️ — Gilbert确为AAIF执行总监；引语被多家媒体引用归因于Axios 8月17日报道，但Axios原文付费墙无法直接验证逐字原话
5. **F-041 MCP采纳数据** ⚠️ — 1万+公开服务器确认（2025年12月官方数据）；1.1亿月下载量无法从权威来源直接证实，官方数据点为9700万（2025年底）和近5亿（2026年7月）。→ **F-050勘误**
6. **F-041 A2A 150+组织** ✅ — AAIF官方博客和LF一周年新闻稿确认
7. **F-043 AWS AgentCore GA日期** ❌ — **硬性事实错误**：Amazon Bedrock AgentCore早在2025-10-13已GA；2026年8月是子功能GA（Payments 8月18日、Registry 8月6日），非平台整体GA。→ **F-051勘误**
8. **F-043 Google Cloud Next 2026** ✅ — 2026年4月22-24日，Gemini Enterprise Agent Platform发布，A2A作为协调层，完全正确
9. **F-046 EU AI Act** ✅ — AI Omnibus 2026-07-27生效，Annex III推迟至2027-12-02，欧盟官方网站完全确认
10. **F-025~F-033 A2A技术规范** ✅ — 全部要素（Agent Card/Task/Message+Part四种类型/Context/HTTP+JSON-RPC 2.0/三种交互模式/黑盒）与官方文档完全一致
11. **F-042 AAIF四大工作流** ⚠️ — 各要素散见不同来源，但"四大工作流至2027年"的明确框架主要来自genee.tech第三方博客，无法在AAIF官网直接确认；MCP v2时间线有歧义（2026-07-28已有重大更新）。→ **F-052勘误**
12. **F-003/F-019 A2A官方定位** ⚠️ — 语义准确但引文为意译非逐字原文：官方用"complement MCP"而非"not a replacement"，用"exchange work"而非"share results"。→ **F-053勘误**

### 核验补充事实

- **F-049**: A2A于2025-06-23在Open Source Summit North America上由Google首次捐赠给Linux Foundation；2026-08-17 AAIF官方博客宣布A2A加入AAIF（Google Cloud公告日期为8月20日）。博文"8月20日Google把A2A捐赠给Linux Foundation旗下AAIF"表述不精确——实际是将已有LF项目转入AAIF治理
- **F-050**: MCP官方下载量数据点：2025年底约9700万/月，2026年7月近5亿/月；博文引用的1.1亿（2026年4月）在增长曲线上合理但无官方来源直接证实，来源neuralcoretech为非权威博客
- **F-051**: Amazon Bedrock AgentCore于2025-10-13正式GA（AWS官方"What's New"确认）；2026年8月GA的是AgentCore Payments（8月18日）和Agent Registry（8月6日），博文将子功能GA混淆为平台整体GA
- **F-052**: AAIF四大工作流框架主要来自genee.tech等第三方博客综合，AAIF官网未直接列出"四大工作流至2027年"的官方路线图；MCP规范2026-07-28已有重大更新（无状态核心/OAuth 2.1+OIDC/任务扩展），"MCP v2"可能已部分交付
- **F-053**: A2A官方文档实际表述："The A2A protocol is an open standard that enables seamless communication and collaboration between AI agents"；"A2A is positioned to complement MCP"；AAIF博客："A2A defines how agents discover each other, delegate tasks, and exchange work"。博文引文为中文意译，核心定位准确但非逐字引用
