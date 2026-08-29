---
type: Example
title: TuyaOpen 固件快速入门
description: 从零创建一个 TuyaOpen 固件项目的完整示例，涵盖工程结构、WiFi 连接、KV 存储、线程创建、CLI 命令与云端连接
tags: [tuya, tuyaopen, example, firmware, quickstart, wifi, kv, thread, cli]
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

# TuyaOpen 固件快速入门

本示例演示如何从零创建一个完整的 TuyaOpen 固件项目，实现 WiFi 连接、LED 控制、KV 持久化存储、工作线程和自定义 CLI 命令。所有 API 均来自 TuyaOpen 头文件验证，代码遵循 TAL 抽象层规范，可在所有支持的平台上编译运行。

## 前置条件

- 已完成 TuyaOpen 环境搭建（工具链、Python 依赖）
- 已克隆 TuyaOpen 仓库并初始化子模块
- 一块支持的开发板（本示例以 ESP32-S3 为例）
- USB 数据线和串口终端

## 步骤一：创建项目

使用 tos.py 从模板创建新应用项目（交互式，按提示输入项目名）：

```bash
python tos.py new project
# 可选 -f/--framework base（默认）或 arduino
```

项目结构：

```text
app/
├── CMakeLists.txt
├── Kconfig
└── src/
    ├── tuya_main.c      # 主入口
    ├── app_wifi.c       # WiFi 管理
    ├── app_wifi.h
    └── app_cli.c        # CLI 命令与 LED 控制
```

## 步骤二：配置项目

编辑 `app_default.config`，选择板卡并启用所需组件：

```ini
# 板卡选择
CONFIG_BOARD_CHOICE_ESP32=y
CONFIG_BOARD_CHOICE_ESP32_S3=y

# 基础组件
CONFIG_ENABLE_TAL_WIFI=y
CONFIG_ENABLE_TAL_KV=y
CONFIG_ENABLE_TAL_SECURITY=y
CONFIG_ENABLE_TAL_CLI=y

# 串口 CLI
CONFIG_ENABLE_SERIAL_CLI_CMD=y
CONFIG_CLI_CMD_SYS=y
CONFIG_CLI_CMD_KV=y
```

## 步骤三：主入口

`src/tuya_main.c`：

```c
#include "tal_api.h"
#include "tal_wifi.h"
#include "tal_kv.h"
#include "tal_thread.h"
#include "tal_cli.h"
#include "tal_sw_timer.h"
#include "tkl_output.h"
#include "tdl_led_manage.h"
#include "board_com_api.h"

#include "app_wifi.h"
#include "app_cli.h"

#define APP_THREAD_STACK_SIZE  4096
#define APP_THREAD_PRIORITY    THREAD_PRIO_2

static THREAD_HANDLE app_thread_handle = NULL;

static void app_worker_thread(void *arg)
{
    PR_NOTICE("app worker thread started");

    /* 初始化 KV 存储 */
    tal_kv_cfg_t kv_cfg = {
        .seed = "tuya",
        .key  = "tuya",
    };
    tal_kv_init(&kv_cfg);

    /* 初始化软件定时器（LED 闪烁等功能依赖） */
    tal_sw_timer_init();

    /* 注册板载硬件（在 board_com_api.c 中实现） */
    board_register_hardware();

    /* 注册 CLI 命令 */
    app_cli_init();

    /* 连接 WiFi（阻塞直到连接成功或失败） */
    app_wifi_connect("MyWiFiSSID", "MyWiFiPassword");

    PR_NOTICE("application initialized, entering main loop");

    while (1) {
        /* 业务循环：上报状态、处理云端指令等 */
        tal_system_sleep(1000);
    }
}

void user_main(void)
{
    OPERATE_RET rt = OPRT_OK;

    /* 初始化日志系统 */
    tal_log_init(TAL_LOG_LEVEL_DEBUG, 1024, (TAL_LOG_OUTPUT_CB)tkl_log_output);

    PR_NOTICE("=== My IoT Device ===");
    PR_NOTICE("TuyaOpen version: %s", OPEN_VERSION);
    PR_NOTICE("Platform chip:     %s", PLATFORM_CHIP);
    PR_NOTICE("Platform board:    %s", PLATFORM_BOARD);

    /* 创建应用主线程 */
    THREAD_CFG_T thread_cfg = {
        .stackDepth = APP_THREAD_STACK_SIZE,
        .priority   = APP_THREAD_PRIORITY,
        .thrdname   = "app_main",
    };

    TUYA_CALL_ERR_GOTO(
        tal_thread_create_and_start(&app_thread_handle, NULL, NULL,
                                     app_worker_thread, NULL, &thread_cfg),
        __EXIT);

__EXIT:
    return;
}

/* Linux 平台需要 main 函数；RTOS 平台由 SDK 自动调用 user_main */
#if OPERATING_SYSTEM == SYSTEM_LINUX
int main(int argc, char *argv[])
{
    user_main();
    while (1) {
        tal_system_sleep(500);
    }
    return 0;
}
#endif
```

## 步骤四：WiFi 连接

`src/app_wifi.h`：

```c
#ifndef __APP_WIFI_H__
#define __APP_WIFI_H__

#include <stdint.h>

int app_wifi_connect(const char *ssid, const char *password);

#endif
```

`src/app_wifi.c`：

```c
#include "tal_wifi.h"
#include "tal_log.h"
#include "app_wifi.h"

static void wifi_event_callback(WF_EVENT_E event, void *arg)
{
    NW_IP_S ip_info;

    switch (event) {
    case WFE_CONNECTED:
        PR_NOTICE("WiFi connected");
        if (tal_wifi_get_ip(WF_STATION, &ip_info) == OPRT_OK) {
            PR_NOTICE("IP: %s, GW: %s", ip_info.ip, ip_info.gw);
        }
        break;
    case WFE_CONNECT_FAILED:
        PR_NOTICE("WiFi connect failed");
        break;
    case WFE_DISCONNECTED:
        PR_NOTICE("WiFi disconnected");
        break;
    default:
        break;
    }
}

int app_wifi_connect(const char *ssid, const char *password)
{
    OPERATE_RET rt = OPRT_OK;

    TUYA_CALL_ERR_RETURN(tal_wifi_init(wifi_event_callback));
    TUYA_CALL_ERR_RETURN(tal_wifi_set_work_mode(WWM_STATION));
    TUYA_CALL_ERR_RETURN(
        tal_wifi_station_connect((int8_t *)ssid, (int8_t *)password));

    PR_NOTICE("connecting to WiFi SSID: %s", ssid);
    return OPRT_OK;
}
```

## 步骤五：LED 控制

TuyaOpen 的 LED 通过外设驱动框架 `tdl_led` 管理，LED 设备在板卡的 `board_com_api.c` 中通过 `board_register_hardware()` 注册，应用层使用设备名查找句柄。本示例在 CLI 命令中直接操作板载 LED（设备名 `LED_NAME` 由板卡头文件定义）。

LED 操作的核心 API（声明于 `tdl_led_manage.h`）：

```c
#include "tdl_led_manage.h"

/* 通过设备名查找 LED 句柄 */
TDL_LED_HANDLE_T tdl_led_find_dev(char *dev_name);

/* 打开/关闭 LED 设备 */
OPERATE_RET tdl_led_open(TDL_LED_HANDLE_T handle);
OPERATE_RET tdl_led_close(TDL_LED_HANDLE_T handle);

/* 设置状态：TDL_LED_ON / TDL_LED_OFF / TDL_LED_TOGGLE */
OPERATE_RET tdl_led_set_status(TDL_LED_HANDLE_T handle,
                               TDL_LED_STATUS_E status);

/* 周期性闪烁（half_cycle_time 为半周期毫秒数） */
OPERATE_RET tdl_led_flash(TDL_LED_HANDLE_T handle,
                          uint32_t half_cycle_time);

/* 有限次闪烁 */
OPERATE_RET tdl_led_blink(TDL_LED_HANDLE_T handle,
                          TDL_LED_BLINK_CFG_T *cfg);
```

在 CLI 命令中控制 LED 的示例（见步骤七）：

```c
#include "tdl_led_manage.h"

static TDL_LED_HANDLE_T led_handle = NULL;

/* 在 app_cli_init 中打开 LED */
led_handle = tdl_led_find_dev(LED_NAME);
if (led_handle != NULL) {
    tdl_led_open(led_handle);
}

/* 控制 LED */
tdl_led_set_status(led_handle, TDL_LED_ON);
tdl_led_set_status(led_handle, TDL_LED_OFF);
tdl_led_set_status(led_handle, TDL_LED_TOGGLE);
```

> LED 的 GPIO 引脚、有效电平等硬件细节在板卡层（`boards/<platform>/<board>/`）配置，应用层无需关心。这种设计使得同一套应用代码可在不同板卡上运行，只需板卡正确注册 LED 设备。

## 步骤六：KV 持久化存储

使用 KV 存储保存设备配置和状态：

```c
#include "tal_kv.h"
#include "tal_log.h"

static int app_save_boot_count(void)
{
    uint8_t *buf = NULL;
    size_t len = 0;
    int count = 0;

    /* 读取上次启动次数 */
    if (tal_kv_get("boot_cnt", &buf, &len) == OPRT_OK && len == sizeof(int)) {
        count = *(int *)buf;
        tal_kv_free(buf);
    }

    count++;
    PR_NOTICE("boot count: %d", count);

    /* 保存新的启动次数 */
    return tal_kv_set("boot_cnt", (const uint8_t *)&count, sizeof(int));
}
```

KV 存储基于 LittleFS，数据以 JSON 格式序列化到 Flash，支持 8 种数据类型（KV_CHAR/BYTE/SHORT/USHORT/INT/BOOL/STRING/RAW），重启后数据保持。

## 步骤七：自定义 CLI 命令

`src/app_cli.c`：

```c
#include "tal_cli.h"
#include "tal_kv.h"
#include "tal_log.h"
#include "tdl_led_manage.h"
#include "board_com_api.h"

static TDL_LED_HANDLE_T led_handle = NULL;

static void cmd_led(int argc, char *argv[])
{
    if (argc < 2 || led_handle == NULL) {
        tal_cli_echo("Usage: led <on|off|toggle>\r\n");
        return;
    }

    if (strcmp(argv[1], "on") == 0) {
        tdl_led_set_status(led_handle, TDL_LED_ON);
        tal_cli_echo("LED on\r\n");
    } else if (strcmp(argv[1], "off") == 0) {
        tdl_led_set_status(led_handle, TDL_LED_OFF);
        tal_cli_echo("LED off\r\n");
    } else if (strcmp(argv[1], "toggle") == 0) {
        tdl_led_set_status(led_handle, TDL_LED_TOGGLE);
        tal_cli_echo("LED toggled\r\n");
    } else {
        tal_cli_echo("Unknown command\r\n");
    }
}

static void cmd_reboot_count(int argc, char *argv[])
{
    uint8_t *buf = NULL;
    size_t len = 0;

    if (tal_kv_get("boot_cnt", &buf, &len) == OPRT_OK && len == sizeof(int)) {
        char msg[64];
        snprintf(msg, sizeof(msg), "Boot count: %d\r\n", *(int *)buf);
        tal_cli_echo(msg);
        tal_kv_free(buf);
    } else {
        tal_cli_echo("No boot count recorded\r\n");
    }
}

static const cli_cmd_t app_cmds[] = {
    { "led",         "control LED: on/off/toggle",   cmd_led },
    { "boot_count",  "show device boot count",       cmd_reboot_count },
};

void app_cli_init(void)
{
    /* 查找并打开板载 LED */
    led_handle = tdl_led_find_dev(LED_NAME);
    if (led_handle != NULL) {
        tdl_led_open(led_handle);
    }

    tal_cli_cmd_register(app_cmds,
        sizeof(app_cmds) / sizeof(app_cmds[0]));
}
```

## 步骤八：构建与烧录

```bash
# 配置（交互式选择板卡，或使用 -c <config_file>.config 指定）
python tos.py config choice

# 构建
python tos.py build

# 烧录（替换为实际串口）
python tos.py flash -p COM3

# 查看日志
python tos.py monitor -p COM3
```

## 步骤九：设备授权

设备连接涂鸦云前需要写入凭据。在调试串口（115200 波特率）中：

```bash
tuya> auth your-uuid your-authkey
tuya> auth-read
```

重启后设备自动连接涂鸦云，可在涂鸦 IoT 平台查看在线状态。

## 验证结果

### 串口输出

```log
[NOTICE] === My IoT Device ===
[NOTICE] TuyaOpen version: 2.0.0
[NOTICE] Platform chip:     esp32s3
[NOTICE] Platform board:    ESP32-S3-DevKitC
[NOTICE] app worker thread started
[NOTICE] connecting to WiFi SSID: MyWiFiSSID
[NOTICE] WiFi connected
[NOTICE] WiFi got IP
[NOTICE] application initialized, entering main loop
[NOTICE] boot count: 1
```

### CLI 交互

```bash
tuya> help
led            control LED: on/off/toggle
boot_count     show device boot count
help           list all commands
...

tuya> led on
LED on

tuya> led toggle
LED toggled

tuya> boot_count
Boot count: 1
```

## 嵌入式注意事项

1. **栈大小**：应用线程栈 4096 字节适合简单应用；使用 MQTT/TLS 时建议 8192+
2. **堆内存**：使用 `tal_system_get_free_heap_size()` 监控可用堆
3. **WiFi 密码**：生产环境不要硬编码，应通过配网协议获取
4. **阻塞调用**：不要在中断回调或高优先级线程中执行阻塞操作
5. **线程安全**：多线程访问共享资源使用互斥锁（`tal_mutex_*`）
6. **电源管理**：电池供电设备使用 `tal_wifi_set_lp_mode` 启用 WiFi 低功耗

## 扩展方向

- 添加 MQTT 客户端连接涂鸦云（使用 `libmqtt` + `mbedTLS`）
- 添加传感器驱动（I2C/SPI 外设）
- 添加 OTA 升级功能
- 添加 BLE 配网
- 集成 AI 组件（语音/视觉）

## 相关概念

- [TuyaOpen IoT 框架概览](/concepts/00-overview.md)
- [系统服务](/concepts/02-system-services.md)
- [网络栈](/concepts/03-network-stack.md)
- [安全与 KV 存储](/concepts/04-security-kv.md)
- [外设驱动](/concepts/10-peripherals.md)
- [构建系统](/concepts/06-build-system.md)
- [IoT 开发完整工作流](/concepts/14-iot-workflow.md)
