---
title: "向日葵企业CLI（awesun-cli）完整学习教程：AI时代的命令行远控工具"
source: "https://service.oray.com/question/51527.html"
date: "2026-07-06"
tags: ["向日葵", "Sunlogin", "awesun-cli", "CLI", "命令行", "MCP", "AI Agent", "自动化运维", "远程控制"]
---

# 向日葵企业CLI（awesun-cli）完整学习教程：AI时代的命令行远控工具

> **官方文档**: https://service.oray.com/question/51527.html
> **更新日期**: 2026-06-17

---

## 📋 目录导航

- [一、概述与学习目标 🎯](#一概述与学习目标)
- [二、核心概念 📚](#二核心概念)
- [三、安装与环境配置 ⚙️](#三安装与环境配置)
- [四、快速上手 🚀](#四快速上手)
- [五、全局选项与账号管理 🔐](#五全局选项与账号管理)
- [六、设备管理命令 💻](#六设备管理命令)
- [七、会话控制命令 🔌](#七会话控制命令)
- [八、桌面/文件/端口转发/SSH命令 🖱️](#八桌面文件端口转发ssh命令)
- [九、AI Agent集成与实战场景 🤖](#九ai-agent集成与实战场景)
- [十、专业洞察、常见问题与资源链接 💡](#十专业洞察常见问题与资源链接)

---

## 一、概述与学习目标 🎯

### 1.1 产品定位

**向日葵CLI（awesun-cli）** 是向日葵基于 MCP（宏指令控制协议）API 实现的命令行主控端版本。无需依赖图形界面，即可在终端中直接调用设备管理、远程桌面控制、文件传输、端口转发等核心功能。

### 1.2 CLI价值与适用场景

凭借轻量化、无交互界面的特性，CLI 尤其适合以下场景：

| 场景类型 | 价值说明 |
|---|---|
| **批量管理** | 一次性管理成百上千台远程设备，无需手动操作GUI |
| **脚本集成** | 将远控能力嵌入Shell/Python等脚本，实现工作流自动化 |
| **自动化运维** | 与CI/CD、监控告警系统集成，实现故障自动恢复 |
| **AI Agent调用** | 作为AI Agent的执行工具，实现智能化远程操作 |
| **无头环境** | 在无图形界面的服务器、容器环境中使用远控能力 |

CLI有助于大幅提升远程工作效率，降低人工重复操作的成本。

### 1.3 学习目标

通过本教程的系统学习，你将能够：

1. **理解CLI核心定位**：掌握MCP API协议基础、会话ID机制、归一化坐标设计
2. **完成环境搭建**：独立完成npm安装、账号登录、基础验证
3. **熟练使用核心命令**：掌握设备管理、会话控制、桌面操作、文件传输、端口转发、SSH等全部命令
4. **实现脚本自动化**：编写Shell脚本实现批量设备巡检、自动唤醒、文件传输等自动化任务
5. **集成AI Agent**：理解CLI与AI Agent的工作原理，实现智能化远程运维
6. **排查常见问题**：掌握错误码含义、配置文件位置、帮助系统使用

### 1.4 整体架构

向日葵CLI采用分层架构设计，从下到上依次为：

| 层级 | 功能说明 |
|---|---|
| **MCP API层** | 宏指令控制协议，提供底层远控能力API |
| **会话管理层** | 管理7种类型会话（desktop/file/cmd2/ssh/desktop_view/newcamera/forward） |
| **命令集层** | device/session/desktop/file/forward/ssh六大命令模块 |
| **输出格式层** | 支持table/json/yaml/wide四种输出格式，适配人工阅读和机器解析 |
| **集成层** | 支持Shell脚本调用、AI Agent集成、CI/CD流水线嵌入 |

---

## 二、核心概念 📚

### 2.1 MCP API说明

**MCP（宏指令控制协议）** 是向日葵远程控制的核心通信协议，CLI正是基于此协议实现的命令行主控端。MCP API将远程控制的各项能力（桌面控制、文件传输、命令执行等）封装为标准化接口，CLI通过调用这些API实现无GUI的远程操作。

与GUI客户端相比，CLI直接面向MCP API编程，具有以下特点：
- 无图形界面依赖，资源占用更低
- 输入输出标准化，适合程序解析
- 命令可组合、可脚本化，支持复杂工作流编排

### 2.2 会话ID格式与作用

**会话ID（session_id）** 是远程会话的唯一标识符，在连接建立成功后由系统返回。

**典型格式示例**：
```
r=123456789;p=desktop;t=desktop;
```

**会话ID字段解析**：

| 字段 | 含义 | 示例值 |
|---|---|---|
| `r=` | 远程设备ID | 123456789 |
| `p=` | 父会话类型 | desktop |
| `t=` | 当前会话类型 | desktop |

**会话ID的重要作用**：
1. 会话建立后，所有后续操作（桌面控制、文件传输、截图等）都需要使用此ID作为凭据
2. 会话ID区分不同的连接类型，不同类型会话的操作命令不同
3. 建议在脚本中将会话ID保存为环境变量，方便后续调用

### 2.3 归一化坐标 [0.0, 1.0]

所有桌面鼠标操作使用**归一化坐标系统**，坐标范围为 [0.0, 1.0]，与远程设备的实际屏幕分辨率无关。

**坐标参考点**：

| 坐标位置 | 归一化坐标 |
|---|---|
| 屏幕左上角 | (0.0, 0.0) |
| 屏幕中心 | (0.5, 0.5) |
| 屏幕右下角 | (1.0, 1.0) |

**设计优势**：
- 跨分辨率兼容：无论远程设备是1080p、2K还是4K屏幕，相同的归一化坐标对应相同的相对位置
- 脚本可移植：同一套自动化脚本可以在不同分辨率的设备上运行
- AI友好：AI Agent无需知道具体分辨率，只需指定相对位置即可操作

### 2.4 七种连接类型详解

向日葵CLI支持7种远程连接类型，覆盖远控全场景需求：

| 连接类型 | 说明 | 后续可用命令 |
|---|---|---|
| **desktop** | 远程桌面控制（可操作） | desktop mouse/type/paste/key combo |
| **file** | 远程文件管理 | file ls/mkdir/rm/mv/transfer |
| **cmd2** | 远程命令行（CMD/Bash） | session exec（执行命令） |
| **ssh** | 远程SSH连接 | ssh address（获取本地转发地址） |
| **desktop_view** | 远程桌面观看（仅观看，无法操作） | session screenshot |
| **newcamera** | 远程摄像头 | - |
| **forward** | 端口转发 | forward config |

---

## 三、安装与环境配置 ⚙️

### 3.1 环境要求

在使用向日葵CLI之前，请确认操作系统满足以下要求：

| 要求项 | 具体说明 |
|---|---|
| **操作系统** | Windows 7 及以上版本 / macOS 10.12 及以上版本 / 主流 Linux 发行版（Ubuntu、CentOS等） |
| **命令行工具** | 具备可用的终端或命令行界面（Windows PowerShell / macOS Terminal / Linux Bash） |
| **网络连接** | 设备可正常访问互联网，以便下载工具并连接向日葵服务 |
| **Node.js环境** | 需预装Node.js和npm包管理器 |

### 3.2 npm安装命令

**方式一：手动安装（推荐）**

在终端中执行npm安装命令，即可自动完成向日葵CLI的部署：

```bash
npm install -g @aweray/awesun-cli
```

此方式特别适合在 Trae、Codex 等集成开发环境中直接操作，方便融入现有工作流。

安装完成后，重新开启一个新的终端或命令行窗口，输入验证命令：

```bash
awesun-cli --version
```

若终端正确返回向日葵CLI的版本号信息，则表示安装已成功，环境准备就绪。

### 3.3 AI Agent安装方式

**方式二：AI Agent工具安装**

将向日葵CLI的安装指令发送给所支持的 AI Agent 工具（例如 Cursor、Claude Code）：

```
帮我安装：npm install -g @aweray/awesun-cli
```

AI 助手将自动解析并执行安装步骤。

> ⚠️ **重要提示**：安装及配置完成后，为确保 CLI 的所有功能模块完整加载并正常生效，需要重启当前使用的 AI Agent 工具。

### 3.4 验证安装

安装完成后，执行以下命令验证安装是否成功：

```bash
# 查看版本号
awesun-cli --version

# 查看帮助信息
awesun-cli --help
```

---

## 四、快速上手 🚀

### 4.1 两种登录方式

在使用向日葵CLI管理远程设备之前，必须先通过身份认证。

#### 方式一：用户名登录（推荐）

执行以下命令，系统将提示输入密码：

```bash
awesun-cli login --user <用户名>
```

将 `<用户名>` 替换为实际的向日葵账号用户名。出于安全考虑，密码输入时屏幕不会回显任何字符，只需正确键入密码并按下回车键即可提交。

#### 方式二：扫码登录

执行以下命令，终端将动态生成一个登录二维码：

```bash
awesun-cli login --qrcode
```

使用手机App的扫一扫功能，扫描终端上的二维码即可完成授权登录。此方式免去手动输入密码的步骤，更加便捷且安全。

> 💡 **提示**：登录验证通过后，会话凭证将加密存储于本地。在凭证有效期内，后续执行 CLI 命令时将自动完成鉴权，无需重复登录。

### 4.2 设备列表 awesun-cli device ls 及字段说明

登录成功后，可查看当前账号下所有已绑定的设备信息：

```bash
awesun-cli device ls
```

执行命令后，终端将以表格形式返回设备清单，示例如下：

```
+------------+------------------+------------------+--------+
| Device ID  | Name             | Status           | OS     |
+------------+------------------+------------------+--------+
| 123456789  | My-Office-PC     | Online           | Windows|
| 987654321  | Server-Room-01   | Offline          | Linux  |
+------------+------------------+------------------+--------+
```

**各字段含义说明**：

| 字段 | 说明 |
|---|---|
| **Device ID** | 设备在向日葵体系中的唯一标识符，在建立远程会话时用作目标地址 |
| **Name** | 为设备设置的自定义名称，便于快速识别 |
| **Status** | 设备当前的在线状态：Online 表示设备已连接至向日葵服务并可接受远程连接；Offline 表示设备未上线或网络不可达 |
| **OS** | 设备所运行的操作系统类型 |

### 4.3 发起远程桌面连接

获取目标设备的远程 ID 后，即可通过向日葵CLI建立远程桌面会话。以下示例假设要连接的设备 ID 为 123456789：

```bash
awesun-cli session connect --type desktop --remote-id 123456789
```

**参数说明**：
- `--type desktop`：指定会话类型为远程桌面
- `--remote-id`：指定目标设备的 Device ID

执行此命令后，系统会提示输入设备的访问密码。输入正确密码后，远程桌面会话将建立。

### 4.4 会话ID保存为环境变量

会话建立成功后，命令行会返回一个会话 ID（session_id），例如：`session_id=r=123456789;p=desktop;t=desktop;`。该 ID 在后续的桌面控制、文件传输等操作中作为会话凭据使用，至关重要。

为便于后续调用，建议将其保存为环境变量：

```bash
# Linux/macOS
SESSION_ID="r=123456789;p=desktop;t=desktop;"

# Windows PowerShell
$SESSION_ID = "r=123456789;p=desktop;t=desktop;"
```

保存后，后续命令即可使用 `$SESSION_ID` 变量引用会话ID：

```bash
# 查询会话状态
awesun-cli session status "$SESSION_ID"

# 截取屏幕
awesun-cli session screenshot "$SESSION_ID" --output ./screenshot.png
```

---

## 五、全局选项与账号管理 🔐

### 5.1 全局选项

以下选项可附加于任意 awesun-cli 命令，用于控制输出格式或调阅帮助信息，其位置通常置于子命令之前。

| 选项 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--output` | `-o` | 设置输出格式 | table |
| `--verbose` | `-v` | 显示详细的输出信息，有助于排查问题 | - |
| `--help` | `-h` | 显示命令的帮助信息 | - |

**--output 选项支持的格式**：

| 格式 | 适用场景 |
|---|---|
| `table` | 默认格式，以表格形式呈现，适合直接阅读 |
| `json` | 输出标准 JSON，便于脚本或自动化工具解析 |
| `yaml` | 输出 YAML 格式，兼具可读性与结构化特性 |
| `wide` | 宽表格模式，展示更多详细信息字段 |

**示例：以 JSON 格式查看设备列表**

```bash
awesun-cli --output json device ls
```

### 5.2 login命令 - 登录向日葵账号

**用途**：登录向日葵账号以使用 CLI 工具的各项功能。

**语法**：

```bash
awesun-cli login [选项]
```

**常用选项**：

| 选项 | 简写 | 说明 |
|---|---|---|
| `--user` | - | 指定要登录的用户名，系统会提示输入密码 |
| `--qrcode` | - | 在终端显示二维码，使用 AweSun App 扫码登录 |

**典型示例**：

```bash
# 使用用户名登录
awesun-cli login --user <您的用户名>

# 扫码登录
awesun-cli login --qrcode
```

### 5.3 logout命令 - 登出当前账号

**用途**：注销当前已登录的向日葵账号。

**语法**：

```bash
awesun-cli logout [选项]
```

**常用选项**：

| 选项 | 简写 | 说明 |
|---|---|---|
| `--clean` | - | 登出时清理本地缓存和设置 |

**典型示例**：

```bash
# 登出当前账号
awesun-cli logout

# 登出并清理本地缓存
awesun-cli logout --clean
```

---

## 六、设备管理命令 💻

### 6.1 device ls - 列出您的设备

**用途**：显示您账号下所有已绑定的远程设备列表。

**语法**：

```bash
awesun-cli device ls [选项]
```

**常用选项**：

| 选项 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--limit` | `-l` | 限制返回的设备数量 | 100 |
| `--page` | `-p` | 指定页码，从 1 开始 | 1 |

**典型示例**：

```bash
# 列出所有设备
awesun-cli device ls

# 列出前 10 台设备
awesun-cli device ls --limit 10

# 查看第二页的设备列表
awesun-cli device ls --page 2
```

### 6.2 device search - 搜索设备

**用途**：根据关键词搜索您的设备。

**语法**：

```bash
awesun-cli device search <关键词> [选项]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<关键词>` | 用于搜索设备名称或描述的文本 |

**常用选项**：

| 选项 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--limit` | `-l` | 限制返回的设备数量 | 100 |
| `--page` | `-p` | 指定页码，从 1 开始 | 1 |

**典型示例**：

```bash
# 搜索名称或描述中包含"office"的设备
awesun-cli device search "office"

# 搜索名称或描述中包含"test"的设备，并限制返回 20 条
awesun-cli device search "test" --limit 20
```

### 6.3 device info - 查看设备详情

**用途**：获取指定设备的详细信息。

**语法**：

```bash
awesun-cli device info <设备ID>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<设备ID>` | 目标设备的唯一标识符 |

**典型示例**：

```bash
# 查看设备 ID 为 123456789 的详细信息
awesun-cli device info 123456789
```

### 6.4 device restart - 远程重启设备

**用途**：远程重启指定的设备。

**语法**：

```bash
awesun-cli device restart <设备ID> [选项]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<设备ID>` | 目标设备的唯一标识符 |

**常用选项**：

| 选项 | 简写 | 说明 | 必填 |
|---|---|---|---|
| `--password` | `-p` | 设备的访问密码或系统密码。如果省略，系统会提示您交互式输入 | 否 |
| `--username` | `-u` | 设备的系统账号。如果指定，系统会提示您输入该账号的系统密码 | 否 |

**密码输入说明**：
- 如果您未提供 `--password` 和 `--username`，系统会提示您输入设备的访问密码
- 如果您提供了 `--username` 但未提供 `--password`，系统会提示您输入该系统账号的密码

**典型示例**：

```bash
# 重启设备，并交互式输入访问密码
awesun-cli device restart 123456789

# 重启设备，并指定系统账号，然后交互式输入系统密码
awesun-cli device restart 123456789 --username ADMIN

# 重启设备，直接提供访问密码（适用于脚本自动化）
awesun-cli device restart 123456789 --password "your_device_password"
```

### 6.5 device shutdown - 远程关闭设备

**用途**：远程关闭指定的设备。

**语法**：

```bash
awesun-cli device shutdown <设备ID> [选项]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<设备ID>` | 目标设备的唯一标识符 |

**常用选项**：

| 选项 | 简写 | 说明 | 必填 |
|---|---|---|---|
| `--password` | `-p` | 设备的访问密码或系统密码。如果省略，系统会提示您交互式输入 | 否 |
| `--username` | `-u` | 设备的系统账号。如果指定，系统会提示您输入该账号的系统密码 | 否 |

**密码输入说明**：与 device restart 命令的密码输入规则相同。

**典型示例**：

```bash
# 关闭设备，并交互式输入访问密码
awesun-cli device shutdown 123456789

# 关闭设备，直接提供访问密码（适用于脚本自动化）
awesun-cli device shutdown 123456789 --password "your_device_password"
```

### 6.6 device wakeup - 远程唤醒设备

**用途**：通过网络唤醒（Wake-on-LAN）功能远程启动处于关机或休眠状态的设备。

**语法**：

```bash
awesun-cli device wakeup <设备ID>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<设备ID>` | 目标设备的唯一标识符 |

**典型示例**：

```bash
# 唤醒设备 ID 为 123456789 的设备
awesun-cli device wakeup 123456789
```

> ⚠️ **重要提示**：远程唤醒功能需要目标设备支持 Wake-on-LAN（WOL）并在 BIOS/UEFI 中启用，同时网络环境也需支持。

---

## 七、会话控制命令 🔌

### 7.1 session ls - 列出活跃会话

**用途**：显示当前所有活跃的远程控制会话。

**语法**：

```bash
awesun-cli session ls [选项]
```

**常用选项**：

| 选项 | 简写 | 说明 | 可选值 |
|---|---|---|---|
| `--type` | `-t` | 按会话类型筛选 | desktop, file, cmd2, ssh, desktop_view, newcamera, forward |

**典型示例**：

```bash
# 列出所有活跃会话
awesun-cli session ls

# 只列出远程桌面会话
awesun-cli session ls --type desktop

# 只列出文件管理会话
awesun-cli session ls --type file
```

### 7.2 session connect - 发起远程连接

**用途**：发起一个新的远程控制会话，支持多种连接类型。

**语法**：

```bash
awesun-cli session connect --type <连接类型> (--remote-id <设备ID> | --fastcode <快码>) [--username <系统账号>]
```

**常用选项**：

| 选项 | 说明 | 必填 | 可选值 |
|---|---|---|---|
| `--type` | 指定远程连接的类型 | 是 | desktop, file, cmd2, ssh, desktop_view, newcamera, forward |
| `--remote-id` | 目标设备的唯一 ID。与 --fastcode 二选一 | 二选一 | - |
| `--fastcode` | 目标设备的快码。与 --remote-id 二选一 | 二选一 | - |
| `--username` | 目标设备的系统账号（仅在 --remote-id 模式下可用） | 否 | - |

**7种连接类型说明**：

| 类型 | 说明 |
|---|---|
| `desktop` | 远程桌面控制（可操作） |
| `file` | 远程文件管理 |
| `cmd2` | 远程命令行（CMD/Bash） |
| `ssh` | 远程 SSH 连接 |
| `desktop_view` | 远程桌面观看模式（仅观看，无法操作） |
| `newcamera` | 远程摄像头 |
| `forward` | 端口转发 |

**密码输入说明**：
- 使用 `--fastcode` 连接时，系统会提示您输入设备的访问密码
- 使用 `--remote-id` 且未指定 `--username` 时，系统会提示您输入设备的访问密码
- 使用 `--remote-id` 并指定 `--username` 时，系统会提示您输入该系统账号的密码

**典型示例**：

```bash
# 通过设备 ID 连接远程桌面
awesun-cli session connect --type desktop --remote-id 123456789

# 通过快码连接远程桌面
awesun-cli session connect --type desktop --fastcode 987654321

# 通过设备 ID 连接远程文件管理
awesun-cli session connect --type file --remote-id 123456789

# 通过设备 ID 连接远程 SSH
awesun-cli session connect --type ssh --remote-id 123456789
```

### 7.3 session status - 查询会话状态

**用途**：查询指定远程控制会话的连接状态。

**语法**：

```bash
awesun-cli session status <会话ID>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标会话的唯一标识符 |

**典型示例**：

```bash
# 查询会话 ID 为 "r=123456789;p=desktop;" 的状态
awesun-cli session status "r=123456789;p=desktop;"
```

### 7.4 session disconnect - 终止会话

**用途**：终止一个或多个活跃的远程控制会话。

**语法**：

```bash
awesun-cli session disconnect <会话ID>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标会话的唯一标识符 |

**典型示例**：

```bash
# 终止会话 ID 为 "r=123456789;p=desktop;" 的会话
awesun-cli session disconnect "r=123456789;p=desktop;"
```

### 7.5 session screenshot - 截取会话屏幕

**用途**：截取指定远程桌面会话的屏幕截图。

**语法**：

```bash
awesun-cli session screenshot <会话ID> [选项]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标桌面会话的唯一标识符 |

**常用选项**：

| 选项 | 简写 | 说明 |
|---|---|---|
| `--output` | `-o` | 截图保存的本地路径和文件名 |

**典型示例**：

```bash
# 截取会话屏幕并保存到当前目录下的 screenshot.png 文件
awesun-cli session screenshot "r=123456789;p=desktop;" --output ./screenshot.png
```

---

## 八、桌面/文件/端口转发/SSH命令 🖱️

> ⚠️ **重要提示**：本章命令按会话类型分类，仅适用于对应类型的活跃会话。

### 8.1 桌面控制命令（desktop/desktop_view类型）

以下命令仅适用于 `desktop` 或 `desktop_view` 类型的活跃会话。所有鼠标操作的坐标均使用**归一化坐标**，范围是 [0.0, 1.0]。

#### desktop mouse click - 模拟鼠标点击

**用途**：在远程桌面的指定坐标模拟鼠标点击操作。

**语法**：

```bash
awesun-cli desktop mouse click <会话ID> --x <X坐标> --y <Y坐标> [选项]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标桌面会话的唯一标识符 |

**常用选项**：

| 选项 | 说明 | 默认值 | 可选值 |
|---|---|---|---|
| `--x` | 鼠标点击的 X 坐标（归一化） | 必填 | 0.0 到 1.0 之间 |
| `--y` | 鼠标点击的 Y 坐标（归一化） | 必填 | 0.0 到 1.0 之间 |
| `--button` | 鼠标按钮 | left | left, right, middle |
| `--clicks` | 点击次数 | 1 | 1（单击）, 2（双击） |

**归一化坐标参考**：

| 位置 | X坐标 | Y坐标 |
|---|---|---|
| 左上角 | 0.0 | 0.0 |
| 屏幕中心 | 0.5 | 0.5 |
| 右下角 | 1.0 | 1.0 |

**典型示例**：

```bash
# 在屏幕中心进行左键单击
awesun-cli desktop mouse click "r=123456789;p=desktop;" --x 0.5 --y 0.5

# 在指定位置进行右键双击
awesun-cli desktop mouse click "r=123456789;p=desktop;" --x 0.3 --y 0.4 --button right --clicks 2
```

#### desktop mouse move - 移动鼠标

**用途**：将远程桌面的鼠标指针移动到指定坐标。

**语法**：

```bash
awesun-cli desktop mouse move <会话ID> --x <X坐标> --y <Y坐标>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标桌面会话的唯一标识符 |

**常用选项**：

| 选项 | 说明 |
|---|---|
| `--x` | 鼠标移动的 X 坐标（归一化） |
| `--y` | 鼠标移动的 Y 坐标（归一化） |

**典型示例**：

```bash
# 将鼠标移动到屏幕中心
awesun-cli desktop mouse move "r=123456789;p=desktop;" --x 0.5 --y 0.5
```

#### desktop type - 输入文本

**用途**：在远程桌面模拟键盘输入文本。此命令会逐字符输入，适用于需要模拟用户打字行为的场景。

**语法**：

```bash
awesun-cli desktop type <会话ID> <要输入的文本> [选项]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标桌面会话的唯一标识符 |
| `<要输入的文本>` | 需要输入的字符串内容 |

**常用选项**：

| 选项 | 说明 | 单位 |
|---|---|---|
| `--delay` | 每个字符输入之间的延迟时间 | 毫秒 |

> ⚠️ **注意**：在使用此命令前，请确保远程桌面上的输入焦点已在目标文本框内。

**典型示例**：

```bash
# 输入文本"Hello World"
awesun-cli desktop type "r=123456789;p=desktop;" "Hello World"

# 输入文本"Hello World"，每个字符之间延迟 300 毫秒
awesun-cli desktop type "r=123456789;p=desktop;" "Hello World" --delay 300
```

#### desktop paste - 粘贴文本

**用途**：在远程桌面模拟粘贴操作，适用于粘贴较长的文本内容。

**语法**：

```bash
awesun-cli desktop paste <会话ID> <要粘贴的文本>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标桌面会话的唯一标识符 |
| `<要粘贴的文本>` | 需要粘贴的字符串内容 |

> ⚠️ **注意**：在使用此命令前，请确保远程桌面上的输入焦点已在目标文本框内。

**典型示例**：

```bash
# 粘贴一段长文本
awesun-cli desktop paste "r=123456789;p=desktop;" "这是一段很长的文本内容，可以用于填充表单或文档。"
```

#### desktop key combo - 模拟组合键

**用途**：在远程桌面模拟按下并释放一组组合键（如 Ctrl+C, Alt+F4）。

**语法**：

```bash
awesun-cli desktop key combo <会话ID> --keys <按键序列> [选项]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标桌面会话的唯一标识符 |

**常用选项**：

| 选项 | 说明 | 格式 |
|---|---|---|
| `--keys` | 逗号分隔的按键序列 | 例如 ctrl,alt,v |
| `--delay` | 按键之间的延迟时间 | 毫秒（默认 97 毫秒） |

**常用组合键表**：

| 功能 | 按键序列 |
|---|---|
| 复制 | `--keys ctrl,c` |
| 粘贴 | `--keys ctrl,v` |
| 剪切 | `--keys ctrl,x` |
| 全选 | `--keys ctrl,a` |
| 保存 | `--keys ctrl,s` |
| 撤销 | `--keys ctrl,z` |
| 关闭窗口 | `--keys alt,F4` |
| 切换应用 | `--keys alt,tab` |

**典型示例**：

```bash
# 模拟 Ctrl+V 粘贴操作
awesun-cli desktop key combo "r=123456789;p=desktop;" --keys ctrl,v

# 模拟 Ctrl+Shift+Esc 打开任务管理器
awesun-cli desktop key combo "r=123456789;p=desktop;" --keys ctrl,shift,esc
```

### 8.2 文件管理命令（file类型）

以下命令仅适用于 `file` 类型的活跃会话。

#### file ls - 列出远程文件

**用途**：列出远程主机指定路径下的文件和文件夹。

**语法**：

```bash
awesun-cli file ls <会话ID> [选项]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标文件会话的唯一标识符 |

**常用选项**：

| 选项 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--path` | `-p` | 要列出的远程路径 | 远程桌面目录 |
| `--limit` | `-l` | 限制返回的文件/文件夹数量 | 100 |
| `--keyword` | `-k` | 根据关键词筛选文件/文件夹 | - |

**典型示例**：

```bash
# 列出远程桌面目录下的文件
awesun-cli file ls "r=123456789;p=file;"

# 列出远程主机指定目录下的文件
awesun-cli file ls "r=123456789;p=file;" --path "/Users/admin/Downloads"

# 在指定目录中搜索包含"report"的文件
awesun-cli file ls "r=123456789;p=file;" --path "/Users/admin" --keyword "report"
```

#### file mkdir - 创建远程文件夹

**用途**：在远程主机上创建新的文件夹。

**语法**：

```bash
awesun-cli file mkdir <会话ID> --path <父级路径> --name <文件夹名称>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标文件会话的唯一标识符 |

**常用选项**：

| 选项 | 说明 |
|---|---|
| `--path` | 新文件夹的父级路径 |
| `--name` | 新文件夹的名称 |

**典型示例**：

```bash
# 在远程主机的 Downloads 目录下创建名为 "NewFolder" 的文件夹
awesun-cli file mkdir "r=123456789;p=file;" --path "/Users/admin/Downloads" --name "NewFolder"
```

#### file rm - 删除远程文件或文件夹

**用途**：删除远程主机上的文件或文件夹。

**语法**：

```bash
awesun-cli file rm <会话ID> --path <文件/文件夹路径> [--recursive]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标文件会话的唯一标识符 |

**常用选项**：

| 选项 | 简写 | 说明 |
|---|---|---|
| `--path` | - | 要删除的文件或文件夹的完整路径 |
| `--recursive` | `-r` | 如果删除的是文件夹，此选项会递归删除其所有内容 |

**典型示例**：

```bash
# 删除远程主机上的文件
awesun-cli file rm "r=123456789;p=file;" --path "/Users/admin/file.txt"

# 递归删除远程主机上的文件夹及其所有内容
awesun-cli file rm "r=123456789;p=file;" --path "/Users/admin/OldFolder" --recursive
```

#### file mv - 重命名远程文件或文件夹

**用途**：重命名远程主机上的文件或文件夹。

**语法**：

```bash
awesun-cli file mv <会话ID> --path <原路径> --new-name <新名称>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标文件会话的唯一标识符 |

**常用选项**：

| 选项 | 说明 |
|---|---|
| `--path` | 原文件或文件夹的完整路径 |
| `--new-name` | 新的文件或文件夹名称（不包含路径） |

**典型示例**：

```bash
# 将远程主机上的 old.txt 文件重命名为 new.txt
awesun-cli file mv "r=123456789;p=file;" --path "/Users/admin/old.txt" --new-name "new.txt"
```

#### file transfer - 传输文件

**用途**：在本地和远程主机之间上传或下载文件/文件夹。

**语法**：

```bash
awesun-cli file transfer <会话ID> --type <传输类型> --local <本地路径> --remote <远程路径> [--override]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标文件会话的唯一标识符 |

**常用选项**：

| 选项 | 说明 | 可选值 |
|---|---|---|
| `--type` | 传输方向 | down（下载）, up（上传） |
| `--local` | 本地文件或文件夹的完整路径 | - |
| `--remote` | 远程文件或文件夹的完整路径 | - |
| `--override` | 如果目标文件已存在，强制覆盖 | - |

**传输类型说明**：

| 类型 | 方向 |
|---|---|
| `down` | 从远程主机下载到本地 |
| `up` | 从本地上传到远程主机 |

**典型示例**：

```bash
# 从远程主机下载文件到本地
awesun-cli file transfer "r=123456789;p=file;" \
  --type down \
  --remote "C:\\Users\\admin\\Documents\\report.pdf" \
  --local "./report.pdf"

# 从本地上传文件到远程主机，并覆盖同名文件
awesun-cli file transfer "r=123456789;p=file;" \
  --type up \
  --local "./upload.zip" \
  --remote "C:\\Users\\admin\\Desktop\\upload.zip" \
  --override
```

#### file transfer status - 查询传输进度

**用途**：查询文件传输任务的当前进度。

**语法**：

```bash
awesun-cli file transfer status <会话ID> [--transfer-id <任务ID>]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标文件会话的唯一标识符 |

**常用选项**：

| 选项 | 说明 |
|---|---|
| `--transfer-id` | 指定要查询的传输任务 ID。如果省略，将显示所有传输任务的进度 |

**典型示例**：

```bash
# 查询所有文件传输任务的进度
awesun-cli file transfer status "r=123456789;p=file;"

# 查询指定传输任务的进度
awesun-cli file transfer status "r=123456789;p=file;" --transfer-id "your_transfer_id"
```

#### file transfer cancel - 取消传输任务

**用途**：取消一个或所有正在进行的文件传输任务。

**语法**：

```bash
awesun-cli file transfer cancel <会话ID> [--transfer-id <任务ID>]
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标文件会话的唯一标识符 |

**常用选项**：

| 选项 | 说明 |
|---|---|
| `--transfer-id` | 指定要取消的传输任务 ID。如果省略，将取消所有传输任务 |

**典型示例**：

```bash
# 取消指定的文件传输任务
awesun-cli file transfer cancel "r=123456789;p=file;" --transfer-id "your_transfer_id"

# 取消所有文件传输任务
awesun-cli file transfer cancel "r=123456789;p=file;"
```

### 8.3 端口转发命令（forward类型）

以下命令仅适用于 `forward` 类型的活跃会话。

#### forward config - 配置端口转发规则

**用途**：为端口转发会话配置具体的转发规则，将远程设备上的端口映射到本地。

**语法**：

```bash
awesun-cli forward config <会话ID> --channels <通道配置>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标端口转发会话的唯一标识符 |

**常用选项**：

| 选项 | 说明 | 格式 |
|---|---|---|
| `--channels` | 端口转发通道的配置 | JSON 数组字符串 |

**JSON通道配置格式**：

```json
[
  {
    "channel_id": "通道名称",
    "address": "目标地址",
    "port": 端口号
  }
]
```

**配置字段说明**：

| 字段 | 说明 |
|---|---|
| `channel_id` | 为您的转发通道指定一个易于识别的名称 |
| `address` | 远程设备上要转发的目标 IP 地址（通常是 127.0.0.1 表示远程设备自身） |
| `port` | 远程设备上要转发的目标端口号 |

**典型示例**：

```bash
# 配置单个端口转发：将远程设备的 22 端口（SSH）转发到本地
awesun-cli forward config "r=123456789;p=forward;" \
  --channels '[{"channel_id":"ssh","address":"127.0.0.1","port":22}]'

# 配置多个端口转发：同时转发 SSH (22) 和 Web 服务 (8080)
awesun-cli forward config "r=123456789;p=forward;" \
  --channels '[{"channel_id":"ssh","address":"127.0.0.1","port":22},{"channel_id":"web","address":"127.0.0.1","port":8080}]'
```

### 8.4 SSH命令（ssh类型）

以下命令仅适用于 `ssh` 类型的活跃会话。

#### ssh address - 获取 SSH 本地连接地址

**用途**：获取通过 AweSun CLI 建立的 SSH 会话的本地连接地址，您可以使用标准的 SSH 客户端连接此地址。

**语法**：

```bash
awesun-cli ssh address <会话ID>
```

**参数**：

| 参数 | 说明 |
|---|---|
| `<会话ID>` | 目标 SSH 会话的唯一标识符 |

**典型示例**：

```bash
# 获取 SSH 本地连接地址
awesun-cli ssh address "r=123456789;p=ssh;"
```

执行此命令后，CLI会返回本地转发地址（如 `127.0.0.1:12345`），然后您可以使用标准SSH客户端连接：

```bash
ssh username@127.0.0.1 -p 12345
```

---

## 九、AI Agent集成与实战场景 🤖

AweSun CLI 作为一个强大的命令行工具，天然支持与 AI Agent（人工智能代理）进行集成，实现自动化、智能化的远程管理和操作。AI Agent 可以通过调用 awesun-cli 命令来执行任务，并通过解析其输出（尤其是 JSON 格式输出）来获取信息并做出决策。

### 9.1 集成优势（4点）

| 优势 | 说明 |
|---|---|
| **自动化任务** | AI Agent 可以自动执行重复性的远程操作，如批量设备巡检、定时文件传输、故障自动重启等 |
| **智能决策** | 结合 AI Agent 的分析能力，可以根据设备状态、日志信息等自动判断并执行相应的远程操作 |
| **跨平台兼容** | AweSun CLI 跨平台特性使得 AI Agent 可以在不同操作系统环境下管理远程设备 |
| **可编程接口** | CLI 本身就是一种可编程接口，方便 AI Agent 通过脚本或编程语言进行调用 |

### 9.2 工作原理（4步骤）

AI Agent 通常通过以下步骤与 AweSun CLI 交互：

| 步骤 | 说明 |
|---|---|
| **① 命令生成** | AI Agent 根据其任务目标和当前状态，生成相应的 awesun-cli 命令 |
| **② 命令执行** | AI Agent 在操作系统层面执行 awesun-cli 命令 |
| **③ 结果解析** | AI Agent 捕获 awesun-cli 命令的输出。为了便于程序化解析，建议在执行命令时使用 `--output json` 选项，让 CLI 输出 JSON 格式的结果 |
| **④ 决策与行动** | AI Agent 解析 JSON 结果，提取所需信息，并根据这些信息进行下一步的决策，可能包括生成新的 awesun-cli 命令或执行其他操作 |

### 9.3 实战场景一：自动化运维批量检查服务器状态

作为运维工程师，您可能需要定期检查多台服务器的运行状态。通过 AweSun CLI，您可以轻松实现自动化。

**完整脚本示例**：

```bash
# 场景：批量检查所有服务器的在线状态，并输出到 CSV 文件

# 1. 登录 AweSun CLI
awesun-cli login --user <您的用户名>

# 2. 获取所有设备列表，并以 JSON 格式输出
#    然后使用 jq 工具提取关键信息并格式化为 CSV
awesun-cli device ls --output json | \
jq -r '(.[] | [.remote_id, .name, .status, .os]) | @csv' > server_status.csv

# server_status.csv 文件内容示例：
# "123456789","My-Office-PC","Online","Windows"
# "987654321","Server-Room-01","Offline","Linux"

# 3. （可选）根据状态进行后续操作，例如唤醒离线设备
#    这里使用简单的 shell 脚本演示，实际可结合更复杂的逻辑
cat server_status.csv | while IFS=',' read -r id name status os;
do
  if [[ "$status" == "\"Offline\"" ]]; then
    echo "发现离线设备：$name ($id)，尝试唤醒..."
    awesun-cli device wakeup "$id"
  fi
done
```

> 💡 **提示**：jq 是一个轻量级且灵活的命令行 JSON 处理器，非常适合在 shell 脚本中处理 CLI 的 JSON 输出。

### 9.4 实战场景二：远程技术支持诊断

当客户遇到技术问题时，技术支持人员可以使用向日葵 CLI 快速连接客户设备，进行诊断并收集必要的文件。

**完整脚本示例**：

```bash
# 场景：连接客户桌面，截取错误界面，并下载日志文件

# 1. 登录 AweSun CLI
awesun-cli login --user <您的用户名>

# 2. 连接客户的远程桌面（假设设备 ID 为 123456789）
#    请确保您已获得客户授权和访问密码
SESSION_ID=$(awesun-cli session connect --type desktop --remote-id 123456789 --output json | jq -r '.session_id')

# 3. 截取当前桌面屏幕，保存为诊断截图
awesun-cli session screenshot "$SESSION_ID" --output "./customer_issue_$(date +%Y%m%d%H%M%S).png"

# 4. 切换到文件管理会话
FILE_SESSION_ID=$(awesun-cli session connect --type file --remote-id 123456789 --output json | jq -r '.session_id')

# 5. 下载客户设备上的日志文件（例如：C:\Program Files\App\logs\app.log）
awesun-cli file transfer "$FILE_SESSION_ID" \
  --type down \
  --remote "C:\\Program Files\\App\\logs\\app.log" \
  --local "./customer_app.log"

# 6. 完成操作后，断开所有会话
awesun-cli session disconnect "$SESSION_ID"
awesun-cli session disconnect "$FILE_SESSION_ID"
```

### 9.5 实战场景三：批量软件部署

在企业环境中，您可能需要向多台远程设备批量部署软件或修改配置。AweSun CLI 结合脚本可以高效完成此任务。

**完整脚本示例**：

```bash
# 场景：向多台服务器上传配置文件并执行重启服务命令

# 假设您有一个设备 ID 列表文件 devices.txt，每行一个设备 ID
# devices.txt 内容示例：
# 123456789
# 987654321

# 1. 登录 AweSun CLI
awesun-cli login --user <您的用户名>

# 2. 遍历设备列表，对每台设备执行操作
while IFS= read -r DEVICE_ID;
do
  echo "正在处理设备：$DEVICE_ID"

  # 建立文件管理会话
  FILE_SESSION_ID=$(awesun-cli session connect --type file --remote-id "$DEVICE_ID" --output json | jq -r '.session_id')

  if [ -z "$FILE_SESSION_ID" ]; then
    echo "⚠️ 无法连接到设备 $DEVICE_ID 的文件会话，跳过。"
    continue
  fi

  # 上传新的配置文件
  awesun-cli file transfer "$FILE_SESSION_ID" \
    --type up \
    --local "./new_config.ini" \
    --remote "C:\\Program Files\\App\\config.ini" \
    --override

  # 断开文件会话
  awesun-cli session disconnect "$FILE_SESSION_ID"

  # 建立命令行会话以执行重启命令
  CMD_SESSION_ID=$(awesun-cli session connect --type cmd2 --remote-id "$DEVICE_ID" --output json | jq -r '.session_id')

  if [ -z "$CMD_SESSION_ID" ]; then
    echo "⚠️ 无法连接到设备 $DEVICE_ID 的命令行会话，跳过重启。"
    continue
  fi

  # 执行重启服务的命令（例如：Windows 服务管理命令）
  awesun-cli session exec "$CMD_SESSION_ID" "net stop MyService && net start MyService"

  # 断开命令行会话
  awesun-cli session disconnect "$CMD_SESSION_ID"

  echo "设备 $DEVICE_ID 处理完成。"
  echo "---"

done < devices.txt
```

---

## 十、专业洞察、常见问题与资源链接 💡

### 10.1 专业洞察

#### CLI与MCP互补定位

CLI与MCP协议是互补关系而非替代关系：

| 维度 | MCP API | CLI (awesun-cli) |
|---|---|---|
| **面向对象** | AI Agent、开发者（协议层） | 命令行用户、脚本、运维人员 |
| **交互方式** | 程序调用、协议交互 | 终端命令、Shell脚本 |
| **使用门槛** | 需要理解协议细节、封装SDK | 即装即用，命令行语法直观 |
| **典型场景** | AI Agent原生集成、SDK二次开发 | 运维脚本、批量操作、自动化流水线 |

**设计理念**：MCP作为底层协议提供标准化远控能力，CLI作为上层工具提供人类友好和脚本友好的访问入口，二者共同构成"协议+工具"的完整生态。

#### "命令行即API"设计理念

向日葵CLI体现了"命令行即API"的现代工具设计哲学：
- **每个命令都是一个API端点**：device ls对应查询设备列表API，session connect对应建立连接API
- **标准化输出**：JSON/YAML输出格式让命令输出可被程序稳定解析
- **可组合性**：通过管道（|）和重定向（>），命令可以像API调用一样组合成复杂工作流
- **无状态设计**：每个命令独立执行，会话通过session_id显式传递，便于脚本管理

#### AI原生工具特征

向日葵CLI具备典型的AI原生工具特征：

| 特征 | 说明 |
|---|---|
| **JSON输出适合解析** | `--output json`选项让AI Agent无需复杂的文本解析即可获取结构化数据 |
| **无GUI依赖** | 无需图形界面，可在服务器、容器、CI/CD环境中运行，适配AI Agent的执行环境 |
| **脚本友好** | 所有参数可通过命令行选项传递，支持非交互式密码输入（--password），便于自动化脚本调用 |
| **明确的错误码** | 0-6共7种错误码，AI Agent可根据退出码判断执行结果并采取相应策略 |
| **三级帮助系统** | awesun-cli --help / awesun-cli device --help / awesun-cli device ls --help，AI Agent可自助查询命令用法 |

#### 归一化坐标设计考量

桌面控制采用[0.0, 1.0]归一化坐标而非绝对像素坐标，是一个深思熟虑的设计决策：

1. **分辨率无关**：同一脚本在1080p、2K、4K屏幕上都能正确点击相对位置
2. **跨设备兼容**：Windows/macOS/Linux不同DPI设置不影响坐标计算
3. **AI友好**：AI Agent无需查询远程分辨率即可操作，降低交互复杂度
4. **可预测性**：(0.5, 0.5)永远是屏幕中心，语义清晰

### 10.2 AI Agent启示

1. **作为Agent执行工具**：awesun-cli可直接作为AI Agent的"手"，让Agent具备远程操作物理设备的能力——从查看屏幕、移动鼠标、输入文本到传输文件、执行命令，形成完整的远程操作闭环。

2. **适合自动化运维场景**：
   - **无人值守巡检**：Agent定期检查设备状态，自动唤醒离线设备
   - **故障自愈**：检测到服务异常时自动远程重启
   - **批量部署**：配置文件更新、软件升级等批量操作自动化
   - **远程协助**：AI客服通过CLI远程诊断客户问题，无需人工介入

### 10.3 常见问题

#### 环境变量配置

您可以通过配置环境变量来简化 awesun-cli 的使用，例如设置默认输出格式。

**配置文件位置**：

| 操作系统 | 配置文件路径 |
|---|---|
| Linux/macOS | `~/.config/awesun-cli/config` |
| Windows | `%APPDATA%\awesun-cli\config` |

**配置文件示例**：

```
# 在此文件中设置环境变量，例如：
AWESUN_OUTPUT=json
```

**优先级规则**：命令行选项的优先级最高，其次是环境变量，最低是配置文件中的设置。

#### 7种错误码

当 awesun-cli 命令执行失败时，会返回一个非零的退出码。了解这些退出码有助于您快速定位问题。

| 退出码 | 说明 |
|---|---|
| **0** | 命令执行成功 |
| **1** | 通用错误 |
| **2** | 参数错误 |
| **3** | API认证失败（登录凭证过期或无效） |
| **4** | 网络连接错误 |
| **5** | 会话不存在 |
| **6** | 设备离线 |

#### 错误输出JSON示例

命令执行失败时，错误信息以JSON格式输出，便于程序解析：

```json
{
  "code": 401,
  "message": "Unauthorized: Invalid API token",
  "timestamp": "2026-04-02T12:03:00Z"
}
```

#### --help三级帮助

CLI内置三级帮助系统，您可以通过--help选项查看任何命令的详细帮助信息：

```bash
# 第一级：查看 awesun-cli 的整体帮助（列出所有命令模块）
awesun-cli --help

# 第二级：查看 device 子命令的帮助（列出device下所有子命令）
awesun-cli device --help

# 第三级：查看 device ls 具体命令的帮助（列出该命令的所有选项和参数）
awesun-cli device ls --help
```

### 10.4 相关资源链接

| 资源 | 路径 |
|---|---|
| 向日葵综合分析Wiki | [sunlogin-comprehensive-analysis-wiki.md](sunlogin-comprehensive-analysis-wiki.md) |
| 向日葵产品系列索引 | [sunlogin-product-series-index.md](sunlogin-product-series-index.md) |
| 向日葵安全产品Wiki | [sunlogin-security-wiki.md](sunlogin-security-wiki.md) |
| 官方CLI文档 | https://service.oray.com/question/51527.html |
