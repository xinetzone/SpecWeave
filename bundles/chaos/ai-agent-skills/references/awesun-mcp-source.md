---
type: Reference
title: awesun-mcp 源码
description: 向日葵 AweSun MCP Server 源码登记，含 22 个工具规格（设备管理 7+远控会话 6+桌面操作 9）与双模式通信
tags: [agent-skills, awesun, mcp, source, reference, remote-control]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-awesun-mcp
    resource: "/references/facts-awesun-mcp.md"
    title: awesun-mcp 事实清单
---

# awesun-mcp 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | 向日葵 AweSun MCP Server |
| 定位 | 通过 MCP 协议将向日葵远程控制能力接入 AI 助手 |
| 源码路径 | `d:\AI\.chaos\libs\awesun-mcp\` |
| 客户端要求 | 向日葵客户端 16.2.3.28762 或更高 |
| 部署方式 | 内置于向日葵客户端，无需额外安装服务端 |
| 通信模式 | Stdio（本地进程通信，低延迟）+ HTTP（远程跨网络调用） |
| 工具总数 | 22 个（设备管理 7 + 远控会话 6 + 桌面操作 9） |

## 工具清单

### 设备管理类（7 个）

| 工具名 | 功能 | 必填参数 | 可选参数 |
|--------|------|---------|---------|
| `device_add` | 添加新设备到设备列表 | name (string) | desc (string) |
| `device_search` | 模糊搜索设备 | limit (int64, 最大 100) | keyword (string) |
| `device_info` | 查询设备完整详细信息 | remote_id (int64) | — |
| `device_update` | 修改设备名称和描述 | remote_id (int64) | name, desc |
| `device_remove` | 移除设备 | remote_id (int64) | — |
| `device_wakeup` | 发送开机指令（需开机棒或 WOL） | remote_id (int64) | — |
| `device_shutdown` | 发送关机指令（设备需在线） | remote_id (int64) | — |

`device_search` 返回的设备对象包含 22 个字段：remote_id、name、description、pc_name、cpu、mac、memory、screen_size、client、os、os_name、base_board、disk_drive、video_controller、network_adapter、version、online、fastcode、login_time、ip、lan_ip、create_time。`device_info` 在此基础上额外返回 plugins（支持的远控插件列表）。

### 远控会话类（6 个）

| 工具名 | 功能 | 必填参数 | 关键说明 |
|--------|------|---------|---------|
| `control_connect` | 发起远控会话连接 | type (string) | 支持 file/desktop/cmd2/ssh/desktop_view/newcamera/forward 七种类型；可选 remote_id |
| `control_sessions` | 查询所有活跃远控会话 | — | 返回会话 ID、类型和状态 |
| `control_disconnect` | 终止活跃远控会话 | session_id (string) | — |
| `control_command` | 在 CMD 会话中执行命令 | command, session_id | 可选 args (array)，返回退出码/stdout/stderr；目前支持 Windows CMD |
| `control_screenshot` | 远程桌面截图 | session_id | 返回 Base64 图片及尺寸；仅支持 desktop/desktop_view |
| `control_portforward` | 配置端口转发规则 | session_id, target_addresses (array) | 仅支持 forward 类型 |

### 桌面操作类（9 个）

| 工具名 | 功能 | 关键参数 |
|--------|------|---------|
| `desktop_click_mouse` | 模拟鼠标点击 | button (left/right/middle)、clicks (2=双击)、coordinates (归一化)、session_id |
| `desktop_move_mouse` | 移动鼠标光标 | coordinates、session_id |
| `desktop_drag_mouse` | 模拟鼠标拖拽 | 路径坐标（归一化）、按键、session_id |
| `desktop_scroll_mouse` | 模拟鼠标滚轮 | coordinates、direction、amount、session_id |
| `desktop_press_keys` | 精确控制按键按下或释放 | keys、action (press/release)、session_id |
| `desktop_typing_keys` | 执行组合快捷键操作 | keys (组合键列表)、session_id |
| `desktop_typing_text` | 逐字符模拟键盘输入文本 | text、session_id |
| `desktop_paste_text` | 通过剪贴板粘贴长文本 | text、session_id |
| `desktop_waiting` | 在操作序列中插入暂停等待 | duration (秒)、session_id |

桌面操作坐标使用归一化值（0.0-1.0），通过 `x_pixel / 屏幕宽度` 计算，左上角为原点 (0.0, 0.0)，右下角为 (1.0, 1.0)。

## 关键文档

| 文件 | 职责 |
|------|------|
| `README.md` | 项目说明、工具分类清单、使用场景、安全机制 |
| `docs/mcp_tools.md` | 22 个工具的完整参数规格与返回字段定义 |

## 使用场景

1. **远程运维自动化**：AI 自动登录远程服务器执行命令、查看日志、重启服务并截图确认。
2. **批量设备管理**：通过设备搜索和筛选批量获取设备状态，识别异常设备并发送告警。
3. **自动化 UI 测试**：结合截图和桌面操作工具自动操作远程桌面完成 UI 测试流程。
4. **远程技术支持**：AI 协助定位问题，直接操作用户设备查看设置、运行诊断命令。

## 安全机制

基于向日葵成熟的远控安全体系，需设备验证码或已信任设备才能建立连接。MCP 服务通过 token 认证（AWESUN_API_TOKEN），本地 API 默认监听 127.0.0.1:8908。
