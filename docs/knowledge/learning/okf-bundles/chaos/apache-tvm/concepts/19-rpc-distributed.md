---
type: Concept
title: RPC 与分布式
description: TVM RPC 远程调用系统与 Disco 分布式执行引擎，涵盖 RPCSession/Endpoint/Channel 三层架构、RPC Server/Tracker/Proxy、minRPC 嵌入式及 Disco Session/Worker
tags: [tvm, runtime, rpc, distributed, disco, tracker, proxy, session, worker]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: runtime-target-arith-source
    resource: "/references/runtime-target-arith-source.md"
    title: Runtime/Target/Arith 源码
---

# RPC 与分布式

TVM 的 RPC（Remote Procedure Call，远程过程调用）系统使编译器和运行时能够透明地访问远程设备，进行交叉编译、远程调优和分布式执行。RPC 是 TVM 自动调优（AutoTVM/MetaSchedule）流程的关键基础设施——调优时在本地生成调度方案，通过 RPC 发送到目标设备测量性能。在 RPC 之上，TVM 进一步构建了 Disco 分布式执行引擎，支持多设备张量并行和大模型分片推理。

## RPC 三层架构

RPC 模块源码位于 `src/runtime/rpc/` 目录 [F-82]，采用三层抽象架构 [F-87]：

### RPCSession：会话层

`rpc_session.h` 定义 `RPCSession` 类，管理远程函数调用和远程对象生命周期 [F-83]。Session 是 RPC 通信的顶层抽象，提供以下能力：

- **函数调用**：通过 `GetFunction(name)` 获取远程函数的本地代理（stub），调用时参数序列化发送到远程执行，返回值反序列化回传。
- **对象生命周期管理**：远程创建的对象（NDArray、Module 等）通过 `RPCObjectRef` 引用机制管理 [F-88]，确保远程对象在本地引用释放时正确释放，避免内存泄漏。
- **模块访问**：远程设备上加载的 Module 通过 Session 可访问，如同本地模块一样调用其中的函数。
- **张量传输**：Session 封装跨设备 NDArray 拷贝，本地张量可作为参数传递给远程函数，远程张量可拷贝回本地。

### RPCEndpoint：端点层

`rpc_endpoint.h` 定义 `RPCEndpoint` 类，处理通信端点的消息收发 [F-84]。Endpoint 负责：

- **消息序列化/反序列化**：将函数调用、参数和返回值编码为二进制协议格式。
- **请求-响应匹配**：为每个请求分配序列号，匹配异步返回的响应。
- **异常传播**：远程执行异常被捕获并传回调用端重新抛出。
- **回调处理**：远程端可能需要回调本地函数（如自定义分配器），Endpoint 支持双向调用。

### RPCChannel：通道层

`rpc_channel.h` 定义 `RPCChannel` 抽象接口，提供底层通信通道抽象 [F-85]。Channel 是可插拔的传输层，具体实现包括：

- **TCP Socket Channel**：基于标准 TCP/IP 的网络通信，用于局域网和云端设备。
- **WebSocket Channel**：基于 WebSocket 的通信，支持浏览器和代理环境。
- **Pipe Channel**：基于命名管道/UNIX domain socket 的本地进程间通信。
- **Custom Channel**：用户可实现自定义通道（如共享内存、InfiniBand RDMA）。

这种分层设计使 RPC 系统可以在不修改上层逻辑的情况下适配不同的传输介质。

## RPC Server / Tracker / Proxy

### RPC Server

RPC Server 是运行在目标设备上的守护进程，接收来自客户端的连接和函数调用请求。Server 端注册可远程访问的函数（包括设备管理、模块加载、内核执行等），并在收到请求时分发执行。

对于 GPU 等设备，RPC Server 直接运行在设备所在主机上，能够访问设备硬件。Server 可以同时服务多个客户端连接，每个连接拥有独立的 Session。

### RPC Tracker

RPC Tracker 是一个集中式的设备注册和发现服务。其工作模式为：

1. **设备注册**：RPC Server 启动时向 Tracker 注册自己的设备信息（设备类型、设备 ID、可用密钥等）。
2. **设备发现**：客户端向 Tracker 查询可用设备，Tracker 返回符合条件的 Server 地址。
3. **负载均衡**：Tracker 跟踪设备的空闲/忙碌状态，将客户端请求分配给空闲设备。
4. **动态扩缩**：Server 可随时加入或离开，Tracker 动态更新设备列表。

Tracker 使大规模自动调优成为可能：可以在一个设备集群上运行多个 RPC Server，调优进程通过 Tracker 请求空闲设备并行测量。

### RPC Proxy

RPC Proxy 是网络代理组件，主要用于以下场景：

- **NAT 穿越**：当目标设备位于内网或防火墙后，Proxy 提供公网访问入口。
- **连接中继**：客户端和服务器都位于受限网络时，通过 Proxy 中继通信。
- **协议转换**：在 TCP 和 WebSocket 等协议间转换。

Proxy 模式下，RPC Server 主动连接 Proxy 并注册，客户端连接 Proxy 后被路由到对应 Server。这种反向连接模式使位于防火墙后的设备也能被访问。

## RPCModule

`rpc_module.cc` 实现 RPC 模块，使远程设备上的模块可通过统一 Module 接口访问 [F-86]。RPCModule 是 TVM Module 系统的远程代理：

1. 客户端通过 Session 调用远程的 `module.Load` 或 `runtime.LoadModule` 加载模块。
2. 返回一个 RPCModule 对象，它持有远程模块的引用句柄。
3. 调用 `RPCModule::GetFunction(name)` 时，返回一个 `ffi::Function` stub。
4. 调用 stub 时，函数名和参数通过 RPC 发送到远程模块执行。
5. 返回值（可能包含远程 NDArray）通过 Session 传回。

这种设计使编译和调优流程无需关心模块是本地还是远程——代码对 Module 接口编程，底层自动处理本地/远程分发。

## minRPC：嵌入式 RPC

minRPC 是 TVM RPC 协议的精简实现，专为资源受限的嵌入式设备设计。其特点包括：

- **最小依赖**：不使用 C++ 标准库的复杂功能，可在裸机环境运行。
- **紧凑二进制协议**：最小化消息开销，适合低带宽连接。
- **静态内存**：使用预分配缓冲区，避免动态内存分配。
- **单线程事件循环**：不需要多线程支持。

minRPC 使得 TVM 能够在微控制器和 IoT 设备上进行远程调优和部署——交叉编译后的模型通过 minRPC 加载到设备执行和测量。

## Python 端集成

Python 端 RPC 会话掩码 `RPC_SESS_MASK = 128` 定义在 `python/tvm/runtime/device.py` [F-89]。远程设备的 device_type 通过此掩码标记，使 Runtime 能区分本地设备和远程设备。Python VM 从 `..rpc.base` 导入 `RPC_SESS_MASK` [F-90]。

Python 端 RPC 使用示例：

```python
# 连接到 RPC Tracker 请求设备
remote = tvm.rpc.connect_tracker(tracker_host, tracker_port)
device = remote.request_device("gpu")

# 上传编译后的模块
remote.upload("compiled_model.tar")
lib = remote.load_module("compiled_model.tar")

# 在远程设备上创建张量并运行
x = tvm.nd.array(input_data, device=device)
y = tvm.nd.empty(output_shape, device=device)
lib["main"](x, y)

# 取回结果
output = y.numpy()
```

## Disco 分布式执行引擎

Disco 是 TVM 的分布式执行引擎，在 RPC 基础设施之上构建，支持多设备张量并行。Disco 模块是可选导入，当 `libtvm_runtime_extra` 不存在时静默设为 None [F-50]。

### Disco 架构

Disco 采用单控制器多工作器（Single-Program-Multiple-Data，SPMD）架构：

- **Session（会话）**：分布式执行的协调者，运行在控制器进程中。Session 将计算图分区并分发给各 Worker，管理全局分布式状态。
- **Worker（工作器）**：运行在每个设备上的执行单元，通过 RPC 与 Session 通信。Worker 持有本地设备上的张量分片，执行接收到的指令。
- **Builtin（内置函数）**：Disco 提供的分布式原语，包括：
  - **广播（broadcast）**：将张量从一个设备复制到所有设备。
  - **散射（scatter）/收集（gather）**：按维度切分/合并张量。
  - **全归约（all-reduce）**：跨设备聚合张量（求和、求最大值等）。
  - **全收集（all-gather）**：收集所有设备上的张量分片。
  - **规约散射（reduce-scatter）**：归约并散射结果。

### 张量并行

Disco 支持张量并行推理，特别适合大语言模型：

1. **权重分片**：模型权重按列或行切分到多个 GPU。
2. **分布式矩阵乘**：每个 GPU 计算矩阵乘的一部分，结果通过 all-reduce 聚合。
3. **KV 缓存分片**：注意力层的 KV 缓存也分布在多设备上。
4. **透明执行**：Relax 编译时通过注解标注分片策略，Disco 运行时自动处理跨设备通信。

### 与 Relax 集成

Relax 的 `distributed` 子包提供分布式算子和注解，在编译期确定张量分片布局。Disco 在运行期执行分布式调度：

- `relax.distributed.CallDistReduce` 等算子被编译为 Disco builtin 调用。
- `ccl`（集合通信）算子映射到 Disco 的通信原语。
- 编译后的分布式函数可在单进程多设备或多进程多节点环境运行。

## RPC 在自动调优中的角色

RPC 是 TVM 自动调优流程的关键使能技术：

1. **交叉编译**：在开发机（x86）上为目标设备（ARM、GPU 等）编译内核。
2. **远程测量**：编译后的内核通过 RPC 上传到目标设备运行，测量实际执行时间。
3. **结果回收**：测量结果通过 RPC 回传到调优器，指导下一代搜索。
4. **并行调优**：利用 Tracker 管理设备池，多设备并行测量加速搜索。

这一流程使开发者无需在目标设备上安装完整的 TVM 编译器——设备端只需运行最小化的 TVM Runtime 和 RPC Server。

## 设计要点

TVM RPC 与分布式系统的设计体现了以下原则：

1. **透明性**：远程 Module/NDArray 通过与本地相同的接口访问，上层代码无需感知位置差异。
2. **分层解耦**：Session/Endpoint/Channel 三层分离，每层可独立替换和测试。
3. **最小化端侧**：minRPC 和最小 Runtime 使端侧部署开销极低，适合嵌入式和边缘设备。
4. **生态友好**：Tracker/Proxy 模式支持多种网络拓扑，适应集群、云端和边缘的不同部署环境。
5. **从调优到推理**：同一 RPC 基础设施既用于开发期的自动调优，也用于生产期的分布式推理，减少技术栈碎片化。

## 相关概念

- [Runtime Module 系统](/concepts/17-runtime-module.md) — RPCModule 是 Module 的远程代理，通过统一接口访问远程设备上的模块
- [MetaSchedule 自动调度](/concepts/09-meta-schedule.md) — RPC 是自动调优的关键基础设施，将编译内核发送到目标设备远程测量性能
- [VM 字节码虚拟机](/concepts/18-vm-bytecode.md) — VM 可通过 RPC 在远程设备上加载执行，支持分布式模型推理
- [Target 与代码生成](/concepts/04-target-codegen.md) — RPC 支持交叉编译工作流，在开发机编译、在目标设备运行
- [Relax 算子体系](/concepts/13-relax-ops.md) — Relax 的 ccl/distributed 算子在 Disco 分布式引擎上映射为集合通信原语
