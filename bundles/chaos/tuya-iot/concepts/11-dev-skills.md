---
type: Concept
title: AI 开发技能体系
description: TuyaOpen Dev Skills 10 个 AI 编码技能，覆盖环境搭建、构建、板卡移植、调试、授权与崩溃解码全流程
tags: [tuya, tuyaopen, dev-skills, agent-skills, ai, coding, skills, mcp]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: tuya-skills-source
    resource: "/references/tuya-skills-source.md"
    title: TuyaOpen 技能与生态源码
  - id: facts-tuya-skills-ecosystem
    resource: "/references/facts-tuya-skills-ecosystem.md"
    title: 技能与生态事实清单
---

# AI 开发技能体系

TuyaOpen-dev-skills 是一组遵循 [Agent Skills 开放标准](https://agentskills.io/) 的 AI 编码技能集合，位于独立仓库 `TuyaOpen-dev-skills/`。每个技能是一个包含 `SKILL.md` 文件的目录，向 AI 编码助手（如 Trae、Cursor、Copilot）提供结构化的开发上下文、代码模板和操作指南。目前包含 10 个核心开发技能，覆盖从环境搭建到调试解码的完整固件开发生命周期。

## Agent Skills 标准

Agent Skills 是一种开放标准，用于向 AI 编码助手提供领域特定知识。每个技能的核心是 `SKILL.md` 文件，包含：

- **技能名称与描述**：何时触发该技能
- **前置条件**：环境要求和依赖
- **操作步骤**：具体的命令和工作流程
- **代码模板**：可复用的代码片段
- **故障排除**：常见问题和解决方案

AI 助手根据用户的自然语言描述自动加载相关技能，无需用户手动查阅文档。技能文件使用 Markdown 编写，易于维护和版本控制。

## 技能目录结构

```text
TuyaOpen-dev-skills/
├── skills/
│   ├── tuyaopen/                  # 8 个核心开发技能
│   │   ├── env-setup/             # 环境搭建
│   │   ├── build/                 # 构建系统
│   │   ├── project-config/        # 项目配置
│   │   ├── code-check/            # 代码检查
│   │   ├── add-board/             # 板卡移植
│   │   ├── dev-loop/              # 开发循环
│   │   ├── device-auth/           # 设备授权
│   │   └── debug-helper/          # 调试辅助
│   ├── tuyaopen-crash-decode/     # 崩溃解码（独立技能）
│   └── tuyaopen-cli-debug/        # CLI 调试（独立技能，含 cli_debug.py）
├── tests/                         # 技能脚本单元测试
├── README.md
└── README_zh.md
```

8 个核心技能组织在 `skills/tuyaopen/` 目录下，崩溃解码和 CLI 调试两个技能因附带独立 Python 脚本而位于 `skills/` 顶层。每个技能可包含 `references/`（补充文档）和 `scripts/`（可执行脚本）子目录。

## 十大核心技能

### 01-env-setup：环境搭建

指导 AI 助手帮助开发者搭建 TuyaOpen 开发环境，包括：
- 工具链安装（GCC ARM、ESP-IDF 等）
- Python 依赖安装（tos.py 依赖）
- 源码获取和子模块初始化
- 环境变量配置
- 首次构建验证

该技能识别不同操作系统（Windows/Linux/macOS）的差异，提供对应的安装命令。

### 02-build：构建系统

传授 CMake + Kconfig + tos.py 构建系统的使用方法：
- `tos.py config`：项目配置
- `tos.py build`：编译构建
- `tos.py clean`：清理构建产物
- `tos.py menuconfig`：交互式配置
- Kconfig 选项语法和依赖关系
- 组件 CMakeLists.txt 编写规范

### 03-project-config：项目配置

指导项目配置管理：
- `app_default.config` 配置文件结构
- 板卡和平台选择
- 组件启用/禁用
- 配置继承和覆盖规则
- 多配置文件管理

### 04-code-check：代码检查

提供代码质量检查能力：
- 编码规范检查
- 静态分析工具使用
- 层级违规检测（防止应用层直接调用厂商 SDK）
- 代码格式化
- 常见错误模式识别

### 05-add-board：板卡移植

指导将 TuyaOpen 移植到新板卡：
- 板卡目录结构创建（`tos.py new board`）
- Kconfig 配置
- `board_config.h` 引脚映射
- TKL 接口实现
- 板卡初始化代码编写
- 构建和验证流程

这是最复杂的技能之一，涉及硬件抽象层的具体实现。

### 06-dev-loop：开发循环

描述日常开发工作循环：
- 代码编写 → 构建 → 烧录 → 调试的迭代流程
- 增量构建技巧
- 日志查看和分析
- 开发效率优化建议

### 07-device-auth：设备授权

处理涂鸦云设备授权：
- UUID/AuthKey 获取和写入
- `auth` CLI 命令使用
- 授权状态检查
- 多环境授权（生产/测试）
- 授权失败排查

### 08-debug-helper：调试辅助

提供调试技巧和工具使用：
- GDB 远程调试配置
- 串口日志分析
- 线程状态检查
- 内存泄漏检测
- 性能分析方法

### 09-tuyaopen-crash-decode：崩溃解码

帮助分析设备崩溃：
- Backtrace 解析
- 寄存器状态解读
- 栈帧分析
- 地址到源码行的映射（addr2line）
- 常见崩溃原因（空指针/栈溢出/看门狗复位）

### 10-tuyaopen-cli-debug：CLI 调试

教授 CLI 命令行调试：
- 内置命令使用（help/sys_*/kv_*/fs_*）
- 自定义命令注册
- 串口终端配置
- CLI 脚本化操作

## 技能与源码的关系

Dev Skills 不是文档的替代品，而是 AI 助手的「操作手册」。技能文件中引用的所有命令、路径、配置项都必须与实际源码一致。技能的维护需要与 TuyaOpen 源码同步更新。

技能中包含的代码模板直接源自 TuyaOpen 的实际代码模式，例如：
- 组件 CMakeLists.txt 模板来自现有组件
- Kconfig 写法参考实际 Kconfig 文件
- CLI 命令注册代码来自 `tal_cli.h` 的真实 API

## 与 MCP 工具的协同

除了 SKILL.md 提供的静态知识，TuyaOpen 还支持通过 MCP（Model Context Protocol）工具提供动态能力：
- 构建系统状态查询
- Kconfig 选项查询
- 源码搜索
- 编译错误分析

技能（Skills）提供「怎么做」的知识，MCP 工具提供「实时数据」的访问，两者结合使 AI 助手能够高效地辅助嵌入式开发。

## 技能安装与使用

将 TuyaOpen-dev-skills 安装到 AI 编码助手中：

1. 克隆仓库到本地
2. 在 AI 助手的技能配置中指向 `skills/` 目录
3. AI 助手会在对话中自动识别相关技能并加载

开发者只需用自然语言描述需求（如「帮我把 TuyaOpen 移植到一块新的 ESP32-S3 板卡」），AI 助手即会自动加载 05-board-porting 技能，按照其中的步骤指导操作。

## 相关概念

- [构建系统](/concepts/06-build-system.md)
- [BSP 板级支持](/concepts/09-board-support.md)
- [IoT 开发完整工作流](/concepts/14-iot-workflow.md)
- [TAL 抽象层架构](/concepts/01-tal-architecture.md)
- [OpenClaw 云 API](/concepts/12-openclaw-api.md)
