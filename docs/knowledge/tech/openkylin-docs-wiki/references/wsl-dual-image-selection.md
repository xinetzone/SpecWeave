---
title: "openKylin 3.0 双 WSL 镜像对照与选型参考（Desktop WSL 远程核验，未落机实测）"
date: 2026-09-30
category: "tech"
tags:
  - openkylin
  - wsl
  - desktop-wsl
  - xrdp
  - ukui
  - storage-planning
  - preflight
status: "remote-verified（容器级事实已远程核验；导入与桌面运行时行为未实测）"
security_level: "public"
source: "方法论编排 session sc-20260930-openkylin-desktop-wsl（R→I→E→V→C，standard）。一手信源：openKylin 官方下载中心与 CDN 元数据（2026-09-30 实测 HTTP HEAD/Range）、Gitee openkylin/docs 官方《openKylin-WSL版本安装》文档（master）、本包 references/wsl-install-sparse-vhd-guide.md 最小镜像本机实测。本机磁盘不足（C: 剩 2.3GB / D: 剩 4.8GB）未做桌面镜像导入实测。"
---

# openKylin 3.0 双 WSL 镜像对照与选型参考

> openKylin 3.0 下载中心对 x86 提供**两种** WSL 形态：336M 的最小镜像与 6.1G 的 Desktop WSL 镜像。本包[实测指南](wsl-install-sparse-vhd-guide.md)只覆盖前者；本文补齐后者的**远程可证事实**、选型决策与磁盘规划，并把所有未经落机验证的运行时结论显式标注、给出后续实测验收清单。
>
> 配套萃取模式：[大归档零下载远程预检法](../../../../retrospective/patterns/code-patterns/large-archive-remote-preflight.md)（本文体积/格式结论的取得方法，可迁移到任意 GB 级归档）。

---

## 1. 证据等级声明（先读）

| 标记 | 含义 | 本文中的项目 |
|---|---|---|
| 【远程核验】 | 2026-09-30 在本机通过 HTTP HEAD/Range 请求直接取得，可复现 | 真实 URL、精确字节数、MD5、gzip 魔数、gzip ISIZE、归档头部条目结构 |
| 【官方口径】 | 官方文档/下载页面声明，未独立验证 | 导入步骤、默认账号密码、xrdp 端口/Session、环境门槛 |
| 【推断】 | 由已核验事实外推，附依据与不确定性 | 解压 tar 真实大小的候选取值、VHD 占用系数 |
| 【待实测】 | 只有落机导入后才能回答 | 真实 VHD 大小、软件包数、导入耗时/内存门槛、xrdp 桌面可用性 |

最小镜像的同项结论若已在[实测指南](wsl-install-sparse-vhd-guide.md)中验证，会注明"最小镜像实测"作为旁证，但**不自动等同于桌面镜像结论**。

---

## 2. 双镜像事实对照表

| 维度 | 最小 WSL 镜像 | Desktop WSL 镜像 |
|---|---|---|
| 下载页条目 | WSL，336M，2026-08-28 | Desktop WSL，6.1G，2026-08-28【官方口径】 |
| 下载 id | 126 | 127 |
| 真实文件 URL 【远程核验】 | `https://cdimage.openkylin.top/3.0/openKylin-3.0-wsl-amd64.wsl` | `https://cdimage.openkylin.top/3.0/openKylin-3.0-desktop-wsl-amd64.wsl` |
| 精确字节数 【远程核验】 | 352,431,812（336.1 MiB / 0.336 GB） | 6,592,986,686（**6,287.4 MiB = 6.14 GiB** / 6.59 GB） |
| 官方 MD5 【远程核验】 | `3c5717cfde5c032c69122fb14fa8e2fa` | `df559de7155ef7c6fe088b2168035c5a` |
| 文件头魔数 【远程核验】 | `1F 8B 08 00`（gzip） | `1F 8B 08 00`（gzip） |
| 归档结构 【远程核验】 | gzip tar，标准 Linux rootfs | gzip tar，头部条目同为标准 rootfs（`./dev`、`./bin`、`./sbin`、`./run/systemd` 等） |
| gzip ISIZE（解压大小 mod 4 GiB） | 1,182,607,360 字节 = 1.101 GiB（未回绕） | 103,258,112 字节 = 98.5 MiB（**已回绕，真值见 §4**） |
| 架构 | 仅 AMD64（x86）【官方口径】 | 仅 AMD64（x86）【官方口径】，无 ARM/LoongArch/RISC-V 形态 |
| 图形桌面 | 不含；纯命令行 | 含 xrdp 远程桌面通路与 UKUI 桌面预装【官方口径】 |
| 官方导入命令 | `wsl --import openKylin .\openKylin <镜像> --version 2` | `wsl --import openKylin-desktop .\openKylin-desktop <镜像> --version 2`【官方口径】 |
| 默认账号 | `openkylin/openkylin`【官方口径+最小镜像实测】 | `openkylin/openkylin`【官方口径，待实测】 |
| 本机实测状态 | 已实测（Win10 19044 + WSL 2.9.3.0，405 包，VHD 约 1.3 GB） | **未实测**（本机剩余磁盘不足） |

> 文件名同源（`openKylin-3.0[-desktop]-wsl-amd64.wsl`）、同日构建、同容器格式、同文档同章节描述，支持"二者是同一打包流水线的两种目标形态"的判断；但**两者的软件包清单包含关系未经比对**（需全量列目），"桌面镜像 = 最小镜像 + 桌面包"是合理推断而非已核验事实。

---

## 3. 远程核验记录（可复现）

以下命令在 PowerShell 7 执行，全程仅消耗约 20 MiB 流量，未下载全量镜像。

```powershell
# ① HEAD 跟随跳转：真实 URL + Content-Length + 是否支持 Range
curl.exe -sIL "https://www.openkylin.top/downloads/download-smp.php?id=127" |
  Select-String -Pattern "HTTP/|location:|content-length:|accept-ranges:" -CaseSensitive:$false
# 302 → https://cdimage.openkylin.top/3.0/openKylin-3.0-desktop-wsl-amd64.wsl
# 200，Content-Length: 6592986686

# ② MD5：下载页页内脚本的 md5ById 映射（id=127）
$html = curl.exe -s "https://www.openkylin.top/downloads/index-cn.html"
(($html -join "`n") | Select-String -Pattern '(?s)md5ById:\s*\{(.*?)\}').Matches.Groups[1].Value
# 127: 'df559de7155ef7c6fe088b2168035c5a'

# ③ 头部 4 字节验魔数：必须落盘后 Format-Hex，勿走文本管道
curl.exe -s -r 0-3 "https://cdimage.openkylin.top/3.0/openKylin-3.0-desktop-wsl-amd64.wsl" -o head.bin
Format-Hex head.bin   # 1F 8B 08 00

# ④ gzip 尾部 4 字节读 ISIZE（小端 UInt32）
$size = 6592986686
curl.exe -s -r "$($size-4)-$($size-1)" "<URL>" -o tail.bin
[BitConverter]::ToUInt32([IO.File]::ReadAllBytes("tail.bin"), 0)  # 103258112

# ⑤ 取前 20 MiB 流式解压后 tar 列目（截断流在尾部报错属正常）
curl.exe -s -r 0-20971519 "<URL>" -o probe.bin
# .NET GzipStream 解压为 probe.tar 后：tar.exe -tf probe.tar | Select-Object -First 40
```

两个实测小教训（已收入模式反模式）：二进制字节走控制台文本管道时 `0x8B` 被替换成 UTF-8 替换符 `EF BF BD`，魔数核验必须落盘用 `Format-Hex`；下载页"6.1G"是十进制近似口径，磁盘规划必须用精确字节数。

---

## 4. 解压体积区间判读与磁盘规划

### 4.1 ISIZE 回绕：为什么不能直接相信 98.5 MiB

gzip 流尾部 4 字节 ISIZE 记录的是解压后大小 **mod 2³²**。桌面镜像读出 98.5 MiB，远小于其 6.14 GiB 压缩体积，说明已越过 4 GiB 回绕点，真实解压 tar 大小为 `98.5 MiB + k × 4 GiB`，候选序列：

| k | 解压 tar 大小（字节） | 约合 | 相对压缩包倍数 | 与旁证的关系（非概率排序） |
|---|---|---|---|---|
| 1 | 4,398,225,408 | 4.1 GiB | 0.67× | 排除：解压体积小于压缩包，对真实 tar 归档不成立 |
| 2 | 8,693,192,704 | 8.1 GiB | 1.32× | 不矛盾：桌面 rootfs 若含大量已压缩素材（PNG 图标/主题/字体/翻译 mo），整体压缩比可显著偏低 |
| 3 | 12,988,160,000 | 12.1 GiB | 1.97× | 不矛盾：介于"素材密集"与"程序密集"两种压缩行为之间 |
| 4 | 17,283,127,296 | 16.1 GiB | 2.62× | 最小镜像实测压缩比 3.36× 向下外推的落点，仅作规划参考列 |
| 5 | 21,578,094,592 | 20.1 GiB | 3.27× | 压缩比与最小镜像实测值 3.36× 几乎一致，同样不矛盾 |
| ≥6 | ≥24.1 GiB | — | ≥3.93× | 压缩比高于以二进制程序为主的最小镜像，与"桌面含更多已压缩素材"的预期相悖，但仅凭头尾信息不能排除 |

**旁证与推断强度**：最小镜像 gzip→tar 实测为 3.36×，但其内容以二进制程序为主（压缩友好）；桌面 rootfs 预期含更多已压缩素材、整体压缩比应更低——这一方向感至多提供"真值倾向于不高于 3.36×（即 k≤5）"的**方向性预期，且该预期本身未经实测**；它**不足以在 k=2～k=5 四个候选之间排序，本文不给点估、不设"最可能"取值**。16.1 GiB（k=4）在 §4.2 仅作为外推参考列出，与其他候选地位相同。真实取值只能靠全量解压实测消歧（列入 §7 清单）。

### 4.2 磁盘规划：三档分层（长期占用 / 标准峰值 / 排障峰值）

导入过程的宿主占用分三段（构成来自最小镜像实测，桌面镜像数值为【推断】）：

| 占用段 | 估算 |
|---|---|
| 下载的 `.wsl` 文件 | 6.14 GiB（可导入后删除） |
| 导入后 `ext4.vhdx` | 解压 tar 有效数据 + ext4 元数据开销；最小镜像实测 VHD/解压 tar ≈ 1.17（仅一个观测点，系数【推断】） |
| 导入期临时解压空间 | 仅"手动解压 tar 再导入"排障路径必然产生（约一个解压 tar）；直接 import 路径见下方流式说明 |

按 §4.1 候选区间的三个代表取值（下界 k=2／参考列 k=4／方向性上限 k=5）的占用矩阵（GiB，约值；三列之间不代表概率高低）：

| 口径 | k=2（8.1 GiB tar） | k=4（16.1 GiB tar，参考列） | k=5（20.1 GiB tar） |
|---|---|---|---|
| ① 导入后长期占用（VHD ≈ tar × 1.17） | ≈ 9.5 | ≈ 19 | ≈ 24 |
| ② 标准路径峰值（① + `.wsl` 6.1，同盘） | ≈ 16 | ≈ 25 | ≈ 30 |
| ③ 排障路径峰值（① + tar + `.wsl`，三者同盘共存） | ≈ 24 | ≈ 41 | ≈ 50 |

**建议预留线**（按"覆盖到哪个候选"表述，不押注具体 k 值）：

- **≥ 20 GiB（跨盘起步线）**：VHD 安装目录与 `.wsl` 下载目录分处两块盘（用 `wsl --import` 第二参数把 VHD 指定到数据盘），只需容纳行①；覆盖 k≤4（≈19 GiB 以内），若真实为 k=5（≈24 GiB）会盘满——接受该风险再用；
- **≥ 25 GiB（推荐，同盘）**：`.wsl` 与 VHD 在同一盘，覆盖 k≤4 的标准路径峰值（行② ≈25 GiB）；
- **≥ 30 GiB（稳妥，同盘）**：覆盖方向性上限 k=5 的标准路径峰值（行② ≈30 GiB）；若实测 k≥6，需按 §4.1 公式重新上算；
- **≥ 45 GiB（排障预留）**：仅当预计需要走"先手动解压为纯 tar 再导入"路径时按行③预留（覆盖 k=4 的 ≈41 GiB；覆盖 k=5 需 ≥50 GiB）。
- 任何档位都**不要**按下载页"6.1G"准备空间：即使区间下界 k=2，导入后长期占用也约 9.5 GiB、同盘峰值约 16 GiB。

**流式写入机制说明（关键假设，未实测）**：`wsl --import` 直接读取 gzip tar 时，通常以**流式解压写入 VHD** 的方式工作，不在宿主磁盘另落一份完整解压 tar——因此标准路径（行②）的峰值一般只是"VHD + `.wsl`"两段，而非三者相加。但该行为**未在桌面镜像实测确认**（最小镜像成功路径为流式，但两者体量相差 18.7 倍，不能据此断言）；一旦因导入失败改用实测指南中"先以 .NET GzipStream 解压为纯 tar 再 import"的排障路径，完整 tar 会真实落盘，必须按行③预留空间。

> 本机 2026-09-30 时点 C: 剩 2.3 GB、D: 剩 4.8 GB，任何候选下都不具备导入条件，这是本文停在远程核验的直接原因。安装目录可用 `wsl --import <名称> <目标目录> <镜像>` 的第二参数指定到任意数据盘，无需占用系统盘。

---

## 5. 桌面镜像使用路径（官方口径转述，未实测）

以下步骤来自官方《openKylin-WSL版本安装》文档（Gitee master，2026-09-30 取全文），**本文未逐条验证**：

1. 环境门槛：Windows 10 2004（内部版本 19041）及以上或 Windows 11，管理员 PowerShell；
2. `wsl --install`、`wsl --set-default-version 2`；
3. 下载 `openKylin-3.0-desktop-wsl-amd64.wsl`（下载后先按 §2 的 MD5 校验）；
4. `wsl --import openKylin-desktop .\openKylin-desktop .\openKylin-3.0-desktop-wsl-amd64.wsl --version 2`；
5. `wsl -d openKylin-desktop` 进入命令行，默认账号密码 `openkylin/openkylin`；
6. 取内网地址：`ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1`（取 IPv4）；
7. Windows 打开"远程桌面连接"（mstsc，未预装可从微软官网下载），计算机栏填 `<IP>:3390`；
8. 登录窗 Session 选 **xorg**，用户名/密码均为 `openkylin`，进入 UKUI 桌面；
9. 注意：xrdp 默认端口 **3390**（非标准 RDP 3389）、默认自启；**WSL 每次重启后 eth0 IP 可能变化**，需重新获取。

官方 FAQ 仅两条：WSL2 内核未安装（装 https://aka.ms/wsl2kernel ）、远程桌面连接失败（查 xrdp 服务与 3390 端口）。磁盘/内存门槛、包清单、VHD 体积、导入失败排障均未覆盖——这正是[实测指南](wsl-install-sparse-vhd-guide.md)对最小镜像补齐、而桌面镜像尚空白的部分。

**同名冲突提醒**：在同一台 Windows 上并存两种镜像时，`wsl --import` 的发行版名必须不同（如 `openKylin-3.0` 与 `openKylin-3.0-desktop`）；重名导入会直接失败，也不要覆盖已有发行版的安装目录。

---

## 6. 选型决策

| 你的诉求 | 选择 | 依据 |
|---|---|---|
| 命令行开发、跑脚本/服务、容器式工具链 | **最小镜像** | 下载量为桌面镜像的 1/18.7；VHD 实测约 1.3 GB；导入 8 秒（最小镜像实测） |
| 必须在 Windows 上获得**完整 UKUI 桌面会话**（开始菜单/设置/全套桌面应用） | **Desktop WSL 镜像** | xrdp 全桌面预装，免自行解决桌面依赖【官方口径】；代价是同盘 25～30 GiB 磁盘预留（跨盘 20 GiB 起步）与分钟级导入【推断/待实测，分层口径见 §4.2】 |
| 只想在 WSL 里运行**个别 Linux GUI 应用**（编辑器、浏览器、工具窗口等） | **优先 WSLg**，不选 6.1 GiB 桌面镜像 | WSLg 提供单应用集成窗口（Win11 及较新 Win10/WSL 支持，以本机 `wsl --version` 能力为准），与最小镜像搭配即可，零额外桌面载荷；它与"完整桌面会话"是两种需求，WSLg 不提供完整 UKUI 会话——只有需要完整桌面会话时才应转向上一行的桌面镜像 |
| 想看桌面但磁盘紧张 | 虚拟机路径或最小镜像自装桌面（自行承担依赖与排障成本，官方未给此路径文档） | 虚拟机方案见 [03 安装路径](../concepts/03-install-paths.md) §3.3 |
| 长期生产/多人环境 | 两个镜像都需先做安全加固（改弱口令、限制端口）再评估 | 见下节 |

> **选型定性**：Desktop WSL 不是"更好的 WSL"，而是"带完整桌面会话的 WSL"。两者机制完全相同（§8-I-1），桌面镜像的全部增量都是在为 xrdp + UKUI 全桌面买单——18.7 倍下载体积、数倍至数十倍磁盘占用、额外一条远程桌面攻击面。**没有完整图形桌面会话需求时，这些代价纯属浪费**：命令行需求选最小镜像，零散 GUI 应用需求走 WSLg；只有"必须在 Windows 上获得一整个 UKUI 桌面（开始菜单/系统设置/全套桌面应用同一会话）"才选桌面镜像。

**最小镜像实测经验对桌面镜像的可迁移性**：

- 可直接迁移（容器格式同构【远程核验】+ WSL 机制通用）：`.wsl` 是 gzip tar 而非 APPX 的判断、`wsl --import` 命令形态、PATH 裁剪时用 `$env:WINDIR\System32\wsl.exe` 全路径与 `WSL_UTF8=1`、默认发行版星标不被 import 改变的验收项、稀疏 VHD 的 `--set-sparse true --allow-unsafe` 拦截与 diskpart compact 双路径（机制相同，**收益与风险随体积放大**）；
- 需重新观测、不可照搬数值：导入失败与空闲内存的阈值关系（桌面镜像解压工作量约大一个数量级，暴露窗口更长）、导入耗时、VHD 实际大小与稀疏化收益；
- 桌面镜像新增的未知面：xrdp/UKUI 相关 systemd 服务在 WSL2 容器内的启动状态（全桌面 rootfs 常带入 acpid/蓝牙/电源等依赖物理硬件的服务，同类 WSL2 发行版有黑屏、残留 X-session 的通用公开案例，但**非 openKylin 实测事实**，仅作排查方向，不写入结论）。

**安全注意**：预置弱口令 `openkylin/openkylin` 与监听 3390 的 xrdp 仅适用于本机体验——首次进入立即 `passwd`；不要把 3390 做公网端口映射；不用时 `wsl --shutdown <发行版名>`。

---

## 7. 待实测验收清单（空间允许时执行）

目标盘按 §4.2 预留空间后（同盘建议 ≥25～30 GiB；若预计走手动解压 tar 的排障路径则 ≥45 GiB），按下列清单一次性采集，可直接把本文【待实测】项转为实测结论：

1. 下载后校验：MD5 = `df559de7155ef7c6fe088b2168035c5a`、字节数 = 6,592,986,686；
2. 全量流式解压为纯 tar，记录真实解压大小，对 §4.1 候选表消歧（确认 k 值）；
3. 记录导入全程耗时；导入前采样空闲物理内存；若复现 `E_UNEXPECTED/E_ABORT`，按[内存分诊模式](../../../../retrospective/patterns/code-patterns/wsl-import-memory-triage-sparse-vhd.md)记录失败指纹；
4. 验收五项（沿用[实测指南](wsl-install-sparse-vhd-guide.md) §3.3）：`wsl -l -v` 与默认星标、`/etc/os-release`、默认用户/UID、`df -h /`、软件包计数（`dpkg-query -W | wc -l`，与最小镜像 405 包做差，量化"桌面增量"）；
5. xrdp 桌面链路：eth0 IPv4 → mstsc `<IP>:3390` → Session xorg → 登录成功进入 UKUI；记录 WSL 重启后 IP 漂移现象；
6. 进入后检查 `systemctl --failed` 与 xrdp 服务状态，记录 WSL2 下失败/被 mask 的硬件相关服务（若有）；
7. 导入后 VHD 逻辑大小与真实占用（`GetCompressedFileSizeW`），回算 VHD/tar 系数，验证或修正 1.17【推断】；
8. 稀疏 VHD 决策：全新桌面系统同样"当下无洞可回收"，记录设置 sparse 后的逻辑/实际占用差；三问定级与 `--allow-unsafe` 纪律沿用实测指南 §5.1；
9. 卸载清理：`wsl --unregister openKylin-3.0-desktop` 后确认 VHD 与磁盘回收。

---

## 8. I 阶段：核心洞察（四元组）

### I-1　两个按钮同源同构，差异是"内容载荷"而非"安装机制"

- **陈述**：两镜像同为 gzip tar rootfs、同日构建、文件名同源、同一篇官方文档、同一条 `wsl --import` 路径、同一默认账号；机制层零差异，全部差异集中在载荷（是否含 xrdp + UKUI 全桌面）与 18.7 倍的下载体积。
- **证据**：F-046（魔数与头部条目同构）、F-045（命名、构建日期与下载条目）、F-048（官方文档同章同导入路径与账号体系）。F 编号对应知识包 [index.md H 组](../index.md)。
- **反常识**："Desktop WSL"听起来像另一个产品或另一套安装器；实测它没有任何安装机制上的新东西，选型问题因此可简化为纯业务问题——"要不要完整图形桌面会话"。
- **行动**：按 §6 决策表二选一即可，不必为"桌面版会不会更难装"预留额外学习成本；但包清单包含关系【待实测】，勿把"同源"表述成"桌面镜像 = 最小镜像 + 桌面包"的事实等式。

### I-2　6.1G 下载只是冰山一角，且大镜像恰好让 gzip ISIZE"秒查解压大小"的技巧失效

- **陈述**：真实下载 6.14 GiB，而导入后还要叠加 VHD 长期占用（9.5～24 GiB）与同盘 `.wsl` 共存峰值（16～30 GiB；手动解压排障路径可达 41～50 GiB，分层口径见 §4.2）；用于廉价估算解压体积的 gzip ISIZE 字段在 >4 GiB 后回绕，本案例读出 98.5 MiB 的荒谬小值，头尾信息只能给出 8.1/12.1/16.1/20.1 GiB 离散候选（k≥6 时 ≥24.1 GiB）。
- **证据**：F-045（精确 Content-Length）、F-047（ISIZE 回绕与候选区间）、最小镜像实测的 VHD/tar 1.17 与临时占用构成。
- **反常识**：直觉按下载页"6.1G"预留空间；真正失败模式是盘备好 7 GiB 却在导入途中盘满，留下半成品 VHD；更隐蔽的是网上常用的"读 gzip 末 4 字节估大小"技巧在大文件上静默给出错误答案而不报错。
- **行动**：大归档下载前一律走[零下载远程预检](../../../../retrospective/patterns/code-patterns/large-archive-remote-preflight.md)五步；磁盘按 §4.2 三档口径依部署路径（跨盘/同盘/排障）规划，而非按下载体积或单一上限；真实 k 值留待全量解压时消歧。

### I-3　同一页面上的两个下载按钮，证据等级并不相同

- **陈述**：最小镜像有完整本机实测（包数、VHD、失败指纹、稀疏 VHD），桌面镜像的公开运行时证据为零——官方文档只有正向操作步骤与两条 FAQ，社区论坛/搜索引擎 2026-09-30 检索无用户实测帖；但文件级属性（字节数、MD5、格式、结构）无需下载即可远程证伪。
- **证据**：F-049（官方文档覆盖空白与社区零实测负证据）、F-045/F-046（字节数、MD5、魔数、结构等远程可证项）。
- **反常识**："官网同页并列"给人同等可信的错觉；实际可验证性天然分两层——**文件级事实可远程证伪，运行时事实只能本机证伪**，下载物"是真的、完整的"不能推出"装完好用"。
- **行动**：本文采用【远程核验/官方口径/推断/待实测】四级标注；在完成 §7 清单前，任何对外材料不写"桌面 WSL 稳定可用"类结论；xrdp 通用坑只作排查方向引用。

---

## 9. V 阶段：四视角对抗审查记录

| 视角 | 攻击点 | 采纳与处置 |
|---|---|---|
| 🔴 魔鬼代言人 | ISIZE 候选为何止于 k=5？k≥6 不能排除；"桌面=最小+桌面包"无包清单证据；1.17 VHD 系数只有一个观测点 | 候选表保留 k≥6 行并标"可能性递减不排除"；§2 将包含关系降级为"合理推断"；1.17 全程标【推断】并列入实测复核项 |
| 🟢 新人视角 | GiB/GB 混用会误判；不知道怎么选安装盘、与现有最小镜像会不会撞名；不知道 mstsc 是什么 | §2 精确字节同时给 MiB/GiB/GB；§4 注明安装目录可指定任意盘；§5 增加同名冲突提醒；mstsc 按官方原文给中文名与获取途径 |
| 🟠 老板视角 | 投入 45 GiB + 分钟级导入的产出是什么？弱口令+xrdp 风险？ | §6 决策表给出各诉求的成本/替代；§6 安全注意给出弱口令、3390 不映射公网、shutdown 三条红线 |
| 🔵 未来视角 | WSLg 普及后 xrdp 全桌面镜像是否是过渡形态？镜像（08-28）早于正式版（09-05）会不会过时？ | §6 区分"完整桌面会话 vs 单应用 GUI"两种需求并引入 WSLg 评估项；开头事实表保留构建日期，提醒使用时复核页面当时的大小与 MD5 |

| ⚪ 二轮修正（用户驱动，2026-09-30） | 原"≥45 GiB"单值门槛把排障路径峰值当作通用门槛，与最小镜像"直接 import 流式写入、不落完整 tar"的实测经验矛盾，会过度吓退读者 | §4.2 改为三档分层（长期 VHD／标准峰值／排障峰值）与 20/25/30/45 四条建议线；显式补充流式写入假设并标注"桌面镜像未实测确认"；§6/§7/I-2 与概念页、最小镜像指南范围声明、知识包索引同步 |
| ⚪ 三轮修正（用户驱动，2026-09-30） | 选型表对"两个镜像 + WSLg"三者语气中立，读者可能把桌面镜像误读为默认/更优选择，为不需要的桌面付出 18.7 倍下载与数倍磁盘代价 | §6 WSLg 行改为"优先 WSLg，不选桌面镜像"，表后新增选型定性（"桌面镜像不是更好的 WSL，而是带完整桌面会话的 WSL"，无桌面需求时代价纯属浪费）；概念页选型表同步同一倾向 |
| ⚪ 四轮修正（用户驱动，2026-09-30） | k=4 标注"按旁证推断最可能"超出了单一压缩比旁证的证据强度：它只支持方向性区间约束，不支持在四个候选间做概率排序；点估措辞会让读者把 16.1 GiB 当成准事实 | §4.1 末列由"可能性评估"改为"与旁证的关系（非概率排序）"，显式声明不给点估；§4.2 三列改为下界/参考列/方向性上限，建议线改为"覆盖到哪个候选"的口径；F-047、概念页、局限⑥同步去除"最可能/推断中值" |

V 门结论：4 视角全覆盖，实质意见 11 条，全部采纳（3 条降级表述、4 条补充读者引导、2 条风险补强、2 条时效/替代路径）；另完成三轮用户驱动修正——二轮磁盘口径分层化、三轮选型倾向显性化、四轮候选去点估（见末三行）。遗留 1 项（xrdp 黑屏等通用坑是否在 openKylin 出现）登记为排查方向而非结论，随 §7 清单关闭。

---

## 10. 局限声明

1. 桌面镜像未落机导入：导入耗时、内存门槛、真实 VHD、包数、xrdp/UKUI 可用性全部为【待实测】，见 §7 清单；
2. ISIZE 候选区间未消歧，§4.2 的三档数字由 1.17 VHD 系数（单一观测点）与三个 k 候选推算，真实占用可能低于或高于建议线；"直接 import 流式写入、不落完整 tar"在桌面镜像未实测，若实际另落临时 tar，标准路径峰值应按行③上修；
3. 事实时点 2026-09-30：镜像构建日期 2026-08-28、3.0 正式版 2026-09-05 发布，官方可能更新镜像，下载前应以页面当时的字节数与 MD5 重新核验；
4. 社区零实测的检索结论受检索词与平台覆盖限制（bbs.openkylin.top 站内检索 + 公开搜索引擎），不排除有未被收录的个人博客记录；
5. xrdp/WSL2 通用故障模式引自 openKylin 之外的公开资料，仅作排查方向，不是 openKylin 桌面镜像的事实陈述。

---

## 11. 参考资料

- [openKylin 3.0 WSL 安装与稀疏 VHD 实操指南（Windows 10 实测）](wsl-install-sparse-vhd-guide.md)
- [openKylin 官方下载中心](https://www.openkylin.top/downloads/index-cn.html)
- 官方文档《openKylin-WSL版本安装》：Gitee `openkylin/docs` → `1入门与参与/1_3系统下载与安装指南/05_openKylin-WSL版本安装.md`
- [大归档零下载远程预检法（模式）](../../../../retrospective/patterns/code-patterns/large-archive-remote-preflight.md)
- [WSL 导入内存分诊与稀疏 VHD 决策模式](../../../../retrospective/patterns/code-patterns/wsl-import-memory-triage-sparse-vhd.md)
- [03 安装路径全景与选型](../concepts/03-install-paths.md)

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20260930-openkylin-desktop-wsl | msg=知识沉淀：Desktop WSL 双形态对照 | ctx={"scenario":"knowledge","chain":"R-I-E-V-C"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G3 | event=GATE_PASSED | session=sc-20260930-openkylin-desktop-wsl | msg=模式「大归档零下载远程预检法」L1单案例，5反模式，含跨域迁移
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V9 | event=GATE_PASSED | session=sc-20260930-openkylin-desktop-wsl | msg=4视角11意见全部采纳
```
