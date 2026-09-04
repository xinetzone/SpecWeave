# Agent系统中Interface/API/ABI/Protocol深度解析 - Verification Checklist

## 目录结构
- [ ] 目标目录 docs/knowledge/learning/agent-interface-deep-dive/ 存在
- [ ] 存在7个.md文件：00-overview.md、01-agent-interface.md、02-agent-api.md、03-agent-abi.md、04-agent-protocol.md、05-agent-comparison.md、06-agent-resources.md

## Frontmatter合规
- [ ] 每个文件包含id字段
- [ ] 每个文件包含title字段
- [ ] 每个文件包含x-toml-ref字段（相对路径正确）
- [ ] 每个文件包含source字段
- [ ] 每个文件包含category: "learning"
- [ ] 每个文件包含tags数组（含agent/interface/api/abi/protocol相关标签）
- [ ] 每个文件包含date字段（2026-07-03）
- [ ] 每个文件包含status: "stable"
- [ ] 每个文件包含author: "SpecWeave"
- [ ] 每个文件包含summary字段（一句话摘要）

## 00-overview.md总览
- [ ] 包含引言说明与通用wiki的区别
- [ ] 包含Agent技术栈四层抽象Mermaid图（Interface→API→ABI→Protocol，方向TD，有颜色区分）
- [ ] 核心区别速览表包含"Agent中对应物"列
- [ ] 包含与已有wiki的关系说明，链接到interface-api-abi-protocol-wiki和agent-communication-protocols
- [ ] 包含阅读路径指南
- [ ] 导航链接：下一章指向01-agent-interface.md，对比章指向05-agent-comparison.md

## 01-agent-interface.md（Agent Interface）
- [ ] 明确定义Agent Interface是"能力契约"而非OOP接口
- [ ] 列出≥5个核心特征
- [ ] 覆盖MCP Tool定义（inputSchema/outputSchema）
- [ ] 覆盖Skill描述文件能力声明
- [ ] 覆盖A2A Agent Card能力声明
- [ ] 代码案例1：TypeScript MCP Tool Interface + JSON Schema
- [ ] 代码案例2：Python Tool函数+类型注解
- [ ] 链接到已有wiki 01-interface.md说明通用概念
- [ ] 双向导航完整（上一章/下一章/对比章），文件名正确

## 02-agent-api.md（Agent API）
- [ ] 明确定义Agent API是Interface的"可调用暴露方式"
- [ ] 列出≥5个核心特征
- [ ] 覆盖MCP JSON-RPC 2.0方法（tools/list, tools/call等）
- [ ] 覆盖ACP RESTful API设计
- [ ] 覆盖A2A Task API
- [ ] 代码案例1：JSON-RPC tools/call请求响应完整示例
- [ ] 代码案例2：curl/fetch调用MCP Server示例
- [ ] 链接到已有wiki 02-api.md说明通用概念
- [ ] 双向导航完整（上一章/下一章/对比章），文件名正确

## 03-agent-abi.md（Agent ABI）
- [ ] 明确定义Agent ABI是跨运行时/跨语言的二进制兼容边界
- [ ] 列出≥4个核心特征
- [ ] 覆盖跨语言调用边界（Python ↔ Node.js）
- [ ] 解释JSON如何作为跨ABI通用序列化格式
- [ ] 解释STDIO/HTTP/SSE如何绕过原生ABI问题
- [ ] 说明为什么MCP选择JSON+STDIO/HTTP而非原生语言绑定
- [ ] 代码案例1：跨语言MCP Server/Client交互示意
- [ ] 代码案例2：JSON序列化抹平语言差异示例
- [ ] 提及WebAssembly作为新兴ABI边界
- [ ] 链接到已有wiki 03-abi.md说明通用概念
- [ ] 双向导航完整（上一章/下一章/对比章），文件名正确

## 04-agent-protocol.md（Agent Protocol）
- [ ] 明确定义Agent Protocol是通信的完整规则集
- [ ] 列出≥5个核心特征
- [ ] 覆盖MCP协议定位（工具调用层）
- [ ] 覆盖ACP协议定位（本地消息层）
- [ ] 覆盖A2A协议定位（跨Agent协作层）
- [ ] 覆盖ANP协议定位（去中心化网络层）
- [ ] 对比STDIO/HTTP/SSE传输层
- [ ] 代码案例1：MCP initialize握手消息
- [ ] 包含Mermaid序列图展示消息流程
- [ ] 链接到已有wiki 04-protocol.md和agent-communication-protocols/
- [ ] 双向导航完整（上一章/下一章/总览），文件名正确

## 05-agent-comparison.md（核心对比章）
- [ ] Agent语境9维度对比表（抽象层级/Agent中作用/数据格式/调用机制/错误处理/典型标准/变更影响/调试工具/违反后果）
- [ ] 四层抽象协同工作说明
- [ ] 包含Agent调用全链路Mermaid图（用户请求→Tool Interface→API→ABI序列化→Protocol传输→结果返回）
- [ ] ≥6个Agent特有FAQ
- [ ] 决策指南可操作（明确定义Tool能力用Interface/暴露方法用API/跨语言关注ABI/外部通信选Protocol）
- [ ] 双向导航完整（上一章/下一章/总览），文件名正确（⚠️下一章是06-agent-resources.md不是06-summary.md）

## 06-agent-resources.md（参考资料）
- [ ] Agent术语表≥15个术语
- [ ] MCP官方规范参考链接
- [ ] A2A官方文档参考链接
- [ ] ACP参考链接
- [ ] JSON-RPC 2.0和JSON Schema规范链接
- [ ] 3条进阶阅读路径（Tool开发者/协议设计者/跨语言Agent）
- [ ] 链接到interface-api-abi-protocol-wiki
- [ ] 链接到agent-communication-protocols
- [ ] 链接到agent-skills-wiki
- [ ] 双向导航完整（上一章/总览），文件名正确

## 代码质量
- [ ] 所有代码块使用正确语言标注（typescript/python/json/bash/mermaid）
- [ ] 每章（01-04）至少包含2个Agent场景代码案例
- [ ] JSON代码示例语法正确（引号、逗号完整）
- [ ] TypeScript/Python代码示例语法正确

## Mermaid图
- [ ] 所有Mermaid图使用```mermaid标记
- [ ] 每个Mermaid图包含方向声明（TD/LR）
- [ ] 总览四层抽象图有颜色/样式区分各层
- [ ] 调用链路图逻辑正确（完整链路）
- [ ] 序列图语法正确（participant/message顺序正确）

## 原子化合规（自动化验证）
- [ ] 运行check-file-size.py：所有7个文件行数<300
- [ ] 运行check-links.py：所有本地链接有效（0个断链）
- [ ] 导航链接中的文件名与实际文件名100%一致

## 与已有资产关联
- [ ] 基础概念（如OOP Interface、OSI模型）提供链接到已有wiki而非重复解释
- [ ] Agent协议细节（MCP/ACP/A2A完整教程）提供链接到agent-communication-protocols/
- [ ] 本教程定位明确：Agent实现视角的深度解析，不重复通用基础概念

## 最终入库
- [ ] 运行generate_index.py成功，新目录被知识库索引收录
