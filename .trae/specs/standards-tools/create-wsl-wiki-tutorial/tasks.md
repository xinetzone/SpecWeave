# WSL Wiki 教程 - 实施计划

## 任务总览
本项目分为三个阶段：目录骨架创建 → 核心章节编写 → 收尾验证。共 12 个有序任务。

---

## [/] Task 1: 创建 wsl-wiki/ 目录骨架与 README.md 导航入口
- **Priority**: 高
- **Depends On**: 无
- **Description**:
  - 创建目录 `.agents/docs/knowledge/learning/08-systems-infrastructure/wsl-wiki/`
  - 编写 README.md 导航入口文件
  - README 包含：教程概述、适用读者、章节列表（12-15章）、阅读路径建议、与现有两份WSL文档的关联
  - README 中关联 wsl-learning-plan.md 和 wsl-cli-and-architecture-wiki.md 作为扩展阅读
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - 目录创建成功
  - README.md 存在且包含完整章节列表
  - 对现有文档的链接使用正确相对路径

---

## Task 2: 编写第 1-3 章（概述与安装、整体架构、快速开始）
- **Priority**: 高
- **Depends On**: Task 1
- **Description**:
  - `00-overview.md`: WSL 是什么、WSL1 vs WSL2 对比、核心特性、适用场景、版本说明（含WSLC preview标注）
  - `01-installation.md`: 系统要求、安装步骤（wsl --install）、发行版管理、升级WSL2、常见安装问题
  - `02-quickstart.md`: 5分钟快速上手、基本命令（wsl/list/run/shutdown）、第一个Linux程序、互操作初体验
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - 三个文件均包含 YAML frontmatter
  - 每章末尾有双向导航链接
  - 包含安装命令的代码块（标注powershell/bash）
  - WSL1/WSL2 对比表格清晰

---

## Task 3: 编写 CLI 完整参考章节（整合现有CLI参考手册）
- **Priority**: 高
- **Depends On**: Task 1
- **Description**:
  - `03-cli-reference.md`: 整合 wsl-cli-and-architecture-wiki.md 内容
  - wsl.exe 命令树完整参考（install/list/run/shutdown/import/export/mount/debug-shell 等）
  - wslc.exe 容器 CLI 完整命令树（container/image/network/volume/session/registry/system/version）
  - 命令主名与别名说明（list是主名，ls/ps是别名）
  - container run 关键参数表
  - CLI 架构四层模型（core/arguments/commands/services）+ 命令执行流程 Mermaid 图
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-7
- **Test Requirements**:
  - 命令树完整覆盖 wsl.exe 和 wslc.exe
  - 包含 CLI 执行流程 Mermaid 图
  - 主名/别名说明正确（源码核实结论）
  - 代码块标注语言类型
  - 每章末尾导航链接完整

---

## Task 4: 编写 Linux 侧核心进程与架构章节（含Mermaid架构图）
- **Priority**: 高
- **Depends On**: Task 2
- **Description**:
  - `04-architecture.md`: WSL2 整体架构
  - Windows 侧组件：wsl.exe、wslservice.exe（COM接口ILxssUserSession）、wslg.exe、wslconfig.exe、wslrelay.exe、wslhost.exe、wslapi.dll
  - Linux 侧五大核心进程详解：mini_init（VM顶层进程）、init（分发版初始化）、plan9（文件服务器）、gns（网络配置服务）、relay（IO中继）、session leader
  - 核心通信机制：COM（Windows侧）+ hvsocket（跨侧）
  - 整体组件架构 Mermaid 图（源自官方wsl.dev架构图）
  - hvsocket 5通道拓扑 Mermaid 图（含wsl.exe→relay直接通道）
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-7
- **Test Requirements**:
  - 包含 2 张 Mermaid 图（整体架构 + hvsocket拓扑）
  - 五大进程职责说明完整
  - 5条hvsocket通道用途标注清晰
  - 标注 wsl.exe→relay 直接IO中继通道（关键发现）
  - 引用源码文件锚点（如src/linux/init/mini_init）

---

## Task 5: 编写文件系统互操作章节（DrvFs/Plan9/双命名空间）
- **Priority**: 中
- **Depends On**: Task 4
- **Description**:
  - `05-filesystem-interop.md`: Windows↔Linux 文件系统互操作
  - Windows 访问 Linux 文件：`\\wsl.localhost\<distro>` / `\\wsl$` 机制（p9rdr.sys驱动 + plan9服务器）
  - Linux 访问 Windows 文件：DrvFs 机制（/mnt/c/ 等挂载点、mount -t drvfs手动挂载、/init多路分发argv[0]判断）
  - 提权/非提权双mount命名空间机制（WSL2关键安全设计）
  - 文件权限映射、大小写敏感、性能建议
  - DrvFs 挂载配置选项（/etc/wsl.conf [automount]）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - 双向访问机制说明完整
  - 双命名空间安全机制解释清晰
  - 包含手动挂载命令示例
  - 引用源码位置（src/linux/init/drvfs.cpp）

---

## Task 6: 编写 WSL Container API 章节（C/C#/C++三语言投影+代码示例）
- **Priority**: 高
- **Depends On**: Task 3, Task 4
- **Description**:
  - `06-wslc-api.md`: WSL Container API（WSLC）
  - Preview 状态说明 + GA 计划提示
  - Session→Container→Process 三层模型（C#多一层WslcService入口）
  - 三语言投影对照表：C（wslcsdk.h/lib/dll）、C#（Microsoft.WSL.Containers NuGet）、C++（Microsoft::WSL::Containers WinRT投影）
  - C API 核心清单（安装/版本/Session/Container/Process/Image/Storage）
  - **完整可运行代码示例**：
    - C 端到端示例（7步生命周期，源自wsl.dev官方示例）
    - C# 示例（异步PullImageAsync进度回调、OutputReceived事件订阅）
    - C++/WinRT 投影示例
  - WSLC_E_* 错误码表
  - WSLC API 对象模型 Mermaid 图
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-7, AC-8
- **Test Requirements**:
  - 包含 WSLC 对象模型 Mermaid 图（累计≥3张Mermaid）
  - C/C#/C++ 三语言代码示例完整可运行
  - 代码示例标注前提条件（链接库、NuGet包）
  - 错误码表包含常见错误值
  - 注明 preview 状态与注意事项

---

## Task 7: 编写网络、配置管理、systemd章节
- **Priority**: 中
- **Depends On**: Task 4
- **Description**:
  - `07-networking.md`: 网络互操作
    - NAT 模式 vs Mirrored 模式对比
    - DNS 隧道机制（dnsTunneling=true）
    - GNS（Guest Network Service）工作原理
    - 端口转发、防火墙配置
    - 网络诊断命令
  - `08-configuration.md`: 配置管理
    - `%USERPROFILE%/.wslconfig` 全局配置（[wsl2]段：memory/processors/networkingMode/dnsTunneling等）
    - `/etc/wsl.conf` 单分发版配置（[boot]/[automount]/[interop]/[network]/[user]）
    - 组策略配置（intune/WSL.admx，AllowWSL/AllowWSLContainer等）
    - wsl --manage 命令
  - `09-systemd.md`: systemd 集成
    - 启用方法（[boot] systemd=true）
    - systemd fork启动流程（init fork→父进程启动systemd(PID1)→子进程继续WSL配置）
    - systemd用户会话同步（login -f <user>）
    - systemd配置保护（binfmt/X11 socket保护）
    - 常见systemd问题排查
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - 网络模式对比表格清晰
  - 配置文件选项分全局/分发版列出
  - systemd fork流程说明正确
  - 包含配置示例代码块

---

## Task 8: 编写调试诊断、开发环境搭建章节
- **Priority**: 中
- **Depends On**: Task 4, Task 7
- **Description**:
  - `10-debugging-diagnostics.md`: 调试与诊断
    - 日志收集：collect-wsl-logs.ps1（-LogProfile networking、-Dump）
    - ETL追踪：wpr -start wsl.wprp、WPA查看
    - 关键Provider：Microsoft.Windows.Lxss.Manager等
    - Windows侧调试：WinDbg附加wslservice.exe、符号路径
    - Linux侧调试：wsl --debug-shell进入根命名空间、gdb附加进程
    - 崩溃转储：LocalDumps注册表配置
    - 诊断脚本：diagnostics/networking.sh等
  - `11-development-env.md`: WSL开发环境搭建最佳实践
    - 开发工具配置（VS Code Remote - WSL、Visual Studio）
    - 跨编译环境（CMake + LLVM/Clang，target <arch>-unknown-linux-musl）
    - Git配置换行符问题
    - Docker集成、GPU计算支持
    - 性能优化建议（文件IO、内存限制）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - 日志收集命令完整（PowerShell代码块）
  - 调试步骤说明清晰
  - 开发环境配置有实操命令
  - 引用诊断脚本路径

---

## Task 9: 编写最佳实践、常见问题FAQ章节
- **Priority**: 中
- **Depends On**: Task 5, Task 7, Task 8
- **Description**:
  - `12-best-practices.md`: WSL使用最佳实践
    - 文件系统性能：避免跨文件系统频繁IO、使用\\wsl.localhost访问Linux文件
    - 内存管理：.wslconfig配置memory限制、自动内存回收
    - 网络配置：Mirrored模式选择、DNS隧道适用场景
    - 安全实践：提权/非提权隔离、不要禁用双命名空间
    - 开发工作流：代码放Linux文件系统、Git配置、VS Code工作流
    - Container API使用建议（preview注意事项）
  - `13-faq-troubleshooting.md`: 常见问题与故障排查
    - 安装失败：虚拟化未启用、组件缺失（WslcGetMissingComponents）
    - 网络不通：NAT/Mirrored切换、防火墙、收集networking日志
    - 文件访问慢：跨文件系统IO问题
    - 内存占用高：memory配置
    - systemd不启动：检查/etc/wsl.conf
    - 容器无法启动：组策略AllowWSLContainer、WSLC_E_*错误码
    - 镜像拉取失败：WSLC_E_WU_SEARCH_FAILED、代理配置
    - 崩溃无堆栈：LocalDumps配置、WinDbg附加
    - 结构化故障排查流程（问题复现→日志收集→初步定位）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - 覆盖学习计划中列出的8类常见问题
  - 每个问题有现象→原因→解决方案结构
  - 最佳实践可操作（具体配置项、命令）
  - 故障排查流程清晰

---

## Task 10: 编写术语表、参考资料与交叉引用
- **Priority**: 低
- **Depends On**: Task 2-9 全部完成
- **Description**:
  - `14-glossary.md`: 术语表
    - 统一术语定义：WSL、WSL2、hvsocket、COM、DrvFs、Plan9、mini_init、init、plan9、gns、relay、WSLC、VHD、interop、binfmt、namespace、cgroup、systemd、NAT、Mirrored、DNS隧道、ETL、WinDbg
    - 每个术语给出中英文对照和一句话解释
  - `15-resources.md`: 参考资料与学习路径
    - 官方资源：wsl.dev、learn.microsoft.com/windows/wsl、WSL开源仓库、WSL2-Linux-Kernel、WSLg
    - 源码文件索引（关键文件路径+作用）
    - 推荐4周学习路径（整合自wsl-learning-plan.md）
    - 项目内交叉引用：wsl-learning-plan.md、wsl-cli-and-architecture-wiki.md
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - 术语表覆盖所有核心术语（≥20个）
  - 参考资料链接有效（公开URL）
  - 学习路径清晰可执行
  - 项目内交叉引用使用相对路径

---

## Task 11: 更新 08-systems-infrastructure/README.md 导航索引
- **Priority**: 低
- **Depends On**: Task 1-10 全部完成
- **Description**:
  - 读取 `.agents/docs/knowledge/learning/08-systems-infrastructure/README.md`
  - 在索引中添加 wsl-wiki/ 条目
  - 添加简要说明和相对路径链接
  - 保持现有文档索引格式
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - README.md 中包含 wsl-wiki/ 链接
  - 链接使用相对路径
  - 不破坏现有其他条目

---

## Task 12: 格式合规性检查与链接修复
- **Priority**: 高
- **Depends On**: Task 1-11 全部完成
- **Description**:
  - 检查所有 13+ 个 md 文件（README + 12-15章）的 YAML frontmatter 完整性
  - 检查并修复所有内部链接为相对路径
  - 检查无 file:/// 绝对路径引用
  - 验证每章末尾双向导航链接正确（上一章/下一章/返回目录）
  - 验证所有 Mermaid 图表语法正确
  - 验证所有代码块标注语言类型
  - 验证三语言代码示例完整
  - 检查文件行数不超过500行限制
  - 运行 link-check-cmd 检查链接有效性
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - 所有文件通过格式检查
  - 无死链、无绝对路径
  - Mermaid图表可渲染
  - 文件行数合规

---

## 任务依赖关系
```
Task 1（目录骨架）
├─→ Task 2（1-3章基础）
│   ├─→ Task 4（架构章节）
│   │   ├─→ Task 5（文件系统）
│   │   ├─→ Task 7（网络/配置/systemd）
│   │   │   └─→ Task 8（调试/开发环境）
│   │   │       └─→ Task 9（最佳实践/FAQ）
│   │   └─→ Task 3（CLI参考，可以与Task 4并行开始）
│   └─→ Task 3（CLI参考）
│       └─→ Task 6（WSLC API，依赖Task 3+4）
└─────────────────────────────────────┘
                                      ↓
                        Task 10（术语表/资源，依赖2-9）
                                      ↓
                        Task 11（更新索引，依赖1-10）
                                      ↓
                        Task 12（格式检查，依赖1-11）
```

## 并行执行说明
- Task 3（CLI）和 Task 4（架构）可在 Task 2 完成后并行执行
- Task 5、Task 7 可在 Task 4 完成后并行执行
- Task 6 需等待 Task 3 和 Task 4 都完成后开始
