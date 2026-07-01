---
title: "WSL 系统学习计划"
category: "learning"
tags: ["wsl", "learning-path", "linux", "windows", "container", "wslc", "plan9", "drvfs", "cmake", "sdk", "diagnostics", "hvsocket", "gns", "systemd"]
date: "2026-07-01"
status: "draft"
author: ""
summary: "基于 .temp/libs/WSL（Microsoft WSL 官方开源仓库）制定的系统学习计划，涵盖 Windows/Linux 三层架构、Linux 侧核心进程（mini_init/init/plan9/gns/relay）、Plan9/DrvFs 文件系统互操作、WSLC Container API（Session→Container→Process 模型）、CMake 跨编译构建系统、组策略与诊断调试，包含 5 个实操练习与 4 周学习路径。"
---

# WSL 系统学习计划

> 基于 `.temp\libs\WSL` 文件夹（Microsoft WSL 官方开源仓库）制定
> 创建日期：2026-07-01

---

## 一、文件夹结构分析

### 1.1 顶层目录功能定位

| 目录 | 功能定位 | 学习优先级 |
|---|---|---|
| `src/` | 核心源代码（Linux/Windows/Shared 三层） | ⭐⭐⭐ |
| `doc/` | 开发者文档（架构、API、调试） | ⭐⭐⭐ |
| `CMakeLists.txt` | 顶层构建配置 | ⭐⭐ |
| `cmake/` | CMake 模块（FindIDL/FindLINUXBUILD 等） | ⭐ |
| `diagnostics/` | 诊断脚本（日志收集、网络排查） | ⭐⭐⭐ |
| `distributions/` | 发行版元数据（DistributionInfo.json） | ⭐⭐ |
| `intune/` | 组策略模板（ADMX/ADML，22 种语言） | ⭐⭐ |
| `localization/` | UI 本地化资源（.resw） | ⭐ |
| `.pipelines/` | Azure CI/CD 流水线 | ⭐ |
| `nuget/` | NuGet 包定义（SDK/PluginApi/Containers） | ⭐⭐ |
| `msipackage/`、`msixinstaller/` | Windows 安装包 | ⭐ |

### 1.2 源代码三层架构（src/）

```
src/
├── linux/              # Linux 侧实现（运行在 WSL2 虚拟机内）
│   ├── init/           # init 进程：mini_init 派生的分发版初始化
│   ├── plan9/          # Plan9 文件服务器（Windows↔Linux 文件互访）
│   ├── netlinkutil/    # Netlink 网络配置工具
│   └── mountutil/      # 挂载工具（drvfs 等）
├── windows/            # Windows 侧实现
│   ├── WslcSDK/        # WSL Container SDK（C/C++/C#/WinRT 投影）
│   ├── common/         # 共享逻辑（网络、分发版、安全、子进程）
│   ├── service/        # wslservice.exe 核心服务
│   ├── wslc/           # wslc.exe CLI（类 Docker 命令）
│   ├── wsl/            # wsl.exe 主入口
│   └── wslg/wslhost/wslrelay/  # 辅助可执行文件
└── shared/             # 跨平台共享代码
    ├── configfile/     # .wslconfig / /etc/wsl.conf 解析器
    └── inc/            # 共享头文件（消息、套接字、CDI schema）
```

### 1.3 文档结构（doc/docs/）

| 文档 | 内容 |
|---|---|
| `dev-loop.md` | 构建、测试、部署全流程 |
| `debugging.md` | 日志收集、调试器附加 |
| `technical-documentation/` | 架构原理（init/plan9/gns/drvfs/relay） |
| `api-reference/` | WSLC API 参考（C/C++/C#） |

---

## 二、核心技术点学习

### 2.1 WSL 整体架构（必学）

**学习目标**：理解 Windows 侧与 Linux 侧的组件交互。

核心架构图（源自 `doc/docs/technical-documentation/index.md`）：

```
Windows 侧                              Linux 侧（WSL2 虚拟机）
─────────────                          ─────────────────────
wsl.exe ──COM──> wslservice.exe ──hvsocket──> mini_init
wslg.exe ──COM──> wslservice.exe              ├─> gns（网络配置）
wslconfig.exe ──COM──> wslservice.exe         ├─> init（分发版初始化）
                                               │    ├─> plan9（文件服务）
                                               │    └─> session leader
                                               │         └─> relay ─> 用户进程
                                               └─> /mnt/wsl（共享挂载点）
```

**关键通信机制**：
- **COM**：Windows 进程间通信（wsl.exe ↔ wslservice.exe）
- **hvsocket**：Windows ↔ Linux 虚拟机套接字
- **lxbus**：WSL1 专用通信通道

### 2.2 Linux 侧核心进程

| 进程 | 职责 | 源码位置 |
|---|---|---|
| `mini_init` | WSL2 虚拟机顶层进程，挂载 VHD、创建命名空间 | `src/linux/init/` |
| `init` | 分发版初始化（挂载 /proc/sys/dev、配置 cgroups、解析 wsl.conf、启动 systemd） | `src/linux/init/init.cpp` |
| `plan9` | Plan9 文件服务器，实现 Windows 访问 `\\wsl.localhost` | `src/linux/init/plan9.cpp` |
| `gns` | Guest Network Service，配置网络（IP、路由、DNS、MTU） | `src/linux/init/GnsEngine.cpp` |
| `relay` | 中继用户进程的 stdin/stdout/stderr 到 Windows | 技术文档 relay.md |

### 2.3 文件系统互操作

**Windows → Linux 访问**（`\\wsl.localhost\<distro>`）：
- `p9rdr.sys`（Windows 重定向驱动）→ wslservice.exe → plan9 服务器
- WSL2 通过 hvsocket 连接 plan9，WSL1 通过 unix socket

**Linux → Windows 访问**（`/mnt/c` 等）：
- DrvFs 机制，通过 `mount -t drvfs C: /mnt/c`
- 区分提权/非提权挂载命名空间（两套独立 mount namespace）
- 实现见 `src/linux/init/drvfs.cpp`

### 2.4 WSL Container API（WSLC）— 重点

**三层模型**：`Session → Container → Process`

**API 层级**（详见 `src/windows/WslcSDK/wslcsdk.h`）：

```c
// Session 层
WslcInitSessionSettings()    // 初始化会话设置
WslcCreateSession()          // 创建会话（含 VHD、CPU、内存配置）
WslcTerminateSession()       // 终止会话

// Container 层
WslcInitContainerSettings()  // 初始化容器设置
WslcCreateContainer()        // 创建容器
WslcStartContainer()         // 启动容器
WslcStopContainer()          // 停止容器（支持信号）
WslcDeleteContainer()        // 删除容器

// Process 层
WslcInitProcessSettings()    // 初始化进程设置
WslcCreateContainerProcess() // 在容器内创建进程
WslcGetProcessIOHandle()     // 获取 stdin/stdout/stderr 句柄
WslcSignalProcess()          // 向进程发送信号

// Image 管理
WslcPullSessionImage()       // 拉取镜像
WslcListSessionImages()      // 列出镜像
WslcPushSessionImage()       // 推送镜像
```

**wslc CLI 命令体系**（类 Docker，见 `src/windows/wslc/commands/`）：
- `container`：run/create/start/stop/kill/exec/attach/inspect/list/logs/stats/prune
- `image`：pull/push/build/import/load/save/tag/inspect/list/prune
- `network`：create/inspect/list/prune
- `volume`：create/inspect/list/prune
- `session`：enter/list/run/shell/terminate
- `registry`：登录认证
- `system` / `version` / `settings`

### 2.5 构建系统

**关键技术点**：
- CMake 3.25+ + Visual Studio 2022
- **跨编译**：用 LLVM/Clang 交叉编译 Linux 侧代码（target: `<arch>-unknown-linux-musl`）
- 依赖管理：FetchContent 拉取 GSL、nlohmann json、yaml-cpp、boost；NuGet 拉取 WSL 内核、WSLg、TAEF 测试框架
- 开发加速：`UserConfig.cmake` 配置 `WSL_DEV_BINARY_PATH` 生成精简包

### 2.6 组策略与配置

**组策略**（`intune/WSL.admx`）：
- `AllowWSL` / `AllowWSL1` / `AllowInboxWSL`
- 自定义内核、系统分发版、内核命令行
- 嵌套虚拟化、内核调试、网络模式
- WSL Container 开关与注册表白名单

**配置文件**：
- `%USERPROFILE%/.wslconfig`：全局 WSL2 配置（网络模式、内存、CPU）
- `/etc/wsl.conf`：单分发版配置（systemd、挂载、互操作）

### 2.7 诊断与调试

**日志收集**（`diagnostics/`）：
- `collect-wsl-logs.ps1`：一键收集（支持 storage/networking/hvsocket 配置文件）
- ETL 追踪：`wpr -start wsl.wprp -filemode`，用 WPA 查看
- 关键 Provider：`Microsoft.Windows.Lxss.Manager`、`Microsoft.Windows.Subsystem.Lxss`

**调试**：
- Windows 侧：WinDbg 附加 wslservice.exe，符号在 `bin/<platform>/<target>`
- Linux 侧：gdb 附加进程，`wsl --debug-shell` 进入根命名空间
- 崩溃转储：注册表配置 `LocalDumps` 自动收集

---

## 三、实践操作环节（5 个实操练习）

### 实操 1：从源码构建 WSL

**目标**：掌握 WSL 构建流程，理解构建系统。

**步骤**：
1. 运行 `tools\setup-dev-env.ps1` 安装依赖（CMake、VS2022、Developer Mode）
2. 配置开发加速：`copy UserConfig.cmake.sample UserConfig.cmake`，取消注释 `WSL_DEV_BINARY_PATH`
3. 生成解决方案：`cmake .`
4. 构建：`cmake --build .`
5. 部署：`powershell tools\deploy\deploy-to-host.ps1`
6. 验证：`wsl --version` 确认安装自编译版本

**验证点**：`bin\x64\Debug\wsl.msi` 生成成功，`wsl --status` 正常输出。

### 实操 2：配置与网络模式对比

**目标**：理解 `.wslconfig` 配置与网络模式差异。

**步骤**：
1. 创建 `%USERPROFILE%/.wslconfig`：
   ```ini
   [wsl2]
   networkingMode=NAT
   memory=4GB
   processors=2
   ```
2. `wsl --shutdown` 后重启，用 `ip a` 观察 NAT 网络拓扑
3. 切换为 `networkingMode=mirrored`，重启后对比网络接口（与宿主共享 IP）
4. 启用 DNS 隧道：`dnsTunneling=true`，观察 `/etc/resolv.conf` 变化
5. 运行 `diagnostics/networking.sh` 收集网络配置快照

**验证点**：能区分 NAT（独立子网）与 Mirrored（镜像宿主网络）模式的接口差异。

### 实操 3：使用 wslc CLI 管理容器

**目标**：掌握 WSL Container CLI 的类 Docker 工作流。

**步骤**：
```bash
# 1. 拉取镜像
wslc image pull ubuntu:24.04

# 2. 列出镜像
wslc image list

# 3. 运行容器
wslc container run -it --name myapp ubuntu:24.04 /bin/bash

# 4. 在运行中的容器内执行命令
wslc container exec myapp apt-get update

# 5. 查看容器日志
wslc container logs myapp

# 6. 停止并删除
wslc container stop myapp
wslc container remove myapp
```

**验证点**：能完成 pull→run→exec→stop→remove 全生命周期操作。

### 实操 4：调用 WSLC SDK API（C 示例）

**目标**：理解 Session→Container→Process 编程模型。

**步骤**：
1. 包含 `src/windows/WslcSDK/wslcsdk.h`，链接 `wslcsdk.lib`
2. 编写最小示例：
   ```c
   #include <wslcsdk.h>
   #include <stdio.h>

   int main() {
       WslcSessionSettings sessionSettings;
       WslcInitSessionSettings(L"MySession", L"C:\\wslc\\storage", &sessionSettings);

       WslcSession session;
       PWSTR error = NULL;
       HRESULT hr = WslcCreateSession(&sessionSettings, &session, &error);
       if (FAILED(hr)) { printf("CreateSession failed: 0x%x\n", hr); return 1; }

       WslcContainerSettings containerSettings;
       WslcInitContainerSettings("ubuntu:24.04", &containerSettings);

       WslcContainer container;
       hr = WslcCreateContainer(session, &containerSettings, &container, &error);
       if (SUCCEEDED(hr)) {
           WslcStartContainer(container, WSLC_CONTAINER_START_FLAG_NONE, &error);
           // ... 创建进程、获取输出 ...
           WslcReleaseContainer(container);
       }
       WslcReleaseSession(session);
       return 0;
   }
   ```
3. 对照 `doc/docs/api-reference/c/error-codes.md` 处理 `WSLC_E_*` 错误码

**验证点**：程序能创建会话、拉起容器并捕获退出码。

### 实操 5：诊断日志收集与故障排查

**目标**：掌握 WSL 故障排查方法论。

**步骤**：
1. **收集常规日志**：
   ```powershell
   .\diagnostics\collect-wsl-logs.ps1
   ```
2. **网络专项排查**：`.\collect-wsl-logs.ps1 -LogProfile networking`
3. **崩溃转储**：
   ```powershell
   .\collect-wsl-logs.ps1 -Dump
   ```
4. **启用调试控制台**：在 `.wslconfig` 添加 `[wsl2] debugConsole=true`
5. **ETL 追踪**：
   ```
   wpr -start wsl.wprp!WSL-Networking -filemode
   # 复现问题
   wpr -stop logs.ETL
   ```
6. 用 `wsl --debug-shell` 进入根命名空间，gdb 附加 gns/mini_init

**验证点**：能独立完成"问题复现→日志收集→初步定位"流程。

---

## 四、知识总结与文档整理

### 4.1 学习笔记结构建议

```
wsl-learning-notes/
├── 01-architecture.md          # 架构总览（组件图 + 通信机制）
├── 02-linux-side.md            # Linux 侧进程职责（mini_init/init/plan9/gns/relay）
├── 03-windows-side.md          # Windows 侧可执行文件职责
├── 04-filesystem-interop.md    # Plan9 + DrvFs 互操作原理
├── 05-networking.md            # GNS + NAT/Mirrored/DNS 隧道
├── 06-wslc-api.md              # Container API 三层模型
├── 07-build-system.md          # CMake 跨编译 + NuGet 依赖
├── 08-configuration.md         # .wslconfig + /etc/wsl.conf + 组策略
├── 09-diagnostics.md           # 日志/调试/崩溃排查
└── 10-faq.md                   # 常见问题解决方案
```

### 4.2 常见问题解决方案清单（FAQ 重点）

| 问题类别 | 现象 | 解决方案 |
|---|---|---|
| 安装失败 | `wsl --install` 报错 | 检查虚拟化是否启用；运行 `WslcGetMissingComponents` |
| 网络不通 | WSL 内无法上网 | 切换 NAT/Mirrored 模式；检查防火墙策略；收集 networking 日志 |
| 文件访问慢 | `/mnt/c` 读写慢 | 避免跨文件系统操作；改用 `\\wsl.localhost` 访问 Linux 文件 |
| 内存占用高 | WSL 占满宿主内存 | `.wslconfig` 配置 `memory=` 限制 |
| systemd 不启动 | `systemctl` 报错 | `/etc/wsl.conf` 添加 `[boot] systemd=true` |
| 容器无法启动 | WSLC 报 `WSLC_E_CONTAINER_NOT_RUNNING` | 检查 `AllowWSLContainer` 组策略；确认镜像存在 |
| 镜像拉取失败 | `WSLC_E_WU_SEARCH_FAILED` | 检查注册表白名单策略；网络代理配置 |
| 崩溃无堆栈 | 进程闪退无日志 | 启用 `LocalDumps` 自动转储；附加 WinDbg |

### 4.3 推荐学习路径（按优先级）

```
第 1 周：架构理解
├─ Day 1-2：阅读 doc/docs/ 全部技术文档
├─ Day 3-4：精读 technical-documentation/ 五篇（init/plan9/gns/drvfs/relay）
└─ Day 5：绘制个人版架构图，对照 mermaid 源图核对

第 2 周：源码走读 + 构建
├─ Day 1-2：实操 1（从源码构建）
├─ Day 3-4：走读 src/linux/init/ 启动流程
└─ Day 5：走读 src/windows/WslcSDK/ API 实现

第 3 周：配置与容器
├─ Day 1-2：实操 2（配置与网络模式）
├─ Day 3-4：实操 3（wslc CLI）
└─ Day 5：实操 4（SDK 编程）

第 4 周：诊断与总结
├─ Day 1-2：实操 5（日志收集与调试）
├─ Day 3-4：整理学习笔记（4.1 结构）
└─ Day 5：编写 FAQ，复盘
```

---

## 五、补充资源

### 5.1 关键源码文件索引

| 文件 | 作用 |
|---|---|
| `src/linux/init/init.cpp` | Linux 分发版 init 主入口 |
| `src/linux/init/plan9.cpp` | Plan9 文件服务器实现 |
| `src/linux/init/GnsEngine.cpp` | GNS 网络配置引擎 |
| `src/linux/init/drvfs.cpp` | DrvFs 挂载实现 |
| `src/windows/WslcSDK/wslcsdk.h` | WSLC SDK 公共 API 定义 |
| `src/windows/wslc/commands/RootCommand.cpp` | wslc CLI 命令根 |
| `src/shared/configfile/configfile.h` | .wslconfig 解析器 |
| `intune/WSL.admx` | 组策略模板定义 |
| `distributions/DistributionInfo.json` | 发行版元数据 |
| `diagnostics/collect-wsl-logs.ps1` | 日志收集脚本 |

### 5.2 外部相关仓库

- [microsoft/WSL2-Linux-Kernel](https://github.com/microsoft/WSL2-Linux-Kernel) - WSL 使用的 Linux 内核
- [microsoft/WSLg](https://github.com/microsoft/wslg) - Linux GUI 应用支持
- [microsoftdocs/wsl](https://github.com/microsoftdocs/wsl) - WSL 用户文档
- [WSL 官方文档](https://learn.microsoft.com/windows/wsl/)

### 5.3 学习产出物清单

- [ ] 个人版 WSL 架构图
- [ ] 5 个实操练习记录与截图
- [ ] 10 篇学习笔记（按 4.1 结构）
- [ ] FAQ 文档
- [ ] 复盘报告

---

> **备注**：本学习计划基于 WSL 仓库源码与官方文档制定，建议结合实际动手操作加深理解。
> WSL Container API 目前处于 **preview** 阶段，正式 GA 计划在 2026 年秋季。
