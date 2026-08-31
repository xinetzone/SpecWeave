---
type: Insights
title: "tuya-iot 架构洞察"
---

# tuya-iot 架构洞察

> I阶段分析。基于 R 阶段 599 条事实（TuyaOpen核心框架 339 条 + 技能与生态 260 条）。
> 分析日期：2026-08-23
>
> **编号约定**：TuyaOpen核心事实编号为 `F-xxx`；技能与生态事实编号为 `S-xxx`，以避免两清单编号区间重叠造成歧义。

---

## 洞察一：TAL/TKL 双层抽象——硬件无关的 IoT SDK 设计范式

**陈述**：TuyaOpen 的核心架构是 TAL（Tuya Abstract Layer，涂鸦抽象层）与 TKL（Tuya Kernel Layer，涂鸦内核层）的双层分离。TAL 是应用层抽象，提供统一的 `tal_` 前缀 API，覆盖日志、内存、线程、互斥锁、信号量、队列、工作队列、事件、定时器、睡眠、OTA、文件系统、UART、KV 存储、安全加密、WiFi、蓝牙、有线网络、蜂窝网络等 20+ 模块。TKL 是内核层移植接口，由各芯片平台厂商实现。TAL 函数通常是 TKL 函数的薄封装——例如 `tal_mutex_create_init()` 直接转发调用 `tkl_mutex_create_init()`，`tal_ota_data_process()` 直接调用 `tkl_ota_data_process()`。这种设计使得应用代码只需依赖 TAL 头文件，即可在 T2/T3/T5AI/ESP32/LN882H/BK7231N/GD32/Linux 等 8 款平台间无缝移植，无需修改一行应用代码。

**证据**：
- F-015, F-016: TAL 全称 Tuya Abstract Layer，设计目标是在不同平台上提供统一简化的 API 层，增强可移植性
- F-017~F-021: `tal_api.h` 聚合所有 TAL 模块头文件，覆盖 20+ 子系统
- F-022, F-023: TAL 实现层通过调用底层 TKL 接口实现功能，TAL 与 TKL 为薄封装关系
- F-074: `tal_mutex_lock` 直接转发到 `tkl_mutex_lock`
- F-103: `tal_ota_data_process` 直接转发到 `tkl_ota_data_process`
- F-024~F-028: 统一命名规范（`tal_` 前缀）、统一返回值 `OPERATE_RET`、统一 C++ 兼容、统一不透明句柄 `void*`
- F-293: boards/Kconfig 定义 8 个板级使能选项，全部默认启用

**反常识**：嵌入式 IoT SDK 的常见做法是为每个芯片平台维护独立的 HAL（硬件抽象层），应用代码往往通过宏条件编译处理平台差异，导致「一次编写，到处调试」。TuyaOpen 的双层抽象反其道而行：TAL 不是「可选的抽象层」，而是唯一的应用编程接口——应用代码被物理禁止直接调用厂商 SDK（代码层级规则明确规定 src 层可调用 tkl 但不可直接调用厂商 SDK，apps 层同样不可调用厂商 SDK）。这种强约束的代价是移植新平台时必须完整实现 TKL 接口集，但收益是应用代码的零条件编译移植。更深层的反常识在于：TAL 并非「最小公分母」抽象——它暴露了 WiFi 混杂模式、802.11 管理帧收发、PSRAM 内存管理、低功耗模式控制等高级特性，说明抽象层不必牺牲功能深度。

**行动**：
- 开发 TuyaOpen 应用时，只包含 `tal_api.h` 及所需模块头文件，绝不直接包含平台厂商 SDK 头文件。
- 移植新平台时，对照 TAL 头文件逐个实现 TKL 函数，未实现的函数应返回 `OPRT_NOT_SUPPORTED` 而非静默成功。
- 判断代码是否可移植的标准：能否在 `CONFIG_BOARD_CHOICE_LINUX=y` 下编译通过——Linux 平台是 TAL 的「参考实现」，也是天然的单元测试环境。

---

## 洞察二：Kconfig + CMake 组件化构建——30+ 可裁剪组件的自动化发现

**陈述**：TuyaOpen 的构建系统由 Kconfig（配置）+ CMake（构建）+ tos.py（命令行封装）三位一体构成。根 CMakeLists.txt 通过 `list_components()` 函数自动发现 `src/` 下所有含 CMakeLists.txt 的子目录作为 SDK 组件，无需手动注册。每个组件遵循统一模式：设置 `MODULE_PATH`、通过 `get_filename_component` 获取 `MODULE_NAME`、定义 `LIB_SRCS` 和 `LIB_PUBLIC_INC`、通过 `add_library(${MODULE_NAME})` 创建静态库、通过 `list(APPEND COMPONENT_LIBS ${MODULE_NAME})` 注册到全局组件列表。可选组件使用 `if (CONFIG_ENABLE_XXX STREQUAL "y")` 条件编译守卫。配置管道为：`app_default.config`（用户 defconfig）→ `.build/cache/using.config`（完全展开）→ `.build/cache/using.cmake`（CMake 变量）→ `.build/cache/include/tuya_kconfig.h`（C 宏）。所有组件对象文件最终打包为静态库 `tuyaos`，应用代码编译为 `tuyaapp` 并链接 `tuyaos`。

**证据**：
- F-301~F-321: 顶层 CMakeLists.txt 完整构建逻辑，含 in-source build 禁止、平台检测、组件自动发现、板级集成
- F-315: `list_components()` 函数自动发现 `src/` 下的所有组件并逐一 `add_subdirectory`
- F-317, F-318: 所有组件打包为 `tuyaos` 静态库，应用为 `tuyaapp`
- F-322~F-326: tos.py 是 Python Click 构建工具，注册 14 个子命令
- F-334~F-339: 组件 CMakeLists.txt 统一模式，条件编译守卫，递归 glob 源文件收集
- S-049, S-050: Kconfig 三种依赖机制（select/depends on/if），构建过程完整描述
- S-040: 配置管道四阶段转换
- F-249, F-255, F-265, F-289: 各组件通过独立 Kconfig 选项控制（CONFIG_ENABLE_LIBLWIP、CONFIG_ENABLE_LIBLVGL、CONFIG_ENABLE_TUYA_P2P、ENABLE_AI_COMPONENTS）

**反常识**：嵌入式构建系统的主流方案是 Makefile + Kconfig（如 ESP-IDF 的早期版本）或单独的 CMake（如 Zephyr 的模块化但需手动维护 Kconfig 文件树）。TuyaOpen 的反常识之处有三：第一，组件发现完全基于文件系统约定（有 CMakeLists.txt 即组件），不需要中央注册表，新增组件只需创建目录；第二，Kconfig 不仅配置内核，还配置第三方库（LVGL v8/v9、LwIP、mbedTLS、MicroPython）和应用能力（AI组件、P2P、蓝牙服务），实现了「全栈配置统一」；第三，`tos.py` 不是简单的 make 封装，它处理了平台工具链下载、子模块固定提交更新、批量构建所有配置、项目脚手架生成等高层工作流，是「SDK 管理器」而非「构建调用器」。

**行动**：
- 新增 SDK 组件时，在 `src/` 下创建目录，放入 CMakeLists.txt 和 Kconfig（如需要配置），无需修改任何中央文件。
- 裁剪固件时，优先通过 `tos.py config menu` 关闭不需要的 `CONFIG_ENABLE_XXX` 选项，而非修改源码。
- 验证所有板卡编译时使用 `tos.py dev bac`（build-all-configs），它会对每个配置先完全清理再构建。
- Agent/CI 环境首次构建前创建 `.cache/.dont_prompt_update_platform` 防止平台更新提示挂起。

---

## 洞察三：全栈 IoT 能力——从驱动到云到 AI 的垂直整合

**陈述**：TuyaOpen 不是一个单一的网络栈或 RTOS 抽象层，而是一个覆盖 IoT 设备完整技术栈的垂直整合 SDK。最底层是 TKL 内核移植接口（线程/内存/时钟/Flash/网络驱动）；其上是 TAL 系统服务（日志/事件/工作队列/定时器/文件系统/KV/安全）；再上是网络栈（WiFi Station/AP/Sniffer、BLE NimBLE、有线以太网、蜂窝网络、LwIP 2.1.2、POSIX socket 抽象）；中间件层包含 MQTT（AWS coreMQTT）、HTTP 主机/客户端、mbedTLS 3.1.0、cJSON、P2P（ICE/KCP/RTP/RTCP）；云服务层包含涂鸦 IoT 云对接（4 级安全等级、BLE 配网、MQTT 直连）；AI 层包含 ai_audio（ASR/TTS/KWS）、ai_video、ai_ui（LVGL）、ai_mcp（Model Context Protocol）、ai_agent；最上层是应用框架和外设驱动（按键/LED/显示屏/触摸屏/摄像头/音频编解码器/IMU/PMIC/红外/编码器/打印机）。这种全栈整合意味着开发者无需自行集成 10+ 个第三方库并处理版本兼容问题。

**证据**：
- F-002, F-003: 支持 ASR/KWS/TTS/STT 语音技术，可集成 DeepSeek/ChatGPT/Claude/Gemini 等 LLM
- F-004, F-005: 支持 Google Home 和 Amazon Alexa，支持蓝牙/Wi-Fi/以太网
- F-145~F-164: 网络层覆盖 WiFi（含 sniffer/管理帧/低功耗）、蓝牙 NimBLE、有线、蜂窝、POSIX/LwIP 双后端
- F-185~F-190: libtls 基于 mbedTLS 封装认证加密、消息摘要、HMAC
- F-240~F-247: MQTT 基于 AWS coreMQTT，HTTP 主机服务支持监听/分发/回复
- F-265~F-277: P2P 组件含 ICE/KCP/RTP/RTCP 五个子组件，支持音视频实时通信
- F-278~F-292: 云服务 4 级安全等级，BLE 配网/控制，AI 组件总开关及子模块（ai_mode/audio/mcp/video/picture/ui）
- F-297~F-300: 13 类外设驱动：按键/LED/音频编解码器/显示/触摸屏/编码器/摇杆/PMIC/摄像头/红外/像素灯/IMU/打印机
- F-257~F-264: MicroPython 集成，可配置堆/栈/REPL/GC/machine 模块

**反常识**：IoT SDK 的常见定位是「联网组件库」——提供 MQTT/HTTP/TLS，其余由开发者自行整合。TuyaOpen 反其道整合了从 Flash 块设备到 LLM Agent 的完整路径。这看似违反「单一职责」原则，实则反映了 AIoT 时代的现实需求：智能摄像头需要 P2P 视频传输 + AI 视觉 + 云控制 + 显示 UI，智能音箱需要音频编解码 + ASR + TTS + LLM + 蓝牙配网，这些能力不是「可选插件」而是产品核心需求。SDK 垂直整合的代价是代码体积增大，但通过 Kconfig 细粒度裁剪（每个组件独立开关、MicroPython 堆 32-256KB 可配），资源受限设备可只包含必要组件。更深层的洞察是：TAL 的统一抽象使得这些全栈能力在 8 款平台上行为一致，这是分散库难以实现的。

**行动**：
- 评估 TuyaOpen 是否适合项目时，先检查 `src/` 目录是否已包含所需能力——大多数 IoT 产品需求无需额外第三方库。
- 资源受限设备通过 Kconfig 关闭不用的组件（如无屏设备关闭 liblvgl 和 display 外设，无音频设备关闭 ai_audio）。
- AI 产品使用 `ENABLE_AI_COMPONENTS` 总开关，按需启用 ai_mcp（连接 LLM）、ai_audio（语音交互）、ai_video（视觉）等子模块。
- 安全等级根据设备资源选择：等级 0-1 适用于资源受限 MCU，等级 2-3 适用于富媒体设备（等级 3 使用安全芯片）。

---

## 洞察四：Agent Skills 赋能嵌入式开发——10 个 AI 技能的结构化知识注入

**陈述**：TuyaOpen-dev-skills 是面向 Claude Code、Cursor IDE 及其他 Agent 型 AI 助手的结构化知识文件集合，包含 10 个技能（8 个核心开发技能 + 2 个独立调试技能）。每个技能遵循 Agent Skills 开放标准（agentskills.io），由 `SKILL.md`（核心指令，自动加载）、`references/`（详细文档，按需加载）、`scripts/`（可执行脚本）三部分组成。8 个核心技能构成完整开发工作流：env-setup（环境搭建）→ project-config（项目/板卡/平台创建）→ build（配置选择与编译）→ flash/monitor（烧录与日志）→ device-auth（设备授权与配网）→ dev-loop（构建-烧录-监控迭代循环）→ code-check（代码格式/敏感信息/Doxygen 头检查）→ add-board（新板卡移植）。2 个独立技能为 crash-decode（崩溃地址解码为源码行号）和 cli-debug（通过串口 CLI 发送命令）。技能描述同时使用英文和中文关键词以支持双语触发。

**证据**：
- S-001~S-014: Dev Skills 总览，8 个核心技能 + 2 个独立技能，Agent Skills 标准，三部分结构
- S-006: 标准开发工作流：env-setup → project-config → build → flash-monitor → device-auth/dev-loop
- S-015~S-026: env-setup 技能详细要求（Python/git/cmake/ninja 版本、三平台激活脚本、环境变量、验证命令）
- S-027~S-050: build 技能（配置选择、menuconfig、defconfig 格式、配置管道、构建命令、批量构建）
- S-051~S-069: project-config 技能（new project/board/platform、双路径入口模式、CMakeLists 模板）
- S-070~S-084: code-check 技能（clang-format、中文字符检查、Doxygen 头、敏感信息占位符）
- S-085~S-094: add-board 技能（板卡目录结构、代码层级规则、ESP32 共享驱动）
- S-095~S-115: dev-loop 技能（Build→Flash→Monitor→Analyze 循环、日志格式、错误码、CLI 命令）
- S-116~S-133: device-auth 技能（三凭据、凭据解析优先级、配网模式、CLI 授权）
- S-134~S-142: debug-helper 技能（非阻塞日志捕获、会话管理、跨平台进程检测）
- S-143~S-162: crash-decode 和 cli-debug 技能（addr2line 解码、CLI 串口通信、JSON 输出）

**反常识**：嵌入式开发的传统认知是「AI 助手不懂硬件」——LLM 训练数据中嵌入式代码远少于 Web/后端代码，且硬件相关问题（串口波特率、内存布局、中断优先级）具有强平台特异性，通用 AI 助手容易给出看似合理但错误的建议。TuyaOpen-dev-skills 的反常识在于：它不试图让 LLM「学习」嵌入式知识，而是将知识结构化为 AI 可按需加载的技能包——SKILL.md 提供触发关键词和最小指令集，references/ 提供深度文档，scripts/ 提供可直接执行的验证脚本。这种「检索增强 + 工具执行」模式比微调模型更高效：知识更新只需修改 Markdown 文件，无需重新训练；AI 在遇到特定任务时加载对应技能，而非依赖参数记忆。更深层的反常识是：技能不仅是「文档」，还包含可执行的诊断脚本（check_env.sh、monitor_helper.py、build_run.py、cli_debug.py），AI 可以直接运行这些脚本获取真实环境状态，而非猜测。

**行动**：
- 在 Claude Code 或 Cursor 中开发 TuyaOpen 项目时，将 TuyaOpen-dev-skills 放入 `.agents/skills/`（项目级）或 `~/.cursor/skills/`（全局级），AI 将自动加载。
- 遇到构建问题时，AI 应先加载 build 技能的 KCONFIG_GUIDE.md，而非盲目修改 CMakeLists。
- 崩溃调试时，使用 crash-decode 技能：先识别平台（T5AI/ESP32/Cortex-M），再用对应 addr2line 工具链解码 PC/LR 地址。
- 设备授权失败时，检查波特率（CLI 始终 115200，非芯片监控波特率）和端口（flash 端口非 monitor 端口）。
- 编写新代码时遵循 code-check 技能：无中文字符、Doxygen 文件头、敏感信息用占位符。

---

## 洞察五：OpenClaw 云 API——智能家居的 SaaS 化控制平面

**陈述**：tuya-openclaw-skills 是 OpenClaw 平台的官方 AI Agent 技能，基于涂鸦 2C 终端用户 API，覆盖 3000+ 智能硬件品类、200+ 国家和地区。API key 格式为 `sk-<PREFIX><rest>`，前两个字符自动映射到 7 个数据中心（中国/美西/中欧/印度/美东/西欧/新加坡），每个数据中心有独立的 REST Base URL 和 WebSocket 地址。功能覆盖 10 大模块：家庭管理、设备查询、设备控制、设备管理（重命名）、天气服务、通知（短信/语音/邮件/App推送）、数据统计、IPC 云抓拍、IPC 视觉识别、设备消息订阅（WebSocket）。认证方式为 `Authorization: Bearer {Api-key}`，所有 API 自动处理 HTTP 429 和 5xx 退避重试。设备控制基于物模型（thing model）：先查询设备 model 获取属性定义（accessMode: ro/wr/rw，typeSpec: value/bool/enum/string），再通过 shadow/properties/issue 下发属性（properties 必须是双重序列化的 JSON 字符串）。

**证据**：
- S-163~S-173: OpenClaw 总览，3000+ 品类，7 个数据中心映射，10 大功能模块，自动重试
- S-174~S-179: 家庭管理 API、设备查询 API（4 个端点，无分页全量返回）
- S-180~S-186: 设备控制（物模型查询、属性下发、accessMode 三种、typeSpec 类型、scale 十进制乘数、常见属性码）
- S-187: 设备管理仅支持重命名
- S-188~S-190: 天气查询 API（codes 数组、lat/lon、时间索引格式）
- S-191~S-193: 通知 API（自发自收模式，SMS/语音/邮件/App推送，频率限制）
- S-194~S-196: 数据统计（小时统计配置/数据，SUM/COUNT/MAX/MIN，24 小时范围限制）
- S-197~S-201: IPC 云抓拍两步流程（allocate→resolve 轮询），PIC/VIDEO 不同等待策略
- S-202~S-205: WebSocket 设备消息订阅（devicePropertyChange、onlineStatusChange 事件）

**反常识**：智能家居云 API 的常见模式是「厂商私有协议 + OAuth 复杂授权」，第三方集成成本高。OpenClaw 的反常识在于：它使用单一静态 API key（Bearer Token）而非 OAuth 流程，将「终端用户」直接作为 API 消费者——这意味着 AI Agent 可以代表用户控制家中所有涂鸦生态设备，无需复杂的 account linking。但这种便捷性有明确边界：通知 API 全部为「自发自收」模式（只能发给当前登录用户），API 处于试用阶段受速率限制约束，WebSocket 仅限服务端运行禁止浏览器连接。这些约束反映了「便捷与安全的平衡」。更深层的设计洞察是物模型的「双重序列化」——properties 必须是 JSON 字符串而非 JSON 对象，这在 API 设计中并不常见，但它使得服务端可以透传任意属性结构而无需强类型绑定，是灵活性与简单性的权衡。

**行动**：
- 获取 API key 后，根据 `sk-` 后两个字符确认数据中心（AY=中国、AZ=美西、EU=中欧等），确保与账号注册区域匹配。
- 控制设备前必须先查询物模型 `/devices/{id}/model`，根据 typeSpec 构造合法属性值，注意 scale 换算（实际值 = 输入值 / 10^scale）。
- 下发属性时注意双重序列化：`{"properties": "{\"switch_led\":true}"}`。
- IPC 抓拍使用 allocate→resolve 两步，PIC 等待 2 秒轮询、VIDEO 等待视频时长+2 秒轮询，不要同步阻塞。
- 实时状态更新使用 WebSocket 订阅，监听 devicePropertyChange（属性变更）和 onlineStatusChange（上下线）事件。

---

## 洞察六：多板级统一支持——8 款芯片平台的代码层级隔离

**陈述**：TuyaOpen 支持 8 款芯片平台（T2/T3/T5AI/ESP32/LN882H/BK7231X/GD32/Linux），通过严格的代码层级规则实现隔离：platform 层（芯片厂商 SDK + tkl 适配层）→ src 层（TuyaOpen SDK 组件，可调用 tkl 但不可直接调用厂商 SDK）→ boards/common 层（平台共享驱动）→ boards/BOARD 层（板卡特定代码）→ apps 层（应用代码，可调用 tkl+src 但不可调用厂商 SDK）。板级选择使用 Kconfig `choice` 结构确保唯一目标板，每个板级选项对应一个 `BOARD_CHOICE_XXX` 配置项，选中后通过 `rsource` 引入对应子目录的 Kconfig。板卡目录标准结构含 CMakeLists.txt、Kconfig、board_com_api.h、board_config.h、`<board_name>.c`。ESP32 平台在 `boards/ESP32/common/` 下维护共享驱动（audio/lcd/display/touch/io_expander/led），新板卡可复用而非重复实现。每款板卡有固定的调试串口和波特率（T2=Uart2/115200、T3/T5AI=Uart1/460800、ESP32=Uart0/115200、LN882H=Uart1/921600、BK7231N=Uart2/115200）。

**证据**：
- F-006~F-012: 8 款目标平台及各自调试串口/波特率
- F-293~F-296: boards/Kconfig 定义 8 个板级选项，choice 结构，自动注册，新板标记
- S-007: Dev Skills 支持 7 类平台（T5AI/ESP32/LINUX/T2/T3/LN882H/BK7231X）
- S-086~S-094: add-board 技能详细规定板卡目录结构、Kconfig 规范、代码层级规则
- S-091: 代码层级规则：platform→src→boards/common→boards/BOARD→apps，各层调用边界明确
- S-092: ESP32 共享驱动清单（6 类驱动，多型号支持）
- S-093: 板卡 CMakeLists.txt 标准模板
- S-094: 板卡驱动函数约定（app_audio_driver_init、board_display_init 等）
- S-107: 各芯片调试波特率速查表
- S-124: T5/T5AI 双串口映射（WCH VID 0x1a86 PID 0x55d2）

**反常识**：多平台支持的常见做法是「一个仓库多个分支」或「每个平台一个独立项目」，导致代码碎片化严重。TuyaOpen 的反常识在于「单仓库 + 层级隔离 + 配置选择」：所有平台代码在同一仓库中，但通过 Kconfig choice 确保只有一个平台被编译，通过代码层级规则防止层间违规调用。这种设计的代价是仓库体积较大（包含所有厂商 SDK），但收益是：应用代码一次编写即可在所有平台编译验证（`tos.py dev bac` 批量构建），平台共享驱动（如 ESP32 common/）可被多款板卡复用，新板卡移植有明确的脚手架和检查清单。更深层的洞察是「共享驱动的下沉策略」——ESP32 common/ 中的驱动不是放在 src/ 层（因为它们依赖 ESP-IDF），也不是放在每个板卡目录（因为代码重复），而是放在平台共享层，这是「代码复用」与「层级隔离」的精妙平衡。

**行动**：
- 移植新板卡时使用 `tos.py new board` 生成脚手架，然后从同平台现有板卡复制修改。
- 严格遵守代码层级：apps 和 src 层禁止直接调用厂商 SDK，必须通过 tkl 或 tal。
- ESP32 新板卡优先检查 `boards/ESP32/common/` 是否已有所需驱动（显示屏/触摸/音频/IO扩展），避免重复造轮子。
- Kconfig 中 `BOARD_CHOICE` 值必须与目录名精确匹配（大小写敏感），`CHIP_CHOICE` 设置芯片标识符。
- 跨平台验证使用 `tos.py dev bac`，它会自动跳过已知问题配置（如 GD32.config）并输出构建日志。

---

## 知识地图

### 概念文档规划

#### 第一批：架构基础（7 篇）

| 编号 | 文件名 | 标题 | 覆盖事实编号 | 前置依赖 |
|------|--------|------|-------------|---------|
| 00 | 00-overview.md | TuyaOpen IoT 框架概览 | F-001~F-028, S-001~S-014 | 无 |
| 01 | 01-tal-architecture.md | TAL 抽象层架构 | F-015~F-028, F-029~F-122 | 00 |
| 02 | 02-system-services.md | 系统服务（线程/内存/日志/事件/工作队列） | F-029~F-122 | 01 |
| 03 | 03-network-stack.md | 网络栈（WiFi/BT/有线/蜂窝） | F-123~F-164 | 01 |
| 04 | 04-security-kv.md | 安全与 KV 存储 | F-165~F-209 | 01 |
| 05 | 05-third-party-libs.md | 第三方库集成 | F-237~F-264 | 00 |
| 06 | 06-build-system.md | 构建系统（CMake+Kconfig+tos.py） | F-301~F-339, S-027~S-069 | 00 |

#### 第二批：应用与生态（8 篇）

| 编号 | 文件名 | 标题 | 覆盖事实编号 | 前置依赖 |
|------|--------|------|-------------|---------|
| 07 | 07-p2p-communication.md | P2P 通信（ICE/KCP/RTP） | F-265~F-277 | 03 |
| 08 | 08-ai-components.md | AI 组件（audio/video/UI/MCP） | F-289~F-292, F-002~F-003 | 02 |
| 09 | 09-board-support.md | BSP 板级支持 | F-293~F-296, S-085~S-094 | 06 |
| 10 | 10-peripherals.md | 外设驱动 | F-297~F-300, F-210~F-236 | 09 |
| 11 | 11-dev-skills.md | AI 开发技能体系 | S-001~S-162 | 06 |
| 12 | 12-openclaw-api.md | OpenClaw 云 API | S-163~S-205 | 00 |
| 13 | 13-ha-integration.md | Home Assistant 集成 | F-004, tuya-home-assistant 源码 | 00 |
| 14 | 14-iot-workflow.md | IoT 开发完整工作流 | S-006, S-095~S-142, S-116~S-133 | 11 |

### 学习路径

1. **入门（理解是什么）**：00 → 01
   - 先建立 TuyaOpen 的全局视图（项目定位、平台支持、双层架构），再深入 TAL 抽象层设计。
2. **核心（理解怎么工作）**：02 → 03 → 04 → 05 → 06
   - 掌握系统服务（线程/内存/日志/事件）、网络栈（WiFi/BT/蜂窝）、安全存储（哈希/AES/KV）、第三方库（MQTT/HTTP/LwIP/LVGL）和构建系统。
3. **进阶（理解怎么用）**：07 → 08 → 09 → 10
   - 学习高级能力（P2P 音视频、AI 组件）和硬件相关（BSP 板级支持、外设驱动）。
4. **生态（理解怎么协作）**：11 → 12 → 13 → 14
   - 掌握 AI 开发技能、OpenClaw 云 API、Home Assistant 集成，最后串起完整开发工作流。

### 示例文档规划

| 文件名 | 标题 | 内容要点 |
|--------|------|---------|
| firmware-quickstart.md | TuyaOpen 固件快速入门 | ① 环境激活（export.sh/ps1/bat）；② 项目创建（tos.py new project）；③ 板卡配置（tos.py config choice）；④ 入口代码结构（user_main 双路径模式）；⑤ Kconfig 配置要点；⑥ 构建烧录监控（build/flash/monitor）；⑦ 设备授权（auth 命令）；⑧ 云连接验证。代码示例使用 C 语言。 |
