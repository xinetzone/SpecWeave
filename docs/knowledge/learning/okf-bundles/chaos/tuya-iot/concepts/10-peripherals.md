---
type: Concept
title: 外设驱动
description: TuyaOpen 外设驱动框架，13 类外设（按键/LED/显示/触摸/摄像头/音频/IMU/PMIC等）、UART驱动与CLI
tags: [tuya, tuyaopen, peripherals, driver, uart, cli, button, led, display, camera, sensor]
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

# 外设驱动

TuyaOpen 在 `src/peripherals/` 目录下提供 13 类外设驱动，覆盖 IoT 和 AIoT 设备的常见硬件需求。所有外设通过 Kconfig 独立配置，可按需裁剪。此外，TAL 层还提供 UART 驱动和 CLI 命令行接口作为系统级外设基础。

## 外设框架概览

外设配置通过 `src/peripherals/Kconfig` 统一管理，使用 `rsource` 递归引入各子目录的 Kconfig 文件。13 类外设分为几组：

### 人机交互

| 外设 | Kconfig 目录 | 典型用途 |
|------|-------------|---------|
| button | `button/` | 物理按键（单击/双击/长按检测） |
| led | `led/` | 普通 GPIO LED 控制 |
| leds_pixel | `leds_pixel/` | WS2812 等可寻址像素灯（ESP32 使用 RMT 驱动） |
| encoder | `encoder/` | 旋转编码器输入 |
| joystick | `joystick/` | 摇杆输入 |
| ir | `ir/` | 红外发射/接收 |

### 音视频与显示

| 外设 | Kconfig 目录 | 典型用途 |
|------|-------------|---------|
| audio_codecs | `audio_codecs/` | 音频编解码器（ES8311/ES8388/ES8389 等） |
| display | `display/` | 显示屏（TFT/OLED/LCD） |
| tp | `tp/` | 触摸屏（FT5x06 等电容触摸） |
| camera | `camera/` | 摄像头传感器 |
| printer | `printer/` | 热敏打印机等 |

### 传感与电源

| 外设 | Kconfig 目录 | 典型用途 |
|------|-------------|---------|
| imu | `imu/` | 惯性测量单元（BMI270 等） |
| pmic | `pmic/` | 电源管理 IC |

## UART 驱动（tal_uart）

UART 是嵌入式系统最基础的通信接口，`tal_driver/uart/tal_uart.h` 提供完整的 UART 抽象。

### 打开模式标志位

| 标志 | 值 | 说明 |
|------|-----|------|
| `O_BLOCK` | 1 | 阻塞模式 |
| `O_ASYNC_WRITE` | 1<<1 | 异步写 |
| `O_FLOW_CTRL` | 1<<2 | 硬件流控 |
| `O_TX_DMA` | 1<<3 | 发送 DMA |
| `O_RX_DMA` | 1<<4 | 接收 DMA |

### 配置结构

```c
typedef struct {
    int rx_buffer_size;
#ifdef CONFIG_TX_ASYNC
    int tx_buffer_size;
#endif
    uint16_t open_mode;
    TUYA_UART_BASE_CFG_T base_cfg;
} TAL_UART_CFG_T;
```

`TUYA_UART_BASE_CFG_T` 包含波特率、数据位、停止位、校验位等基础配置。`CONFIG_TX_ASYNC` 宏控制是否启用异步发送缓冲区配置。

### 核心 API

```c
#include "tal_uart.h"

/* 初始化 UART */
OPERATE_RET tal_uart_init(TUYA_UART_NUM_E port_id, TAL_UART_CFG_T *cfg);

/* 读取数据（返回读取字节数 >=0 或错误 <0） */
int tal_uart_read(TUYA_UART_NUM_E port_id, uint8_t *buf, uint32_t len);

/* 发送数据（返回发送字节数或错误） */
int tal_uart_write(TUYA_UART_NUM_E port_id, const uint8_t *buf, uint32_t len);

/* 反初始化 */
OPERATE_RET tal_uart_deinit(TUYA_UART_NUM_E port_id);

/* 获取接收缓冲区待读数据大小 */
int tal_uart_get_rx_data_size(TUYA_UART_NUM_E port_id);
```

### 接收中断回调

```c
/* 回调签名 */
typedef void (*TAL_UART_IRQ_CB)(TUYA_UART_NUM_E port_id,
                                 void *buff, uint16_t len);

/* 注册接收中断回调（无返回值） */
void tal_uart_rx_reg_irq_cb(TUYA_UART_NUM_E port_id,
                             TAL_UART_IRQ_CB rx_cb);
```

### Linux 平台端口映射

Linux 平台上端口 ID 高 16 位表示 UART 类型（`TUYA_UART_TYPE_E`），低 16 位表示端口号。使用 `TUYA_UART_PORT_ID(type, port)` 宏组合端口 ID。这使得在 Linux 上可以同时访问物理 UART、USB 串口、pty 等不同类型的串口设备。

## CLI 命令行（tal_cli）

CLI 提供串口命令行交互能力，是调试、配置和设备授权的重要通道。

### 命令结构

```c
typedef void (*cli_cmd_func_cb_t)(int argc, char *argv[]);

typedef struct {
    const char *name;   /* 命令名 */
    const char *help;   /* 帮助文本 */
    cli_cmd_func_cb_t func;  /* 回调函数 */
} cli_cmd_t;
```

### 核心 API

```c
#include "tal_cli.h"

/* 初始化 CLI（默认使用 UART0），返回 0 成功 */
int tal_cli_init(void);

/* 指定 UART 端口初始化 CLI，uart_num 为端口号 */
int tal_cli_init_with_uart(uint8_t uart_num);

/* 批量注册 CLI 命令，num 为命令数量（uint8_t） */
int tal_cli_cmd_register(const cli_cmd_t *cmd, uint8_t num);

/* 向 CLI 终端回显字符串 */
void tal_cli_echo(char *string);
```

### CLI 波特率

CLI 波特率固定为 **115200**（硬编码于 `tal_cli.c` 中 `cfg.base_cfg.baudrate = 115200`），跨所有平台一致。注意不要与各芯片的调试日志波特率混淆：

| 平台 | 日志波特率 | CLI/授权波特率 |
|------|-----------|---------------|
| T2 | 115200 | 115200 |
| T3/T5AI | 460800 | 115200 |
| ESP32 | 115200 | 115200 |
| LN882H | 921600 | 115200 |
| BK7231N | 115200 | 115200 |

### CLI 配置门控

CLI 功能需要以下 Kconfig 选项：
- `CONFIG_ENABLE_SERIAL_CLI_CMD=y`：启用串口 CLI（必须）
- `CONFIG_CLI_CMD_SYS=y`：启用 sys_* 系统命令
- `CONFIG_CLI_CMD_FS=y`：启用 fs_* 文件系统命令
- `CONFIG_CLI_CMD_KV=y`：启用 kv_* KV 存储命令

### 内置 CLI 命令

固件启动后，在调试串口看到 `tuya> ` 提示符即可输入命令：

| 命令 | 功能 |
|------|------|
| `help` | 列出所有已注册命令 |
| `auth <uuid> <authkey>` | 写入设备凭据到 KV 存储 |
| `auth-read` | 读取当前存储的凭据 |
| `auth-reset` | 清除凭据 |
| `sys_version` | 固件版本 |
| `sys_reset` | 软复位 |
| `kv_dump` | 转储所有 KV（需 CONFIG_CLI_CMD_KV） |
| `fs_ls <path>` | 列出文件系统目录 |
| `fs_cat <path>` | 查看文件内容 |
| `thread_list` | 列出线程和栈使用情况 |
| `heap_stats` | 堆内存使用统计 |
| `wifi_info` | WiFi 状态信息 |

### 注册自定义命令

```c
static void cmd_hello(int argc, char *argv[])
{
    tal_cli_echo("Hello from custom command!\r\n");
}

static const cli_cmd_t custom_cmds[] = {
    { "hello", "print hello message", cmd_hello },
};

void app_register_cli_commands(void)
{
    tal_cli_cmd_register(custom_cmds, sizeof(custom_cmds)/sizeof(custom_cmds[0]));
}
```

## 图像处理（tal_image）

`src/tal_image/` 提供图像处理基础能力，虽然不完全属于外设驱动，但常与摄像头外设配合使用：

`tal_image.h` 是统一入口头文件，聚合五个子模块：
- `tal_image_yuv422_to_rgb.h`：YUV422 转 RGB 色彩空间
- `tal_image_yuv422_to_binary.h`：YUV422 转二值图
- `tal_image_rotate.h`：图像旋转（90°/180°/270°）
- `tal_image_jpeg_codec.h`：JPEG 编解码
- `tal_image_scale.h`：图像缩放

JPEG 解码提供两种实现：
- `tjpgd/`：TJpgDec，极简 JPEG 解码器，适合资源受限设备
- `libjpegturbo/`：libjpeg-turbo，高性能 SIMD 加速 JPEG 编解码

## DMA2D 硬件加速

`src/tal_driver/dma2d/` 提供 DMA2D（Chrom-ART）硬件加速支持，用于：
- 矩形填充（快速清屏）
- 像素格式转换（YUV→RGB、颜色空间转换）
- 图像混合（Alpha blending）
- 像素块拷贝

DMA2D 在带显示屏的 GUI 应用中可显著减轻 CPU 负担，加速 LVGL 渲染。

## 外设与板卡的关系

外设驱动位于 `src/peripherals/`，是平台无关的。具体的硬件连接（I2C 地址、GPIO 引脚、SPI 总线号）在板卡配置中定义：

```text
src/peripherals/display/     ← 平台无关显示驱动框架
    ↓ 调用 TKL 接口
boards/ESP32/common/lcd/     ← ESP32 平台共享 LCD 驱动（ST7789等）
    ↓ 使用具体引脚
boards/ESP32/MY_BOARD/board_config.h  ← 引脚映射
```

这种分层使得：
- 同一外设驱动可在不同芯片平台上工作（通过 TKL 抽象 I2C/SPI/GPIO）
- 同平台不同板卡可共享驱动实现（在 boards/common/ 中）
- 应用代码只调用外设高层 API，不关心底层总线和引脚

## 相关概念

- [BSP 板级支持](/concepts/09-board-support.md)
- [TAL 抽象层架构](/concepts/01-tal-architecture.md)
- [系统服务](/concepts/02-system-services.md)
- [AI 组件](/concepts/08-ai-components.md)
- [IoT 开发完整工作流](/concepts/14-iot-workflow.md)
