---
type: Concept
title: 构建系统
description: TuyaOpen CMake+Kconfig+tos.py 三位一体构建系统，组件自动发现、配置管道、项目脚手架与批量构建
tags: [tuya, tuyaopen, cmake, kconfig, tos.py, build, ninja, 构建系统]
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

# 构建系统

TuyaOpen 采用 CMake（>= 3.16）+ Kconfig + tos.py 三位一体构建系统。CMake 负责构建文件生成和编译，Kconfig 负责功能配置和裁剪，tos.py 作为统一命令行入口封装完整工作流。组件通过文件系统约定自动发现，无需手动维护中央注册表。

## 构建架构

```text
tos.py (CLI 入口, Python Click)
  │
  ├── Kconfiglib (配置)
  │     app_default.config → using.config → using.cmake → tuya_kconfig.h
  │
  ├── CMake + Ninja (构建)
  │     list_components() 自动发现 src/ 下组件
  │     每个组件编译为静态库 → 打包为 libtuyaos.a
  │     应用编译为 libtuyaapp.a → 链接 tuyaos
  │
  └── 平台工具链
        platform/<chip>/toolchain_file.cmake
        platform/<chip>/platform_config.cmake
```

## 顶层 CMakeLists.txt

### 基本配置

- CMake 最低版本要求：3.16
- 启用 `CMAKE_EXPORT_COMPILE_COMMANDS` 以支持 clangd 等语言服务器
- **禁止原地构建**：要求使用独立构建目录（如 `.build/`），源码目录与构建目录必须不同
- 支持 Windows、Apple、UNIX 三平台检测
- 通过 Python 脚本 `get_system_processor.py` 获取系统处理器架构

### 框架与平台参数

- 框架类型 `TOS_FRAMEWORK` 默认为 "base"，支持 "arduino" 模式
- 平台参数通过三个变量传入：
  - `TOS_PROJECT_PLATFORM`：平台（如 ESP32、T5AI、LINUX）
  - `TOS_PROJECT_CHIP`：芯片型号
  - `TOS_PROJECT_BOARD`：板卡名称

### Kconfig 集成

- Kconfig 工具位于 `tools/kconfiglib`
- 配置缓存目录：`${TOP_BINARY_DIR}/cache`
- 配置输入：`app_default.config`（用户 defconfig）
- 配置输出：
  - `using.config`：完全展开的 Kconfig 配置
  - `using.cmake`：CMake 变量格式
  - `include/tuya_kconfig.h`：C 宏头文件
- Kconfig 头文件模板：`tools/kconfiglib/config.h.in`
- 支持应用默认配置文件 `app_default.config`

### 平台集成

- 平台工具链文件：`${PLATFORM_PATH}/toolchain_file.cmake`
- 平台配置：`${PLATFORM_PATH}/platform_config.cmake`
- 板级 CMakeLists.txt：`boards/${PLATFORM}/${BOARD}/CMakeLists.txt`（存在时自动加入构建）

### 组件自动发现

`list_components()` 函数自动扫描 `src/` 下的所有子目录，每个包含 CMakeLists.txt 的目录被识别为一个组件并逐一 `add_subdirectory`。这意味着新增 SDK 组件只需创建目录和 CMakeLists.txt，无需修改任何中央构建文件。

### 构建产物

- SDK 组件对象文件打包为静态库 `tuyaos`（变量 `COMPONENTS_ALL_LIB`）
- 应用静态库名为 `tuyaapp`（变量 `EXAMPLE_LIB`），链接 `tuyaos`
- 构建参数文件 `build_param` 输出到 `${TOP_BINARY_DIR}/build`，由 `gen_build_param.cmake` 生成
- 最终二进制输出到 `.build/bin/`
- Linux 平台产生原生 ELF，复制到 `dist/<project_name>_<version>/`

### 自定义目标

定义三个自定义构建目标：
- `example`：构建示例应用
- `platform_clean`：平台级清理
- `clean_all`：全量清理

构建命令优先使用平台目录下的 `build_example.py`，否则回退到 `build_example.sh`。

## tos.py 命令行工具

`tos.py` 是 TuyaOpen 的构建工具入口，使用 Python 3 和 Click 框架。Windows 平台支持 PowerShell shell 补全（`click_pwsh`）。

### 全局选项

- `-d/--debug`：启用调试日志，默认日志级别为 INFO

### 子命令（14 个）

| 命令 | 用途 |
|------|------|
| `version` | 显示版本号（如 v1.3.0-23-g6bcb5aa） |
| `prepare` | 准备构建环境（下载工具链等） |
| `check` | 验证工具版本并运行 `git submodule update --init` |
| `config` | 配置管理（choice/menu/save 子命令） |
| `build` | 编译项目 |
| `clean` | 清理构建产物 |
| `flash` | 烧录固件到设备 |
| `monitor` | 串口监控日志 |
| `update` | 更新平台子模块到固定提交 |
| `new` | 创建新项目/板卡/平台 |
| `dev` | 开发工具（批量构建等） |
| `idf` | ESP32 专用，透传到 `idf.py` |
| `hello` | 测试命令 |

### config 子命令

- `tos.py config choice`：交互式选择已验证配置
- `tos.py config choice -c <CONFIG_NAME>`：非交互式选择（Agent/CI 首选）
- `tos.py config choice -d`：仅使用板卡默认配置
- `tos.py config menu`：基于终端的 Kconfig menuconfig 编辑器（需 TTY）
- `tos.py config save`：将当前配置保存为命名预设

所有配置选择变体都会触发完全清理（full clean），所选配置写入 `app_default.config`。

配置查找优先级：项目 `config/` 目录 > `boards/` 全局配置。

### build 子命令

- `tos.py build`：标准构建
- `tos.py build -v`：详细模式（显示完整编译器命令）

Agent/CI 首次构建前需创建 `.cache/.dont_prompt_update_platform` 文件，防止平台更新提示挂起。

### clean 子命令

- `tos.py clean`：ninja clean（增量清理）
- `tos.py clean -f`：完全清理（删除 `.build/` 目录）

### new 子命令

- `tos.py new project`：从模板创建新应用（支持 `--framework base/arduino`）
- `tos.py new board`：在 `boards/<platform>/` 下创建新板卡 BSP 目录
- `tos.py new platform`：搭建新平台移植骨架

### dev 子命令

- `tos.py dev bac`（build-all-configs）：对每个配置先完全清理再构建，用于验证所有板卡变体编译
- 支持 `--dist ./output` 保存二进制、`-o ./logs` 保存构建日志
- `BAC_SKIP_CONFIGS` 列表定义跳过的配置（当前包含 GD32.config）

### flash 和 monitor

- `tos.py flash -p <port>`：烧录到指定串口（推荐）
- `tos.py flash`：自动检测端口
- `tos.py monitor -p <port>`：交互式串口监控
- `tos.py monitor -l`：非阻塞日志捕获（配合 monitor_helper.py）

## 组件 CMakeLists.txt 模式

每个组件遵循统一的 CMake 编写模式：

```cmake
set(MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR})
get_filename_component(MODULE_NAME ${MODULE_PATH} NAME)

if (CONFIG_ENABLE_XXX STREQUAL "y")
    file(GLOB_RECURSE LIB_SRCS "${MODULE_PATH}/src/*.c")
    set(LIB_PUBLIC_INC "${MODULE_PATH}/include")

    add_library(${MODULE_NAME} STATIC ${LIB_SRCS})
    target_include_directories(${MODULE_NAME} PUBLIC ${LIB_PUBLIC_INC})

    list(APPEND COMPONENT_LIBS ${MODULE_NAME})
    list(APPEND COMPONENT_PUBINC ${LIB_PUBLIC_INC})
    set(COMPONENT_LIBS ${COMPONENT_LIBS} PARENT_SCOPE)
    set(COMPONENT_PUBINC ${COMPONENT_PUBINC} PARENT_SCOPE)
endif()
```

关键点：
- 库名从目录名自动获取，避免硬编码
- 可选组件用 `CONFIG_ENABLE_XXX` 守卫
- 源文件通过 `file(GLOB_RECURSE)` 递归收集，新增源文件无需修改 CMakeLists
- 组件名和头文件路径通过 `PARENT_SCOPE` 向上传播

## Kconfig 配置体系

### 配置文件格式

`app_default.config` 使用 Kconfig defconfig 格式，只需指定与默认值不同的项：

```ini
# 平台和板卡选择（两者都必须设置）
CONFIG_BOARD_CHOICE_T5AI=y
CONFIG_BOARD_CHOICE_TUYA_T5AI_EVB=y

# 布尔选项
CONFIG_ENABLE_LIBLVGL=y
# CONFIG_ENABLE_NIMBLE is not set

# 字符串
CONFIG_X="value"

# 整数
CONFIG_X=1234
```

### 平台选择

- 平台选择：`CONFIG_BOARD_CHOICE_<PLATFORM>=y`
- 板卡选择：`CONFIG_BOARD_CHOICE_<BOARD>=y`
- 两者都必须设置
- `CHIP_CHOICE` 和 `PLATFORM_CHOICE` 由板卡 Kconfig 自动设置，不应手动设置

常见配置示例：
- LINUX/Ubuntu：`CONFIG_BOARD_CHOICE_LINUX=y` + `CONFIG_BOARD_CHOICE_UBUNTU=y`
- T5AI EVB：`CONFIG_BOARD_CHOICE_T5AI=y` + `CONFIG_BOARD_CHOICE_TUYA_T5AI_EVB=y`
- ESP32-S3：`CONFIG_BOARD_CHOICE_ESP32=y` + `CONFIG_BOARD_CHOICE_ESP32_S3=y`

### Kconfig 依赖机制

三种依赖关系：
- `select X`：强制启用 X（安全，可省略 X 的 depends）
- `depends on X`：必须先启用 X，否则选项被静默忽略
- `if (X)` 块：同 depends on

### 配置管道

```text
app_default.config (用户 defconfig)
       │
       ▼
using.config (完全展开，含所有默认值)
       │
       ▼
using.cmake (CMake 变量格式，set(VAR "y"))
       │
       ▼
tuya_kconfig.h (C 宏格式，#define VAR 1)
```

配置缓存在 `.build/cache/` 目录下，生成的头文件在 `.build/cache/include/`。

## 项目结构

### 应用项目

新创建的 base 框架应用包含：

```text
my_project/
├── CMakeLists.txt          # 收集 src/、include/，链接 tuyaos
├── app_default.config      # 板卡配置（首次构建前必须设置）
└── src/
    └── tuya_app_main.c     # 入口文件（必须此文件名）
```

### 入口代码模式

`tuya_app_main.c` 遵循双路径入口模式：

```c
#include "tal_api.h"

static void user_main(void)
{
    /* 应用初始化代码 */
    PR_NOTICE("Application started");
}

#if OPERATING_SYSTEM == SYSTEM_LINUX
int main(int argc, char *argv[])
{
    user_main();
    return 0;
}
#else
void tuya_app_main(void)
{
    THREAD_CFG_T cfg = {
        .stackDepth = 1024 * 4,
        .priority = THREAD_PRIO_1,
        .thrdname = "tuya_app_main",
    };
    tal_thread_create_and_start(NULL, NULL, NULL,
                                (THREAD_FUNC_CB)user_main, NULL, &cfg);
}
#endif
```

`SYSTEM_LINUX`（值 100）由 LINUX 平台 Kconfig 自动设置。Linux 下 `main()` 直接调用 `user_main()`；MCU 下 `tuya_app_main()` 创建线程调用。

### Arduino 框架

Arduino 模式入口文件为 `src/tuya_app_main.cpp`，使用 Arduino 风格的 `setup()`/`loop()`。

## 环境激活

每个终端会话需要激活 SDK 环境：

| 平台 | 命令 |
|------|------|
| Linux/macOS | `. ./export.sh` |
| Windows PowerShell | `. .\export.ps1` |
| Windows CMD | `export.bat` |

激活后设置：
- `$OPEN_SDK_ROOT`：SDK 根路径
- `$OPEN_SDK_PYTHON`：venv Python
- `$OPEN_SDK_PIP`：venv pip
- `$VIRTUAL_ENV`：venv 路径
- SDK 根目录加入 `PATH`

验证环境：`tos.py version` 和 `tos.py check`。

## 构建过程详解

完整的构建流程：

1. **下载平台工具链**：首次构建时自动下载对应平台的编译器工具链
2. **运行 prepare**：初始化子模块、准备平台文件
3. **Kconfiglib 生成配置**：读取 `app_default.config`，展开默认值，生成三个配置输出文件
4. **CMake/Ninja 生成构建文件**：根据 `using.cmake` 和 CMakeLists.txt 生成 build.ninja
5. **编译 SDK 组件**：`src/` 下每个启用的组件编译为静态库
6. **编译板卡代码**：`boards/` 下的 BSP 和共享驱动
7. **编译应用**：应用代码编译为 `tuyaapp`，链接 `tuyaos`
8. **输出二进制**：最终固件到 `.build/bin/`，Linux ELF 复制到 `dist/`

## 产品分发

`cli_dev.py` 提供产品二进制分发功能：
- 产品二进制命名格式：`{app_name}_{config}_QIO_{app_ver}.bin`
- 配置名规范化函数 `_normalize_config_name()` 自动去除 `.config` 后缀
- 支持批量构建并保存到 `--dist` 目录

## 相关概念

- [TuyaOpen IoT 框架概览](/concepts/00-overview.md)
- [TAL 抽象层架构](/concepts/01-tal-architecture.md)
- [BSP 板级支持](/concepts/09-board-support.md)
- [AI 开发技能体系](/concepts/11-dev-skills.md)
- [IoT 开发完整工作流](/concepts/14-iot-workflow.md)
- [TuyaOpen 固件快速入门](/examples/firmware-quickstart.md)
