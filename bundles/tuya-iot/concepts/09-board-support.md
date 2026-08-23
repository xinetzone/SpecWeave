---
type: Concept
title: BSP 板级支持
description: TuyaOpen BSP 架构，8 款芯片平台支持、代码层级隔离、板卡目录结构、共享驱动与移植流程
tags: [tuya, tuyaopen, bsp, board, platform, esp32, t5ai, 移植]
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

# BSP 板级支持

TuyaOpen 通过 BSP（Board Support Package）层支持 8 款芯片平台，采用严格的代码层级隔离机制确保应用和 SDK 组件的平台无关性。板级代码位于 `boards/` 目录，平台适配代码位于 `platform/` 目录，两者通过 Kconfig choice 机制选择唯一目标板。

## 支持的平台

`boards/Kconfig` 定义了 8 个板级使能选项，全部默认启用，使用 Kconfig `choice` 结构确保同一时刻只选择一个目标板：

| 平台 | Kconfig 选项 | 典型板卡 | 调试串口 | 波特率 |
|------|-------------|---------|---------|--------|
| Linux | `BOARD_CHOICE_LINUX` | Ubuntu/Raspberry Pi/DshanPi | 原生终端 | - |
| T2 | `BOARD_CHOICE_T2` | T2-U | Uart2 | 115200 |
| T3 | `BOARD_CHOICE_T3` | T3 LCD Devkit | Uart1 | 460800 |
| T5AI | `BOARD_CHOICE_T5AI` | Tuya T5AI EVB | Uart1 | 460800 |
| ESP32 | `BOARD_CHOICE_ESP32` | ESP32/ESP32-S3/ESP32-C3/C6 | Uart0 | 115200 |
| LN882H | `BOARD_CHOICE_LN882H` | LN882H/EWT103-W15 | Uart1 | 921600 |
| BK7231X | `BOARD_CHOICE_BK7231X` | BK7231N | Uart2 | 115200 |
| GD32 | `BOARD_CHOICE_GD32` | GD32 系列 | - | - |

每个板级选项对应一个 `BOARD_CHOICE_XXX` 配置项，选中后通过 `rsource` 引入对应子目录的 Kconfig。文件中包含 `# <new-board-enable>` 和 `# <new-board-kconfig>` 标记，用于自动化添加新板支持。

## 代码层级规则

TuyaOpen 对各层代码的调用关系有严格规定，这是实现跨平台移植的核心保障：

| 层级 | 目录 | 可调用 | 不可调用 |
|------|------|--------|---------|
| **platform** | `platform/<chip>/` | 厂商 SDK | - |
| **TKL 适配** | `platform/<chip>/tkl/` | 厂商 SDK | - |
| **boards/common** | `boards/<platform>/common/` | tkl_*、厂商 SDK | - |
| **boards/BOARD** | `boards/<platform>/<board>/` | tkl_*、厂商 SDK、boards/common | - |
| **src（SDK 组件）** | `src/tal_*/`、`src/lib*/` | tal_*、tkl_* | 厂商 SDK |
| **apps（应用）** | `apps/`、`examples/` | tal_*、tkl_* | 厂商 SDK |

关键规则：
1. **应用和 SDK 组件禁止直接调用芯片厂商 SDK**，必须通过 TKL/TAL 接口
2. boards/common 和 boards/BOARD 可以直接调用厂商 SDK，因为它们本身就是平台特定代码
3. Linux 平台是「参考实现」——如果代码能在 Linux 下编译通过，说明没有违规调用厂商 SDK

## 板卡目录结构

每个板卡位于 `boards/<PLATFORM>/<BOARD_NAME>/`，标准结构包含：

```text
boards/ESP32/ESP32-S3-DevKitC/
├── CMakeLists.txt       # 板卡构建文件
├── Kconfig              # 板卡配置选项
├── board_com_api.h      # 板卡通用 API 声明
├── board_config.h       # 硬件常量定义
└── esp32-s3-devkitc.c   # 板卡初始化实现
```

### Kconfig 规范

板卡 Kconfig 中：
- `BOARD_CHOICE` 值必须与目录名精确匹配（大小写敏感）
- `CHIP_CHOICE` 设置芯片标识符（如 `"esp32s3"`）
- `BOARD_CONFIG` 用 `select` 自动启用板卡支持的外设

### board_config.h

定义硬件常量，例如：
- 显示类型（`BOARD_DISPLAY_TYPE`）
- IO 扩展器类型（`BOARD_IO_EXPANDER_TYPE`）
- 引脚映射（GPIO 分配）
- 外设地址（I2C/SPI）

### 板卡驱动函数

板卡需要实现的标准函数：
- `app_audio_driver_init(name)`：音频驱动初始化（有音频功能时必需）
- `board_display_init()`：显示初始化（ESP32 专用）
- `board_display_get_panel_io_handle()`：获取面板 IO 句柄（ESP32 专用）
- `board_display_get_panel_handle()`：获取面板句柄（ESP32 专用）

注意：T5AI 板卡不需要 `board_display_*` 函数，其显示通过 TKL display 层实现。

## ESP32 共享驱动

ESP32 平台在 `boards/ESP32/common/` 下维护了丰富的共享驱动，新板卡可直接复用：

| 驱动类别 | 支持型号/类型 |
|---------|--------------|
| **audio**（音频） | no-codec、ES8311、ES8388、ES8389、ATK |
| **lcd**（显示屏） | SSD1306（OLED）、SH8601、ST7789（TFT） |
| **display**（显示） | LVGL port（LVGL 移植层） |
| **touch**（触摸） | FT5x06 电容触摸 |
| **io_expander**（IO扩展） | TCA9554、XL9555 |
| **led**（LED） | WS2812（ESP RMT 驱动） |

这种「共享驱动下沉到平台 common 层」的设计避免了每块板卡重复实现相同驱动，是代码复用与层级隔离的平衡。

## 板卡 CMakeLists.txt 模板

板卡 CMakeLists.txt 遵循与 SDK 组件相同的模式：

```cmake
set(MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR})
get_filename_component(MODULE_NAME ${MODULE_PATH} NAME)

aux_source_directory(${MODULE_PATH} LIB_SRCS)
set(LIB_PUBLIC_INC "${MODULE_PATH}")

add_library(${MODULE_NAME} STATIC ${LIB_SRCS})
target_include_directories(${MODULE_NAME} PUBLIC ${LIB_PUBLIC_INC})

list(APPEND COMPONENT_LIBS ${MODULE_NAME})
list(APPEND COMPONENT_PUBINC ${LIB_PUBLIC_INC})
set(COMPONENT_LIBS ${COMPONENT_LIBS} PARENT_SCOPE)
set(COMPONENT_PUBINC ${COMPONENT_PUBINC} PARENT_SCOPE)
```

使用 `aux_source_directory` 自动收集源文件，新增 .c 文件无需修改 CMakeLists。

## 添加新板卡流程

使用 `tos.py new board` 命令可自动生成板卡骨架（交互式，先从菜单选择平台，再输入板卡名）：

```bash
tos.py new board
# 提示：Choice platform → 选择 ESP32
# 提示：Input new board name → 输入 MY_BOARD
```

该命令会：
1. 从 `tools/app_template/board_template/` 复制模板到 `boards/ESP32/MY_BOARD/`，创建标准文件（Kconfig、CMakeLists.txt、board_com_api.h、board_config.h、源文件）
2. 自动在平台 Kconfig 中注册新板卡选项（通过 `# <new-board-add:>` 标记插入）

手动移植步骤：
1. 从同平台现有板卡复制目录
2. 编辑 Kconfig（设置正确的 BOARD_CHOICE、CHIP_CHOICE、select 外设）
3. 在平台 Kconfig 中注册新板卡
4. 编辑 board_config.h（引脚映射、硬件常量）
5. 实现板卡初始化和驱动代码
6. 创建项目配置文件（config/MY_BOARD.config）
7. 非交互式选择：`tos.py config choice -c MY_BOARD`
8. 构建验证：`tos.py build`

ESP32 芯片名默认为 `esp32s3`，其他平台使用平台名。

## 平台选择配置

在 `app_default.config` 中必须同时设置平台和板卡：

```ini
# ESP32-S3 示例
CONFIG_BOARD_CHOICE_ESP32=y
CONFIG_BOARD_CHOICE_ESP32_S3=y

# T5AI EVB 示例
CONFIG_BOARD_CHOICE_T5AI=y
CONFIG_BOARD_CHOICE_TUYA_T5AI_EVB=y

# Linux/Ubuntu 示例
CONFIG_BOARD_CHOICE_LINUX=y
CONFIG_BOARD_CHOICE_UBUNTU=y
```

`CHIP_CHOICE` 和 `PLATFORM_CHOICE` 由板卡 Kconfig 自动设置，不应手动设置。

## 平台工具链

每个平台在 `platform/<chip>/` 下包含：

| 文件/目录 | 职责 |
|----------|------|
| `toolchain_file.cmake` | CMake 工具链文件（编译器路径、编译选项） |
| `platform_config.cmake` | 平台构建配置 |
| `platform_config.yaml` | 平台子模块固定提交记录 |
| `tkl/` | TKL 接口实现 |
| `vendor/` 或芯片 SDK | 厂商提供的底层 SDK |

首次构建时 tos.py 会自动下载对应平台的工具链。`tos.py update` 将每个平台子模块切换到 `platform_config.yaml` 中固定的提交，确保版本一致性。

## 双串口平台

T5/T5AI 使用 WCH 双串口芯片（VID 0x1a86 PID 0x55d2）：
- Linux：ttyACM0 用于 flash/auth，ttyACM1 用于 monitor/log
- Windows：较低 COM 号用于 flash，较高 COM 号用于 monitor/log
- CLI/授权波特率始终为 115200（与监控波特率 460800 不同）

## 相关概念

- [构建系统](/concepts/06-build-system.md)
- [TAL 抽象层架构](/concepts/01-tal-architecture.md)
- [外设驱动](/concepts/10-peripherals.md)
- [AI 开发技能体系](/concepts/11-dev-skills.md)
- [IoT 开发完整工作流](/concepts/14-iot-workflow.md)
