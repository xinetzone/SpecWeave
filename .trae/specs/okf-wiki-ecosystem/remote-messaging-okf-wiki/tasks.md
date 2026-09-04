# remote 消息通信生态 OKF Wiki - 实施计划

## [x] Task 1: 创建 messaging 分组脚手架与分类索引
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `projects/awesome-okf-xs/bundles/messaging/` 目录
  - 创建 4 个知识束子目录（libzmq/cppzmq/pyzmq/dramatiq），每个含 concepts/、examples/、references/、spec/ 子目录
  - 生成 `messaging/index.md` 分组索引（type: category，含 okf_version、生态关系图、知识束概览表占位、推荐学习路径）
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `programmatic` TR-1.1: messaging/ 及 4 个知识束目录结构存在，每个含 concepts/examples/references/spec 四个子目录
  - `programmatic` TR-1.2: messaging/index.md 含 type: category frontmatter 和 okf_version: "0.2"
- **Notes**: 知识束概览表中的具体文档数在 E 阶段完成后回填

## [x] Task 2: libzmq R+I 阶段（事实采集与架构洞察）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 深度阅读 libzmq 源码：`include/zmq.h`（公共 C API）、`src/ctx.hpp/cpp`（上下文）、`src/socket_base.hpp/cpp`（套接字基类）、`src/session_base.hpp/cpp`（会话）、`src/pipe.hpp/cpp`（管道）、`src/zmtp_engine.hpp/cpp`（ZMTP 协议引擎）、`src/io_thread.hpp/cpp`（I/O 线程）、`src/poller.hpp`/`poll.cpp`（多路复用）、`src/msg.hpp/cpp`（消息）、`src/mailbox.hpp/cpp`（邮箱）、`src/object.hpp/cpp`（命令传递）、各 socket 类型实现（pub/sub/req/rep/router/dealer/push/pull/pair/stream 等）、`src/options.hpp/cpp`（套接字选项）、`src/tcp_*.cpp`、`src/ipc_*.cpp`、`src/inproc` 等传输层
  - 提取 ≥60 条编号事实 F-001~F-xxx 写入 `messaging/libzmq/spec/facts.md`，每条标注源码路径与行号
  - 提炼 4-6 个核心架构洞察四元组，设计知识地图（文档分组、学习路径、每篇概念覆盖哪些 F-xxx），写入 `messaging/libzmq/spec/insights.md`
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `human-judgement` TR-2.1: facts.md 每条事实含源码路径+行号，无推断性表述（"用于"/"目的是"）
  - `human-judgement` TR-2.2: insights.md 每个洞察含陈述/证据(F-xxx)/反常识/行动四要素
  - `human-judgement` TR-2.3: 知识地图明确 concepts 文档列表及每篇覆盖的 F-xxx 范围
- **Notes**: libzmq 是 4 个项目中规模最大的，src/ 下 200+ 文件；R 阶段聚焦核心架构文件，平台特定传输仅概要

## [x] Task 3: cppzmq R+I 阶段
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 阅读 cppzmq 源码：`zmq.hpp`（核心 header，context_t/socket_t/message_t/buffer/error_t/poller_t 等）、`zmq_addon.hpp`（高层抽象：multipart、recv_multipart/send_multipart 等）
  - 提取 ≥30 条事实写入 `messaging/cppzmq/spec/facts.md`
  - 提炼 3-4 个洞察 + 知识地图，写入 `messaging/cppzmq/spec/insights.md`
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `human-judgement` TR-3.1: facts.md 每条事实含行号，零推测
  - `human-judgement` TR-3.2: insights.md 四元组完整，知识地图覆盖 RAII/类型安全/buffer 抽象/poller/multipart

## [x] Task 4: pyzmq R+I 阶段
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 阅读 pyzmq Python 层源码：`zmq/__init__.py`、`zmq/sugar/`（context/socket/frame/poll/tracker/attrsetter）、`zmq/_future.py`、`zmq/asyncio.py`、`zmq/constants.py`、`zmq/error.py`、`zmq/decorators.py`、`zmq/backend/__init__.py`（后端选择）、`zmq/backend/cffi/`（CFFI 后端：context/socket/message/error）、`zmq/auth/`（认证：base/thread/asyncio/certs）、`zmq/eventloop/`（ioloop/zmqstream/future）、`zmq/green/`（gevent 适配）、`zmq/devices/`、`zmq/log/handlers.py`、`zmq/utils/`
  - Cython 后端 `zmq/backend/cython/` 的 `.pyx`/`.pxd` 文件仅在 references 中登记关键函数，不逐行分析
  - 提取 ≥45 条事实写入 `messaging/pyzmq/spec/facts.md`
  - 提炼 4-5 个洞察 + 知识地图，写入 `messaging/pyzmq/spec/insights.md`
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `human-judgement` TR-4.1: facts.md 覆盖 sugar 层、_future/asyncio、backend 选择、auth、eventloop、green、devices
  - `human-judgement` TR-4.2: insights.md 含双后端（Cython/CFFI）选择机制、sugar 纯 Python 封装层、asyncio 集成等洞察
- **Notes**: pyzmq AGENTS.md 禁止 LLM 向 pyzmq 项目贡献；本任务在独立 awesome-okf-xs 仓库中编写原创教育文档，不修改 pyzmq 任何文件

## [x] Task 5: dramatiq R+I 阶段
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 阅读 dramatiq 源码：`dramatiq/__init__.py`、`actor.py`（Actor 装饰器）、`broker.py`（Broker 抽象基类）、`brokers/redis.py`、`brokers/rabbitmq.py`、`brokers/stub.py`、`worker.py`（Worker 线程模型）、`message.py`（Message 编码/解码）、`middleware.py`（中间件基类与内置中间件）、`encoder.py`（JSON/pickle/messagepack 编码器）、`common.py`（工具函数）、`errors.py`、`generic.py`、`logging.py`、`threading.py`、`watcher.py`（文件监听自动重载）、`cli.py`（命令行）、`results/`（结果后端）、`canteen.py`、`asyncio.py`、`compat.py`、`py.typed`
  - 提取 ≥45 条事实写入 `messaging/dramatiq/spec/facts.md`
  - 提炼 4-5 个洞察 + 知识地图，写入 `messaging/dramatiq/spec/insights.md`
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `human-judgement` TR-5.1: facts.md 覆盖 Actor/Broker/Worker/Message/Middleware/Encoder/Results/CLI/Watcher
  - `human-judgement` TR-5.2: insights.md 含 actor 装饰器机制、broker 抽象与多后端、worker 线程模型、中间件管道、消息编码与重试等洞察

## [x] Task 6: libzmq E 阶段（批量生成 OKF 文档）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 按信源先行原则：先生成 references/ 信源登记文件（≥6 篇：zmq-h.md 公共 C API、ctx.md 上下文、socket-base.md 套接字基类、session-pipe.md 会话与管道、zmtp-engine.md ZMTP 引擎、io-poller.md I/O 线程与多路复用）
  - 分批生成 concepts/（每批 ≤7 篇）：≥12 篇概念文档，按学习路径编号（00 整体架构 → 01 上下文与生命周期 → 02 套接字与消息模式 → 03 消息 msg_t → 04 管道与会话 → 05 ZMTP 协议引擎 → 06 I/O 线程与 poller → 07 命令传递与 mailbox → 08 套接字选项 → 09 传输层 TCP/IPC/inproc → 10 Pub/Sub 模式 → 11 Req/Rep/Router/Dealer → 12 Push/Pull/Pair/Stream 等）
  - 生成 examples/（≥3 篇：Pub/Sub 天气更新、Req/Rep 基本请求应答、Router/Dealer 异步代理）
  - 最后生成各级 index.md 和 log.md
  - 根 index.md 含 type: bundle + okf_version: "0.2" frontmatter
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: concepts/ 下 ≥12 个 .md 文档（不含 index.md）
  - `programmatic` TR-6.2: references/ 下 ≥6 个信源文件
  - `programmatic` TR-6.3: examples/ 下 ≥3 个示例文件
  - `programmatic` TR-6.4: 每个非 index/log .md 文件含 type/title/description/sources frontmatter
  - `human-judgement` TR-6.5: 概念文档中文正文、代码块标注语言、每篇结尾有"相关概念"章节

## [x] Task 7: cppzmq E 阶段
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 生成 references/（≥2 篇：zmq-hpp.md 核心头文件、zmq-addon.md 扩展头文件）
  - 分批生成 concepts/（≥5 篇：00 整体架构与设计目标、01 context_t RAII 上下文、02 socket_t 类型安全套接字、03 message_t 与 buffer 抽象、04 错误处理与异常、05 poller_t 多路复用、06 multipart 多部分消息）
  - 生成 examples/（≥2 篇：Hello World push/pull、多部分消息收发）
  - 最后生成 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: concepts/ ≥5 文档，references/ ≥2，examples/ ≥2
  - `programmatic` TR-7.2: frontmatter 完整

## [x] Task 8: pyzmq E 阶段
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 生成 references/（≥4 篇：sugar-api.md sugar 层、future-asyncio.md 异步、backend.md 双后端、auth-devices.md 认证与设备）
  - 分批生成 concepts/（≥7 篇：00 整体架构与双后端、01 Context 上下文、02 Socket 与 sugar 语法、03 Frame/Message 消息、04 Poller 轮询、05 asyncio/Future 异步、06 auth 安全认证、07 eventloop/green/devices 生态）
  - 生成 examples/（≥2 篇：Pub/Sub 异步、Req/Rep 带认证）
  - 最后生成 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-8.1: concepts/ ≥7，references/ ≥4，examples/ ≥2
  - `programmatic` TR-8.2: frontmatter 完整，sources 标注 Python 源码路径

## [x] Task 9: dramatiq E 阶段
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 生成 references/（≥4 篇：actor-broker.md Actor 与 Broker、worker-middleware.md Worker 与中间件、message-encoder.md 消息与编码、brokers-backend.md 三种 Broker 后端）
  - 分批生成 concepts/（≥7 篇：00 整体架构、01 Actor 装饰器、02 Broker 抽象、03 Worker 线程模型、04 Message 与重试、05 Middleware 中间件、06 Encoder 序列化、07 Results 结果后端、08 CLI 与 Watcher）
  - 生成 examples/（≥2 篇：Redis broker 快速上手、RabbitMQ 自定义中间件）
  - 最后生成 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1: concepts/ ≥7，references/ ≥4，examples/ ≥2
  - `programmatic` TR-9.2: frontmatter 完整

## [x] Task 10: V 阶段独立验证（全 4 个知识束）
- **Priority**: high
- **Depends On**: Task 6, Task 7, Task 8, Task 9
- **Description**:
  - 对每个知识束执行：结构检查、frontmatter 检查、链接检查
  - Grep 级 API 真实性验证：提取文档中引用的每个类名/函数名/方法名，在对应源码中 Grep 验证存在性；发现虚构 API 立即修复
  - 代码示例检查：API 调用签名与源码一致
  - Index 完整性检查：index 列出的文件均存在且无遗漏
  - 输出验证报告，逐一修复发现的问题
  - 回填 messaging/index.md 中各知识束的准确文档计数
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: 所有内部 `/` 开头链接目标文件存在（0 断链）
  - `programmatic` TR-10.2: 文档中引用的关键类名/函数名 100% 在源码中 Grep 命中
  - `programmatic` TR-10.3: 每个非保留 .md 文件含非空 type 字段
  - `programmatic` TR-10.4: 子目录 index.md 无 frontmatter，根 index.md 含 okf_version
  - `human-judgement` TR-10.5: 代码示例 API 签名与源码一致
- **Notes**: V 阶段必须独立于 E 阶段（黑盒验证），不能由生成文档的同一上下文自我验证

## [x] Task 11: C 阶段收尾与根索引更新
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 更新 `bundles/index.md`：新增 messaging 分组条目，更新 total_bundles（+4）和 groups（+1）计数，在分组导航表和分组详情中添加 messaging 章节
  - 更新各知识束 log.md 记录 V 阶段验证结果
  - 回顾工作流，补充反模式与迁移验证（若有新模式则记录，但不强制写入 patterns/ 目录）
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-11.1: bundles/index.md 新增 messaging 分组条目，计数正确
  - `programmatic` TR-11.2: bundles/index.md 中 messaging 链接指向存在的文件
