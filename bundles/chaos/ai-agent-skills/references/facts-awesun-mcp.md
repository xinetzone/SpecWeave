# awesun-mcp 事实清单

> R阶段事实采集。源码路径：d:\AI\.chaos\libs\awesun-mcp\
> 采集日期：2026-08-23

## 项目概述

- F-001: 项目名称为"向日葵 AweSun MCP Server"，通过 MCP 协议将向日葵远程控制能力接入 AI 助手 — 源码：`README.md:1-3`
- F-002: 需要向日葵客户端版本 16.2.3.28762 或更高，并启用相关功能 — 源码：`README.md:5`
- F-003: 内置于向日葵客户端，无需额外安装服务端，一键启用自动生成 MCP 配置 — 源码：`README.md:18-20`
- F-004: 支持双模式通信：Stdio 模式（本地进程通信，低延迟）和 HTTP 模式（远程跨网络调用） — 源码：`README.md:22-24`

## 工具分类与数量

- F-005: 共提供 22 个工具，分三大类：7 个设备管理工具 + 6 个远控会话工具 + 9 个桌面操作工具 — 源码：`README.md:27`
- F-006: 设备管理类工具包括：device_add、device_search、device_info、device_update、device_remove、device_wakeup、device_shutdown — 源码：`README.md:74-80`
- F-007: 远控会话类工具包括：control_connect、control_sessions、control_disconnect、control_command、control_screenshot、control_portforward — 源码：`README.md:86-91`
- F-008: 桌面操作类工具包括：desktop_click_mouse、desktop_move_mouse、desktop_drag_mouse、desktop_scroll_mouse 等 9 个 — 源码：`README.md:97-100`

## 设备管理工具规格

- F-009: device_add 将新设备添加到设备列表，必填参数 name（string），可选参数 desc（string），返回 remote_id — 源码：`docs/mcp_tools.md:9-23`
- F-010: device_search 根据关键词模糊搜索设备，必填参数 limit（int64，最大 100），可选参数 keyword（string），返回 total 和 devices 数组 — 源码：`docs/mcp_tools.md:27-42`
- F-011: device_search 返回的设备对象包含 22 个字段：remote_id、name、description、pc_name、cpu、mac、memory、screen_size、client、os、os_name、base_board、disk_drive、video_controller、network_adapter、version、online、fastcode、login_time、ip、lan_ip、create_time — 源码：`docs/mcp_tools.md:44-66`
- F-012: device_info 查询指定设备完整详细信息，必填参数 remote_id（int64），返回字段比 device_search 多一个 plugins（支持的远控插件列表） — 源码：`docs/mcp_tools.md:70-102`
- F-013: device_update 修改设备名称和描述，必填参数 remote_id（int64），可选参数 name 和 desc — 源码：`docs/mcp_tools.md:106-117`
- F-014: device_wakeup 向绑定开机硬件的设备发送开机指令，需设备配置开机棒或主板支持 WOL — 源码：`README.md:79`
- F-015: device_shutdown 向在线远程设备发送关机指令，设备需在线且被控端支持关机 — 源码：`README.md:80`

## 远控会话工具规格

- F-016: control_connect 发起远控会话连接，必填参数 type（string），支持类型：file（远程文件）、desktop（远程桌面）、cmd2（远程 CMD，Windows）、ssh（远程 SSH，Linux/Mac）、desktop_view（桌面观看）、newcamera（摄像头）、forward（端口转发） — 源码：`README.md:86`、`docs/mcp_tools.md`（control_connect 节）
- F-017: control_connect 可选参数 remote_id（integer），通过已存在设备发起远控，连接成功返回会话 ID — 源码：`README.md:86`
- F-018: control_sessions 查询所有当前活跃远控会话，包括会话 ID、类型和状态 — 源码：`README.md:87`
- F-019: control_disconnect 终止指定活跃远控会话，必填参数 session_id（string） — 源码：`README.md:88`
- F-020: control_command 在已建立的 CMD 远程会话中执行命令，目前支持 Windows CMD，必填参数 command（string）和 session_id（string），可选参数 args（array），返回退出码、标准输出和错误输出 — 源码：`README.md:89`
- F-021: control_screenshot 对远程桌面会话截图，返回 Base64 编码图片数据及尺寸信息，仅支持 desktop/desktop_view 类型 — 源码：`README.md:90`
- F-022: control_portforward 配置端口转发规则（覆盖），仅支持 forward 类型会话，必填参数 session_id 和 target_addresses（array） — 源码：`README.md:91`

## 桌面操作工具规格

- F-023: desktop_click_mouse 模拟鼠标点击，必填参数 button（left/right/middle）、clicks（integer，2 为双击）、coordinates（array，归一化坐标）、session_id — 源码：`README.md:97`
- F-024: 桌面操作坐标使用归一化值（0.0-1.0），通过 x_pixel/屏幕宽度 计算 — 源码：`README.md:97`
- F-025: desktop_drag_mouse 模拟鼠标拖拽，支持按住指定按键沿路径移动，路径坐标需归一化 — 源码：`README.md:99`
- F-026: desktop_move_mouse 将鼠标光标移动到指定坐标位置，常用于拖拽前定位 — 源码：`README.md:98`
- F-027: desktop_scroll_mouse 在指定位置模拟鼠标滚轮滚动，支持向上或向下滚动指定次数 — 源码：`README.md:100`

## 使用场景

- F-028: 远程运维自动化：AI 自动登录远程服务器执行命令、查看日志、重启服务并截图确认 — 源码：`README.md:37-38`
- F-029: 批量设备管理：通过设备搜索和筛选批量获取设备状态，识别异常设备并发送告警 — 源码：`README.md:40-41`
- F-030: 自动化 UI 测试：结合截图和桌面操作工具自动操作远程桌面完成 UI 测试流程 — 源码：`README.md:43-44`
- F-031: 远程技术支持：AI 协助定位问题，直接操作用户设备查看设置、运行诊断命令 — 源码：`README.md:46-47`

## 安全机制

- F-032: 基于向日葵成熟的远控安全体系，需设备验证码或已信任设备才能建立连接 — 源码：`README.md:31-32`
