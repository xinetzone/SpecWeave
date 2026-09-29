---
title: "openKylin 3.0 WSL 导入排障与稀疏 VHD 启用复盘"
date: 2026-09-29
source: "session:sc-20260929-openkylin-wsl-install-sparse（本机实测，Windows 10.0.19044 + WSL 2.9.3.0）"
type: "retrospective-report"
template: "four-file-atomic-retrospective-v2"
template_version: "2.1"
tags: [wsl, openkylin, vhdx, sparse, memory-triage, windows, environment-setup]
---

# openKylin 3.0 WSL 导入排障与稀疏 VHD 启用复盘报告

> 方法论编排：场景 1 里程碑复盘 + 场景 4 知识沉淀复合链路，`R → I → E → V → C`，depth=standard。
> 编排 session：`sc-20260929-openkylin-wsl-install-sparse`。

## 一、执行摘要

本次任务在 Windows 10（19044）+ WSL 2.9.3.0 环境中，将本地 openKylin 3.0 WSL 镜像（`openKylin-3.0-wsl-amd64.wsl`，336.1 MB）安装为 WSL2 发行版 `openKylin-3.0`，并在安装完成后为其虚拟磁盘启用稀疏 VHD。安装阶段经历四次失败：三次 `Wsl/Service/RegisterDistro/E_UNEXPECTED`（VHD 写入进度分别停在 62 MB、262 MB、336 MB）与一次 `Wsl/Service/RegisterDistro/CreateVm/E_ABORT`。在内存空闲量恢复到约 4.5 GB 后，以解压后的纯 tar 执行 `wsl --import`，8 秒注册成功。稀疏 VHD 首次设置被官方安全策略拦截（`E_INVALIDARG`，提示"由于潜在的数据损坏，目前已禁用稀疏 VHD 支持"），经用户显式授权后追加 `--allow-unsafe` 设置成功，`fsutil sparse queryflag` 复验为 sparse，发行版启动完整性正常。

**关键指标**：

- 交付产物：3 个（复盘报告 1 篇 + 实操教程 1 篇 + 可复用代码模式 1 篇）
- 安装尝试：5 次（4 次失败、1 次成功），最终导入耗时 8 秒
- 失败错误码：2 类（`RegisterDistro/E_UNEXPECTED` ×3、`RegisterDistro/CreateVm/E_ABORT` ×1）
- 提炼可复用模式：1 个模式文件，内含 2 个子模式（低内存 WSL 导入排障法、稀疏 VHD 风险决策框架）
- 默认发行版：安装前后均为 `podman-machine-default`，未发生切换

---

## 二、R 阶段：事实收集（F-001 ~ F-029）

> G1 声明：本节为纯客观陈述，不含因果推断词；每条事实来自本会话命令输出或会话执行记录。

### 2.1 环境基线

| 编号 | 事实 |
|---|---|
| F-001 | 操作系统为 Windows 10.0.19044.7725；WSL 版本 2.9.3.0，内核版本 6.18.35.2-1，WSLg 1.0.79 |
| F-002 | 任务开始前 `wsl -l -v` 仅列出一个发行版：`podman-machine-default`（Stopped，WSL2），并为默认发行版（带 `*` 标记） |
| F-003 | 宿主机 PATH 环境变量被裁剪，直接输入 `wsl` 无法解析，全程使用全路径 `$env:WINDIR\System32\wsl.exe`；设置 `$env:WSL_UTF8=1` 后中文输出正常 |
| F-004 | 宿主机常驻三类安全软件：奇安信无边界安全系统防护、腾讯电脑管家系统防护、Windows Defender；当前会话非提权运行 |
| F-005 | 源文件 `d:\AI\.chaos\envs\openKylin-3.0-wsl-amd64.wsl` 大小 352,431,812 字节（336.1 MB），修改时间 2026-09-29 11:05:13，文件头魔数为 `1F 8B`（gzip） |
| F-006 | 对源文件执行归档完整性遍历时列出 27,930 个条目，含 `./etc/os-release`、`./etc/apt/`、`./var/lib/dpkg/info/` 等标准 rootfs 路径，遍历全程无报错 |
| F-007 | `wsl --help` 输出中 `--install --from-file` 支持 `--location`、`--name`、`--vhd`、`--vhd-size` 参数 |

### 2.2 安装尝试时间线（5 次尝试）

| 编号 | 事实 |
|---|---|
| F-008 | 尝试 1：创建目录 `d:\AI\.chaos\envs\openKylin-3.0` 后执行 `wsl --install --from-file <源文件> --location <该目录> --name openKylin-3.0 --version 2 --no-launch`，数秒内失败，错误码 `Wsl/Service/RegisterDistro/E_UNEXPECTED`；残留 ext4.vhdx 约 62 MB |
| F-009 | 尝试 1 失败后清理了残留的 ext4.vhdx |
| F-010 | 尝试 2：执行 `wsl --import openKylin-3.0 <目录> <.wsl 文件> --version 2`，失败，错误码同为 `Wsl/Service/RegisterDistro/E_UNEXPECTED`；ext4.vhdx 写入至约 262 MB |
| F-011 | 隔离实验：用 84 字节最小空 rootfs（empty.tar.gz）以 `wsl --import` 导入名为 `wsl-selftest` 的自测发行版，工作目录为 `d:\AI\.chaos\envs\.selftest`；实验结束后该目录已删除 |
| F-012 | 使用 .NET `System.IO.Compression.GzipStream` 将 .wsl 流式解压为纯 tar（rootfs.tar，1.10 GB，位于临时工作目录 `.selftest` 内），解压耗时约 7 秒；尝试 3、4、5 均以该 tar 文件为输入 |
| F-013 | 尝试 3：对纯 tar 执行 `wsl --import` 到原安装目录，失败，错误码 `Wsl/Service/RegisterDistro/E_UNEXPECTED`；ext4.vhdx 写入至约 336 MB |
| F-014 | 尝试 4：改用目录 `D:\WSL\openKylin-3.0` 执行 `wsl --import`（纯 tar），约 1 秒后失败，错误码 `Wsl/Service/RegisterDistro/CreateVm/E_ABORT`；目标目录未生成 |
| F-015 | 尝试 4 当时采样：`FreePhysicalMemory` 约 0.8 GB、`FreeVirtualMemory` 约 1.3 GB；进程列表中 Trae CN 相关进程占用内存约 3,125 MB |
| F-016 | 执行 `wsl --shutdown`，等待约 3 秒后再次采样：`FreePhysicalMemory` 约 4.51 GB、`FreeVirtualMemory` 约 4.35 GB |
| F-017 | 尝试 5：内存恢复后对纯 tar 执行 `wsl --import openKylin-3.0 d:\AI\.chaos\envs\openKylin-3.0 rootfs.tar --version 2`，8 秒成功，生成 ext4.vhdx 约 1.20 GB |
| F-018 | 成功后 `wsl -l -v` 列出 `openKylin-3.0`（Stopped，WSL2），默认发行版仍为 `podman-machine-default` |

### 2.3 发行版验收事实

| 编号 | 事实 |
|---|---|
| F-019 | 发行版内 `/etc/os-release` 内容：`NAME="openKylin"`、`VERSION="3.0 (huanghe)"`、`PRETTY_NAME="openKylin 3.0"`、`VERSION_CODENAME=huanghe`、`ID=openkylin` |
| F-020 | 启动后内核为 `6.18.35.2-microsoft-standard-WSL2`；默认登录用户 `openkylin`，UID 1000 |
| F-021 | `/etc/wsl.conf` 含 `[user] default = openkylin` 与 `[boot] systemd=true` 两段配置；软件包计数 405（口径 `dpkg-query -W | wc -l`；`dpkg -l | wc -l` 因含 5 行表头输出 410）；根分区挂载为 `/dev/sdd`，容量 1007G |
| F-022 | 临时解压目录 `.selftest`（含 rootfs.tar 与自测包）已删除，删除方式为 `Remove-Item -Recurse -Force`（DeleteFile 工具尝试移入回收站失败）；`D:\WSL` 目录识别为 podman machine 数据目录，未做改动 |

### 2.4 稀疏 VHD 阶段事实

| 编号 | 事实 |
|---|---|
| F-023 | 设置前基线：`fsutil sparse queryflag` 输出 "This file is NOT set as sparse"；ext4.vhdx 逻辑大小约 1.26 GB；两个发行版均为 Stopped |
| F-024 | 执行 `wsl --manage openKylin-3.0 --set-sparse true` 返回错误码 `Wsl/Service/E_INVALIDARG`，中文提示"由于潜在的数据损坏，目前已禁用稀疏 VHD 支持。要强制发行版使用稀疏 VHD，请运行：wsl.exe --manage <DistributionName> --set-sparse true --allow-unsafe" |
| F-025 | 公开检索到 2026 年 9 月多篇中文技术文章记录同一拦截信息与同一 `--allow-unsafe` 绕过方式，并给出 diskpart `compact vdisk` 作为无数据损坏风险的替代路径 |
| F-026 | 用户在知情选择（强制启用 / diskpart 压缩 / 保持现状）后选择"强制启用 sparse"；执行前采样空闲物理内存 2.60 GB，执行 `wsl --shutdown` 后运行 `wsl --manage openKylin-3.0 --set-sparse true --allow-unsafe`，输出"操作成功完成"，退出码 0 |
| F-027 | 设置后复验：`fsutil sparse queryflag` 输出 "This file is set as sparse"；发行版可正常启动并执行命令（用户 openkylin/UID 1000、df 正常、dpkg 可列出 405 包）；通过 `GetCompressedFileSizeW` 测得实际磁盘占用 1,293.4 MB，逻辑大小 1,317 MB；D 盘剩余 4.21 GB |
| F-028 | 验收后执行 `wsl --terminate openKylin-3.0`，最终 `wsl -l -v` 两个发行版均为 Stopped，默认发行版仍为 `podman-machine-default` |
| F-029 | 任务收尾阶段（2026-09-29 12:20）再次采样：D 盘剩余 4.21 GB，空闲物理内存 1.59 GB；此时两个发行版均为 Stopped |

**G1 自检**：事实 29 条（≥20）；无"因为/导致/所以"等因果词；命令、错误码、数值均有会话输出可追溯；内存采样、文件大小等数字按实测原样记录。**PASS**。

---

## 三、过程分析

### 3.1 失败过程的现象特征

1. 四次失败出现在两条命令路径（`--install --from-file`、`--import`）与两种输入形态（gzip .wsl、纯 tar）上，错误码以 `E_UNEXPECTED` 为主，最后一次为 `CreateVm/E_ABORT`。
2. 三次 `E_UNEXPECTED` 的 VHD 写入进度分别为 62 MB、262 MB、336 MB，停止位置每次不同。
3. 尝试 4 的失败发生在约 1 秒内，错误层级从"注册发行版"变为"创建 VM"，同期内存空闲量处于全流程最低值（0.8 GB）。
4. `wsl --shutdown` 后内存空闲量上升至 4.51 GB，随后同一条 `--import` 命令在原语义路径上一次成功。

### 3.2 排查中被排除的假设

| 假设 | 排除依据（事实编号） |
|---|---|
| 安装包损坏 | F-005 文件大小与官方 336 MB 最小镜像吻合；F-006 全量 27,930 条目遍历无报错；F-012 gzip 可完整解压 |
| `--from-file` 命令路径缺陷 | F-010 改用 `--import` 后出现同类失败 |
| gzip 解压环节问题 | F-012 解压成功且 F-013 纯 tar 导入仍失败 |
| 目标路径/目录权限问题 | F-013 原路径失败、F-014 更换常规路径后仍失败（错误码还发生了变化） |
| 架构或虚拟化栈不可用 | F-002 已有 podman-machine-default 正常注册运行；镜像为 amd64 与主机一致 |

### 3.3 成功因素

1. **非确定性失败位置**这一特征引导排查方向从"输入物正确性"转向"运行时资源状态"。
2. 保留了源安装包，使强制稀疏化具备低成本兜底（注销后重新导入约 8 秒），支撑了 F-026 的风险决策。
3. 操作前后均执行 `wsl -l -v` 与发行版内验收命令，默认发行版与文件系统完整性均有取证。

### 3.4 改进机会

1. WSL 重型操作（import/manage）前应固化"内存空闲量检查 + `wsl --shutdown`"前置步骤。
2. 本机内存长期偏紧（任务收尾时采样空闲仅 1.59 GB，见 F-029），应识别 Trae 多进程 + 三套杀软的常驻占用基线。
3. 稀疏 VHD 的语义（面向未来删除回收，不压缩存量数据）需要在操作前向干系人明确说明。

---

## 四、I 阶段：核心洞察（四元组）

> G2 声明：每条含陈述 / 证据（F 编号）/ 反常识 / 行动，四个维度互不重叠。

### 洞察 I-1：非确定性失败位置是"资源类故障"的判别信号

- **陈述**：同一导入命令反复失败、但 VHD 写入进度每次停在不同位置（62/262/336 MB），是资源型约束（内存、句柄、临时空间）的典型形态；若为输入物损坏，失败位置应稳定复现。
- **证据**：F-008/F-010/F-013 三次进度不一致；F-015 同期内存空闲 0.8 GB；F-016 释放后 4.51 GB；F-017 同命令成功。
- **反常识**：看到"灾难性故障（E_UNEXPECTED）"这类措辞，直觉会怀疑安装包或磁盘；实际错误信息的严重性与根因层级不对应，措辞最吓人的错误反而来自最平凡的内存不足。
- **行动**：任何 WSL/HCS 类操作出现"失败位置不稳定"时，第一步采样 `Win32_OperatingSystem.FreePhysicalMemory` 并执行 `wsl --shutdown`，而非重下镜像或更换路径。

### 洞察 I-2：`E_UNEXPECTED` 与 `E_ABORT` 更可能是同一资源因素的两种表现形态

- **陈述**：三次注册阶段失败报 `RegisterDistro/E_UNEXPECTED`，内存采样最低的一次在 VM 创建阶段秒败报 `CreateVm/E_ABORT`；两者出现在同一条命令链上，时序证据显示其与内存水位强相关（F-014~F-017）。需要限定：尝试 1-3 失败时未做同期内存采样；尝试 3 与尝试 5 之间的唯一干预 `wsl --shutdown` 同时改变了内存水位与 WSL 服务/Utility VM 状态，两者未做对照。因此"共同资源因素"为本机单案例的最可能解释，不是排他性结论。
- **证据**：F-008/F-010/F-013（UNEXPECTED，解压中途）、F-014（E_ABORT，1 秒）、F-015（0.8 GB 空闲）、F-016（shutdown 后 4.51 GB）、F-017（同命令成功）。
- **反常识**：按错误码字面会把它们当作两类独立故障分别排查；按阶段与时序看，错误码分段（RegisterDistro vs CreateVm）更可能只反映"资源压力在哪个阶段耗尽"，而非指示不同问题。
- **行动**：建立 WSL 排障判读规则——先看错误发生阶段与持续时长（秒败 = VM 起不来；中途败 = 展开过程中断），再采样资源水位，不被错误码文字牵着走；后续同类案例应在尝试全程记录内存曲线，以把"最可能"升级为可复证结论。

### 洞察 I-3：稀疏 VHD 是"未来策略"而非"当下压缩"，且设置门槛本身是风险信号

- **陈述**：WSL 对含数据的现有 VHD 默认拒绝设置稀疏（F-024），强制设置成功后 VHD 实际占用仅下降约 24 MB（1,317 vs 1,293.4 MB，F-027）；稀疏标志改变的是后续删除行为的空间回收语义，不回收当前已分配块。
- **证据**：F-023 设置前非 sparse；F-024 官方拦截与 `--allow-unsafe` 提示；F-027 设置后实际占用差仅 24 MB；F-025 diskpart compact 为替代路径。
- **反常识**："启用稀疏以节省磁盘空间"的直觉预期是文件立刻变小；实际对一个全新、内部几乎全是有效数据的 VHD，稀疏化当下几乎无空间可省，真正收益递延到未来删除场景。
- **行动**：将"立即回收存量"与"未来自动回收"拆成两个决策问题——前者用 diskpart 只读挂载 + `compact vdisk`（无损坏风险），后者才用 sparse；对存量关键数据系统默认不使用 `--allow-unsafe`。

### 洞察 I-4：强制稀疏化的实际风险应由"重建成本"而非警告文字定级

- **陈述**：`--allow-unsafe` 的警告是通用性风险提示（元数据重写期断电/崩溃可能损坏文件系统），但本次对象是安装后零用户数据的全新发行版，且源包保留、导入耗时 8 秒，最坏情况的重建成本极低。
- **证据**：F-005/F-006 源包完整；F-017 导入 8 秒；F-021 系统处于初始状态；F-026 在用户知情三选后执行；F-027 设置后启动与文件系统验证正常。
- **反常识**：看到"潜在数据损坏"会一律拒绝或直接照做；两种反应都没有做风险分级。真正决定可否点"强制"的不是警告强度，而是"坏掉以后恢复要付多大代价"。
- **行动**：遇到 `--allow-unsafe` 类开关时走三问——有无用户数据？有无可独立重建的源/备份？重建时长可接受吗？三问均为低风险才可执行，执行前仍需关闭发行版并确认资源水位。

**G2 自检**：洞察 4 条（≥3），四元组完整，维度独立（故障判读 / 错误码语义 / 功能语义 / 风险决策），均含反常识点与具体行动。**PASS**。

---

## 五、E 阶段：可迁移模式

完整结构化模式文档已独立入库：

1. [wsl-import-memory-triage-sparse-vhd.md](../../../patterns/code-patterns/wsl-import-memory-triage-sparse-vhd.md)——**WSL 导入内存分诊与稀疏 VHD 决策模式**（一个模式文件内含两个子模式）：内存分诊法（7 步 + 5 反模式）与稀疏 VHD 决策法（6 步 + 4 反模式），含触发边界、检验标准与跨场景迁移，成熟度 L1（单案例本机实测 + 公开实测互证）。
2. 既有模式 [wsl-distro-install-migration-guide.md](../../../patterns/code-patterns/wsl-distro-install-migration-guide.md) 覆盖离线安装、迁移与默认用户配置，本篇为其排障与磁盘空间维度的增量补充，不重复其内容。

**G3 自检**：模式具备适用/不适用边界、3+ 反模式、检验标准、跨域迁移示例、成熟度标注与唯一 id。**PASS**。

---

## 六、V 阶段：对抗审查记录

fresh-context 独立子代理对三份产出物执行四视角对抗审查（魔鬼代言人 / 新人 / 老板 / 未来），共出具意见 18 条（P0×1、P1×5、P2×7、P3×5），覆盖全部四个视角。

**裁定与处置**：

- P0×1：模式文件磁盘占用测量片段未给 `$vhd` 赋值，照抄必报错 → 已补变量赋值、MB 换算输出与 Add-Type 重复执行保护，已回归。
- P1×5：①"同一根因"对尝试 1-3 属证据外推（无同期内存采样）且 `wsl --shutdown` 同时改变内存与服务状态 → I-2、教程 Q2、模式反模式统一降级为"最可能的共同资源因素（单案例时序证据）"，并新增局限第 5 条；②杀软"未做对照"限定仅报告有 → 教程 §4.2 与模式成熟度节同步补注；③验收"405 包"口径不一致（`dpkg -l | wc -l` 实测 410）→ 实测确认 405 的口径为 `dpkg-query -W | wc -l`，三处统一；④"2~3 GB 阈值"把稀疏化场景的 2.6 GB 采样错配为导入数据点 → 教程与模式均标注"0.8 失败 / 4.5 成功两点间经验区间，下界未测定"；⑤报告 F-022 与 F-012/F-017 的 rootfs.tar 位置时间线矛盾 → F-012 补注产物位于 `.selftest` 且尝试 3-5 共用，矛盾消除。
- P2/P3：采纳 9 条（diskpart 管理员权限、fsutil 全路径、PowerShell 7 前提与 try/finally、验收步骤重排、§5.1 先裸命令取证、公开互证补 URL、F-029 补采、术语"原安装目录"、模式计数说明）；P3-3（status 措辞）因正文已声明单环境实测日期，维持不变。

**回归确认**：P0 片段按修复后内容重新审阅语法完整；405 口径经发行版实机复验（`dpkg-query -W | wc -l` = 405、`dpkg -l | wc -l` = 410）；三份文档相对链接经 `check-links.py` 机械检查 0 断链。V 门标准（4 视角、意见 ≥5、采纳 ≥2 并回归）全部满足，**PASS**。

---

## 七、原子行动项（G4）

| # | 行动项 | Owner | 验收标准 | 状态 |
|---|---|---|---|---|
| A1 | 复盘报告归档至 task-reports 并登记 toctree | 本次会话 | 文件存在、`check-links.py` 对该目录 0 断链 | 已完成 |
| A2 | 实操教程入 `docs/knowledge/tech/openkylin/`，并在 openKylin 调研报告 §7.2 建立交叉引用 | 本次会话 | toctree 含教程条目；调研报告"未实测"局限与教程互链 | 已完成 |
| A3 | 排障模式入库 code-patterns 并登记 toctree | 本次会话 | 模式文件含 frontmatter/id/反模式 ≥3；索引按字母序插入 | 已完成 |
| A4 | 保留 `.wsl` 源包作为 openKylin-3.0 的重建兜底，暂不删除 | 用户 | 源包 336.1 MB 仍在 `.chaos/envs/` | 持续 |
| A5 | 后续在发行版内大量删除数据后，若需立即回收 D 盘空间，执行 diskpart 只读压缩（非 sparse） | 用户/未来会话 | 删除后 `compact vdisk` 前后有大小对比取证 | 待触发 |
| A6 | 本次仅落盘文档与索引变更；git 提交需用户明确授权后按原子提交执行 | 用户 | 未经授权不执行 git commit | 待确认 |

**G4 自检**：行动项单一职责、可独立验证、有验收标准。**PASS**。

---

## 八、局限声明

1. 单机单环境实测（Windows 10 19044 / WSL 2.9.3.0 / openKylin 3.0 amd64）。导入操作的内存观测只有两点：0.8 GB（尝试 4，失败）与 4.5 GB（尝试 5，成功）；2.6 GB 是稀疏化操作前的采样，不是导入数据点。三点均为本机实测值而非官方阈值，失败/成功之间的经验下界未测定，模式成熟度标注为 L1。
2. 杀软拦截为环境变量之一，本机常驻奇安信、腾讯电脑管家、Defender 三套安全软件；当前会话非提权无法加白或查看拦截日志，未做对照实验；其与失败的关联性未证实亦未完全排除，内存压力为最可能但非唯一解释。
3. 稀疏 VHD 的"未来自动回收"效果尚无后续删除场景的实测数据，24 MB 的差值只代表设置当下。
4. 本报告仅记录命令行可观察事实，未读取 WSL 服务内部日志（事件查看器相关查询当时无输出）。
5. 因果推断强度有限：尝试 1-3 失败时未做同期内存采样，内存结论主要由尝试 4 的低水位采样与尝试 5 的时序成功间接支撑；尝试 3 与尝试 5 之间唯一干预 `wsl --shutdown` 同时释放内存并重置 WSL 服务/Utility VM，未做对照分离，故"共同资源因素"为最可能解释而非排他性根因。

---

## 九、质量门汇总

| 门 | 标准 | 结果 |
|---|---|---|
| G1 | 事实 ≥20、无因果词、可溯源 | PASS（F-001~F-029，29 条） |
| G2 | 洞察 ≥3、四元组完整、维度独立 | PASS（I-1~I-4） |
| G3 | 模式有边界、步骤、反模式 ≥3、检验、迁移、成熟度 | PASS（L1，独立入库） |
| V 门 | 4 视角、意见 ≥5、采纳 ≥2 并回归 | PASS（18 条意见：P0×1/P1×5/P2×7/P3×5；P0/P1 全部修复回归，详见 §六） |
| G4 | 行动项原子化、可独立验证 | PASS（A1~A6） |
