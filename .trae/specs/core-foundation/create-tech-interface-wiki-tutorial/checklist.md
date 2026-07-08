---
version: "1.0"
x-toml-ref: "../../../../.meta/toml/.trae/specs/core-foundation/create-tech-interface-wiki-tutorial/checklist.toml"
---
# 技术接口概念Wiki教程 - Verification Checklist

## 目录结构与元数据
- [x] 教程目录 `docs/knowledge/learning/interface-api-abi-protocol-wiki/` 已创建
- [x] 包含7个Markdown文件：00-overview.md ~ 06-resources.md
- [x] 每个文件YAML frontmatter完整（id/title/category/tags/date/status/author/summary）
- [x] category字段统一为"learning"，date为"2026-07-03"，status为"stable"
- [x] 每个文件行数 < 300行（最大164行，共870行）

## 00-overview.md 总览文档
- [x] 包含教程引言与目标读者说明
- [x] 包含四个概念的层次概览Mermaid图
- [x] 包含清晰的阅读路径/目录指引
- [x] 设置正确的下一章导航链接（指向01-interface.md）

## 01-interface.md 接口章节
- [x] 给出软件工程通用定义与OOP特定含义
- [x] 列出至少5个核心特征（6个：抽象性/规范性/多态/可实现性/契约性/解耦性）
- [x] 说明OOP与函数式编程两种范式中的应用场景
- [x] 提供至少2个代码案例（支付网关OOP + 函数式策略模式）
- [x] 包含双向导航：上一章(00-overview)、下一章(02-api)

## 02-api.md API章节
- [x] 给出API精确定义，明确与Interface的层次区别
- [x] 详述REST/GraphQL/SOAP/gRPC/库API五种类型及特点
- [x] 核心特征覆盖：调用方式、数据格式、协议支持、版本控制、认证
- [x] 说明系统集成/服务调用/第三方开发/微服务等应用场景
- [x] 提供至少3个主流API案例（GitHub REST/Stripe/GraphQL）
- [x] 包含curl/fetch/GraphQL实际调用代码示例
- [x] 包含双向导航：上一章(01-interface)、下一章(03-abi)

## 03-abi.md ABI章节
- [x] 定义ABI技术内涵，清晰说明与API的本质区别（源码兼容vs二进制兼容）
- [x] 列出5个核心技术特征（数据表示/调用约定/内存布局/符号修饰/系统调用）
- [x] 说明编译器开发/跨语言调用(FFI)/OS系统调用/动态链接等场景
- [x] 提供底层系统案例（Python ctypes调用C标准库）
- [x] 包含双向导航：上一章(02-api)、下一章(04-protocol)

## 04-protocol.md 协议章节
- [x] 给出网络协议与软件协议的综合定义
- [x] 列出5个核心特征（规则性/层次性/交互性/标准化/可扩展性）
- [x] 简述OSI七层与TCP-IP四层分层模型
- [x] 对比5种主流网络协议（HTTP/TCP/WebSocket/UDP/MQTT）的特点与场景
- [x] 包含软件协议场景说明（IPC/数据库协议/消息队列/序列化协议）
- [x] 包含双向导航：上一章(03-abi)、下一章(05-comparison)

## 05-comparison.md 对比分析章节
- [x] 包含四概念9维度对比表格
- [x] 分析5组概念间关联关系（API↔Protocol、Interface↔API、Interface↔ABI等）
- [x] 展示从抽象到具体的层次链：Interface → API → ABI → Protocol
- [x] 包含Mermaid架构层次图展示抽象栈
- [x] 澄清5个常见混淆点FAQ
- [x] 提供分场景决策指南表格
- [x] 包含双向导航：上一章(04-protocol)、下一章(06-resources)

## 06-resources.md 参考资料章节
- [x] 包含术语表（17个术语）
- [x] 列出三分类权威参考资料（书籍5本/RFC 5项/语言规范4项）
- [x] 提供4个进阶方向的扩展阅读建议
- [x] 包含导航：上一章(05-comparison)、返回目录(00-overview)、本教程结束标记

## 代码示例与图表
- [x] 代码示例使用正确的语言标记（typescript/bash/python/graphql等）
- [x] 代码示例具有说明性，可运行或逻辑清晰
- [x] Mermaid图表语法正确（3个：层次图1+抽象栈图1+可扩展其他）
- [x] 多语言示例平衡（TypeScript/Python/Go/命令行等）

## 链接与质量验证
- [x] 所有内部链接使用相对路径，无file:///绝对路径
- [x] 运行 `python .agents/scripts/check-links.py` 通过（20个本地链接100%有效）
- [x] 运行 `python .agents/scripts/check-file-size.py` 通过（所有文件<800行阈值）
- [x] 技术术语准确，参考权威来源
- [x] 语言专业且可读，适合初中级到高级开发人员
- [x] 双向导航链接完整且正确
