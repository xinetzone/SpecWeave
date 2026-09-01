---
type: Facts
title: "TuyaOpen 技能与生态项目事实清单"
---

# TuyaOpen 技能与生态项目事实清单

> R 阶段事实采集。每条事实标注 `文件路径:行号`。零推测。采集日期：2026-08-22。

## 1. TuyaOpen Dev Skills 总览

1. TuyaOpen Dev Skills 是面向 Claude Code、Cursor IDE 及其他 Agent 型 AI 助手的结构化知识文件集合，用于加速 TuyaOpen 硬件项目开发（`.chaos/libs/TuyaOpen-dev-skills/README.md:10`）。
2. 技能（Skills）是结构化的 `SKILL.md` 文件，向 AI 编码助手提供特定工具、框架和工作流的深度上下文理解（`.chaos/libs/TuyaOpen-dev-skills/README.md:14`）。
3. 技能遵循 [Agent Skills](https://agentskills.io/) 开放标准，可在 Claude Code（TuyaOpen IDE）、Cursor 及任何兼容 AI 助手中自动加载（`.chaos/libs/TuyaOpen-dev-skills/README.md:22`）。
4. 技能列表共 8 个核心开发技能：env-setup、build、project-config、code-check、add-board、dev-loop、device-auth、debug-helper（`.chaos/libs/TuyaOpen-dev-skills/README.md:26-35`）。
5. 另有 2 个独立技能包：`tuyaopen-crash-decode`（崩溃解码）和 `tuyaopen-cli-debug`（CLI 调试），位于 `skills/` 根目录下（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:1`；`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:1`）。
6. 标准开发工作流为：env-setup → project-config → build → flash-monitor → device-auth/dev-loop，dev-loop 出错后回到 build（`.chaos/libs/TuyaOpen-dev-skills/README.md:41-51`）。
7. 支持平台包括 T5AI、ESP32（ESP32/ESP32-S3/ESP32-C3/ESP32-C6）、LINUX（Ubuntu/Raspberry Pi/DshanPi）、T2（T2-U）、T3（T3 LCD Devkit）、LN882H（LN882H/EWT103-W15）、BK7231X（`.chaos/libs/TuyaOpen-dev-skills/README.md:57-65`）。
8. Cursor 自动从 `.agents/skills/`、`.cursor/skills/`（项目级）和 `~/.cursor/skills/`（用户全局级）加载技能（`.chaos/libs/TuyaOpen-dev-skills/README.md:69-75`）。
9. 每个技能遵循 Agent Skills 标准：`SKILL.md`（核心指令，自动加载）、`references/`（详细文档，按需加载）、`scripts/`（Agent 可直接执行的脚本）（`.chaos/libs/TuyaOpen-dev-skills/README.md:132-135`）。
10. SKILL.md frontmatter 字段包括 `name`、`description`、`license`、`compatibility`（`.chaos/libs/TuyaOpen-dev-skills/README.md:150`）。
11. 项目许可证为 Apache License 2.0（`.chaos/libs/TuyaOpen-dev-skills/README.md:157`）。
12. 主 SDK 仓库为 https://github.com/tuya/TuyaOpen，官方文档为 https://tuyaopen.ai/docs/quick-start（`.chaos/libs/TuyaOpen-dev-skills/README.md:139-140`）。
13. 项目结构中 `skills/tuyaopen/` 包含 8 个子技能目录，每个目录含 SKILL.md 及可选的 references/scripts（`.chaos/libs/TuyaOpen-dev-skills/README.md:115-130`）。
14. 技能描述同时使用英文和中文关键词，以支持双语触发（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:7`）。

## 2. env-setup 技能

15. 技能名为 `tuyaopen/env-setup`，许可证 Apache-2.0（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:2-8`）。
16. 兼容性要求：Ubuntu/Debian with apt-get（或 macOS/Windows 等效）、Python >= 3.6、git >= 2.0、cmake >= 3.28、make >= 3.0、ninja >= 1.6（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:9-12`）。
17. 环境激活后设置三个变量：`$OPEN_SDK_ROOT`（SDK 根路径）、`$OPEN_SDK_PYTHON`（venv Python 可执行文件）、`$VIRTUAL_ENV`（活动 venv 路径）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:21-25`）。
18. Linux/macOS 激活命令为 `. ./export.sh`，Windows PowerShell 为 `. .\export.ps1`，Windows CMD 为 `export.bat`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:67-71`）。
19. 每个终端会话只需激活一次（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:65`）。
20. 激活后还设置 `$OPEN_SDK_PIP`，并将 SDK 根目录加入 `PATH`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:73`）。
21. 验证命令：`tos.py version`（显示版本，如 v1.3.0-23-g6bcb5aa）和 `tos.py check`（验证工具版本并运行 `git submodule update --init`）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:78-79`）。
22. Ubuntu/Debian 系统依赖安装命令包含 lcov、cmake-curses-gui、build-essential、ninja-build、wget、git、python3、python3-pip、python3-venv、libc6-i386、libsystemd-dev（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:57-58`）。
23. 内置检查脚本分三平台：`check_env.sh`（Linux/macOS）、`check_env.bat`（Windows CMD）、`check_env.ps1`（Windows PowerShell）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:84-88`）。
24. 故障排除：`python3-venv` 缺失时执行 `sudo apt-get install python3-venv`；激活失败且 `.venv/` 存在时 `rm -rf .venv/ && . ./export.sh`；`tos.py: command not found` 时重新运行 export 脚本（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/SKILL.md:92-97`）。
25. `check_env.sh` 脚本使用 `set -euo pipefail`，定义 `check()` 和 `warn()` 两个函数，返回 0 表示环境健康，非零表示有问题（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/scripts/check_env.sh:5-19`）。
26. `check_env.sh` 检查 VIRTUAL_ENV 是否以 `.venv` 结尾、OPEN_SDK_ROOT 是否设置，以及 tos.py、git、cmake、ninja、python3 是否可用（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/scripts/check_env.sh:29-47`）。

## 3. build 技能

27. 技能名为 `tuyaopen/build`，许可证 Apache-2.0，要求 TuyaOpen 环境已激活，cmake >= 3.28、ninja >= 1.6（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:2-12`）。
28. 所有路径和命令相对于 TuyaOpen SDK 根目录（`$OPEN_SDK_ROOT`）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:19`）。
29. 可构建项目位于两个目录：`apps/`（应用项目，如 `apps/tuya_cloud/switch_demo`）和 `examples/`（示例项目，如 `examples/get-started/sample_project`）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:23-26`）。
30. 选择已验证配置的命令：`tos.py config choice`（交互式）、`tos.py config choice -c TUYA_T5AI_EVB`（非交互式，Agent/CI 首选）、`tos.py config choice -d`（仅板卡默认配置）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:38-43`）。
31. 所有配置选择变体都会触发完全清理（full clean），所选配置写入 `app_default.config`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:45`）。
32. 配置查找优先级：项目 `config/` 目录 > `boards/` 全局配置（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:47`）。
33. `-c` 标志按文件名匹配配置，`.config` 扩展名可选；名称未找到时命令报错并列出可用配置名（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:49-51`）。
34. Menuconfig 命令 `tos.py config menu` 是基于终端的 Kconfig 编辑器，需 TTY；按键支持箭头或 h/j/k/l，`?` 查看帮助，退出时写入 `app_default.config`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:54-60`）。
35. `app_default.config` 使用 Kconfig defconfig 格式，只需指定与默认值不同的项（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:64`）。
36. 平台选择用 `CONFIG_BOARD_CHOICE_<PLATFORM>=y`（如 T5AI、ESP32、LINUX），板卡选择用 `CONFIG_BOARD_CHOICE_<BOARD>=y`，两者都必须设置（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:76-77`）。
37. `CHIP_CHOICE` 和 `PLATFORM_CHOICE` 由板卡 Kconfig 自动设置，不应手动设置（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:78`）。
38. 布尔选项用 `CONFIG_X=y` 启用或 `# CONFIG_X is not set` 禁用；字符串用 `CONFIG_X="value"`；整数用 `CONFIG_X=1234`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:79-80`）。
39. LINUX/Ubuntu 配置为 `CONFIG_BOARD_CHOICE_LINUX=y` + `CONFIG_BOARD_CHOICE_UBUNTU=y`；T5AI EVB 为 `CONFIG_BOARD_CHOICE_T5AI=y` + `CONFIG_BOARD_CHOICE_TUYA_T5AI_EVB=y`；ESP32-S3 为 `CONFIG_BOARD_CHOICE_ESP32=y` + `CONFIG_BOARD_CHOICE_ESP32_S3=y`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:86-90`）。
40. 配置管道：`app_default.config` → `.build/cache/using.config`（完全展开）→ `.build/cache/using.cmake`（CMake 变量）→ `.build/cache/include/tuya_kconfig.h`（C 宏）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:96-104`）。
41. 构建命令：`tos.py build`（标准）和 `tos.py build -v`（详细，显示完整编译器命令）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:115-116`）。
42. Agent/CI 首次构建前需创建 `.cache/.dont_prompt_update_platform` 文件以防止平台更新提示挂起（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:119-123`）。
43. 构建所有配置命令 `tos.py dev bac`（build-all-configs），对每个配置先完全清理再构建，用于验证所有板卡变体编译（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:127-131`）。
44. 清理命令：`tos.py clean`（ninja clean）和 `tos.py clean -f`（完全清理，删除 `.build/`）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:136-137`）。
45. LINUX 平台产生原生 ELF 二进制，构建输出复制到 `dist/`，规范路径为 `./dist/<project_name>_<version>/<project_name>_<version>.elf`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:146-158`）。
46. Windows 构建缓慢可能是 `MSPCManagerService` 干扰，需终止进程并将项目目录加入 Windows 安全排除项（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:164`）。
47. Kconfig 依赖指南详细说明了 `select`/`depends on`/`if` 机制及 Agent 策略，位于 `references/KCONFIG_GUIDE.md`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/SKILL.md:110`）。
48. Kconfig 三种依赖机制：`select X`（强制启用，安全省略）、`depends on X`（必须先启用 X 否则选项被静默忽略）、`if (X)` 块（同 depends on）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/references/KCONFIG_GUIDE.md:5-9`）。
49. 构建系统架构：Kconfiglib 处理配置，CMake 生成 ninja 构建文件，根 CMakeLists.txt 通过 `list_components()` 自动发现 `src/` 下每个有 CMakeLists.txt 的子目录作为 SDK 组件（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/references/KCONFIG_GUIDE.md:67-95`）。
50. 构建过程：下载平台工具链 → 运行 prepare → Kconfiglib 生成配置 → CMake/ninja 生成构建文件 → 编译 SDK 组件和板卡代码 → 应用代码编译为 `tuyaapp` 并链接 `tuyaos` 静态库 → 最终二进制输出到 `.build/bin/`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/build/references/KCONFIG_GUIDE.md:87-96`）。

## 4. project-config 技能

51. 技能名为 `tuyaopen/project-config`，要求环境已激活；交互式命令需 TTY 终端（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:2-12`）。
52. `tos.py new project` 在当前工作目录从模板创建新应用，支持 `--framework base`（默认）和 `--framework arduino`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:29-33`）。
53. base 框架入口文件为 `src/tuya_app_main.c`，入口点 `user_main()`；在 Linux 上运行为 `main()`，在 MCU 上通过 `tuya_app_main()` 生成线程（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:42-45`）。
54. arduino 框架入口文件为 `src/tuya_app_main.cpp`，使用 Arduino 风格的 `setup()`/`loop()`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:46`）。
55. 新项目生成结构含 `CMakeLists.txt`（收集 src/、include/，链接 tuyaos）和 `src/tuya_app_main.c`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:48-53`）。
56. 新项目无 `app_default.config`，首次构建前必须配置平台/板卡（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:60`）。
57. `tos.py new board` 在 `boards/<platform>/` 下创建新板卡 BSP 目录，含 Kconfig、CMakeLists.txt、board_com_api.h、板卡源文件，并自动在平台 Kconfig 中注册（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:62-71`）。
58. `tos.py new board` 对 ESP32 芯片名默认 `esp32s3`，其他平台使用平台名（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:72`）。
59. `tos.py config choice -c <name>` 为非交互式配置选择，首选用于 Agent/CI（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:112-117`）。
60. `tos.py config save` 交互式将当前 `app_default.config` 保存为项目 `config/` 目录下的命名预设（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:102-108`）。
61. 非交互式项目创建需手动写三个文件：`CMakeLists.txt`、`app_default.config`、`src/tuya_app_main.c`；项目可位于 `examples/` 或 `apps/`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:121-136`）。
62. CMakeLists.txt 标准模板使用 `aux_source_directory` 自动收集 src 下所有 .c 文件，`add_library(${EXAMPLE_LIB})`，无需逐个列出（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:140-170`）。
63. 入口源文件必须命名为 `tuya_app_main.c`，遵循双路径入口模式：Linux 下 `main()` 直接调用 `user_main()`，MCU 下 `tuya_app_main()` 创建线程调用 `user_main()`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:194-241`）。
64. `OPERATING_SYSTEM == SYSTEM_LINUX`（值 100）由 LINUX 平台 Kconfig 自动设置（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:241`）。
65. MCU 线程参数：stackDepth = 1024*4，priority = THREAD_PRIO_1，thrdname = "tuya_app_main"（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:229-231`）。
66. `tos.py update` 将每个平台子模块切换到 `$OPEN_SDK_ROOT/platform/platform_config.yaml` 中固定的提交，在 `git pull` 后运行（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/SKILL.md:254-258`）。
67. tos.py 命令参考列出 version、check、new project/board/platform、config choice/menu/save、build、clean、flash、monitor、update、dev bac、idf 等命令及其交互性（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/references/TOS_COMMANDS.md:3-27`）。
68. `tos.py new platform` 搭建新平台移植骨架，含工具链模板、`tuyaos_adapter/` 移植骨架和 `boards/<name>/` 板卡 Kconfig（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/references/TOS_COMMANDS.md:29-39`）。
69. `tos.py idf <cmd>` 是 ESP32 专用，透传到 ESP-IDF 的 `idf.py`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/project-config/references/TOS_COMMANDS.md:26`）。

## 5. code-check 技能

70. 技能名为 `tuyaopen/code-check`，要求 clang-format 已安装（Linux: `apt install clang-format`；macOS: `brew install clang-format`；Windows: `choco install llvm`）和 Python 3（venv 激活）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:2-11`）。
71. `tools/check_format.py` 验证 C/C++ 文件（.c/.cpp/.h/.hpp/.cc/.cxx）的三条规则：clang-format 合规、无中文字符（含注释和字符串）、正确的文件头（Doxygen 风格，含 @file/@brief/@copyright）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:20-24`）。
72. .clang-format 位于仓库根目录，基于 LLVM 风格，4 空格缩进（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:22`）。
73. `.clang-format-ignore` 中列出的路径排除检查，包括第三方库 cJSON、FlashDB、lwip、coreMQTT、littlefs、backoffAlgorithm、coreHTTP、qrcode 等（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:26,132-141`）。
74. 检查特定文件：`$OPEN_SDK_PYTHON tools/check_format.py --debug --files path/to/file.c`，支持 glob 模式（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:38-42`）。
75. 递归检查目录：`$OPEN_SDK_PYTHON tools/check_format.py --debug --dir src/tal_system/`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:47`）。
76. PR 模式（CI/pre-merge）使用 `git diff` 检查相对基线分支修改的文件，默认 `--base master`，可用 `--base main`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:59-65`）。
77. `--files` 和 `--dir` 必须配合 `--debug` 标志，在 PR 模式下被忽略（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:77`）。
78. 退出码：0 = 所有检查通过，1 = 发现错误；头文件警告（建议）不导致失败，只有错误才失败（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:79-80`）。
79. Agent 工作流：修改 → 运行 `check_files.py <changed_files>` → 格式错误用 `clang-format -style=file -i <file>` 自动修复 → 中文字符替换为英文 → 头文件错误补 Doxygen 头（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:84-92`）。
80. 敏感信息检查：设备凭据（UUID/AuthKey/TUYA_OPENSDK_UUID/TUYA_OPENSDK_AUTHKEY）必须用占位符；产品 ID（TUYA_PRODUCT_ID）用占位符；不得硬编码 API 密钥/令牌/私钥/证书/Wi-Fi 凭据（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:96-103`）。
81. 生成或修改 `tuya_config.h` 时始终使用占位符值 `"your_uuid_here"`、`"your_authkey_here"`；若出现看似真实凭据需警告用户；永不记录/提交/显示真实凭据（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:106-110`）。
82. 每个 .c/.h 文件必须以 `/** */` Doxygen 头开始，含 @file、@brief、@version、@date、@copyright；@copyright 格式为 `Copyright (c) <year>[-<year>] <holder> All Rights Reserved.`，必须包含当前年份（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/SKILL.md:114-126`）。
83. `check_files.py` 是跨平台包装器，通过向上搜索 `.clang-format` 定位仓库根目录，调用 `tools/check_format.py --debug --files`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/scripts/check_files.py:12-25,66-67`）。
84. `check_files.py` 校验所有文件路径必须在仓库根目录内，防止路径逃逸（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/scripts/check_files.py:46-54`）。

## 6. add-board 技能

85. 技能名为 `tuyaopen/add-board`，支持平台为 T5AI、ESP32、LINUX、T2、T3、LN882H、BK7231X（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/SKILL.md:2-11`）。
86. 板卡目录结构 `boards/<PLATFORM>/<BOARD_NAME>/` 含 CMakeLists.txt、Kconfig、board_com_api.h、board_config.h、`<board_name>.c`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/SKILL.md:34-43`）。
87. 添加新板卡步骤：从同平台现有板卡复制 → 编辑 Kconfig → 在平台 Kconfig 注册 → 编辑 board_config.h → 实现板卡驱动 → 创建项目配置 → 构建验证（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/SKILL.md:45-108`）。
88. Kconfig 中 `BOARD_CHOICE` 值必须与目录名精确匹配（大小写敏感）；`CHIP_CHOICE` 设置芯片标识符（如 `"esp32s3"`）；`BOARD_CONFIG` 用 `select` 自动启用板卡支持的外设（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/SKILL.md:57-73`）。
89. `board_config.h` 定义硬件常量，如显示类型（`BOARD_DISPLAY_TYPE`）、IO 扩展器类型（`BOARD_IO_EXPANDER_TYPE`）、引脚映射等（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/SKILL.md:80-86`）。
90. 非交互式选择新板卡配置：`tos.py config choice -c MY_NEW_BOARD`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/SKILL.md:105`）。
91. 代码层级规则：platform（芯片厂商 SDK + tkl 适配层）→ src（TuyaOpen SDK 组件，可调用 tkl 但不可直接调用厂商 SDK）→ boards/common（平台共享驱动）→ boards/BOARD（板卡特定代码）→ apps（应用代码，可调用 tkl+src 但不可调用厂商 SDK）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/references/BOARD_LAYERS.md:7-18`）。
92. ESP32 共享驱动位于 `boards/ESP32/common/`：audio（no-codec/ES8311/ES8388/ES8389/ATK）、lcd（SSD1306/SH8601/ST7789）、display（LVGL port）、touch（FT5x06）、io_expander（TCA9554/XL9555）、led（WS2812 ESP RMT）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/references/BOARD_LAYERS.md:22-31`）。
93. 板卡 CMakeLists.txt 标准模板使用 `aux_source_directory` 收集源文件，`add_library(${MODULE_NAME})`，并通过 `COMPONENT_LIBS`/`COMPONENT_PUBINC` 父级作用域注册组件（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/references/BOARD_LAYERS.md:37-51`）。
94. 板卡驱动函数：`app_audio_driver_init(name)`（音频时必需）、`board_display_init()`/`board_display_get_panel_io_handle()`/`board_display_get_panel_handle()`（ESP32 专用）；T5AI 板卡不需要 board_display_* 函数，其显示通过 tkl_display 层（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/add-board/references/BOARD_LAYERS.md:55-63`）。

## 7. dev-loop 技能

95. 技能名为 `tuyaopen/dev-loop`，要求环境激活、设备通过 USB 连接（MCU 目标）或原生 Linux 主机（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:2-12`）。
96. 标准开发迭代周期：Build → Flash → Monitor Logs → Analyze Results → Decide（出错则 Fix Code 后回到 Build）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:21-30`）。
97. 烧录命令：`tos.py flash -p <port>`（指定端口，推荐）、`tos.py flash`（自动检测端口）、`tos.py flash -p <port> -d`（调试输出）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:38-40`）。
98. T5/T5AI 双串口典型映射：Linux 下 flash = ttyACM0，monitor/log = ttyACM1；Windows 下较低 COM 号为 flash，较高 COM 号为 monitor/log（不保证，失败则交换）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:43-47`）。
99. Linux 串口权限需执行一次 `sudo usermod -aG dialout $USER` 然后重启（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:47`）。
100. 日志捕获：交互式用 `tos.py monitor -p <port>`，后台非阻塞用 `monitor_helper.py start -p <port>` → tail → stop（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:49`）。
101. 日志文件位于 `<project_dir>/.target_logging/`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:50`）。
102. LINUX 快捷脚本：`build_run.py`（默认 30 秒超时，传 0 表示无超时），执行 build + run + 自动分析（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:57-61`）。
103. TuyaOpen 日志格式为 `[MM-DD HH:MM:SS ty X][source_file.c:line] message`，X 为日志级别 E/W/N/I/D/T（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:75-79`）。
104. 关键日志模式：`[... ty E]` 为 PR_ERR 错误；`feed watchdog` 为约每 10 秒的健康心跳（正常）；`OPRT_` 后接负数为 SDK 操作失败；`mqtt connected`/`MQTT_CONNECTED` 为云连接成功；`TUYA_EVENT_DIRECT_MQTT_CONNECTED` 为直连 MQTT 事件（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:83-90`）。
105. 日志级别层次：ERR > WARN > NOTICE > INFO > DEBUG > TRACE，默认级别 DEBUG（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:98-102`）。
106. 设备健康状态信号：`feed watchdog` 每约 10 秒、初始化后无 PR_ERR、`mqtt connected`；无输出可能是端口/波特率错误或崩溃前崩溃；启动循环为初始化崩溃；看门狗复位为死锁/无限循环；MQTT 失败需检查网络/凭据/PID 不匹配（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:110-117`）。
107. 各芯片波特率：T2=115200、T3/T5AI=460800、ESP32=115200、LN882H=921600（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:146`）。
108. 内置 CLI（`tal_cli`）通过调试 UART 访问，提示符为 `tuya> `（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/SKILL.md:106`；`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/references/ERROR_CODES.md:21`）。
109. 常见错误码：OPRT_OK=0、OPRT_COM_ERROR=-1、OPRT_INVALID_PARM=-2、OPRT_MALLOC_FAILED=-3、OPRT_NOT_SUPPORTED=-4、OPRT_NETWORK_ERROR=-5、OPRT_NOT_FOUND=-6；完整定义在 `src/common/include/tuya_error_code.h`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/references/ERROR_CODES.md:5-15`）。
110. CLI 内置命令：`help`（列出所有命令）、`auth <uuid> <authkey>`（写入设备凭据）、`auth-read`（读取存储凭据）、`auth-reset`（清除凭据）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/references/ERROR_CODES.md:31-36`）。
111. 注册自定义 CLI 命令使用 `tal_cli_cmd_register()`，命令结构体为 `cli_cmd_t`（含 name/help/func 字段）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/references/ERROR_CODES.md:42-52`）。
112. 批量测试 `tos.py dev bac` 支持 `--dist ./output` 保存二进制、`-o ./logs` 保存构建日志（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/references/ERROR_CODES.md:58-62`）。
113. `build_run.py` 函数 `_python_exe()` 返回 `$OPEN_SDK_PYTHON` 或 `sys.executable`；`_tos_py()` 返回 `$OPEN_SDK_ROOT/tos.py`；`_log_dir()` 返回 `<cwd>/.target_logging`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/scripts/build_run.py:14-27`）。
114. `build_run.py` 的 `find_binary()` 按 `dist/**/*.elf` 和 `.build/bin/*` 模式查找可执行文件；`analyze_log(lines)` 统计 `ty E]` 错误数、`ty W]` 警告数、`feed watchdog` 数（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/scripts/build_run.py:30-45`）。
115. `build_run.py` 检查 `app_default.config` 存在，构建后验证二进制修改时间不早于构建开始时间（防止陈旧/注入文件），运行时按超时终止，分析日志若有错误则退出码 1（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/scripts/build_run.py:57-116`）。

## 8. device-auth 技能

116. 技能名为 `tuyaopen/device-auth`，要求 Tuya IoT 平台账号（platform.tuya.com）获取凭据（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:2-11`）。
117. TuyaOpen 设备连接涂鸦云需三个凭据：Product ID（PID，宏 `TUYA_PRODUCT_ID`）、UUID（宏 `TUYA_OPENSDK_UUID`）、AuthKey（宏 `TUYA_OPENSDK_AUTHKEY`）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:20-26`）。
118. 凭据解析优先级（首次成功优先）：1. KV 存储（通过 CLI `auth` 命令写入，键 `UUID_TUYAOPEN`/`AUTHKEY_TUYAOPEN`）；2. OTP/模组 flash（`tuya_iot_license_read()` 从硬件读取）；3. 源代码宏（`tuya_config.h` 中）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:30-35`）。
119. `tuya_config.h` 位置因项目而异，如 `apps/tuya_cloud/switch_demo/src/tuya_config.h`、`apps/tuya.ai/your_chat_bot/include/tuya_config.h`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:54-57`）。
120. 部分 README 引用的 `TUYA_DEVICE_UUID`/`TUYA_DEVICE_AUTHKEY` 是过时名称，实际宏为 `TUYA_OPENSDK_UUID`/`TUYA_OPENSDK_AUTHKEY`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:59`）。
121. AP 配网二维码可选宏 `TUYA_NETCFG_PINCODE`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:48-52`）。
122. PID 获取：登录 Tuya IoT 平台 → 创建匹配设备类型的产品 → 复制 PID（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:64-67`）。
123. UUID+AuthKey 三种方式：预烧录模组（OTP 内置）、从涂鸦平台购买、免费开发者授权码；仅 TuyaOpen 专用授权码可用，标准涂鸦模组授权码不兼容（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:71-77`）。
124. T5/T5AI 板卡（WCH 双串口，VID `0x1a86` PID `0x55d2`）：较低枚举端口通常用于 flash/auth，较高端口用于 monitor/log（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:94`）。
125. 占位符检测模式：值含 `your_`、`xxx`、`here`、空字符串，或短于预期长度（UUID 约 20 字符，AuthKey 约 32 字符）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/SKILL.md:118-119`）。
126. 串口授权使用 **flash 端口**（非 monitor 端口），授权波特率始终 **115200**，与芯片类型无关（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/references/PROVISIONING.md:8-14`）。
127. CLI 授权命令：`auth <UUID> <AUTHKEY>`（写入 KV 存储）、`auth-read`（读取当前凭据）、`auth-reset`（清除凭据）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/references/PROVISIONING.md:29-34`）。
128. 授权失败排查：检查波特率（115200，非芯片监控波特率）、检查端口（flash 端口）、检查固件（`tuya_authorize_init()` 须在 `tuya_iot_init()` 前调用）、检查 CLI 初始化（`tal_cli_init()` 必须调用）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/references/PROVISIONING.md:37-43`）。
129. 配网模式：BLE（Kconfig `NETCFG_TUYA_BLE`，手机通过 BLE 发送 Wi-Fi 凭据，最常见）、AP（`NETCFG_TUYA_WIFI_AP`，设备创建热点）、BLE+AP（两者都支持）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/references/PROVISIONING.md:50-55`）。
130. 应用通过 `netmgr_conn_set(NETCONN_WIFI, NETCONN_CMD_NETCFG, &(netcfg_args_t){.type = NETCFG_TUYA_BLE | NETCFG_TUYA_WIFI_AP})` 配置配网（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/references/PROVISIONING.md:59-62`）。
131. AP 模式下若定义 `TUYA_NETCFG_PINCODE`，使用 PBKDF2(pincode, uuid) 派生 TLS-PSK，启用二维码安全配对（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/references/PROVISIONING.md:65-66`）。
132. 配网流程：设备未配网状态 → BLE 广播/创建 AP → 用户用 Tuya Smart/Smart Life App 扫描 → App 发送 SSID+密码+激活令牌 → 设备连 Wi-Fi 并激活 → `TUYA_EVENT_DIRECT_MQTT_CONNECTED` 事件触发（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/references/PROVISIONING.md:69-75`）。
133. LINUX 平台设备直接使用主机网络，无需配网，`tuya_iot_start()` 后立即连云（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/device-auth/references/PROVISIONING.md:78-79`）。

## 9. debug-helper 技能

134. 技能名为 `tuyaopen/debug-helper`，使用 `tos.py monitor -l` 提供非阻塞串口日志捕获，无额外依赖（仅 Python 标准库）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/SKILL.md:2-29`）。
135. 四个命令：`start -p <port> [-l <logfile>]`（后台启动监控）、`tail [-n N]`（读取最后 N 行，默认 200）、`stop`（终止监控释放串口）、`status`（检查运行状态）；加 `--json` 输出机器可读格式（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/SKILL.md:46-53`）。
136. 日志和会话状态写入 `<project_dir>/.target_logging/`，其中 `<project_dir>` 是含 `app_default.config` 的目录，脚本通过从 CWD 向上搜索自动定位（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/SKILL.md:56-59`）。
137. 会话文件 `session.json` 存储 PID + 日志文件路径；同一时间只运行一个监控会话，启动新会话会自动停止前一个（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/SKILL.md:68-71`）。
138. T5/T5AI 双串口（WCH，VID 0x1a86 PID 0x55d2）：Linux 典型 ttyACM0=flash、ttyACM1=monitor；Windows 低 COM=flash、高 COM=monitor（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/SKILL.md:74-80`）。
139. `monitor_helper.py` 的 `_sdk_root()` 从 `$OPEN_SDK_ROOT` 或向上搜索 `tos.py` 获取 SDK 根；`_project_root()` 向上搜索 `app_default.config` 获取项目根（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/scripts/monitor_helper.py:28-59`）。
140. `_is_monitor_process(pid)` 验证 PID 属于 `tos.py monitor` 进程（Windows 用 wmic 查询 CommandLine，Linux 读 `/proc/<pid>/cmdline`），避免误杀无关进程（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/scripts/monitor_helper.py:118-132`）。
141. `cmd_start()` 启动时若已有会话先停止；自定义日志文件必须位于 `.target_logging/` 目录内；Windows 使用 `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`，Linux 使用 `start_new_session=True`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/scripts/monitor_helper.py:152-184`）。
142. `cmd_tail()` 从会话读取日志文件最后 N 行；`cmd_stop()` 终止进程并清除会话文件；`cmd_status()` 返回运行状态和 PID/日志路径（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/scripts/monitor_helper.py:187-221`）。

## 10. crash-decode 与 cli-debug 技能

143. `tuyaopen-crash-decode` 技能将固件崩溃转储（PC、LR、栈指针）解码为源文件:行号，通过调用各平台对应的 `addr2line` 调试 ELF；覆盖 T5AI（BK7258 ARM Cortex-M）、ESP32/S3（Xtensa）、T2、T3、LN882H（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:2-14`）。
144. 平台识别：T5AI 特征为 `Firmware name: app@cpu0`/`app@cpu1` 或路径含 `bk7258`，工具链前缀 `arm-none-eabi-`；ESP32 特征为 `ESP-IDF`/`EPC1/2/3`/`EXCVADDR`/`Guru Meditation Error`，前缀 `xtensa-esp32-elf-`/`xtensa-esp32s3-elf-`；T2/T3/LN882H 为 Cortex-M 寄存器无前缀，用 `arm-none-eabi-`；LINUX 为 `RIP`/`RSP`，用系统 `addr2line`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:31-36`）。
145. T5AI 双核：`app@cpu0` ↔ CP 核心 ↔ `bk7258/app.elf`；`app@cpu1` ↔ AP 核心 ↔ `bk7258_ap/app.elf`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:38`）。
146. ARM 工具链 `addr2line` 位于 `TuyaOpen/platform/tools/gcc-arm-none-eabi-10.3-2021.10/bin/arm-none-eabi-addr2line`，首次 `tos.py build` 自动下载；ESP32 工具链在 `TuyaOpen/platform/ESP32/esp-idf` 下（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:44-58`）。
147. 调试 ELF 搜索顺序：T5AI 查 `dist/*/debug/bk7258_ap/app.elf` 和 `dist/*/debug/bk7258/app.elf`；单核平台查 `dist/*/*/*.elf`；构建树查 `.build/bin/debug/*/app.elf`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:64-74`）。
148. ELF 必须与刷入的二进制完全匹配；若崩溃后重新构建，需重新刷写复现或 `git checkout` 到精确提交后 `tos.py clean -f && tos.py build` 重新生成匹配 ELF（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:77`）。
149. 解码命令使用 `addr2line -e $ELF -f -C -i <addresses>`，`-i` 内联模式、`-f` 显示函数名、`-C` 反修饰 C++ 符号（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:81-93`）。
150. Cortex-M 崩溃转储中 PC/LR 行格式为 `pc x 0x21d8e96`/`lr x 0x21d5863`；Xtensa 为 `PC : 0x...`/`EPC1 : 0x...`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:112-119`）。
151. 栈帧返回地址过滤：保留与 PC/LR 同一 16MB 区域（宽松：同一高位字节）的 `data:` 值，丢弃 NULL、小整数（<0x10000）、明显的栈/堆指针（0x3fc/0x60f/0x2801 等 T5 SRAM/PSRAM）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:121-132`）。
152. `addr2line` 返回 `??` 但 ELF 匹配时，可能是函数间地址（如字面量池），可用 `*-nm --size-sort` 查找最近符号或 `*-objdump -d` 反汇编周围地址（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-crash-decode/SKILL.md:136-151`）。
153. `tuyaopen-cli-debug` 技能通过 UART 向 TuyaOpen 设备串口 CLI（tal_cli）发送命令并捕获响应，自动发现 USB 串口和平台波特率（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:2-9`）。
154. cli-debug 依赖：pyserial（`pip install pyserial`）、固件须以 `CONFIG_ENABLE_SERIAL_CLI_CMD=y` 编译（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:26-39`）。
155. 可选 CLI 功能门控：`CONFIG_CLI_CMD_SYS=y`（sys_* 命令）、`CONFIG_CLI_CMD_FS=y`（fs_* 文件系统命令）、`CONFIG_CLI_CMD_KV=y`（kv_* 键值存储命令）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:36-38`）。
156. cli-debug 子命令：`help`（发送 help 列出所有命令）、`send <cmd>`（发送单条命令返回响应）、`list-ports`（列出候选串口，不连接）、`raw <text>`（发送原始字节不处理换行）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:70-75`）。
157. CLI 波特率始终为 115200，硬编码于 `TuyaOpen/src/tal_cli/src/tal_cli.c:811`（`cfg.base_cfg.baudrate = 115200;`），跨平台一致；不要与 `tos.py monitor` 的平台特定日志波特率混淆（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:88-98`）。
158. T5AI 双串口：脚本自动选择较高编号的 T5 端口用于 CLI，可用 `-p` 覆盖（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:101-108`）。
159. 常见 CLI 命令：`help`、`sys_version`（固件版本）、`sys_reset`（软复位）、`kv_dump`（转储所有 KV）、`fs_ls /`（列出根文件系统）、`fs_cat <path>`、`thread_list`（线程和栈使用）、`heap_stats`（堆使用）、`wifi_info`（Wi-Fi 状态）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:114-124`）。
160. JSON 输出稳定键：`ok`、`port`、`baud`、`command`、`output`（清理后响应）、`raw`（完整原始响应）、`error`、`hint`（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:176-187`）。
161. `cli_debug.py` 常量：`CLI_BAUD = 115200`；T5AI VID `0x1A86` PID `0x55D2`；常见串口 VID/PID 含 CP210x（0x10C4:0xEA60）、CH340（0x1A86:0x7523）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/cli_debug.py:69-80`）。
162. 2025-06-25 实测结果：端口自动发现成功识别 `/dev/ttyACM1`（VID 0x1a86 PID 0x55d2，WCH CH34x 双串口，评分 65）为 T5AI 监控/CLI 端口；但当时 DuckyClaw 固件未编译 `CONFIG_ENABLE_SERIAL_CLI_CMD=y`，脚本正确报告无响应（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen-cli-debug/SKILL.md:222-237`）。

## 11. OpenClaw 智能家居技能

163. `tuya-openclaw-skills` 是 OpenClaw 平台的官方 AI Agent 技能，基于涂鸦 2C 终端用户 API，覆盖 3000+ 智能硬件品类、200+ 国家和地区（`.chaos/libs/tuya-openclaw-skills/README.md:1-3`）。
164. 技能名为 `tuya-smart-control`，版本 1.0.0，emoji 🏠，需环境变量 `TUYA_API_KEY`，pip 依赖 `requests>=2.28.0` 和 `websockets>=12.0`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:2-4`）。
165. 认证方式为 Header `Authorization: Bearer {Api-key}`；凭据从环境变量 `TUYA_API_KEY` 读取，Base URL 从 API key 前缀自动识别，可通过 `TUYA_BASE_URL` 覆盖（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:13-14`）。
166. API key 格式为 `sk-<PREFIX><rest>`，`sk-` 后前两个字符映射到数据中心（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:14`；`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/api-conventions.md:5`）。
167. 7 个数据中心映射：AY=中国（`https://openapi.tuyacn.com`，WS `wss://wsmsgs.tuyacn.com`）、AZ=美西（`https://openapi.tuyaus.com`，WS `wss://wsmsgs.iot-wus.com`）、EU=中欧（`https://openapi.tuyaeu.com`，WS `wss://wsmsgs.iot-eu.com`）、IN=印度（`https://openapi.tuyain.com`，WS `wss://wsmsgs.iot-ap.com`）、UE=美东（`https://openapi-ueaz.tuyaus.com`，WS `wss://wsmsgs.iot-eus.com`）、WE=西欧（`https://openapi-weaz.tuyaeu.com`，WS `wss://wsmsgs.iot-weu.com`）、SG=新加坡（`https://openapi-sg.iotbing.com`，WS `wss://wsmsgs.iot-sea.com`）（`.chaos/libs/tuya-openclaw-skills/README.md:43-51`）。
168. 中国大陆用户从 tuyasmart.com 获取 API key，国际用户从 tuya.ai 获取；API key 区域必须与 Tuya 账号注册区域匹配（`.chaos/libs/tuya-openclaw-skills/README.md:32-37`；`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/api-conventions.md:17-20`）。
169. 功能模块共 10 项：家庭管理、设备查询、设备控制、设备管理（重命名）、天气服务、通知（短信/语音/邮件/App推送）、数据统计、IPC 云抓拍、IPC 视觉识别、设备消息订阅（WebSocket）（`.chaos/libs/tuya-openclaw-skills/README.md:13-24`）。
170. 所有 API 当前处于试用阶段，受速率限制和调用配额约束（`.chaos/libs/tuya-openclaw-skills/README.md:5-7`）。
171. 前置要求 Python 3.7+、`requests` 库、`websockets` 库（用于实时设备消息订阅）（`.chaos/libs/tuya-openclaw-skills/README.md:59-62`）。
172. REST API 统一成功响应格式 `{"success": true, "t": <timestamp>, "result": {...}}`；错误响应 `{"success": false, "code": <code>, "msg": "..."}`；SDK 自动检查 success 并在失败时抛出 `TuyaAPIError`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/api-conventions.md:35-58`）。
173. HTTP 429 和瞬时 5xx 响应自动带退避重试（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/api-conventions.md:58`）。
174. 家庭管理 API：列出所有家庭 `GET /v1.0/end-user/homes/all`，列出家庭内房间 `GET /v1.0/end-user/homes/{home_id}/rooms`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/home-and-space.md:3-56`）。
175. 家庭响应字段含 home_id、name、role（owner/admin/member）、create_time、latitude/longitude（格式 `{"Value": "30.3"}`，可作天气查询参数）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/home-and-space.md:17-44`）。
176. 设备查询 API 共 4 个：列出所有设备 `GET /v1.0/end-user/devices/all`、家庭内设备 `GET /v1.0/end-user/homes/{home_id}/devices`、房间内设备 `GET /v1.0/end-user/homes/room/{room_id}/devices`、单设备详情 `GET /v1.0/end-user/devices/{device_id}/detail`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-query.md:3-154`）。
177. 设备列表字段：device_id、name、category（品类代码）、category_name、product_id、online、room_id（可选）、total（总数）；所有列表 API 单次返回全量设备无分页（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-query.md:36-46,215`）。
178. 设备详情额外含 product_name、firmware_version、firmware_update_available、properties（当前功能属性值映射，键为属性 dp code）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-query.md:199-213`）。
179. 设备不存在时详情返回 `{"success": true, "result": null}`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-query.md:189-197`）。
180. 设备控制：查询物模型 `GET /v1.0/end-user/devices/{device_id}/model`，下发属性 `POST /v1.0/end-user/devices/{device_id}/shadow/properties/issue`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-control.md:3-148`）。
181. 物模型 `result.model` 是 JSON 字符串需再次解析；结构含 modelId、services 数组，每个 service 含 code/name/description/properties（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-control.md:25-73`）。
182. 属性 accessMode 三种：`ro`（只读，仅查询）、`wr`（只写，可控制但不可读当前值）、`rw`（读写）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-control.md:93`；`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:162-164`）。
183. typeSpec 类型：value（数值，含 min/max/step/unit/scale）、bool、enum（range 列表）、string（maxlen）；其他类型 float/double/date/raw/bitmap/struct/array（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-control.md:99-129`）。
184. scale 为十进制乘数，实际值 = 输入值 / 10^scale（如 scale=1 且原始值 255，则实际值 25.5）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-control.md:105`）。
185. 下发属性请求体 `properties` 必须是 JSON 字符串（非对象），需双重序列化 `{"properties": "{\"switch_led\":true}"}`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-control.md:158-170`）。
186. 常见控制场景属性码：灯开关 switch_led（bool）、亮度 bright_value（value 10-1000）、色温 temp_value（0-1000）、空调开关 switch（bool）、温度 temp_set（16-30）、模式 mode（enum auto/cold/hot）、插座 switch_1（bool）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-control.md:184-193`）。
187. 设备管理仅支持重命名：`POST /v1.0/end-user/devices/{device_id}/attribute`，请求体 `name`（最大 50 字符，不可为空）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-management.md:3-24`）。
188. 天气查询 `GET /v1.0/end-user/services/weather/recent`，参数 codes（JSON 数组字符串，如 `["w.temp","w.humidity","w.condition","w.hour.7"]`）、lat、lon（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/weather.md:7-23`）。
189. 天气响应数据键格式 `{attribute}.{time_index}`，如 `w.temp.0`（当前温度）、`w.temp.1`（1 小时后）；`w.hour.N` 指定返回未来 N 小时数据；expiration 为缓存过期分钟数（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/weather.md:50-57`）。
190. 支持天气属性码：w.temp、w.humidity、w.condition、w.conditionNum、w.pressure、w.realFeel、w.uvi、w.windDir、w.windLevel、w.windSpeed、w.hour.N（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/weather.md:63-77`）。
191. 通知 API 全部为自发自收模式（只能发给当前登录用户）：SMS `POST /v1.0/end-user/services/sms/self-send`、语音 `POST /v1.0/end-user/services/voice/self-send`、邮件 `POST /v1.0/end-user/services/mail/self-send`、App推送 `POST /v1.0/end-user/services/push/self-send`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/notifications.md:1-148`）。
192. SMS 签名固定为"Smart Life"，无需传参；SMS 限制：同号 24 小时内 15 条、50 秒内相同内容 2 次（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/notifications.md:30-40`）。
193. 邮件限制：同邮箱 24 小时 30 封、50 秒内相同内容 2 次；语音限制：同号 24 小时 15 次（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/notifications.md:68-112`）。
194. 数据统计：查询小时统计配置 `GET /v1.0/end-user/statistics/hour/config`，查询小时统计数据 `GET /v1.0/end-user/statistics/hour/data`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/statistics.md:3-52`）。
195. 统计配置字段：dev_id、dp_id、dp_code（如 ele_usage）、statistic_type（SUM/COUNT/MAX/MIN）、interval（固定 "hour"）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/statistics.md:33-40`）。
196. 统计数据查询参数 dev_id/dp_code/statistic_type/start_time/end_time，时间格式 `yyyyMMddHH`，单次时间范围不超过 24 小时，end_time >= start_time；返回数组每元素为 `{"yyyyMMddHH": "value"}`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/statistics.md:56-89`）。
197. IPC 云抓拍两步：allocate（`POST /v1.0/end-user/ipc/{device_id}/capture/allocate`，请求设备抓拍/录像并上传）→ resolve（`POST /v1.0/end-user/ipc/{device_id}/capture/resolve`，轮询获取可访问 URL）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/ipc-cloud-capture.md:7-175`）。
198. capture_json 字段：device_id、capture_type（PIC/VIDEO）、pic_count（1-5）、video_duration_seconds（默认 10，1-60）、home_id（可选）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/ipc-cloud-capture.md:29-38`）。
199. resolve 返回 status 为 ACCEPTED（URL 就绪）或 NOT_READY（继续轮询，error_code OBJECT_NOT_READY）；consent=true 返回 decrypt_image_url/decrypt_video_url，false 返回 raw_presigned URL（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/ipc-cloud-capture.md:135-173`）。
200. PIC 抓拍等待策略：首次 resolve 前等待 2 秒，每约 2 秒轮询直到 URL 出现或 30 秒超时，超时后最多再试 3 次（每次间隔 3 秒）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/ipc-cloud-capture.md:194-208`）。
201. VIDEO 录像等待策略：首次 resolve 前等待 `max(5, video_duration_seconds_effective)+2` 秒，每约 2 秒轮询直到 120 秒超时，超时后最多再试 3 次（每次间隔 5 秒）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/ipc-cloud-capture.md:218-232`）。
202. 设备消息订阅为 WebSocket，仅限服务端运行，禁止从浏览器/移动端连接；复用同一 TUYA_API_KEY，无单独凭据（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-message.md:5-13`）。
203. WebSocket 消息格式：顶层 `data` 和 `eventType`（devicePropertyChange 或 onlineStatusChange）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-message.md:50-57`）。
204. devicePropertyChange 事件 data.devId 为设备 ID，data.status 为属性变更数组，每项含 code/value/time（毫秒时间戳）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-message.md:63-82`）。
205. onlineStatusChange 事件 data.status 为 "online" 或 "offline"，data.time 为毫秒时间戳（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-message.md:111-128`）。
206. 致命关闭码（停止重连）：1002、1003、1008、1011；服务器错误检测：含 error/errorMsg/errorCode（非 SUCCESS）或 success:false（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-message.md:42-44`）。
207. 装饰器注册：`@client.on_property_change`、`@client.on_online_status`、`@client.on_raw_message`；`await client.connect()` 阻塞并自动重连；`client.stop()` 优雅停止；`TuyaDeviceMQClient.format_timestamp(ts_ms)` 格式化时间戳（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-message.md:33-41`）。
208. 设备过滤可传 `device_ids=["id1","id2"]` 仅监控特定设备；从事件触发通知时强制 30 分钟冷却节流（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:152-155`；`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/device-message.md:281`）。
209. 支持控制的属性类型仅 bool/enum/value(Integer)/string 四种基本类型（`.chaos/libs/tuya-openclaw-skills/README.md:228-233`；`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:310-317`）。
210. 不支持操作：门锁控制（开锁/解锁）、实时视频流（云抓拍/短视频支持）、图片上传下载、复杂数据类型控制（raw/bitmap/struct/array）、OTA 固件升级、设备配网/移除（`.chaos/libs/tuya-openclaw-skills/README.md:237-246`；`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:320-328`）。
211. 设备控制工作流 6 步：定位设备（房间+品类优先 > 设备名模糊匹配 > 多候选消歧）→ 获取当前状态（检查 result 非 null 和 online=true）→ 查询物模型能力（检查 accessMode）→ 映射命令（相对调整时按 min/max/step 计算并钳制）→ 下发属性 → 等待 1-2 秒后验证（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:146-188`）。
212. 多设备批量控制时在请求间加 0.5-1 秒延迟避免限流（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:239`）。
213. IPC 视觉识别工作流：抓拍 PIC → 获取 decrypt_image_url → 下载图片 → 发送给 AI 视觉模型 → 返回自然语言描述（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:259-268`）。
214. CLI 退出码：2 = 使用/参数验证错误，1 = 运行时/API/网络错误（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:304`；`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/error-handling.md:50-51`）。
215. API 错误码：1010 token invalid、1108 uri path invalid、10001 invalid parameter、10010 end user not exist、10011 no bound contact、40000901 device not exist、40000903 modelId not exist、429 rate limited、500 system error（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/references/error-handling.md:20-30`）。
216. `tuya_api.py` 模块导出 `TuyaAPI` 和 `TuyaAPIError`；`_PREFIX_TO_BASE_URL` 字典映射 7 个前缀到 Base URL；`_resolve_base_url(api_key)` 解析 `sk-` 后前两字符大写（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py:22-72`）。
217. `TuyaAPI.__init__` 接受 api_key/base_url/timeout（默认 30），从环境变量读取缺失值，设置 `Authorization: Bearer` 头，配置 requests.Session 对 429/500/502/503/504 重试 3 次（backoff 0.5，尊重 Retry-After）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py:87-115`）。
218. TuyaAPI 主要方法：get_homes、get_rooms、get_all_devices、get_home_devices、get_room_devices、get_device_detail、get_device_model、issue_properties、rename_device、get_weather、send_sms、send_voice、send_mail、send_push、get_statistics_config、get_statistics_data（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py:141-249`）。
219. TuyaAPI IPC 方法：ipc_ai_capture_allocate、ipc_ai_capture_resolve、ipc_ai_capture_pic_resolve_with_wait、ipc_ai_capture_pic_allocate_and_fetch、ipc_ai_capture_video_resolve_with_wait、ipc_ai_capture_video_allocate_and_fetch（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py:274-478`）。
220. `tuya_device_mq_client.py` 定义 `TuyaDeviceMQClient` 类和 `_resolve_ws_uri(api_key)` 函数；类含 on_property_change/on_online_status/on_raw_message 装饰器、connect（异步阻塞自动重连）、stop、is_running、format_timestamp 静态方法（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_device_mq_client.py:62-244`）。
221. 数据出站声明：API key 发送到用户配置的 base_url 用于认证，设备 ID 和控制命令发送到 base_url，API key 还发送到自动检测的 WebSocket URI 用于实时订阅认证（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/SKILL.md:332-341`）。

## 12. Home Assistant 集成

222. `tuya-home-assistant` 仓库托管的 **Tuya v2 集成**已不再由 Tuya 开发者团队维护，仅提供文档；官方集成位于 Home Assistant Core（`.chaos/libs/tuya-home-assistant/README.md:36-50`）。
223. Tuya Home Assistant 集成用于控制 Powered by Tuya (PBT) 设备，使用 tuya-iot-python-sdk（Tuya Open API 的 Python 版本），由 Tuya 官方和 HA 社区维护（`.chaos/libs/tuya-home-assistant/README.md:32`）。
224. 前置条件：设备需先在 Tuya Smart 或 Smart Life app 中添加；需在 Tuya IoT 平台创建独立账号（不能用 app 凭据登录）（`.chaos/libs/tuya-home-assistant/README.md:57-61`）。
225. 支持 7 大类、50 小类设备（`.chaos/libs/tuya-home-assistant/README.md:63-66`）。
226. 新 Smart Life 集成（Beta）已开源，不再需要注册云开发项目和续期 IoT Core Service 资源；但与现有 Tuya 集成不兼容且无法迁移设备；暂不支持本地控制（`.chaos/libs/tuya-home-assistant/README.md:13-24`）。
227. 安装前提：在 Tuya IoT 平台创建 Smart Home 类型云项目、添加至少一个真实或虚拟设备、授权 API 服务；系统需 Python 3.8+（含 python3-dev）（`.chaos/libs/tuya-home-assistant/docs/install.md:5-11`）。
228. 仅 Home Assistant 2021.10.4 及更高版本支持官方 Tuya 集成（`.chaos/libs/tuya-home-assistant/docs/install.md:19`）。
229. 配置字段：Country（app 账号区域）、Tuya IoT Access ID/Secret（云项目 Authorization Key）、Account（app 账号，非 IoT 平台账号）、Password（app 密码）（`.chaos/libs/tuya-home-assistant/docs/install.md:40-48`）。
230. Tuya v2 与官方 Tuya 集成不兼容，若安装了 tuya_v2 需删除 `custom_components/tuya_v2` 文件夹后重启（`.chaos/libs/tuya-home-assistant/docs/faq.md:5-9`）。
231. 扫码关联设备失败通常因云项目数据中心与 app 账号区域不匹配，需切换正确数据中心重新扫码；可在 Overview > Edit 添加数据中心（`.chaos/libs/tuya-home-assistant/docs/faq.md:13-33`）。
232. API 服务免费试用过期后可在 Cloud > My Services 申请延长最多 6 个月；试用版有 API 调用配额限制（`.chaos/libs/tuya-home-assistant/docs/faq.md:35-51`）。
233. 涂鸦完全禁止跨区域 API 调用和消息订阅，跨区域数据传输有数据安全违规风险（`.chaos/libs/tuya-home-assistant/docs/faq.md:53-54`）。
234. 获取日志：在 configuration.yaml 添加 `logger: default: critical; logs: homeassistant.components.tuya: debug`，日志从 home-assistant.log 或 Configuration/Logs 获取（`.chaos/libs/tuya-home-assistant/docs/get_log.md:7-18`）。
235. 相关项目：Tuya IoT Python SDK 和 Tuya Connector Python（`.chaos/libs/tuya-home-assistant/README.md:99-101`）。

## 13. Smart Life 平台

236. `tuya-smart-life` 是新的 Smart Life (Beta) Home Assistant 集成，使用 tuya-device-sharing-sdk，由 Tuya 官方团队维护（`.chaos/libs/tuya-smart-life/README.md:23`）。
237. 该项目已于 2024.2 版本正式并入 Home Assistant 官方核心仓库，本仓库不再继续迭代（`.chaos/libs/tuya-smart-life/README.md:13`）。
238. Smart Life 集成移除了 Tuya 云开发工作流，用户只需用 Smart Life app 扫码登录即可将设备同步到 HA（`.chaos/libs/tuya-smart-life/README.md:34-36`）。
239. 从 Tuya 集成迁移到 Smart Life 需在 Smart Life app 账号中重新设置设备，不支持直接迁移（`.chaos/libs/tuya-smart-life/README.md:38`）。
240. 前置条件：设备需先在 Smart Life app 中添加（`.chaos/libs/tuya-smart-life/README.md:48-49`）。
241. 支持 7 大类、50 小类设备（`.chaos/libs/tuya-smart-life/README.md:51-54`）。
242. manifest.json 域名为 `smartlife`，integration_type 为 `hub`，iot_class 为 `cloud_push`，config_flow 为 true，依赖 ffmpeg，版本 0.1.0，requirements 为 `tuya-device-sharing-sdk==0.2.0`（`.chaos/libs/tuya-smart-life/custom_components/smartlife/manifest.json:2-46`）。
243. manifest.json 配置了 11 个 DHCP MAC 地址前缀用于设备发现（105A17、10D561、1869D8、381F8D、508A06、68572D、708976、7CF666、84E342、D4A651、D81F12）（`.chaos/libs/tuya-smart-life/custom_components/smartlife/manifest.json:7-40`）。
244. const.py 中 DOMAIN = "smartlife"；PLATFORMS 列表含 16 个实体平台：alarm_control_panel、binary_sensor、button、camera、climate、cover、fan、humidifier、light、number、scene、select、sensor、siren、switch、vacuum（`.chaos/libs/tuya-smart-life/custom_components/smartlife/const.py:30-60`）。
245. const.py 中配置常量：CONF_ENDPOINT、CONF_USER_CODE、CONF_CLIENT_ID（值 "HA_3y9q4ak7g4ephrvke"）、CONF_SCHEMA（值 "haauthorize"）（`.chaos/libs/tuya-smart-life/custom_components/smartlife/const.py:34-37`）。
246. 自定义组件代码含 16 个实体平台 .py 文件加 __init__.py、base.py、config_flow.py、const.py、diagnostics.py、util.py、manifest.json、strings.json 及翻译文件（`.chaos/libs/tuya-smart-life/custom_components/smartlife/` 目录列表）。
247. 开发者扩展指令集时：下载诊断文件查看 category/function/status_range/status → 在对应实体代码文件的字典中添加支持 → 本地测试后提交 PR（`.chaos/libs/tuya-smart-life/README.md:58-98`）。
248. PR 工作流：fork dev 分支 → 开发 → 提交 → 创建 PR 到 dev 分支 → 评审 → 内部测试 → 合并 main → 发版（`.chaos/libs/tuya-smart-life/README.md:101-117`）。

## 14. 测试与工具脚本

249. 测试目录 `tests/` 含三个测试文件：test_build_run.py、test_check_files.py、test_monitor_helper.py（`.chaos/libs/TuyaOpen-dev-skills/tests/` 目录列表）。
250. `test_build_run.py` 通过 `sys.path.insert` 将 `skills/tuyaopen/dev-loop/scripts` 加入路径后导入 build_run 模块（`.chaos/libs/TuyaOpen-dev-skills/tests/test_build_run.py:1-5`）。
251. `test_analyze_log_counts_errors` 验证 analyze_log 对含 1 个 ty E、1 个 ty W、2 个 feed watchdog 的日志返回 (1,1,2)（`.chaos/libs/TuyaOpen-dev-skills/tests/test_build_run.py:8-18`）。
252. `test_analyze_log_empty` 验证空日志返回 (0,0,0)；`test_analyze_log_no_errors` 验证仅含 feed watchdog 和 mqtt connected 的日志返回 (0,0,1)（`.chaos/libs/TuyaOpen-dev-skills/tests/test_build_run.py:21-36`）。
253. OpenClaw `requirements.txt` 内容为 `requests>=2.28.0,<3.0.0` 和 `websockets>=12.0`（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/requirements.txt:1-2`）。
254. TuyaOpen Dev Skills 脚本均为跨平台设计：build_run.py 替代 build_run_linux.sh；check_files.py 替代 check_files.sh；monitor_helper.py 处理 Windows（tasklist/wmic/taskkill）和 Linux（os.kill//proc）差异（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/dev-loop/scripts/build_run.py:2`；`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/code-check/scripts/check_files.py:3`；`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/debug-helper/scripts/monitor_helper.py:104-149`）。
255. TuyaOpen Dev Skills env-setup 提供三平台检查脚本：check_env.sh（bash）、check_env.bat（CMD）、check_env.ps1（PowerShell）（`.chaos/libs/TuyaOpen-dev-skills/skills/tuyaopen/env-setup/scripts/` 目录列表）。
256. OpenClaw CLI 命令参数计数映射 `_COMMAND_ARG_COUNT`：rooms/device_detail/model/sms/voice 需 1 参；control/rename/mail/push/weather 需 2 参；stats_data 需 5 参；ipc_pic_fetch 需 2 参；ipc_video_fetch 需 3 参（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py:36-42`）。
257. OpenClaw CLI 敏感命令集合 `_SENSITIVE_COMMANDS` 含 sms/voice/mail/push；`_sanitize_message` 和 `_redact_args` 用于在错误输出中脱敏（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py:52-53,510-527`）。
258. OpenClaw CLI 验证函数：`_validate_time_yyyyMMddHH`（校验时间格式）、`_validate_stats_time_window`（end>=start 且窗口<=24h）、`_validate_lat_lon`（纬度 [-90,90]、经度 [-180,180]）（`.chaos/libs/tuya-openclaw-skills/tuya-smart-control/scripts/tuya_api.py:575-601`）。
259. TuyaOpen Dev Skills 项目含 GitHub Actions 工作流 release.yml 和 sync-gitee.yml，以及 scripts/sync-gitee-release.sh（`.chaos/libs/TuyaOpen-dev-skills/.github/workflows/` 目录列表）。
260. TuyaOpen Dev Skills 含 release.json 发布元数据文件和 README_zh.md 中文文档（`.chaos/libs/TuyaOpen-dev-skills/` 目录列表）。
