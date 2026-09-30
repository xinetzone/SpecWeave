# 03 安装路径全景与选型：五条路径与决策表

> 文档站 1_3 板块有 21 篇安装文档，覆盖 x86 物理机、虚拟机、WSL、ARM 开发板、RISC-V 开发板与 qemu。本文不逐篇复述，而是给出选型决策、每条路径的官方文档要点与已知坑。

## 3.1 选型决策表

| 你的情况 | 推荐路径 | 成本 | 官方文档 |
|---|---|---|---|
| 只想快速体验命令行、Windows 主力机 | **WSL 最小镜像**（下载 336 MiB，gzip 压缩态，见下） | 最低，不动宿主；磁盘预留 1.3 GB+（本机实测） | 《openKylin-WSL版本安装》 |
| Windows 主力机且想体验**完整 UKUI 图形桌面会话** | **Desktop WSL 镜像**（xrdp 桌面预装，免装虚拟机）；仅零散 GUI 应用需求优先 WSLg 搭配最小镜像、不必下桌面镜像；需要完整隔离体验再选虚拟机 | 中：下载 6.14 GiB；磁盘预留 **跨盘 20 GiB 起步、同盘推荐 25～30 GiB**（手动解压排障路径需 ≥45 GiB；分层估算，未落机实测），详见[双镜像对照](../references/wsl-dual-image-selection.md) | 《openKylin-WSL版本安装》桌面分支 |
| 想体验完整 UKUI 桌面、愿意装虚拟机 | 虚拟机（Hyper-V / virt-manager / KVM） | 低 | 5 篇虚拟机指南 |
| 要长期日常使用、有空闲 x86 整机 | Live USB 物理安装 | 中 | 《3_openKylin安装指南》等 4 篇 |
| 使用苹果芯片/Intel Mac | Mac 安装指南 | 中 | 《2_安装指南（MacOS）》 |
| 有 ARM 开发板（树莓派/飞腾派/香橙派等） | ARM 板级镜像 | 中高 | 6 篇 ARM 文档 |
| 有 RISC-V 开发板（K1/LicheePi4A/Milk-V 等） | RISC-V 统一/板级镜像 | 高 | 7 篇 RISC-V 文档 |
| 无 RISC-V 硬件但想验证 RVA23 | qemu 模拟 | 中 | 《openKylin-RVA23版本使用指南》 |

## 3.2 WSL 路径（Windows）

**官方标准流程**（《openKylin-WSL版本安装》）：

1. 环境门槛：Windows 10 2004（内部版本 19041）+ 或 Windows 11；管理员 PowerShell；
2. `wsl --install` 与 `wsl --set-default-version 2`；
3. 从官网下载两个镜像之一：基础 `openKylin-3.0-wsl-amd64.wsl`、桌面 `openKylin-3.0-desktop-wsl-amd64.wsl`；
4. `wsl --import openKylin .\openKylin <镜像文件> --version 2` 导入；
5. `wsl -d openKylin` 启动，**预置用户名与密码均为 `openkylin`**；
6. 桌面版另需：启动后 `ip addr show eth0` 取内网 IPv4 → Windows 远程桌面连接 `<IP>:3390` → Session 选 **xorg**，账号密码同为 openkylin。WSL 重启后 IP 可能变。

> **体积预期（最小镜像，本机实测口径，S26）**：基础镜像下载文件约 336M，但它是 **gzip 压缩的 tar**（文件头 `1F 8B`），导入时 WSL 会解压为约 1.1G 量级的 VHD 虚拟磁盘，故磁盘预留应按 1.1G 以上而非 336M 规划；安装额外软件后 VHD 还会增长。336M 为 2026-09-29 时点 3.0 镜像的实测值，具体以官网下载页当时文件大小为准。

> **Desktop WSL 镜像（2026-09-30 远程核验，未落机实测，S27–S31）**：下载文件 `openKylin-3.0-desktop-wsl-amd64.wsl` 精确为 6,592,986,686 字节（**6.14 GiB**，官网展示"6.1G"），MD5 `df559de7155ef7c6fe088b2168035c5a`，同为 gzip tar rootfs（魔数 `1F 8B 08 00`），构建日期 2026-08-28。gzip 尾部 ISIZE 已过 4 GiB 回绕点（读数 98.5 MiB），解压 tar 真值落在 8.1～20.1 GiB 候选区间（最小镜像 3.36× 压缩比只提供方向性参考，现有证据不足以在候选间排序、不设点估）；按 VHD≈tar×1.17 推算，**导入后长期占用约 9.5～24 GiB，同盘标准导入峰值约 16～30 GiB，建议跨盘预留 ≥20 GiB 起步、同盘 25～30 GiB**（若走"先手动解压 tar 再导入"排障路径，tar 会额外落盘，需 ≥45～50 GiB；`wsl --import` 直接导入通常流式写入 VHD、不另落完整 tar，但桌面镜像未实测确认）；官方流程的发行版名为 `openKylin-desktop`（与最小镜像并存时名称必须不同）。精确对照表、分层占用矩阵、选型决策、安全红线与待实测验收清单见 [双 WSL 镜像对照与选型参考](../references/wsl-dual-image-selection.md)。

> **安全警告**：预置账号/密码 `openkylin/openkylin` 是公开弱口令，仅适用于本机体验——① 首次进入后应立即用 `passwd` 修改密码；② xrdp 的 3390 端口只用于本机/WSL 内网，**切勿**把该端口映射到公网；③ 不用时可 `wsl --shutdown openKylin` 停止发行版。

**官方 FAQ 仅覆盖两项**："WSL 2 内核未安装"（装 aka.ms/wsl2kernel 更新包）与远程桌面连接失败（查 xrdp 与 3390 端口）。

**本仓已补的实测内容（重要，官方文档未覆盖）**：

- `.wsl` 文件本质是 **gzip 压缩的 tar**（文件头 `1F 8B`），不是 APPX/ZIP；
- 低内存环境下导入可能报 `RegisterDistro/E_UNEXPECTED`（解压中途失败）或 `CreateVm/E_ABORT`；处置顺序：`wsl --shutdown` 释放 VM 内存 → 待空闲物理内存充裕再导入 → 必要时用 .NET GzipStream 流式解压为纯 tar 后再 import；
- 导入后 VHD 位于安装目录，稀疏 VHD（删除文件自动向宿主回收空间）需 `wsl --manage <发行版> --set-sparse true --allow-unsafe`，对含数据的现有 VHD 该开关被安全策略拦截，必须带 `--allow-unsafe`。

完整命令、4 次失败排障记录与验收步骤见同包实测文档：[openKylin 3.0 WSL 安装与稀疏 VHD 实操指南（Windows 10 实测）](../references/wsl-install-sparse-vhd-guide.md)（仅覆盖最小镜像）；两镜像精确对照、桌面镜像磁盘规划与实测清单见 [双 WSL 镜像对照与选型参考](../references/wsl-dual-image-selection.md)。

## 3.3 虚拟机路径（x86）

官方文档覆盖四种虚拟化环境：

| 文档 | 环境 | 适合 |
|---|---|---|
| 《5_Hyper-v&openKylin-x86虚拟机安装指南》 | Windows 自带 Hyper-V | Win10/11 专业版用户 |
| 《6_virt-manager&openKylin-x86虚拟机安装指南》 | Linux 上 virt-manager | Linux 主机用户 |
| 《使用KVM虚拟机》（1_4） | KVM | 深入配置 |
| 《04_openKylin 2.0 SP2虚拟机安装新手指南》 | 通用图文 | 第一次装虚拟机的新人 |
| 《1_虚拟化技术简介》 | 概念 | 了解虚拟化原理 |

通用要点：先在 BIOS/UEFI 确认 CPU 虚拟化已开启（FAQ 有"如何查看 CPU 是否支持虚拟化"条目）；镜像下载后校验 MD5；虚拟机网络默认 NAT 即可。

## 3.4 物理机路径（x86）

《3_openKylin安装指南》《4_openKylin系统安装指南》《1_安装过程简记》三篇内容互补，主线为：

1. 官网下载对应架构 ISO；
2. 制作 USB 引导盘（1_4 另有《U盘启动器_制作系统启动U盘》与《刻录_创建ISO镜像》）；
3. USB 引导启动 → 图形安装界面分区与部署；
4. 首次进入后可切换 PC/平板模式（1.0 时代文档重点，3.0 桌面形态以实际版本为准）。

安装后首做事项参考[04 桌面使用](04-desktop-usage.md)：系统更新、查看显卡/无线网卡兼容情况。

## 3.5 ARM 设备路径（6 篇）

| 设备 | 文档 |
|---|---|
| 树莓派 | 《在树莓派上安装openKylin》 |
| 飞腾派 | 《在飞腾派上安装openKylin》 |
| 香橙派 AIpro | 《在香橙派AIpro上安装openKylin》 |
| 双椒派 chilliepi | 《在chilliepi（双椒派）上安装openKylin》 |
| coolpi | 《在coolpi上安装openKylin》 |
| 通用 | 《arm上安装openKylin》 |

SP1 起提供 ARM 通用镜像（飞腾 D3000、此芯 P1 等）。板级文档多为社区投稿，**刷写工具、跳线、启动介质细节随板卡型号变化**，务必同时核对开发板厂商资料与镜像发布日期。

## 3.6 RISC-V 路径（7 篇，openKylin 的差异化投入）

- **开发板实装** 5 篇：SpacemiT K1、LicheePi 4A、Milk-V Pioneer、UR-DP1000、RuyiBook；
- **总览**：《riscv上安装openKylin》汇总五板 + qemu 六条路径；
- **无硬件验证**：《openKylin-RVA23版本使用指南》给出 qemu 启动 RVA23 版本的环境要求与启动命令两步法。

背景知识：SP1 推出统一 RISC-V 镜像与烧录工具，3.0 对齐 RVA23 标准并做 RVV 优化（性能数字为官方口径，引用需标注，见[同包项目调研 I-4](../references/project-overview.md)）。

## 3.7 安装阶段常见问题导航

| 现象 | 去哪查 |
|---|---|
| 看不到 USB 启动项 | 查 BIOS 启动模式与启动盘制作方式（FAQ：USB 3.0 检查） |
| 安装后无 Wi-Fi | 《无线网卡支持》（按芯片制造商查表）+ 《网卡常见问题》 |
| 黑屏/分辨率异常 | 《GPU常见问题》、系统设置分辨率篇、《从NVIDIA官网安装闭源显卡驱动》 |
| 虚拟机里跑不起来 | FAQ"CPU 是否支持虚拟化" + 《虚拟化技术简介》 |
| WSL 导入失败 | 同包[实测排障指南](../references/wsl-install-sparse-vhd-guide.md) |
| tty 终端中文乱码 | 《openKylin系统如何在tty1终端正常显示中文》 |

> 上一篇：[02 版本与生命周期](02-release-lifecycle.md) ｜ 下一篇：[04 桌面环境与基础使用](04-desktop-usage.md)
