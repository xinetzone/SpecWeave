# 变更日志

## 2026-08-23

- 初始生成 Tuya IoT OKF v0.2 文档 bundle
- 基于 R 阶段事实清单（TuyaOpen 核心 339 条 + 技能与生态 260 条）与 I 阶段 6 个核心洞察生成
- 创建 15 篇概念文档，分两批：
  - 第一批（架构基础）：框架概览、TAL 架构、系统服务、网络栈、安全与 KV、第三方库、构建系统
  - 第二批（应用与生态）：P2P 通信、AI 组件、BSP 板级支持、外设驱动、AI 开发技能、OpenClaw 云 API、Home Assistant 集成、IoT 开发工作流
- 创建 1 篇示例文档：TuyaOpen 固件快速入门
- 创建 2 篇信源登记文件：TuyaOpen 核心框架源码、技能与生态源码
- 创建所有索引文件（根 index.md、concepts/index.md、references/index.md、examples/index.md）
- 关键 API 函数名经 TuyaOpen 头文件 Grep 验证（tal_wifi_station_connect、tal_kv_init/set/get、tal_thread_create_and_start、tal_cli_cmd_register 等）

## 2026-08-23（V 阶段验证与修复）

- 完成结构完整性验证：26 个文件全部存在，目录结构符合 OKF v0.2 规范
- 完成 Frontmatter 规范验证：16 个内容文件均含 9 个必需字段
- 完成内部链接验证：全部以 `/` 开头，无断链
- 完成 Grep API 验证：tal_/tkl_/tdl_ 前缀、19 类 TAL 头文件路径、10 个 SKILL.md 路径、tos.py 命令签名、P2P/AI 组件目录、OpenClaw API 端点均经源码核实
- 创建 verification-report.md，记录 7 大类验证结果与 11 处修复
- V 阶段直接修复的问题：
  - `tos.py new app --name` → `tos.py new project`（交互式）
  - `tos.py new board --platform/--name` → 交互式 `tos.py new board`
  - `tos.py flash/monitor COM3` → `tos.py flash/monitor -p COM3`
  - `tos.py config choice -c ESP32_S3` → 交互式 `tos.py config choice`
  - WiFi 事件回调签名（WF_EVENT_E + WFE_* 事件）
  - CLI API 签名（tal_cli_cmd_register 参数 uint8_t，返回 int）
  - LED 控制改为 tdl_led 驱动框架
  - UART 接收中断回调签名修正
  - dev-skills 目录结构修正为 skills/tuyaopen/ 实际路径
- 结论：验证通过，零虚构，bundle 可发布
