---
type: Concept
title: 网络栈
description: TuyaOpen 网络栈架构，涵盖 WiFi Station/AP/Sniffer、蓝牙 NimBLE、有线以太网、蜂窝网络与 POSIX/LwIP 双后端
tags: [tuya, tuyaopen, network, wifi, bluetooth, ble, lwip, cellular, 网络]
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

# 网络栈

TuyaOpen 提供完整的多介质网络栈，覆盖 WiFi（Station/AP/Sniffer）、蓝牙（BLE/NimBLE）、有线以太网和蜂窝网络四种连接方式。网络抽象层 `tal_network` 支持 POSIX socket 和 LwIP 双后端，使应用代码可在 Linux 和 RTOS 间无缝切换。

## WiFi（tal_wifi）

WiFi 是 TuyaOpen 最核心的网络能力，`tal_wifi.h` 提供从基础连接到高级抓包的全套 API。

### 初始化与事件

WiFi 初始化需注册 station 事件回调：

```c
#include "tal_wifi.h"

static void wifi_event_cb(WF_EVENT_E event, void *data)
{
    switch (event) {
    case WFE_CONNECTED:
        PR_NOTICE("WiFi connected");
        break;
    case WFE_DISCONNECTED:
        PR_NOTICE("WiFi disconnected");
        break;
    default:
        break;
    }
}

OPERATE_RET ret = tal_wifi_init(wifi_event_cb);
```

### Station 模式

Station（STA）模式连接到现有 WiFi 网络：

```c
/* 连接到 AP */
tal_wifi_station_connect("MySSID", "MyPassword");

/* 断开连接 */
tal_wifi_station_disconnect();

/* 获取连接状态 */
WF_STATION_STAT_E stat = tal_wifi_station_get_status();

/* 获取错误状态 */
WF_STATION_ERR_STAT_E err = tal_wifi_station_get_err_stat();

/* 获取已连接 AP 的 RSSI */
int8_t rssi = tal_wifi_station_get_conn_ap_rssi();

/* 获取已连接 AP 信息 */
tal_wifi_get_connected_ap_info(&ap_info);

/* 快速连接（使用缓存凭据） */
tal_fast_station_connect();
```

### AP 扫描

```c
AP_IF_S *ap_list = NULL;
int ap_num = 0;

/* 扫描所有 AP */
tal_wifi_all_ap_scan(&ap_list, &ap_num);
for (int i = 0; i < ap_num; i++) {
    PR_INFO("SSID: %s, RSSI: %d", ap_list[i].ssid, ap_list[i].rssi);
}
tal_wifi_release_ap(ap_list);

/* 按 SSID 扫描指定 AP */
tal_wifi_assign_ap_scan("TargetSSID", &ap_list, &ap_num);
```

扫描结果通过 `tal_wifi_release_ap()` 释放内部分配的内存。

### SoftAP 模式

设备可创建热点供其他设备连接（常用于配网）：

```c
WF_AP_CFG_IF_S ap_cfg = {
    .ssid = "TuyaOpen-Device",
    .s_len = strlen(ap_cfg.ssid),
    .passwd = "12345678",
    .p_len = strlen(ap_cfg.passwd),
    .channel = 6,
    .security = WF_SECURITY_WPA2_PSK,
};
tal_wifi_ap_start(&ap_cfg);
/* ... */
tal_wifi_ap_stop();
```

### 混杂模式（Sniffer）

支持 802.11 帧捕获，可用于网络分析或特殊配网协议：

```c
static void sniffer_cb(const uint8_t *buf, uint32_t len, void *data)
{
    /* 处理 802.11 帧 */
}

tal_wifi_sniffer_set(TRUE, sniffer_cb, NULL);
/* ... */
tal_wifi_sniffer_set(FALSE, NULL, NULL);
```

头文件中定义了 802.11 帧类型常量：Probe Request(0x40)、Probe Response(0x50)、Auth(0xB0)、Beacon(0x80)、Data(0x08)、QoS Data(0x88)、MIMO Data(0xff)，以及 Beacon/Data/MIMO 帧结构（使用 `#pragma pack(1)` 确保 1 字节对齐）。

### 管理帧收发

```c
/* 发送管理帧 */
tal_wifi_send_mgnt(frame_buf, frame_len);

/* 注册接收管理帧回调 */
tal_wifi_register_recv_mgnt_callback(enable, callback, data);
```

### IP 与 MAC 地址管理

```c
/* IP 地址（按接口类型 WF_IF_E 区分） */
tal_wifi_get_ip(iface, &ip_info);
tal_wifi_set_ip(iface, &ip_info);

/* MAC 地址 */
tal_wifi_get_mac(mac_addr);
tal_wifi_set_mac(mac_addr);

/* BSSID */
tal_wifi_get_bssid(bssid);
```

### 工作模式与信道

```c
/* 工作模式（STA/AP/STA+AP） */
tal_wifi_set_work_mode(mode);
WF_WK_MD_E mode = tal_wifi_get_work_mode();

/* 信道管理 */
tal_wifi_set_cur_channel(channel);
uint8_t ch = tal_wifi_get_cur_channel();

/* 国家码 */
tal_wifi_set_country_code(country_code);
```

### WiFi 低功耗

```c
tal_wifi_lp_enable();
tal_wifi_lp_disable();
tal_wifi_set_lps_dtim(dtim);  /* 设置 DTIM 周期 */
```

### RF 校准与扩展接口

```c
/* RF 校准 */
BOOL_T calibrated = tal_wifi_rf_calibrated();

/* ioctl 扩展接口（命令类型 WF_IOCTL_CMD_E） */
tal_wifi_ioctl(cmd, in, in_len, out, out_len);
```

## 蓝牙（tal_bluetooth）

蓝牙组件通过 Kconfig 选项 `CONFIG_ENABLE_BLUETOOTH` 控制编译，源文件通过 `file(GLOB_RECURSE)` 递归收集 `src/*.c`。

TuyaOpen 支持 NimBLE 协议栈替代板级 BLE 栈，通过 `CONFIG_ENABLE_NIMBLE` 选项控制。NimBLE 源文件和头文件通过递归 glob 收集，包含 `nimble/host` 私有头文件目录。

蓝牙在 TuyaOpen 中主要用于：
- **BLE 配网**（`ENABLE_BT_NETCFG`，默认启用）：手机通过 BLE 发送 WiFi 凭据
- **BLE 控制**（`ENABLE_BT_CTRL`，默认启用）：蓝牙遥控和设备控制
- **BLE IoT 服务**（`ENABLE_BT_SERVICE`，默认关闭）：通用蓝牙 IoT 服务

蓝牙配置参数包括：
- 广播间隔：范围 10-2000ms，最小默认 30ms，最大默认 60ms
- 扫描间隔：默认 30ms，范围 10-2000ms
- 扫描窗口：默认 10ms，范围 10-2000ms
- NimBLE Host 任务优先级：默认 9（范围 0-100），栈大小默认 5120（范围 0-10000）

## 有线网络（tal_wired）

有线网络 API 简洁明了：

```c
#include "tal_wired.h"

/* 获取链路状态 */
WIRED_STAT_E stat = tal_wired_get_status();

/* 注册状态变更回调 */
static void status_cb(TKL_WIRED_STAT_E stat)
{
    PR_NOTICE("wired link status: %d", stat);
}
tal_wired_set_status_cb(status_cb);

/* IP 地址管理 */
tal_wired_set_ip(&ip_info);
tal_wired_get_ip(&ip_info);

/* MAC 地址管理 */
tal_wired_get_mac(mac);
tal_wired_set_mac(mac);
```

状态类型 `WIRED_STAT_E` 直接映射为 `TKL_WIRED_STAT_E`，状态变更回调类型映射为 `TKL_WIRED_STATUS_CHANGE_CB`。

## 蜂窝网络（tal_cellular）

蜂窝模块通过 `ENABLE_CELLULAR` 宏条件编译，采用描述符模式实现平台适配：

```c
/* 初始化 */
OPERATE_RET tal_cellular_init(void);

/* 获取状态 */
OPERATE_RET tal_cellular_get_status(TKL_CELLULAR_STATUS_E *stat);

/* 注册状态回调 */
OPERATE_RET tal_cellular_set_status_cb(TKL_CELLULAR_STATUS_CHANGE_CB cb);

/* 获取 IP */
OPERATE_RET tal_cellular_get_ip(TKL_CELLULAR_IP_S *ip);
```

内部实现维护静态指针 `sg_cellular` 指向 `TKL_CELLULAR_DESC_T` 描述符，通过 `tkl_cellular_desc_get()` 获取。描述符包含函数指针：`init`、`get_status`、`set_status_cb`、`get_ip` 等。当描述符或对应函数指针为 NULL 时返回 `OPRT_NOT_SUPPORTED`，使得无蜂窝硬件的平台无需提供桩实现。

## 网络抽象（tal_network）

`tal_network.c` 提供 POSIX 兼容的 socket 抽象，支持两种后端：

### POSIX 后端

在 Linux 等 POSIX 系统上，直接包含标准网络头文件：
```c
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
```

### LwIP 后端

在 RTOS 系统上使用 LwIP 协议栈（版本 2.1.2），包含：
```c
#include "lwip/netdb.h"
#include "lwip/dns.h"
```

### 统一执行宏

`TAL_NET_EXEC_OP` 宏统一执行网络操作：获取活跃 ops 表 → 检查函数指针非 NULL → 调用或返回默认值并打印错误。这种设计使得应用代码无需关心底层是 POSIX 还是 LwIP。

### LwIP 配置

LwIP 通过 `CONFIG_ENABLE_LIBLWIP` 选项控制编译：
- 源文件从 `lwip-2.1.2/src/core/*.c` 和 `src/api/*.c` 递归收集
- 额外包含 `netif/ethernet.c`
- 移植层源文件从 `port/*.c` 收集
- 支持 PPP 协议（`CONFIG_ENABLE_LWIP_PPP_SUPPORT`），从 `netif/ppp/*.c` 收集
- 公开头文件目录包含 `src/include`、`src/include/lwip`、`src/include/lwip/apps`、`src/include/compat`

## 网络协议中间件

在网络栈之上，TuyaOpen 提供应用层协议库：

### MQTT（libmqtt）

基于 AWS coreMQTT 实现，包含 Tuya 封装层 `mqtt_client_wrapper.c`。公开头文件目录为 `include`，私有头文件目录为 `coreMQTT/source/include`。MQTT 是设备连接涂鸦云的主要协议。

### HTTP（libhttp）

提供轻量级嵌入式 HTTP 主机服务 `http_host.h`：
- 支持监听、接收、分发、回复
- HTTP 方法最大长度 12，路径最大长度 96
- 配置包含端口、backlog、接收/发送超时、最大请求大小、线程栈深度和优先级
- 请求结构包含客户端 fd、原始请求、方法、路径、请求体及用户上下文
- 同时提供 HTTP 下载（`http_download.h`）、HTTP 会话（`http_session.h`）、门户认证（`http_captive.h`）等功能

### mbedTLS（libtls）

封装 mbedTLS 3.1.0 提供密码学操作：
- `cipher_wrapper.h` 基于 mbedTLS 封装认证加密/解密
- `cipher_params_t` 包含 key、nonce、ad（附加数据）、data 及各自长度
- `mbedtls_cipher_auth_encrypt_wrapper()` 输出密文和 tag
- `mbedtls_cipher_auth_decrypt_wrapper()` 验证 tag 并解密
- `mbedtls_message_digest()` 通用消息摘要
- `mbedtls_message_digest_hmac()` 通用 HMAC

## 云连接安全等级

涂鸦云服务定义 4 级安全等级（`TUYA_SECURITY_LEVEL`，范围 0-3，默认 1）：

| 等级 | 适用设备 | 认证方式 |
|------|---------|---------|
| 0 | 资源受限设备 | 仅能访问涂鸦云 |
| 1 | 资源受限设备 | 单向认证 |
| 2 | 资源丰富设备 | 双向认证 |
| 3 | 资源丰富设备 | 双向认证 + 安全芯片保护敏感信息 |

设备连云成功后会触发事件，日志中可见 `mqtt connected` 或事件 `TUYA_EVENT_DIRECT_MQTT_CONNECTED`。

## 相关概念

- [TAL 抽象层架构](/concepts/01-tal-architecture.md)
- [系统服务](/concepts/02-system-services.md)
- [安全与 KV 存储](/concepts/04-security-kv.md)
- [P2P 通信](/concepts/07-p2p-communication.md)
- [第三方库集成](/concepts/05-third-party-libs.md)
- [OpenClaw 云 API](/concepts/12-openclaw-api.md)
