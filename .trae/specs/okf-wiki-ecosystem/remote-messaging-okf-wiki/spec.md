---
title: "remote 消息通信生态 OKF Wiki - 产品需求文档"
status: "draft"
---

# remote 消息通信生态 OKF Wiki - 产品需求文档

## Overview
- **Summary**：系统学习 `external/libs/remote/` 下全部 4 个开源项目（libzmq、cppzmq、pyzmq、dramatiq）的源码，在 `projects/awesome-okf-xs/bundles/messaging/` 下生成符合 OKF v0.2 规范的中文源码教程知识束，每个项目独立成束，包含 concepts/（概念文档）、examples/（实战示例）、references/（信源登记）三层结构。
- **Purpose**：将 ZeroMQ 消息通信生态（C 核心库 → C++ 绑定 → Python 绑定 → Python 分布式任务队列）的架构设计与核心 API 以可溯源、可验证的中文 Wiki 形式沉淀，填补 awesome-okf-xs 文档库在消息通信/分布式系统领域的空白。
- **Target Users**：需要理解 ZeroMQ 内部架构（socket patterns、ZMTP 协议、I/O 线程模型）的 C++/Python 开发者；需要在 Python 中使用 pyzmq 构建消息系统的工程师；需要使用 dramatiq 构建分布式任务处理系统的开发者。

## Goals
- 为 libzmq（ZeroMQ C++ 核心库）生成完整 OKF 知识束，覆盖公共 C API、上下文/套接字/会话/管道/引擎核心架构、消息模式、ZMTP 协议、I/O 多路复用
- 为 cppzmq（C++ header-only 绑定）生成 OKF 知识束，覆盖 RAII 封装、类型安全、message_t/buffer 抽象、多部分消息、poller、错误处理
- 为 pyzmq（Python 绑定，Cython+CFFI 双后端）生成 OKF 知识束，覆盖 Context/Socket/Frame、sugar 语法层、asyncio/future、poller、auth、green/gevent、eventloop
- 为 dramatiq（Python 分布式任务队列）生成 OKF 知识束，覆盖 Actor/Broker/Worker/Message/Middleware/Encoder/Results、Redis/RabbitMQ/Stub broker、CLI、watcher
- 新建 `messaging/` 生态分组索引（category index），更新 bundles 根索引
- 所有 API 引用经 Grep 级源码验证，零虚构 API；所有文档 frontmatter 符合 OKF v0.2 规范

## Non-Goals (Out of Scope)
- 不修改任何上游项目源码（libzmq/cppzmq/pyzmq/dramatiq 均为只读分析对象）
- 不生成 CZMQ（ZeroMQ 高层 C 封装）、JeroMQ（Java 实现）、NetMQ（C# 实现）等 remote/ 目录外的 ZeroMQ 生态项目
- 不覆盖 libzmq 所有 200+ 源文件的逐行分析（聚焦公共 API 与核心架构文件，平台特定代码如 VMCI/TIPC/VSOCK 仅作概要）
- 不提供二进制安装/编译指南（聚焦源码架构与 API 理解）
- 不向上游项目贡献任何内容（pyzmq 的 AGENTS.md 禁止 LLM 为其项目贡献；本任务产出物位于独立的 awesome-okf-xs 文档库，是关于 pyzmq 的原创教育性分析，非向 pyzmq 贡献）

## Background & Context
- `external/libs/remote/` 目录包含 4 个项目：libzmq（C++98 核心库，src/ 下 200+ 文件）、cppzmq（header-only，zmq.hpp + zmq_addon.hpp）、pyzmq（Python 包，Cython/CFFI 双后端 + sugar 纯 Python 层）、dramatiq（纯 Python，16 个核心模块 + 3 个 broker 后端）
- awesome-okf-xs 现有 23 个分组、236 个知识束，无消息通信/分布式系统分组，需新建 `messaging/` 分组
- 已有成熟范例（onnx/onnx、tooling/ninja、myst/mdurl 等）提供 OKF 格式参照
- 工作流遵循 source-code-to-okf-wiki 技能的 R→I→E→V→C 五阶段链路，由 seven-concepts-cmd 方法论编排（场景4：知识沉淀 R→I→E）
- pyzmq 含 AGENTS.md 声明"All LLM contributions are strictly forbidden"——此约束针对向 pyzmq 上游贡献；本任务在独立仓库 awesome-okf-xs 中编写关于 pyzmq 的原创中文教程，将 pyzmq 源码作为信源引用（类似技术书籍分析开源项目），不修改 pyzmq 仓库任何文件

## Functional Requirements
- **FR-1**：在 `bundles/messaging/` 下创建 4 个知识束目录（libzmq/、cppzmq/、pyzmq/、dramatiq/），每个含 concepts/、examples/、references/、spec/ 子目录
- **FR-2**：每个知识束的 spec/ 目录包含 facts.md（编号事实清单 F-xxx）和 insights.md（3-5 个架构洞察四元组 + 知识地图）
- **FR-3**：每个知识束的 references/ 目录包含信源登记文件，每个文件 frontmatter 的 sources 字段指向具体源码路径
- **FR-4**：每个知识束的 concepts/ 目录包含按学习路径编号的概念文档（00-xx.md ~ NN-xx.md），覆盖核心架构与 API
- **FR-5**：每个知识束的 examples/ 目录包含可运行的实战示例文档（代码块标注语言）
- **FR-6**：每个知识束包含根 index.md（带 type: bundle + okf_version frontmatter）、log.md、以及 concepts/examples/references 三个子目录的 index.md（无 frontmatter）
- **FR-7**：创建 `bundles/messaging/index.md` 分组索引（type: category），汇总 4 个知识束概览表、生态关系图、推荐学习路径
- **FR-8**：更新 `bundles/index.md` 根索引，新增 messaging 分组条目并更新 total_bundles/groups 计数
- **FR-9**：所有交叉引用使用 `/` 开头的 bundle-relative 路径；中文正文、英文 kebab-case 文件名
- **FR-10**：每个非保留 .md 文件包含可解析的 YAML frontmatter，含 type 字段；概念/示例/信源文档含 title、description、tags、sources、generated、verified、status、stale_after

## Non-Functional Requirements
- **NFR-1**：零虚构 API——V 阶段对文档中引用的每个类名/函数名/方法名在源码中 Grep 验证存在性
- **NFR-2**：事实可溯源——每个概念文档的 frontmatter sources.facts 引用 F-xxx 编号，references 文档标注源码路径与行号
- **NFR-3**：分批生成——E 阶段每批生成 ≤7 个文件，防止上下文过载
- **NFR-4**：信源先行——references/ 文件先于 concepts/ 生成；index.md 最后生成
- **NFR-5**：链接完整——所有内部交叉引用无断链
- **NFR-6**：内容深度对齐已有高质量知识束（如 onnx/onnx 14概念+4示例+8信源），libzmq 因规模最大应最详尽（≥12 概念），cppzmq 较精简（≥5 概念），pyzmq/dramatiq 中等（≥7 概念）

## Constraints
- **Technical**：Markdown + YAML frontmatter（OKF v0.2）；源码只读；Windows 环境路径分隔符需注意
- **Business**：产出物位于 git submodule（awesome-okf-xs）内，遵循子项目规范但不修改其 .agents/ 规范文件
- **Dependencies**：source-code-to-okf-wiki 技能（R→I→E→V→C 工作流）、seven-concepts-cmd（方法论编排）；无外部依赖安装

## Assumptions
- 用户认可新建 `messaging/` 分组（bundles/ 下无现有消息通信分组）
- pyzmq 的 AGENTS.md LLM 禁令不适用于在独立仓库编写关于 pyzmq 的原创教育文档
- libzmq 聚焦核心架构（ctx/socket_base/session_base/pipe/engine/zmtp_engine/io_thread/poller），平台特定传输（VMCI/TIPC/VSOCK/NORM/PGM）仅在传输层概念文档中概要提及
- dramatiq 的 broker 后端（redis/rabbitmq/stub）均需覆盖

## Acceptance Criteria

### AC-1: 知识束目录结构完整
- **Given**：4 个源码项目位于 external/libs/remote/
- **When**：E 阶段完成
- **Then**：bundles/messaging/ 下存在 libzmq/、cppzmq/、pyzmq/、dramatiq/ 四个目录，每个含 concepts/、examples/、references/、spec/ 子目录及 index.md、log.md
- **Verification**: `programmatic`

### AC-2: facts.md 零推测
- **Given**：R 阶段事实采集完成
- **When**：审查 facts.md
- **Then**：每条事实 F-xxx 指向具体源码文件路径与行号，无"用于"/"目的是"等推断性表述
- **Verification**: `human-judgment`

### AC-3: 洞察四元组完整
- **Given**：I 阶段完成
- **When**：审查 insights.md
- **Then**：每个洞察包含陈述、证据（引用 F-xxx）、反常识点、行动建议四要素，且设计了知识地图（学习路径）
- **Verification**: `human-judgment`

### AC-4: API 真实性 Grep 验证通过
- **Given**：V 阶段验证
- **When**：对文档中引用的每个类名/函数名/方法名执行 Grep
- **Then**：100% 在对应源码中找到定义，无虚构 API
- **Verification**: `programmatic`

### AC-5: frontmatter 符合 OKF v0.2
- **Given**：所有 .md 文件生成
- **When**：检查每个非保留 .md 文件
- **Then**：含可解析 YAML frontmatter 且有非空 type 字段；根 index.md 含 okf_version: "0.2"；子目录 index.md 无 frontmatter
- **Verification**: `programmatic`

### AC-6: 交叉引用无断链
- **Given**：所有文档生成
- **When**：检查所有 `/` 开头的内部链接
- **Then**：每个链接目标文件存在
- **Verification**: `programmatic`

### AC-7: 内容深度达标
- **Given**：E 阶段完成
- **When**：统计各知识束内容文档数
- **Then**：libzmq ≥12 概念 + ≥3 示例 + ≥6 信源；cppzmq ≥5 概念 + ≥2 示例 + ≥2 信源；pyzmq ≥7 概念 + ≥2 示例 + ≥4 信源；dramatiq ≥7 概念 + ≥2 示例 + ≥4 信源
- **Verification**: `programmatic`

### AC-8: 分组索引与根索引更新
- **Given**：所有知识束生成
- **When**：检查 messaging/index.md 和 bundles/index.md
- **Then**：messaging/index.md 含 4 个知识束概览表与生态关系图；bundles/index.md 新增 messaging 分组且 total_bundles/groups 计数正确
- **Verification**: `human-judgment`

## Open Questions
- [ ] pyzmq 知识束是否应覆盖 Cython `.pyx` 后端源码（backend/cython/），还是仅聚焦 Python 层（sugar/、_future.py、asyncio.py 等）？倾向：Python 层为主，Cython 层在 references 中登记核心 `.pyx` 文件的关键函数但不逐行分析。
