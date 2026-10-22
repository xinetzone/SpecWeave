# 04 技术栈分叉：包格式、桌面地位与 AI 落点

> 读完本文你会知道：两边在包管理、系统架构、桌面、硬件架构、标志性技术与 AI 化方向上的硬差异，以及这些差异如何影响迁移成本与团队技能要求。

## 4.1 一张总表

| 层 | openEuler | openKylin |
|---|---|---|
| 包管理 | RPM / dnf；软件中心 213,330 包、325 应用镜像（页面口径）；25.09 创新版起 epkg 多环境多版本；分类含 OEPKG、CONDA（O-023） | dpkg / apt（K-007）；自有 OKBS/UKBS 编译平台与 PPA 流程 |
| 桌面 | 非主线，官方文档提供 DDE（统信）、UKUI（麒麟）两份装后安装指南；root 不能直接登录图形桌面（O-026） | 产品本体：默认 UKUI（3.0 为 4.24），自研 wlcom Wayland 合成器；隔空手势、全局语音输入、三岛任务栏等（K-009） |
| 应用格式与系统形态 | 常规 RPM 为主；创新版试 epkg | 开明 Kaiming（base+runtime+app，crun/OCI 沙箱）；OSTree 不可变系统、原子更新回滚；磐石架构=不可变系统+KARE+开明包（K-008） |
| 移动/兼容生态 | — | KARE 跨版本兼容；早期 KMRE 移动运行环境；openKylin Wine 助手（本地包 F-019/F-041） |
| 内核策略 | LTS 线锁长期内核（24.03 为 6.6），SP 内叠特性；银河麒麟 V10 商业版内核主版本 4.19 生命周期内不变（O-016/O-031） | LTS 6.6；创新版 3.0 跨代 7.0，支持 Rust for Linux，首批系统工具 Rust 重写（K-006） |
| 架构 | x86_64、aarch64、ARM32、LoongArch64、RISC-V；材料另列 SW-64、Power 口径（O-021） | X86、ARM、LoongArch、RISC-V 四架构同源；RVA23/RVV，统一 RISC-V 镜像覆盖多开发板（K-010） |
| 虚拟化/容器 | StratoVirt 轻量虚拟化、iSula 轻量容器、KubeOS（O-027） | 通用虚拟化与 VirtIO-GPU 硬件视频加速（本地包 F-041）；Docker 应用镜像 20 余款（本地包 F-032） |
| 运维与性能 | A-Tune 智能优化、A-OPS 智能运维、Gazelle 用户态协议栈、Rubik 在离线混布、etMem、Gala（O-027/O-028） | 分级冻结机制（本地包 F-041） |
| 可靠性/热补丁 | SysCare 热补丁、SysMaster（O-027） | OSTree 原子更新与回滚（K-008） |
| 安全 | SecGear 机密计算、secPaver、机密虚拟机（SP4）、eBPF 行为分析主动防御（O-019/O-028/O-029） | 后量子密码 ML-KEM/ML-DSA/SLH-DSA（openHiTLS）、TPM 可信链、火焰卫士、Compliance/SBOM/KYChain SIG（K-006、本地包 F-042） |
| 工具链 | 毕昇 JDK 与毕昇编译器、EulerFS、Uniproton 实时内核（O-028） | GCC 15、LLVM 22、glibc 2.42、JDK 25（3.0 组件，K-006） |
| 架构方法论 | 榫卯：全栈原子化解耦；Soft Bus 与 OpenHarmony 生态互通（O-028） | 核心组件自主选型（1.0 为 20+，2.0/3.0 为 180+）与自有镜像构建流水线（本地包 F-033/F-034） |
| AI 落点 | 集群侧：系统智能中枢、NPU 算力切分、推理服务快恢、Conch 沙箱（百毫秒启动）、Token 能效官方口径提升 20%—30%、SkillHub（O-029/O-019） | 端侧：智能体开放底座（模型/记忆/工具/权限/桌面能力统一架构）、MCP 调桌面、统一 AI SDK、技能仓库、Token 中心、AgentOS/Claw Box OS 镜像（K-011） |
| 获取渠道 | 华为云/腾讯云/AWS/Azure/阿里云镜像、容器镜像、EulerLauncher、WSL、MacOS（O-025） | 官网 ISO、WSL（基础镜像 336M）、开发板镜像、衍生镜像（本地包 F-031） |

## 4.2 包管理分叉的实际分量

包格式不是可以忽略的细节，它决定三件事：

1. **存量软件与迁移路径**：CentOS 系停服替代在包格式、命令习惯（dnf/yum、systemd 服务封装）与运维脚本上与 openEuler 同构，是公开案例最密集的迁移方向（O-032 行业案例）；Debian/Ubuntu 桌面软件与第三方 deb 仓库的存量在 openKylin 侧直接可用（K-007）。
2. **团队技能栈**：RPM spec 与 dnf 仓库管理、deb/rules 与 apt 源管理是两套不同的工程能力，运维自动化脚本、漏洞处置流程、镜像构建流水线都要按此分流。
3. **自研包格式的方向**：openEuler 在创新版试验 epkg（多环境多版本，O-023），openKylin 已有开明包的 base/runtime/app 三层与 OCI 沙箱实践（K-008）；两者都在尝试"应用与系统解耦"，但尚未互换生态，选型时不计为等价能力。

## 4.3 桌面：可选组件与一等产品的差距

openEuler 官方文档确实提供 DDE 与 UKUI 的装后安装指南（`dnf install dde` / `dnf install ukui`，O-026），但以下事实界定了它与 openKylin 的差距性质：

- openEuler 主线介质是服务器/云/嵌入式镜像（O-024），桌面是仓库组件；openKylin 的版本号、市场叙事与发布节奏围绕桌面体验组织（UKUI 3.1→4.0→4.10→4.20→4.24 与发行版同步演进，K-009）。
- openKylin 桌面侧有一整套围绕默认桌面的自研件：wlcom 合成器、开明应用分发、不可变系统、移动兼容、隔空手势/语音输入等（K-008/K-009）。
- 外设与整机适配的汇聚方向不同：openKylin 侧国产显卡、CPU、整机型号按 SP 公布适配清单（本地包 F-023），openEuler 的兼容叙事以服务器硬件、云与板卡为主。

结论（洞察 I-4）：**"`dnf install ukui` 能装上"证明组件存在，不证明桌面就绪**；以桌面为目标工作负载时，必须用 openKylin 默认介质或 openEuler 加桌面后的实测对比来裁决，不能用特性表打勾替代。

## 4.4 架构支持：重叠面与差异化投入

- 重叠面：X86（Intel/AMD/海光/兆芯）、ARM（飞腾等）、LoongArch（龙芯）两边都覆盖（O-021/K-010）。
- openEuler 的差异化在服务器 ARM（鲲鹏生态，O-014 关联数据）与嵌入式板卡（openEuler Embedded 26.03，hi3403/hi3591，O-020）。
- openKylin 的差异化在 RISC-V 桌面/开发板：统一镜像与烧录工具覆盖 VisionFive2、LicheePi4a、Milk-V Pioneer、SpacemiT K1 等，对齐 RVA23，RVV 优化性能数字为官方口径待复测（K-010、本地包 F-020/F-030）。
- 申威 SW-64 与 Power 在 openEuler 材料中出现（O-021），投入深度需逐架构核查当前版本的镜像与维护 SIG，不能仅凭材料列举判定可用。

## 4.5 AI 栈：同名 AgentOS，两层不同物

| 对照 | openEuler 2026（集群侧） | openKylin 3.0（端侧） |
|---|---|---|
| 服务对象 | 数据中心、超节点、推理服务集群（O-019/O-029） | 个人桌面上的智能体与 AI PC 用户（K-011） |
| 关键能力 | NPU 算力切分、推理服务快恢、在离线混布、eBPF 主动防御、Conch 百毫秒沙箱、能效优化 | MCP 调用桌面能力、统一 AI SDK（多模型适配）、本地模型工具、技能仓库、Token 额度中心 |
| 开放形态 | SkillHub（skillhub.openeuler.org）、SIG 议题（AI 生态、Agent Infra 等四大相关方向，O-030） | openKylin-skills 仓库、第三方智能体（KylinBot、WorkBuddy、OpenClaw 等）与衍生镜像 |
| 评估清单 | 算力隔离粒度、故障恢复 RTO、混布干扰、能效实测 | 协议开放性、第三方智能体权限对等性、技能签名审计、模型可否本地替换 |

两边的性能与能效数字（20%—30% 能效、RISC-V FP16 最高 36.5 倍等）均为**官方口径**，本知识包未复测，不得作为容量规划依据（V 审查 V-01 统一裁定）。
