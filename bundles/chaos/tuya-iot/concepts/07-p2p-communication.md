---
type: Concept
title: P2P 通信
description: TuyaOpen P2P 音视频通信架构，涵盖 ICE 穿透、KCP 可靠传输、RTP/RTCP 媒体流与 SDP 协商
tags: [tuya, tuyaopen, p2p, ice, kcp, rtp, rtcp, sdp, webrtc, 音视频]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: tuyaopen-core-source
    resource: "/references/tuyaopen-core-source.md"
    title: TuyaOpen 核心框架源码
  - id: facts-tuyaopen-core
    resource: "/references/facts-tuyaopen-core.md"
    title: TuyaOpen 核心框架事实清单
---

# P2P 通信

TuyaOpen 的 P2P 组件（`src/tuya_p2p/`）提供设备与移动端/云端之间的点对点实时通信能力，主要用于 IPC（网络摄像头）音视频传输、远程控制和低延迟数据通道。该组件通过 `CONFIG_ENABLE_TUYA_P2P` 选项控制编译（默认关闭），由五个子组件构成完整的实时通信栈。

## 架构概览

P2P 模块采用分层架构：

```text
┌─────────────────────────────────────┐
│         应用层（IPC/音视频）          │
├─────────────────────────────────────┤
│  svc_streaming_p2p  (流式 P2P 服务)  │
│  svc_ipc_core       (IPC 核心服务)   │
├─────────────────────────────────────┤
│  lib_rtp  (RTP/RTCP 媒体传输)        │
├─────────────────────────────────────┤
│  base_ice  (ICE 穿透 + KCP + SDP)    │
├─────────────────────────────────────┤
│  tal_network / tal_wifi (网络层)     │
└─────────────────────────────────────┘
```

五个子组件通过 CMakeLists.txt 组织：
- `base_ice`：ICE 网络穿透、KCP 可靠 UDP、SDP 协商
- `lib_rtp`：RTP/RTCP 媒体打包与传输
- `pjproject`：PJSIP 多媒体框架（SIP/SDP 基础）
- `svc_ipc_core`：IPC 设备核心逻辑
- `svc_streaming_p2p`：P2P 流媒体服务

## base_ice：穿透与传输层

base_ice 是 P2P 通信的网络基础，集成了 KCP 可靠传输、ICE NAT 穿透和 SDP 信令处理。

### KCP 可靠 UDP

`ikcp.c` 和 `ikcp.h` 实现了 KCP 协议——一种快速可靠的 ARQ（自动重传请求）协议，运行于 UDP 之上。与 TCP 相比，KCP 在牺牲适当带宽的前提下大幅降低传输延迟，适合音视频等对延迟敏感的实时场景。KCP 负责将不可靠的 UDP 数据报转化为有序、可靠、流量可控的数据流。

### ICE 协议

ICE（Interactive Connectivity Establishment）是 NAT 穿透标准协议，TuyaOpen 实现了完整的 ICE 栈：

- `pj_ice.c` / `pj_ice.h`：ICE 会话管理、候选地址收集、连通性检查
- `pj_sdp.c` / `pj_sdp.h`：SDP（Session Description Protocol）构建与解析
- `pj_sync_condition.c` / `pj_sync_condition.h`：同步条件变量，用于 ICE 检查过程中的线程同步

ICE 工作流程：
1. 收集候选地址（主机地址、服务器反射地址、中继地址）
2. 通过信令通道交换 SDP（含候选地址列表）
3. 执行连通性检查（STUN bind 请求/响应）
4. 选定最优路径对（NAT 直连或中继转发）
5. 建立 P2P 连接

### Tuya 媒体服务扩展

- `tuya_media_service_rtc.c`：Tuya 自定义媒体服务 RTC 实现，在标准 ICE 之上集成涂鸦信令
- `tuya_sdp.c` / `tuya_sdp.h`：Tuya SDP 扩展，添加涂鸦特有的媒体属性
- `tuya_rtp.h`：Tuya RTP 头定义，与标准 RTP 兼容但可能包含扩展字段

### 工具与错误处理

- `tuya_error.c` / `tuya_error.h`：P2P 模块统一错误码定义
- `tuya_log.h`：P2P 专用日志宏
- `tuya_misc.c` / `tuya_misc.h`：杂项工具函数
- `queue.h`：队列数据结构

## lib_rtp：RTP/RTCP 媒体层

lib_rtp 实现 RTP（Real-time Transport Protocol）和 RTCP（RTP Control Protocol），负责音视频数据的打包、传输和质量反馈。

### RTP 核心头文件

| 头文件 | 职责 |
|--------|------|
| `rtp.h` | RTP 核心接口 |
| `rtp-packet.h` | RTP 数据包结构 |
| `rtp-header.h` | RTP 头解析与构建 |
| `rtp-header-extension.h` | RTP 头扩展 |
| `rtp-ext.h` | 扩展定义 |
| `rtp-demuxer.h` | RTP 解复用器（按 SSRC/PT 分流） |
| `rtp-member.h` | RTP 成员（参与方）管理 |
| `rtp-member-list.h` | 成员列表 |
| `rtp-ssrc.h` | SSRC（同步源标识符）管理 |
| `rtp-time.h` | RTP 时间戳处理 |

### RTCP 实现

源文件实现了完整的 RTCP 报告类型：

| 源文件 | RTCP 包类型 | 用途 |
|--------|------------|------|
| `rtcp-sr.c` | Sender Report | 发送方报告（发送统计） |
| `rtcp-rr.c` | Receiver Report | 接收方报告（接收统计） |
| `rtcp-bye.c` | BYE | 会话离开通知 |
| `rtcp-app.c` | APP | 应用自定义消息 |
| `rtcp-xr.c` | Extended Report | 扩展报告（VoIP 质量指标） |
| `rtcp.c` | RTCP 核心 | 包构建/解析/调度 |

RTCP 提供的反馈信息包括：丢包率、抖动、往返时间（RTT）、累计丢包数等，发送方可根据这些信息动态调整码率（拥塞控制）。

### RTP 辅助组件

- `rtp-profile.c`：RTP Profile（负载类型映射）
- `rtp-queue.c`：RTP 包队列（抖动缓冲、重排序）
- `rtp-param.c`：RTP 参数配置
- `rtp-util.c`：工具函数
- `rtp.c`：RTP 核心实现

## SDP 协商

SDP（Session Description Protocol）在 P2P 建立过程中描述媒体能力和网络候选地址。TuyaOpen 的 SDP 实现包含标准字段和 Tuya 扩展：

- 会话级字段（v=, o=, s=, c=, t=）
- 媒体级字段（m= audio/video, port, protocol, payload types）
- ICE 候选地址（a=candidate:...）
- DTLS 指纹（a=fingerprint:...，用于加密）
- 编解码器参数（a=rtpmap, a=fmtp）

SDP 交换后，双方通过 ICE 检查建立传输通道，然后通过 RTP 传输媒体数据。

## P2P 连接建立流程

典型的 P2P 连接建立过程：

1. **设备上线**：设备连接涂鸦云，注册设备 ID 和能力
2. **客户端请求**：App 请求与设备建立 P2P 连接
3. **信令交换**：通过云端 MQTT/长连接通道交换 SDP offer/answer
4. **ICE 穿透**：双方收集候选地址并进行连通性检查
5. **通道建立**：选定最优路径（直连或中继）
6. **媒体协商**：通过 SDP 协商音视频编解码器、分辨率、码率
7. **RTP 传输**：通过 base_ice 的 KCP/UDP 通道传输 RTP 包
8. **RTCP 监控**：定期发送 RTCP 报告，监控连接质量
9. **连接断开**：发送 RTCP BYE 或超时断开

## 与 AI 组件的协同

P2P 组件与 AI 组件协同工作，构成智能 IPC 解决方案：

- `ai_video`：视频编码/解码、AI 视觉处理，输出编码后的 H.264/H.265 帧通过 RTP 传输
- `ai_audio`：音频采集/编解码（G.711/AAC/Opus），双向语音对讲
- `ai_mcp`：通过 MCP 协议与 LLM 交互，实现智能告警、语音助手等功能
- `tal_image`：图像处理（YUV→RGB、缩放、旋转、JPEG 抓拍）

典型场景：摄像头检测到移动 → AI 识别为人形 → 通过 P2P 向 App 推送告警视频 → 用户通过 App 语音对讲 → 音频经 RTP 下行到设备。

## 编译与配置

启用 P2P 功能：

```ini
# app_default.config
CONFIG_ENABLE_TUYA_P2P=y
```

P2P 模块包含第三方代码（pjproject、KCP），编译时可能需要额外的栈大小和堆内存。资源受限设备应评估是否需要完整 P2P 能力，或仅使用云端中转方案。

## 相关概念

- [网络栈](/concepts/03-network-stack.md)
- [AI 组件](/concepts/08-ai-components.md)
- [系统服务](/concepts/02-system-services.md)
- [第三方库集成](/concepts/05-third-party-libs.md)
