---
id: "wsl-learning-plan"
title: "WSL 系统学习计划"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/08-systems-infrastructure/wsl-learning-plan.toml"
category: "learning"
tags: ["wsl", "learning-path", "linux", "windows", "container", "wslc", "plan9", "drvfs", "cmake", "sdk", "diagnostics", "hvsocket", "gns", "systemd", "winrt", "nuget", "com", "error-codes"]
date: "2026-07-01"
status: "stable"
author: ""
summary: "基于 external/WSL 源码 + wsl.dev 开发者文档 + learn.microsoft.com 官方文档制定的系统学习计划，涵盖 Windows/Linux 三层架构、Linux 侧核心进程（mini_init/init/plan9/gns/relay）、Plan9/DrvFs 文件系统互操作、WSLC Container API 三语言投影（C/C#/C++ WinRT）、CMake 跨编译构建、组策略与诊断调试，包含 5 个实操练习、官方端到端示例、完整错误码表与 4 周学习路径。"
---
# WSL 系统学习计划

> 基于 `external\WSL` 文件夹（Microsoft WSL 官方开源仓库）+ 官方在线文档制定
> 创建日期：2026-07-01
> 文档来源：
> - 源码：`external\WSL`
> - 开发者文档：[wsl.dev](https://wsl.dev/)（API 参考、技术文档）
> - 用户文档：[learn.microsoft.com/windows/wsl](https://learn.microsoft.com/zh-cn/windows/wsl/)（容器功能、CLI 用法）
> - 容器 API 参考：[wsl.dev/api-reference](https://wsl.dev/api-reference/)（C / C# / C++ 三语言投影）

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

核心架构图（综合 `wsl.dev/technical-documentation/` 各组件文档与源码绘制）：

```
Windows 侧                              Linux 侧（WSL2 虚拟机）
─────────────                          ─────────────────────
wsl.exe ──COM──> wslservice.exe ──hvsocket①──> mini_init（VM 顶层进程）
wslg.exe ──COM──> wslservice.exe              │       │
wslconfig.exe ──COM──> wslservice.exe         │       ├─ hvsocket②通知通道（进程退出/分发版终止）
                                               │       │     （向 wslservice 回报事件）
                                               │       │
                                               │       ├─> gns（网络配置，独立 hvsocket 通道）
                                               │       │
                                               │       └─> LxMiniInitMessageLaunchInit
                                               │            └─> init（分发版初始化，每分发版独立 mount/pid/UTS namespace）
                                               │                 ├─ 挂载 /proc /sys /dev
                                               │                 ├─ 配置 cgroups
                                               │                 ├─ 解析 /etc/wsl.conf
                                               │                 ├─ 启动 systemd（可选）
                                               │                 ├─ 挂载 drvfs（提权/非提权两套 mount namespace）
                                               │                 ├─> plan9（hvsocket 文件服务器）
                                               │                 └─> session leader
                                               │                      └─ LxInitMessageCreateProcessUtilityVm
                                               │                           └─> relay
                                               │                                ├ fork() 父进程：中继 stdin/stdout/stderr
                                               │                                └ fork() 子进程：exec() 用户进程
                                               │
                                               └─> /mnt/wsl（所有分发版共享挂载点）
```

**关键通信机制**（官方文档确认）：
- **COM**：Windows 进程间通信（wsl.exe/wslg.exe/wslconfig.exe ↔ wslservice.exe）
- **hvsocket**：Windows ↔ Linux 虚拟机套接字
  - mini_init 维护**两条独立 hvsocket 通道**：①命令通道（接收 wslservice 命令）②通知通道（向 wslservice 回报事件）
  - gns 维护独立 hvsocket 通道用于网络配置
  - relay 维护多个 hvsocket 通道（stdin/stdout/stderr/终端尺寸/退出通知）
- **lxbus**：WSL1 专用通信通道（WSL2 不使用）

**mini_init 命令通道关键消息**（`src/shared/inc/lxinitshared.h`）：
- `LxMiniInitMessageLaunchInit`：挂载 VHD + 启动新分发版
- `LxMiniInitMessageMount`：挂载磁盘到 `/mnt/wsl`（`wsl --mount`）
- `LxMiniInitMessageImport` / `LxMiniInitMessageExport`：导入/导出分发版
- `EJECT_VHD_MESSAGE`：弹出磁盘

**init 命令通道关键消息**（`src/shared/inc/lxinitshared.h`）：
- `LxInitMessageInitialize`：配置分发版
- `LxInitMessageCreateSession`：创建 session leader
- `LxInitMessageTerminateInstance`：终止分发版
- `LxInitMessageRemountDrvfs`：动态切换 drvfs 命名空间

### 2.2 Linux 侧核心进程

| 进程 | 职责 | 启动方式 | 源码位置 |
|---|---|---|---|
| `mini_init` | WSL2 VM 顶层进程：挂载 /proc/sys/dev、配置日志/tty、连接 wslservice 两条 hvsocket 通道、启动 gns、维护 VM（内存回收/调试 shell/IO 同步/文件系统扩容/磁盘格式化） | 内核启动完成后执行 `/init` | `src/linux/init/mini_init` |
| `init` | 分发版初始化：挂载 /proc/sys/dev、配置 cgroups、注册 binfmt（interop）、解析 /etc/wsl.conf、启动 systemd、挂载 drvfs、配置 wslg；通过 `argv[0]` 多路分发（`/init` 或 `/mount.drvfs`） | mini_init 发送 `LxMiniInitMessageLaunchInit` 后启动，每分发版独立 mount/pid/UTS namespace | `src/linux/init/init.cpp` |
| `plan9` | Plan9 文件服务器：通过 hvsocket（WSL2）或 unix socket（WSL1）向 Windows 暴露分发版文件系统，支撑 `\\wsl$` 和 `\\wsl.localhost` | init 启动 | `src/linux/init/plan9.cpp` |
| `gns` | Guest Network Service：通过独立 hvsocket 通道接收 wslservice 网络配置（接口 IP、路由、DNS、MTU）；启用 DNS 隧道时还负责响应 DNS 请求 | mini_init 启动 | `src/linux/init/GnsEngine.cpp` + `src/windows/service/exe/GnsChannel.cpp` |
| `relay` | 中继用户进程 IO：创建多个 hvsocket 通道（stdin/stdout/stderr/终端尺寸/退出通知），fork() 后父进程负责中继，子进程 exec() 用户进程 | session leader 收到 `LxInitMessageCreateProcessUtilityVm` 后创建 | 技术文档 relay.md |
| `session leader` | 会话首进程，负责创建用户进程上下文，relay 的父进程 | init 收到 `LxInitMessageCreateSession` 后创建 | 技术文档 session-leader.md |

### 2.3 文件系统互操作

**Windows → Linux 访问**（`\\wsl.localhost\<distro>` 或 `\\wsl$\<distro>`）：
- `p9rdr.sys`（Windows 重定向驱动）注册两个 UNC 路径前缀
- 路径被访问时 → `p9rdr.sys` 通过 COM 调用 `wslservice.exe` 启动对应分发版 → 连接其 plan9 服务器（WSL2 走 hvsocket，WSL1 走 unix socket）→ 文件可被 Windows 访问
- plan9 服务器由 `init` 在每个分发版中创建

**Linux → Windows 访问**（`/mnt/c` 等）：
- **DrvFs 机制**，挂载点默认位于 `/mnt`，指向 Windows 驱动器根目录
- 手动挂载：`mount -t drvfs C: /tmp/my-mount-point`
- 内部由 `/usr/sbin/mount.drvfs`（符号链接到 `/init`）处理；`/init` 启动时检查 `argv[0]`，若为 `mount.drvfs` 则运行 `MountDrvfsEntry()`（见 `src/linux/init/drvfs.cpp`）
- 根据配置可挂载为：`drvfs`（WSL1）/ `plan9` / `virtio-plan9` / `virtiofs`（取决于 `.wslconfig`）

**提权 vs 非提权双命名空间**（WSL2 关键安全机制）：
- WSL 在分发版内区分提权（管理员级）和非提权（用户级）Linux 进程
- 实现方式：维护**两套独立 mount namespace**，分别提供提权/非提权访问 Windows 驱动器
- 分发版创建时，wslservice 通过 `LX_INIT_CONFIGURATION_INFORMATION` 消息告知创建者的提权状态，init 据此挂载对应版本的 plan9 服务器
- 首次在未挂载的命名空间创建进程时，wslservice 发送 `LxInitMessageRemountDrvfs` 给 init，触发另一套命名空间挂载
- 源码：`src/windows/service/exe/WslCoreInstance.cpp` + `src/linux/drvfs.cpp`

### 2.4 WSL Container API（WSLC）— 重点

> **状态**：当前为 **preview**，正式 GA 计划在 **2026 年秋季**。preview 期间可能有不兼容变更，仅用于可行性评估，不要部署到生产环境。
> **官方文档**：[wsl.dev/api-reference](https://wsl.dev/api-reference/) | [learn.microsoft.com 容器功能](https://learn.microsoft.com/zh-cn/windows/wsl/wsl-container)

#### 2.4.1 三语言投影（官方确认）

同一套底层能力通过三种语言投影暴露，统一遵循 **Session → Container → Process** 三层模型：

| 语言 | 命名空间 / 头文件 | NuGet / 库 | 参考文档 |
|---|---|---|---|
| C | `wslcsdk.h` | `wslcsdk.lib` / `wslcsdk.dll` | [wsl.dev/api-reference/c](https://wsl.dev/api-reference/c/) |
| C# | `Microsoft.WSL.Containers` | `Microsoft.WSL.Containers`（NuGet 包） | [wsl.dev/api-reference/csharp](https://wsl.dev/api-reference/csharp/) |
| C++ | `Microsoft::WSL::Containers`（C++/WinRT 投影） | `winrt/Microsoft.WSL.Containers.h` | [wsl.dev/api-reference/cpp](https://wsl.dev/api-reference/cpp/) |

C# 投影采用**四层对象模型**（比三层多一个服务入口）：

| 对象 | 职责 |
|---|---|
| `WslcService` | 服务级静态入口：检查/安装所需 WSL 组件、查询服务版本 |
| `Session` | WSL 提供支持的容器主机：管理镜像（pull/import/load/push/tag/delete）、创建容器 |
| `Container` | 会话中创建的容器：start/stop/inspect/delete、运行其他进程 |
| `Process` | 容器内 Linux 进程：读 stdout/stderr、写 stdin、发送信号、通过事件观察退出码 |

典型流程：`WslcService.GetMissingComponents()` → `new Session(settings); session.Start()` → `session.PullImageAsync()` → `session.CreateContainer(settings)` → `container.Start()` → 交互 `container.InitProcess` → `container.Stop/Delete` → `session.Terminate()`。

#### 2.4.2 C API 核心 API 清单

详见 `src/windows/WslcSDK/wslcsdk.h` 与 [wsl.dev/api-reference/c](https://wsl.dev/api-reference/c/)：

```c
// Install & Version
WslcGetMissingComponents()   // 检查缺失的 WSL 组件
WslcGetVersion()             // 查询 WSL 版本

// Session 层
WslcInitSessionSettings()    // 初始化会话设置（名称、存储路径）
WslcSetSessionSettingsCpuCount() / WslcSetSessionSettingsMemory()  // 自定义资源
WslcCreateSession()          // 创建会话
WslcTerminateSession()       // 终止会话
WslcReleaseSession()         // 释放会话句柄

// Container 层
WslcInitContainerSettings()  // 初始化容器设置
WslcSetContainerSettingsName() / WslcSetContainerSettingsInitProcess()
WslcCreateContainer()        // 创建容器
WslcStartContainer()         // 启动容器（WSLC_CONTAINER_START_FLAG_*）
WslcStopContainer()          // 停止容器（支持信号 + 超时）
WslcDeleteContainer()        // 删除容器（WSLC_DELETE_CONTAINER_FLAG_*）
WslcGetContainerState()      // 查询容器状态
WslcGetContainerInitProcess() // 获取 init 进程
WslcReleaseContainer()       // 释放容器句柄

// Process 层
WslcInitProcessSettings()    // 初始化进程设置
WslcSetProcessSettingsCmdLine()
WslcCreateContainerProcess() // 在容器内创建进程
WslcGetProcessIOHandle()     // 获取 stdin/stdout/stderr 句柄
WslcGetProcessExitEvent()    // 获取退出事件句柄
WslcGetProcessExitCode()     // 获取退出码
WslcSignalProcess()          // 向进程发送信号
WslcReleaseProcess()         // 释放进程句柄

// Image 管理
WslcPullSessionImage()       // 拉取镜像（WslcPullImageOptions）
WslcListSessionImages()      // 列出镜像
WslcPushSessionImage()       // 推送镜像

// Storage（VHD-backed）
// 见 wsl.dev/api-reference/c/storage-apis/
```

#### 2.4.3 官方端到端示例（C，源自 wsl.dev）

完整 7 步生命周期（节选自 [wsl.dev/api-reference/c/end-to-end-example](https://wsl.dev/api-reference/c/end-to-end-example/)）：

```c
#include <winsock2.h>
#include <windows.h>
#include <stdio.h>
#include <objbase.h>
#include <filesystem>
#include "wslcsdk.h"

#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "wslcsdk.lib")

int main() {
    // 0. 初始化 COM + 检查 WSL 组件
    CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    WslcComponentFlags missing = WSLC_COMPONENT_FLAG_NONE;
    HRESULT hr = WslcGetMissingComponents(&missing);
    if (FAILED(hr) || missing != WSLC_COMPONENT_FLAG_NONE) {
        printf("WSL components are missing. Run: wsl --install\n");
        return 1;
    }

    // 1. 创建会话（可自定义 CPU/内存）
    WslcSessionSettings sessionSettings;
    std::filesystem::path storagePath = std::filesystem::current_path();
    WslcInitSessionSettings(L"MyApp", storagePath.c_str(), &sessionSettings);
    WslcSetSessionSettingsCpuCount(&sessionSettings, 4);
    WslcSetSessionSettingsMemory(&sessionSettings, 4096);

    WslcSession session = nullptr;
    PWSTR error = nullptr;
    hr = WslcCreateSession(&sessionSettings, &session, &error);
    if (FAILED(hr)) { /* 错误处理 */ return 1; }

    // 2. 拉取镜像
    WslcPullImageOptions pullOpts = {};
    pullOpts.uri = "docker.io/library/alpine:latest";
    WslcPullSessionImage(session, &pullOpts, &error);

    // 3. 配置 init 进程
    WslcProcessSettings initProcSettings;
    WslcInitProcessSettings(&initProcSettings);
    PCSTR argv[] = { "/bin/echo", "Hello from WSL Container!" };
    WslcSetProcessSettingsCmdLine(&initProcSettings, argv, 2);

    // 4. 配置并创建容器
    WslcContainerSettings containerSettings;
    WslcInitContainerSettings("alpine:latest", &containerSettings);
    WslcSetContainerSettingsName(&containerSettings, "hello-container");
    WslcSetContainerSettingsInitProcess(&containerSettings, &initProcSettings);

    WslcContainer container = nullptr;
    WslcCreateContainer(session, &containerSettings, &container, &error);

    // 5. 启动容器
    WslcStartContainer(container, WSLC_CONTAINER_START_FLAG_NONE, &error);

    // 6. 等待 init 进程退出
    WslcProcess initProc = nullptr;
    WslcGetContainerInitProcess(container, &initProc);
    HANDLE exitEvent = nullptr;
    WslcGetProcessExitEvent(initProc, &exitEvent);
    WaitForSingleObject(exitEvent, 30000);  // 30 秒超时
    INT32 exitCode = 0;
    WslcGetProcessExitCode(initProc, &exitCode);
    printf("Process exited with code: %d\n", exitCode);

    // 7. 清理（按序释放）
    WslcStopContainer(container, WSLC_SIGNAL_SIGTERM, 10, nullptr);
    WslcDeleteContainer(container, WSLC_DELETE_CONTAINER_FLAG_NONE, nullptr);
    WslcReleaseContainer(container);
    WslcTerminateSession(session);
    WslcReleaseSession(session);
    CoUninitialize();
    return 0;
}
```

#### 2.4.4 C# 投影示例（源自 learn.microsoft.com）

通过 NuGet 安装：`dotnet add package Microsoft.WSL.Containers`

```csharp
using Microsoft.WSL.Containers;

// 检查组件
ComponentFlags missing = WslcService.GetMissingComponents();
if (missing != ComponentFlags.None) {
    Console.WriteLine($"WSL components are missing ({missing}). Run: wsl --install");
    return;
}

// 创建会话
var sessionSettings = new SessionSettings("MyApp", @"C:\WslcData") {
    CpuCount = 4,
    MemoryMB = 4096
};
var session = new Session(sessionSettings);
session.Start();

// 拉取镜像（带进度回调）
var pull = session.PullImageAsync(new PullImageOptions("docker.io/library/alpine:latest"));
pull.Progress = (op, progress) =>
    Console.WriteLine($"Pull: {progress.Status} {progress.CurrentBytes}/{progress.TotalBytes}");
await pull;

// 创建容器并订阅输出
var initProcess = new ProcessSettings {
    CmdLine = new[] { "/bin/echo", "Hello from WSL Container!" },
    OutputMode = ProcessOutputMode.Event
};
var containerSettings = new ContainerSettings("alpine:latest") {
    Name = "hello-container",
    InitProcess = initProcess
};
var container = session.CreateContainer(containerSettings);
container.InitProcess.OutputReceived += data =>
    Console.Write(Encoding.UTF8.GetString(data));
container.Start();

// 清理
container.Stop(Signal.SIGTERM, TimeSpan.FromSeconds(10));
container.Delete(DeleteContainerFlags.None);
session.Terminate();
```

#### 2.4.5 wslc CLI 命令体系

类 Docker CLI，详见 `src/windows/wslc/commands/` 与 [learn.microsoft.com 容器功能](https://learn.microsoft.com/zh-cn/windows/wsl/wsl-container)：

```bash
# 运行容器
wslc run --rm -it ubuntu:latest bash -c "echo Hello world from WSL container!"

# 镜像管理（list 是主名，ls 是别名，root 下可用 images）
wslc image list                    # 或 wslc image ls，或直接 wslc images

# 运行 Web 服务器示例
wslc run -it --rm -d -p 8080:80 --name web nginx
curl localhost:8080
wslc container list                # 或 wslc container ls，或 wslc container ps
wslc container stop web
```

完整命令子体系（主名 / 别名）：
- `container`：run / create / start / stop / kill / exec / attach / inspect / list（ls, ps）/ logs / stats / prune / remove（delete, rm）
- `image`：pull / push / build / import / load / save / tag / inspect / list（ls）/ prune / remove（delete, rm）
  - root 下：`images`（≡ image list）、`rmi`（≡ image remove）
- `network`：create / inspect / list（ls）/ prune / remove（delete, rm）
- `volume`：create / inspect / list（ls）/ prune / remove（delete, rm）
- `session`：enter / list（无别名）/ run / shell / terminate
- `registry`：login / logout
- `system` / `version` / `settings`

> **CLI 命令名完整核实表**：详见 [wsl-cli-and-architecture-wiki.md §二](wsl-cli-and-architecture-wiki.md)

#### 2.4.6 错误码表（源自 wsl.dev/api-reference/c/error-codes）

所有 `WSLC_E_*` 错误码基于 `FACILITY_ITF`，基址 `WSLC_E_BASE = 0x0600`：

| 符号 | Hex 值 | 含义 |
|---|---|---|
| `WSLC_E_IMAGE_NOT_FOUND` | 0x80040601 | 镜像未找到 |
| `WSLC_E_CONTAINER_PREFIX_AMBIGUOUS` | 0x80040602 | 容器名前缀歧义 |
| `WSLC_E_CONTAINER_NOT_FOUND` | 0x80040603 | 容器未找到 |
| `WSLC_E_VOLUME_NOT_FOUND` | 0x80040604 | 卷未找到 |
| `WSLC_E_CONTAINER_NOT_RUNNING` | 0x80040605 | 容器未运行 |
| `WSLC_E_CONTAINER_IS_RUNNING` | 0x80040606 | 容器正在运行 |
| `WSLC_E_SESSION_RESERVED` | 0x80040607 | 会话名已占用 |
| `WSLC_E_INVALID_SESSION_NAME` | 0x80040608 | 会话名非法 |
| `WSLC_E_NETWORK_NOT_FOUND` | 0x80040609 | 网络未找到 |
| `WSLC_E_WU_SEARCH_FAILED` | 0x8004060A | Windows Update 搜索失败（镜像拉取） |
| `WSLC_E_SDK_UPDATE_NEEDED` | 0x8004060B | SDK 版本过旧需更新 |
| `WSLC_E_CONTAINER_DISABLED` | 0x8004060C | 容器功能被禁用 |
| `WSLC_E_REGISTRY_BLOCKED_BY_POLICY` | 0x8004060D | 注册表被组策略阻止 |
| `WSLC_E_VOLUME_NOT_AVAILABLE` | 0x8004060E | 卷不可用 |
| `WSLC_E_SESSION_NOT_FOUND` | 0x8004060F | 会话未找到 |

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

# 2. 列出镜像（list 是主名，ls 是别名，两者等价；root 下也可用 images）
wslc image list     # 或 wslc image ls，或直接 wslc images

# 3. 运行容器
wslc container run -it --name myapp ubuntu:24.04 /bin/bash

# 4. 在运行中的容器内执行命令
wslc container exec myapp apt-get update

# 5. 查看容器列表（list 是主名，ls/ps 是别名，三者等价）
wslc container list  # 或 wslc container ls，或 wslc container ps

# 6. 查看容器日志
wslc container logs myapp

# 7. 停止并删除（remove 是主名，rm/delete 是别名）
wslc container stop myapp
wslc container remove myapp  # 或 wslc container rm
```

**验证点**：能完成 pull→run→exec→list→logs→stop→remove 全生命周期操作。

> **CLI 命令名说明**：经源码核实（详见 [wsl-cli-and-architecture-wiki.md §1.1](wsl-cli-and-architecture-wiki.md)），`list`/`remove` 是所有 list/remove 类命令的**主名**，`ls`/`ps`/`rm`/`delete` 是其**别名**，所有写法等价合法。先前版本中"官方 CLI 用 ls/ps 而非 list"的论断是误判，已修正。

### 实操 4：调用 WSLC SDK API（C 示例）

**目标**：理解 Session→Container→Process 编程模型，跑通官方端到端示例。

**步骤**：
1. 包含 `src/windows/WslcSDK/wslcsdk.h`，链接 `wslcsdk.lib` 与 `ole32.lib`（COM）
2. 以 [wsl.dev 官方端到端示例](https://wsl.dev/api-reference/c/end-to-end-example/) 为模板，实现 7 步生命周期（详见 §2.4.3）：
   - **0**：`CoInitializeEx` 初始化 COM + `WslcGetMissingComponents` 检查组件
   - **1**：`WslcInitSessionSettings` + `WslcSetSessionSettingsCpuCount/Memory` + `WslcCreateSession`
   - **2**：`WslcPullSessionImage`（使用 `WslcPullImageOptions`，uri 形如 `docker.io/library/alpine:latest`）
   - **3**：`WslcInitProcessSettings` + `WslcSetProcessSettingsCmdLine`（如 `/bin/echo`）
   - **4**：`WslcInitContainerSettings` + `WslcSetContainerSettingsName/InitProcess` + `WslcCreateContainer`
   - **5**：`WslcStartContainer`（flags = `WSLC_CONTAINER_START_FLAG_NONE`）
   - **6**：`WslcGetContainerInitProcess` + `WslcGetProcessExitEvent` + `WaitForSingleObject` + `WslcGetProcessExitCode`
   - **7**：按序释放 `Stop → Delete → Release → Terminate → Release → CoUninitialize`
3. 对照 §2.4.6 错误码表处理 `WSLC_E_*`（如 `WSLC_E_IMAGE_NOT_FOUND` 0x80040601、`WSLC_E_CONTAINER_NOT_RUNNING` 0x80040605）
4. 错误字符串通过 `PWSTR error` 输出参数获取，用 `CoTaskMemFree(error)` 释放

**进阶练习**：
- 改写为 C# 版本：`dotnet add package Microsoft.WSL.Containers`，使用 `PullImageAsync` 的进度回调与 `InitProcess.OutputReceived` 事件订阅（参考 §2.4.4）
- 扩展为交互式进程：配置 `ProcessOutputMode`，向 stdin 写入数据

**验证点**：程序能完成"组件检查→会话创建→镜像拉取→容器创建→启动→等待 init 进程退出并打印退出码→清理"全流程。

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

### 5.2 外部相关仓库与官方文档

**GitHub 仓库**：
- [microsoft/WSL2-Linux-Kernel](https://github.com/microsoft/WSL2-Linux-Kernel) - WSL 使用的 Linux 内核
- [microsoft/WSLg](https://github.com/microsoft/wslg) - Linux GUI 应用支持
- [microsoftdocs/wsl](https://github.com/microsoftdocs/wsl) - WSL 用户文档
- [WSLC API 示例](https://aka.ms/wslc-samples) - 官方端到端可运行示例（涵盖端口映射、卷挂载、GPU 访问、交互式 stdin/stdout）

**官方在线文档**：
- [wsl.dev](https://wsl.dev/) - WSL 开发者文档（开源文档，MkDocs Material）
  - [技术文档](https://wsl.dev/technical-documentation/) - 组件架构详解（mini_init/init/plan9/gns/drvfs/relay/session-leader/wslservice/boot-process/interop/systemd）
  - [API 参考](https://wsl.dev/api-reference/) - WSL Container API 三语言投影
    - [C API](https://wsl.dev/api-reference/c/)（结构/回调/Session/Container/Process/Image/Storage/Install/枚举/错误码/端到端示例）
    - [C# API](https://wsl.dev/api-reference/csharp/)（Data/Settings/Core/Service 类、委托事件、枚举）
    - [C++ API](https://wsl.dev/api-reference/cpp/)（C++/WinRT 投影）
  - [dev-loop](https://wsl.dev/dev-loop/) - 构建/测试/部署全流程
- [learn.microsoft.com/windows/wsl](https://learn.microsoft.com/zh-cn/windows/wsl/) - WSL 用户文档（安装、配置、容器功能）
  - [WSL 容器功能](https://learn.microsoft.com/zh-cn/windows/wsl/wsl-container) - wslc.exe CLI 与容器 API 概览（含 C#/C++ 代码片段）
  - [wsl-config](https://learn.microsoft.com/windows/wsl/wsl-config) - .wslconfig 与 /etc/wsl.conf 配置参考

### 5.3 学习产出物清单

- [ ] 个人版 WSL 架构图（含 mini_init 双 hvsocket 通道、relay fork-exec 模型）
- [ ] 5 个实操练习记录与截图
- [ ] 10 篇学习笔记（按 4.1 结构）
- [ ] FAQ 文档
- [ ] 复盘报告
- [ ] C / C# / C++ 三语言投影对照表（同一场景的等价写法）

---

> **备注**：本学习计划基于 WSL 仓库源码与官方在线文档（wsl.dev + learn.microsoft.com）制定，建议结合实际动手操作加深理解。
> WSL Container API 目前处于 **preview** 阶段，正式 GA 计划在 **2026 年秋季**。preview 期间 API 可能有 breaking changes，仅用于可行性评估。
> **本计划已于 2026-07-01 整合 wsl.dev 与 learn.microsoft.com 官方文档内容**：补充了 mini_init 双 hvsocket 通道、relay fork-exec 模型、drvfs 双命名空间机制、三语言投影（C/C#/C++ WinRT）、C# 四层对象模型、官方端到端示例、完整错误码表，并修正了 wslc CLI 命令（`ls`/`ps` 而非 `list`）。
