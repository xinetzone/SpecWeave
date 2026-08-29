---
type: Concept
title: IoT 开发完整工作流
description: TuyaOpen IoT 项目从零到上线的完整开发流程，涵盖环境搭建、项目创建、板卡移植、功能开发、调试授权与部署
tags: [tuya, tuyaopen, workflow, development, firmware, deployment, ota, cli]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: tuyaopen-core-source
    resource: "/references/tuyaopen-core-source.md"
    title: TuyaOpen 核心框架源码
  - id: tuya-skills-source
    resource: "/references/tuya-skills-source.md"
    title: TuyaOpen 技能与生态源码
  - id: facts-tuyaopen-core
    resource: "/references/facts-tuyaopen-core.md"
    title: TuyaOpen 核心框架事实清单
---

# IoT 开发完整工作流

TuyaOpen 提供了从环境搭建到固件部署的完整开发工作流，配合 tos.py 命令行工具和 AI Dev Skills，使嵌入式 IoT 开发更加高效。本文梳理从零开始创建一个 TuyaOpen IoT 产品的完整流程，涵盖环境准备、项目创建、板卡配置、功能开发、调试、云授权和 OTA 部署。

## 开发流程总览

```text
环境搭建 → 获取源码 → 选择板卡 → 配置项目 → 功能开发 → 构建 → 烧录
    → 调试 → 设备授权 → 云端验证 → OTA 部署
```

## 阶段一：环境搭建

### 1.1 获取工具链

首次构建时，tos.py 会自动下载对应平台的工具链。也可手动安装：

- **ARM 平台**（T2/T3/T5AI/BK7231N/LN882H/GD32）：GCC ARM Embedded
- **ESP32 平台**：ESP-IDF 工具链（CMake 自动集成）
- **Linux 平台**：系统 GCC，无需额外工具链

### 1.2 安装 Python 依赖

```bash
pip install -r py_dependencies/requirements.txt
```

tos.py 依赖的 Python 包包括 Kconfig 解析库、CMake 辅助工具、串口通信库等。

### 1.3 验证安装

```bash
python tos.py --help
```

### 1.4 AI 辅助环境

安装 TuyaOpen-dev-skills 到 AI 编码助手，获得 10 个开发技能的智能辅助。AI 助手可在环境搭建阶段自动检测缺失依赖并提供安装命令。

## 阶段二：获取源码

```bash
git clone https://github.com/tuya/TuyaOpen.git
cd TuyaOpen
git submodule update --init --recursive
```

`tos.py update` 命令可将各平台子模块切换到 `platform_config.yaml` 中固定的提交版本，确保团队使用一致的 SDK 版本。

## 阶段三：选择或移植板卡

### 3.1 使用现有板卡

TuyaOpen 支持 8 款平台的多款开发板，通过 Kconfig choice 选择：

```bash
# 交互式选择板卡
python tos.py config

# 非交互式选择
python tos.py config choice -c TUYA_T5AI_EVB
```

### 3.2 移植新板卡

如果目标硬件不在支持列表中，使用 AI 技能辅助移植：

```bash
python tos.py new board
# 交互式：先选择平台（如 ESP32），再输入板卡名（如 MY_BOARD）
```

移植步骤：
1. 从同平台参考板卡复制目录
2. 编辑 `board_config.h`：引脚映射、外设地址
3. 编辑 `Kconfig`：设置 `BOARD_CHOICE`、`CHIP_CHOICE`、`select` 所需外设
4. 实现 TKL 接口（GPIO/I2C/SPI/UART/Flash 等）
5. 实现板卡初始化函数
6. 构建验证

关键原则：板卡代码可以调用厂商 SDK，但应用和 SDK 组件只能调用 TAL/TKL 接口。

## 阶段四：项目配置

### 4.1 配置文件

项目根目录的 `app_default.config` 定义编译配置：

```ini
# 选择板卡
CONFIG_BOARD_CHOICE_ESP32=y
CONFIG_BOARD_CHOICE_ESP32_S3=y

# 启用组件
CONFIG_ENABLE_TAL_WIFI=y
CONFIG_ENABLE_TAL_KV=y
CONFIG_ENABLE_TAL_SECURITY=y
CONFIG_ENABLE_LIBMQTT=y

# 启用 AI 组件（如需要）
ENABLE_AI_COMPONENTS=y
```

### 4.2 交互式配置

```bash
python tos.py menuconfig
```

通过菜单界面浏览和修改 Kconfig 选项，组件依赖关系自动处理。

### 4.3 组件裁剪

根据产品需求和硬件资源（RAM/Flash）裁剪组件：
- 纯传感器节点：禁用 WiFi（使用 Zigbee/BLE）、禁用 AI 组件、禁用显示
- 智能摄像头：启用 WiFi、P2P、AI 视频、摄像头外设、音频编解码器
- 智能音箱：启用 WiFi/BLE、AI 音频、音频编解码器、AI UI、显示

## 阶段五：功能开发

### 5.1 应用入口

应用代码位于 `app/src/`，入口函数为 `user_main()`：

```c
#include "tal_api.h"
#include "tal_wifi.h"
#include "tal_kv.h"
#include "tal_log.h"

void user_main(void)
{
    tal_log_init(TAL_LOG_LEVEL_INFO, 1024, TAL_LOG_PRINTF_CB(NULL));
    tal_kv_init();

    PR_INFO("TuyaOpen application started");

    /* 初始化外设、连接网络、启动业务逻辑 */
}
```

### 5.2 网络连接

```c
/* WiFi Station 连接 */
WF_AP_CFG_IF_S wifi_cfg = {
    .ssid = "MyWiFi",
    .slen = strlen("MyWiFi"),
    .passwd = "password",
    .plen = strlen("password"),
};
tal_wifi_station_connect(&wifi_cfg);
```

### 5.3 云连接

使用 MQTT 连接涂鸦云：
1. 通过 KV 存储读取设备凭据（UUID/AuthKey）
2. 初始化 MQTT 客户端
3. 建立 TLS 连接
4. 订阅设备 Topic
5. 上报设备状态和接收指令

### 5.4 外设驱动

通过 TAL 接口访问外设，或使用 `src/peripherals/` 中的高层驱动：

```c
#include "tal_gpio.h"
#include "tal_uart.h"

/* GPIO 输出控制 LED */
tal_gpio_init(GPIO_LED, TAL_GPIO_MODE_OUTPUT_PP, TAL_GPIO_DRIVING_LEVEL_HIGH);
tal_gpio_write(GPIO_LED, TAL_GPIO_LEVEL_HIGH);

/* UART 读取传感器数据 */
TAL_UART_CFG_T uart_cfg = {
    .open_mode = O_BLOCK,
    .base_cfg = { .baudrate = 115200, .parity = TUYA_UART_PARITY_TYPE_NONE },
};
tal_uart_init(TUYA_UART_NUM_1, &uart_cfg);
tal_uart_read(TUYA_UART_NUM_1, buf, sizeof(buf));
```

### 5.5 注册 CLI 命令

```c
#include "tal_cli.h"

static void cmd_status(int argc, char *argv[])
{
    tal_cli_echo("Device: running\r\n");
}

static const cli_cmd_t cmds[] = {
    { "status", "show device status", cmd_status },
};

tal_cli_cmd_register(cmds, sizeof(cmds)/sizeof(cmds[0]));
```

## 阶段六：构建与烧录

### 6.1 构建

```bash
python tos.py build
```

构建产物位于 `build/output/`，包括：
- 固件二进制文件（`.bin`）
- ELF 文件（用于调试和崩溃解码）
- 映射文件（`.map`，用于分析内存使用）

### 6.2 清理

```bash
python tos.py clean          # 清理构建产物
python tos.py distclean      # 完全清理（包括配置）
```

### 6.3 烧录

```bash
python tos.py flash [PORT]
```

不同平台的烧录方式：
- ESP32：esptool 通过 UART 烧录
- T2/T3/T5AI：Tuya 烧录工具通过 WCH 双串口
- BK7231N/LN882H：厂商专用烧录工具
- Linux：直接运行可执行文件

## 阶段七：调试

### 7.1 串口日志

```bash
python tos.py monitor [PORT]
```

日志级别通过 `tal_log_init()` 的第一个参数控制：
- `TAL_LOG_LEVEL_EMERG`/`ALERT`/`CRIT`/`ERR`/`WARNING`/`NOTICE`/`INFO`/`DEBUG`

各平台日志波特率不同（T3/T5AI 为 460800，其余多为 115200/921600），但 CLI 波特率固定为 115200。

### 7.2 CLI 调试

在调试串口输入 `help` 查看所有可用命令。常用调试命令：
- `thread_list`：查看线程状态和栈使用
- `heap_stats`：堆内存统计
- `wifi_info`：WiFi 状态
- `kv_dump`：KV 存储内容
- `sys_reset`：软复位

### 7.3 GDB 调试

支持通过 JTAG/SWD 或串口进行 GDB 远程调试，配合 IDE（VS Code + Cortex-Debug）可设置断点、查看变量、单步执行。

### 7.4 崩溃解码

设备崩溃时串口会输出 backtrace 和寄存器信息。使用 `addr2line` 工具将地址转换为源码位置：

```bash
arm-none-eabi-addr2line -e build/output/firmware.elf -f -p 0x40012345
```

AI Dev Skills 的 09-crash-decode 技能可自动分析崩溃日志。

### 7.5 代码检查

```bash
python tos.py check
```

执行代码规范检查和层级违规检测，确保应用层没有直接调用厂商 SDK。

## 阶段八：设备授权

设备连接涂鸦云需要有效的 UUID 和 AuthKey：

### 8.1 获取凭据

在涂鸦 IoT 平台创建产品，获取设备三元组（UUID/AuthKey/ProductID）。

### 8.2 写入凭据

通过 CLI 写入设备：

```bash
tuya> auth <uuid> <authkey>
```

凭据通过 `tal_kv_set()` 安全存储到 Flash KV 区域，重启后保持。

### 8.3 验证授权

```bash
tuya> auth-read
```

确认凭据已正确写入。重启后设备应自动连接涂鸦云。

## 阶段九：云端验证

1. 在涂鸦 IoT 平台查看设备在线状态
2. 通过 App 或 API 发送控制指令
3. 验证设备状态上报
4. 测试 OTA 升级通道
5. 检查日志中的云端通信

## 阶段十：OTA 部署

TuyaOpen 内置 OTA 能力：
- 通过 HTTPS 下载固件升级包
- 支持差分升级（节省 Flash 和带宽）
- 双分区 A/B 切换，升级失败可回滚
- 签名验证，防止恶意固件

OTA 流程：
1. 在涂鸦 IoT 平台上传新固件版本
2. 设备通过 MQTT 收到升级通知
3. 下载固件包到备用分区
4. 校验签名和完整性
5. 写入完成后重启切换到新固件
6. 新版本上报升级成功

## 开发最佳实践

### 内存管理
- 嵌入式设备 RAM 有限，避免大的栈分配（线程栈通常 2-8KB）
- 使用 `tal_system_get_heap_size()` 和 `tal_system_get_free_heap_size()` 监控堆
- 长时间运行的系统注意内存泄漏
- 使用内存池代替频繁的 malloc/free

### 实时性
- 高优先级线程用于时间关键任务（音频、传感器读取）
- 工作队列处理延迟不敏感的任务
- 临界区尽量短，避免在中断中做复杂处理
- 注意优先级反转（使用优先级继承互斥锁）

### 功耗优化
- WiFi 低功耗模式（`tal_wifi_set_lp_mode`）
- 合理使用睡眠（`tal_sleep`）
- 空闲时关闭外设时钟
- 传感器使用中断而非轮询

### 安全性
- 设备凭据使用 `tal_security` 加密存储
- 所有云端通信使用 TLS（mbedTLS）
- 固件升级验证签名
- 不在日志中输出敏感信息（AuthKey、密码）

### 代码层级
- 应用代码只调用 `tal_*` 接口
- 需要新硬件能力时在 TKL 层实现
- 平台相关代码放在 `boards/` 和 `platform/`
- 使用 `tos.py check` 验证层级合规性

## AI 辅助开发

TuyaOpen-dev-skills 为每个开发阶段提供 AI 辅助：

| 开发阶段 | 对应技能 |
|---------|---------|
| 环境搭建 | 01-env-setup |
| 构建配置 | 02-build-system、03-project-config |
| 板卡移植 | 05-board-porting |
| 日常编码 | 04-code-check、06-dev-cycle |
| 设备授权 | 07-device-auth |
| 问题调试 | 08-debug-assist、09-crash-decode、10-cli-debug |

开发者用自然语言描述任务，AI 助手自动加载对应技能并提供指导，大幅降低嵌入式开发的学习曲线。

## 相关概念

- [TuyaOpen IoT 框架概览](/concepts/00-overview.md)
- [构建系统](/concepts/06-build-system.md)
- [BSP 板级支持](/concepts/09-board-support.md)
- [外设驱动](/concepts/10-peripherals.md)
- [AI 开发技能体系](/concepts/11-dev-skills.md)
- [系统服务](/concepts/02-system-services.md)
- [安全与 KV 存储](/concepts/04-security-kv.md)
