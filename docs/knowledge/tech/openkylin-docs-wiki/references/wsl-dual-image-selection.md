---
title: "openKylin 3.0 双 WSL 镜像对照与选型参考（Desktop WSL 已于 2026-10-08 落机实测）"
date: 2026-09-30
last_verified: 2026-10-08
category: "tech"
tags:
  - openkylin
  - wsl
  - desktop-wsl
  - xrdp
  - ukui
  - storage-planning
  - preflight
status: "verified（远程文件级事实 + 2026-10-08 落机导入、容器/xrdp 服务级与交互式 UKUI 桌面会话全链路实测；含一次黑屏故障的根因定位与用户级修复）"
security_level: "public"
source: "方法论编排 session sc-20260930-openkylin-desktop-wsl（R→I→E→V→C，standard）与 sc-20261008-openkylin-desktop-wsl-install（落机安装）。一手信源：openKylin 官方下载中心与 CDN 元数据（2026-09-30 实测 HTTP HEAD/Range，2026-10-08 复核未变）、Gitee openkylin/docs 官方《openKylin-WSL版本安装》文档（master）、本包 references/wsl-install-sparse-vhd-guide.md 最小镜像本机实测、2026-10-08 桌面镜像本机导入实测（Win10 26220 + WSL 3.0.2.0：51.6 秒导入成功、1900 包、VHD 13.01 GiB、xrdp/xrdp-sesman active、3390 监听）。"
---

# openKylin 3.0 双 WSL 镜像对照与选型参考

> openKylin 3.0 下载中心对 x86 提供**两种** WSL 形态：336M 的最小镜像与 6.1G 的 Desktop WSL 镜像。本包[实测指南](wsl-install-sparse-vhd-guide.md)只覆盖前者；本文补齐后者的**远程可证事实**、选型决策与磁盘规划，并把所有未经落机验证的运行时结论显式标注、给出后续实测验收清单。
>
> **🟢 2026-10-08 落机实测更新（Win10 26220 + WSL 3.0.2.0）**：桌面镜像已按 §7 清单完成导入、容器级验收与**交互式 UKUI 桌面全链路**——51.6 秒流式导入成功（零失败）、软件包 **1900**（较最小镜像 +1495）、解压体积候选 **k=3（约 12.1 GiB，压缩比 1.97×）消歧**、VHD 实测 **13.01 GiB**、同盘标准路径峰值实测 **19.2 GiB**、`xrdp`/`xrdp-sesman` active 且 3390 监听正常、Windows 侧 `localhost:3390` 转发可用；首次登录出现的**纯黑屏已定位并修复**（根因 `startwm.sh` 清掉 `XDG_RUNTIME_DIR` 致窗口管理器 KWin 冷启动不驻留，用户级 `~/.xsession` 补环境变量 + WM 看门狗，重登验证通过，见 §5.1）。唯一失败单元为良性的 `systemd-binfmt`。下文以【2026-10-08 实测】标注落机结论。
>
> 配套萃取模式：[大归档零下载远程预检法](../../../../retrospective/patterns/code-patterns/large-archive-remote-preflight.md)（本文体积/格式结论的取得方法，可迁移到任意 GB 级归档）。

---

## 1. 证据等级声明（先读）

| 标记 | 含义 | 本文中的项目 |
|---|---|---|
| 【远程核验】 | 2026-09-30 在本机通过 HTTP HEAD/Range 请求直接取得，可复现（2026-10-08 复核未变） | 真实 URL、精确字节数、MD5、gzip 魔数、gzip ISIZE、归档头部条目结构 |
| 【2026-10-08 实测】 | 桌面镜像落机导入后直接测得 | 导入耗时、软件包数、真实 VHD、ext4 有效数据（k 值消歧）、流式写入证实、xrdp/sesman 服务态、3390 监听、localhost 转发、失败单元、**mstsc→xorg 交互 UKUI 桌面会话（黑屏已修复后验证可正常进入）** |
| 【官方口径】 | 官方文档/下载页面声明，未独立验证 | 官方未覆盖的黑屏类运行时故障（文档 FAQ 仍只 2 条，不含 WM/XDG 排障） |
| 【推断】 | 由已核验事实外推，附依据与不确定性 | （原"解压 tar 候选取值/VHD 系数"两项已于 2026-10-08 实测落定） |
| 【待实测】 | 只有真实操作后才能回答 | `--shutdown`（整机 WSL 重启）后 eth0 IP 是否漂移（本机 `--terminate` 单发行版未漂移）；内存导入失败阈值下界；unregister 物理回收 |

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
| gzip ISIZE（解压大小 mod 4 GiB） | 1,182,607,360 字节 = 1.101 GiB（未回绕） | 103,258,112 字节 = 98.5 MiB（**已回绕；2026-10-08 落机消歧 k=3，真值约 12.1 GiB，见 §4.1**）【2026-10-08 实测】 |
| 架构 | 仅 AMD64（x86）【官方口径】 | 仅 AMD64（x86）【官方口径】，无 ARM/LoongArch/RISC-V 形态 |
| 图形桌面 | 不含；纯命令行 | 含 xrdp 远程桌面通路与 UKUI 桌面预装；xrdp/xrdp-sesman 开箱 enabled+active，mstsc→xorg 实测可进完整 UKUI 桌面（首登黑屏按 §5.1 修复）【官方口径+2026-10-08 实测】 |
| 官方导入命令 | `wsl --import openKylin .\openKylin <镜像> --version 2` | `wsl --import openKylin-3.0-desktop D:\WSL\openKylin-3.0-desktop <镜像> --version 2`【2026-10-08 实测，51.6 秒成功】 |
| 默认账号 | `openkylin/openkylin`【官方口径+最小镜像实测】 | `openkylin/openkylin`【官方口径+2026-10-08 实测：sudo 接受该口令；UID 1000】 |
| 本机实测状态 | 已实测（Win10 19044 + WSL 2.9.3.0，405 包，VHD 约 1.3 GB） | **已实测（2026-10-08，Win10 26220 + WSL 3.0.2.0）**：51.6 秒导入、1900 包、VHD 13.01 GiB、xrdp 链路 active；交互 UKUI 桌面经 mstsc→xorg 实测可进入（首登黑屏已按 §5.1 修复） |

> 文件名同源（`openKylin-3.0[-desktop]-wsl-amd64.wsl`）、同日构建、同容器格式、同文档同章节描述，支持"二者是同一打包流水线的两种目标形态"的判断；软件包计数实测 **405 → 1900（桌面增量 +1495 包）【2026-10-08 实测】**，但**两者的软件包清单包含关系仍未逐包 diff**（需全量列目），"桌面镜像 = 最小镜像 + 桌面包"依然是合理推断而非已核验事实。

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

> **🟢 2026-10-08 落机消歧：k=3，真实解压 tar ≈ 12.1 GiB（12,988,160,000 字节），整体压缩比 1.97×【2026-10-08 实测】**。
>
> 未做"全量解压为纯 tar"的字节级对账（避免再落一份 ~12 GiB 临时文件），改用导入后 ext4 有效数据双向夹逼：`df -B1 /` 实测已用 **13,380,390,912 字节（12.46 GiB）**。
> - **排除 k=2（tar 8.1 GiB）**：ext4 已用反比 tar 大 4.3 GiB（54%），该差额只能来自块松弛/元数据/日志，对 1900 包规模的 rootfs 不可能到 50% 量级；
> - **排除 k≥4（tar ≥16.1 GiB）**：tar 体积 ≈ 文件有效载荷 + 每条目 512 B 头，要比 ext4 有效数据大出 ≥3.6 GiB，需要约 700 万以上条目头，不可能；
> - **k=3 自洽**：tar 12.1 GiB 与 ext4 已用 12.46 GiB 相差 0.36 GiB（3%），方向上 ext4 略大（4K 块分配松弛 + 日志 + 元数据），量级吻合。
>
> 残余不确定性：硬链接/稀疏文件的 tar 记账方式可能在小数位上移动结论，但 k 值整数级判定不受影响（相邻候选间距 4 GiB）。方向性预期（压缩比低于最小镜像 3.36×）以 1.97× 命中。

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

> **🟢 2026-10-08 实测对账（真值 k=3，同盘 D:）【2026-10-08 实测】**：
>
> | 口径 | 事前估算（k=3 未列，按邻列内插约 14+6≈20） | 实测值 |
> |---|---|---|
> | 导入后 VHD（逻辑大小＝真实占用，非稀疏） | 模型 1.17×tar ≈ 14.2 GiB | **13.01 GiB**（13,971,226,624 字节） |
> | VHD / ext4 有效数据（12.46 GiB） | —— | **1.044**；VHD / tar(k=3) ≈ **1.075** |
> | 同盘标准路径峰值（`.wsl` + VHD） | 16～25 GiB | **19.2 GiB**（D: 54.88 → 35.73 GiB，差值精确对账） |
> | 导入耗时 | "分钟级"【推断】 | **51.6 秒**（导入前空闲内存 11.94 GiB，一次成功零失败） |
>
> 结论修正：① 单一观测点的 1.17 VHD 系数在桌面镜像上复测为 **1.04～1.08**（系数随镜像内容/文件尺寸分布变化，不宜当通用常数）；② 事前 20/25/30 GiB 三条建议线对真值（19.2）全部安全，25 GiB 同盘线仍推荐（余量 ~6 GiB）；③ 跨盘场景容纳行① 实测仅需 **~14 GiB**（原 20 GiB 起步线偏保守约 6 GiB，作为安全余量保留无害）。

**流式写入机制说明（2026-10-08 已证实）**：~~`wsl --import` 直接读取 gzip tar 时，通常以流式解压写入 VHD……未在桌面镜像实测确认~~。桌面镜像**直接 `wsl --import` gzip `.wsl` 已实测为流式**：导入前后 D: 占用差值恰为 6.14（`.wsl`）+ 13.01（VHD）= 19.15 GiB，**不存在第三份临时 tar**，标准路径峰值即"VHD + `.wsl`"两段。只有导入失败后改用实测指南中"先以 .NET GzipStream 解压为纯 tar 再 import"的排障路径时，完整 tar（本案约 12.1 GiB）才会真实落盘，按行③预留。

> 本机 2026-09-30 时点 C: 剩 2.3 GB、D: 剩 4.8 GB，不具备导入条件，这是本文当时停在远程核验的直接原因；2026-10-08 磁盘已腾出（C: 61.2 / D: 54.9 GiB 空闲）后完成实测。安装目录可用 `wsl --import <名称> <目标目录> <镜像>` 的第二参数指定到任意数据盘，无需占用系统盘。

---

## 5. 桌面镜像使用路径（官方口径 + 2026-10-08 逐条实测标注）

> 📖 **日常使用入口**：导入完成后，"每天怎么启动桌面、一键启动器怎么做、用完怎么关、常见问题怎么办"已独立成篇，新手直接看 [openKylin 桌面启动与日常使用教程](wsl-desktop-startup-tutorial.md)。本节保留官方流程的逐条实测记录与排障细节。

以下步骤来自官方《openKylin-WSL版本安装》文档（Gitee master，2026-09-30 取全文），2026-10-08 在本机逐条验证（标注✅者为已实测）：

1. 环境门槛：Windows 10 2004（内部版本 19041）及以上或 Windows 11，管理员 PowerShell；本机 Win10 26220 + WSL 3.0.2.0 ✅；
2. `wsl --install`、`wsl --set-default-version 2`；
3. 下载 `openKylin-3.0-desktop-wsl-amd64.wsl`（下载后先按 §2 的 MD5 校验）；本机 6.14 GiB 约 3 分钟下完 ✅；
4. `wsl --import openKylin-3.0-desktop D:\WSL\openKylin-3.0-desktop .\openKylin-3.0-desktop-wsl-amd64.wsl --version 2`；**51.6 秒成功，流式导入不落临时 tar** ✅（发行版名与官方示例不同，用带版本号的名字避免与最小镜像撞名）；
5. `wsl -d openKylin-3.0-desktop` 进入命令行，默认账号密码 `openkylin/openkylin`；实测默认用户 `openkylin` UID 1000、sudo 接受该口令 ✅；
6. 取内网地址：`ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1`（取 IPv4）；本机实测 `172.25.189.68` ✅；
7. Windows 打开"远程桌面连接"（mstsc，未预装可从微软官网下载），计算机栏填 `localhost:3390`；首次连接默认弹黄色证书警告（xrdp 自签证书 CN=`localhost.localdomain`，与 `localhost` 名称不匹配且颁发者不受信，本机回环无真实风险）——临时可勾"不再询问"点【是】；**根治方案（2026-10-08 本机已验证）为重签 SAN 覆盖 localhost/127.0.0.1 的证书并导入 Windows 当前用户受信任根，此后直进登录窗**，完整脚本与回滚见[启动教程 §4.1](wsl-desktop-startup-tutorial.md)；
8. 登录窗 Session 选 **xorg**，用户名/密码均为 `openkylin`，进入 UKUI 桌面；**2026-10-08 实测可正常进入完整 UKUI（壁纸/任务栏/开始菜单/桌面图标齐全）**——但**首次登录出现纯黑屏**，根因与修复见 §5.1（本镜像必踩，导入后建议先按 §5.1 打补丁再登录）；
9. 注意：xrdp 默认端口 **3390**（非标准 RDP 3389）、开箱 enabled 且启动即 active ✅；**WSL `--shutdown` 后 eth0 IP 可能变化**（本机 `--terminate` 单发行版后 IP 未变，`--shutdown` 是否漂移待复现），嫌麻烦直接用第 7 步的 `localhost:3390`。

### 5.1 实测排障：登录后纯黑屏（KWin 窗口管理器冷启动不驻留）

> 这是 2026-10-08 首登实测**实际命中**的故障（此前只在 §6 登记为"外部通用排查方向"，现已取得 openKylin 镜像内证据与修复）。官方 FAQ 不覆盖。

**症状判别（三步，避免误判成"没装好"）**：xrdp 登录窗认证通过、窗口能连上，但进入后整屏纯黑、无任务栏无壁纸。先在 WSL 里取进程证据：

```bash
# 发行版内执行（或 wsl -d openKylin-3.0-desktop -u openkylin -e bash -c '...'）
pgrep -a -x kwin_x11          # 黑屏根因信号：无输出 = 窗口管理器没在跑
ps -ef | grep -E "ukui-panel|peony-qt-desktop|ukui-session" | grep -v grep   # 这些若都在，说明桌面其实起来了、只缺 WM
grep -i "XDG_RUNTIME_DIR" ~/.config/ukui-session/ukuismserver.log | head     # 命中 "not set" 即本故障
```

**根因（证据链）**：openKylin 3.0 的 UKUI 4.x 窗口管理器是 **KWin**（`kwin_x11`，非旧版 ukwm；包 `kwin-x11` 已预装、`x-window-manager` alternatives 也指向它）。`/etc/xrdp/startwm.sh` 在启动会话前执行了 `unset XDG_RUNTIME_DIR`；ukui-session 在 Xorg ready 仅约 1 秒后经 ukuismserver 拉起 `kwin_x11`（日志 `the wm start command is ("kwin_x11")`），此时 `XDG_RUNTIME_DIR` 缺失、回退到无效的 `/var/tmp/runtime-openkylin`，**kwin 冷启动不驻留，而会话不会二次拉起** → 无合成器绘制根窗口 = 黑屏。同一 X server 在就绪约 2 分钟后手动 `DISPLAY=:10 kwin_x11 --replace` 却能稳定常驻，证明是**冷启动环境/时序**而非 GL 或安装兼容问题。

**修复（用户级、可逆，不动系统文件/不装包）**：改写 `~/.xsession`（先 `cp ~/.xsession ~/.xsession.bak` 备份）——补回 `XDG_RUNTIME_DIR`，并加一个前 ~15 秒、仅在 WM 缺失时幂等补拉的看门狗：

```sh
#!/bin/sh
[ -z "$XDG_RUNTIME_DIR" ] && export XDG_RUNTIME_DIR="/run/user/$(id -u)"
(
  sleep 3
  for n in 1 2 3 4 5 6; do
    pgrep -x kwin_x11 >/dev/null 2>&1 && exit 0
    kwin_x11 --replace >/tmp/kwin-watchdog.log 2>&1 &
    sleep 2
  done
) &
exec ukui-session
```

**验证（2026-10-08 实测）**：结束旧会话（`pkill -u openkylin -x Xorg`，注意用 `-x` 精确匹配进程名，勿用 `-f` 匹配命令行会误杀自身 shell）后重新 mstsc 登录：稳定进入 UKUI 桌面；存活 kwin 的父进程链为 `kwin_x11 ← ukuismserver ← ukui-session ← xrdp-sesexec`，进程环境 `XDG_RUNTIME_DIR=/run/user/1000` 正确，证明**决定性修复是补回环境变量（会话自此自己成功拉起 WM），看门狗仅为前几秒兜底**（其首次补拉因 WM 已在位报一条 `FATAL ERROR ... open display :10.0` 后即退出，属正常竞态、无害）。回滚：`cp ~/.xsession.bak ~/.xsession`。

> 排查纪律：黑屏先取**进程与会话日志**（xrdp-sesman.log、~/.config/ukui-session/ukuismserver.log、~/.xsession-errors、~/.xorgxrdp.*.log）区分"会话没起 / WM 没起 / GL 起不来"三类，不要直接重启 WSL 或重装——本机这套证据把三类里的第二类钉死了。本次排障已萃取为可复用模式：[xrdp 黑屏三层分诊法（连接/会话/窗口管理器）](../../../../retrospective/patterns/code-patterns/xrdp-black-screen-window-manager-triage.md)（L1 单案例，含 6 反模式与跨桌面/跨网关迁移）。

官方 FAQ 仅两条：WSL2 内核未安装（装 https://aka.ms/wsl2kernel ）、远程桌面连接失败（查 xrdp 服务与 3390 端口）。磁盘/内存门槛、包清单、VHD 体积、导入失败排障均未覆盖——最小镜像侧由[实测指南](wsl-install-sparse-vhd-guide.md)补齐，桌面镜像侧由本文 2026-10-08 实测与 §7 清单补齐。

**同名冲突提醒**：在同一台 Windows 上并存两种镜像时，`wsl --import` 的发行版名必须不同（如 `openKylin-3.0` 与 `openKylin-3.0-desktop`）；重名导入会直接失败，也不要覆盖已有发行版的安装目录。2026-10-08 实测：导入不改变默认发行版星标（导入前后默认均为 `podman-machine-default`）✅。

---

## 6. 选型决策

| 你的诉求 | 选择 | 依据 |
|---|---|---|
| 命令行开发、跑脚本/服务、容器式工具链 | **最小镜像** | 下载量为桌面镜像的 1/18.7；VHD 实测约 1.3 GB；导入 8 秒（最小镜像实测） |
| 必须在 Windows 上获得**完整 UKUI 桌面会话**（开始菜单/设置/全套桌面应用） | **Desktop WSL 镜像** | xrdp 全桌面预装，免自行解决桌面依赖【官方口径+服务级实测 active】；实测代价：下载 6.14 GiB（约 3 分钟）、**同盘峰值 19.2 GiB、VHD 长期 13.0 GiB、导入 51.6 秒**【2026-10-08 实测】；事前 25～30 GiB 建议线偏保守但仍推荐作余量 |
| 只想在 WSL 里运行**个别 Linux GUI 应用**（编辑器、浏览器、工具窗口等） | **优先 WSLg**，不选 6.1 GiB 桌面镜像 | WSLg 提供单应用集成窗口（Win11 及较新 Win10/WSL 支持，以本机 `wsl --version` 能力为准），与最小镜像搭配即可，零额外桌面载荷；它与"完整桌面会话"是两种需求，WSLg 不提供完整 UKUI 会话——只有需要完整桌面会话时才应转向上一行的桌面镜像 |
| 想看桌面但磁盘紧张 | 虚拟机路径或最小镜像自装桌面（自行承担依赖与排障成本，官方未给此路径文档） | 虚拟机方案见 [03 安装路径](../concepts/03-install-paths.md) §3.3 |
| 长期生产/多人环境 | 两个镜像都需先做安全加固（改弱口令、限制端口）再评估 | 见下节 |

> **选型定性**：Desktop WSL 不是"更好的 WSL"，而是"带完整桌面会话的 WSL"。两者机制完全相同（§8-I-1），桌面镜像的全部增量都是在为 xrdp + UKUI 全桌面买单——18.7 倍下载体积、数倍至数十倍磁盘占用、额外一条远程桌面攻击面。**没有完整图形桌面会话需求时，这些代价纯属浪费**：命令行需求选最小镜像，零散 GUI 应用需求走 WSLg；只有"必须在 Windows 上获得一整个 UKUI 桌面（开始菜单/系统设置/全套桌面应用同一会话）"才选桌面镜像。

**最小镜像实测经验对桌面镜像的可迁移性**：

- 可直接迁移（容器格式同构【远程核验】+ WSL 机制通用）：`.wsl` 是 gzip tar 而非 APPX 的判断、`wsl --import` 命令形态、PATH 裁剪时用 `$env:WINDIR\System32\wsl.exe` 全路径与 `WSL_UTF8=1`、默认发行版星标不被 import 改变的验收项、稀疏 VHD 的 `--set-sparse true --allow-unsafe` 拦截与 diskpart compact 双路径（机制相同，**收益与风险随体积放大**）；
- 需重新观测、不可照搬数值：导入失败与空闲内存的阈值关系、导入耗时、VHD 实际大小与稀疏化收益——**2026-10-08 已取得桌面镜像观测点**：空闲内存 11.94 GiB 时零失败、导入 51.6 秒、VHD 13.01 GiB（非稀疏，逻辑＝真实占用，全新系统无洞可回收）；内存下界仍未测定（本次高水位一次成功，不构成阈值证据）；
- 桌面镜像新增的未知面：xrdp/UKUI 相关 systemd 服务在 WSL2 容器内的启动状态——**2026-10-08 实测**：`systemctl --failed` 全机仅 1 个失败单元 `systemd-binfmt`（WSL 宿主已预置 WSLInterop binfmt 注册，systemd-binfmt 遇重复注册退出 1；单元自带 generator drop-in 在失败后把 `:WSLInterop:M::MZ::/init:FP` 重新注册恢复，属良性且有自恢复证据），未见 acpid/蓝牙/电源类失败；xrdp、xrdp-sesman 均开箱 enabled+active。**交互登录实际命中一次纯黑屏**，已按 §5.1 定位为 `XDG_RUNTIME_DIR` 被清导致 KWin 冷启动不驻留（非 GL/硬件类、非外部传闻的黑屏），用户级修复并经重登验证；至此该镜像桌面链路从服务到交互全通。

**安全注意**：预置弱口令 `openkylin/openkylin` 与监听 3390 的 xrdp 仅适用于本机体验——首次进入立即 `passwd`；不要把 3390 做公网端口映射；不用时 `wsl --shutdown <发行版名>`。

---

## 7. 验收清单（2026-10-08 已执行：8 项实测闭环，第 9 项卸载用户选择不执行）

目标盘按 §4.2 预留空间后（同盘建议 ≥25 GiB；若预计走手动解压 tar 的排障路径则 ≥45 GiB），按下列清单一次性采集，可直接把本文【待实测】项转为实测结论。**2026-10-08 实测环境：Win10 26220 / WSL 3.0.2.0 / 内核 6.18.40.1-1 / D: 同盘（导入前 54.88 GiB 空闲）/ 空闲内存 11.94 GiB**：

1. ✅ 下载后校验：MD5 = `df559de7155ef7c6fe088b2168035c5a`（Get-FileHash 精确一致）、字节数 = 6,592,986,686（精确一致）、魔数 `1F 8B 08 00`；
2. ✅ 解压大小消歧（等价路径）：未落整份纯 tar，以导入后 `df -B1 /` 有效数据 13,380,390,912 字节（12.46 GiB）双向夹逼，确认 **k=3（tar ≈ 12.1 GiB，压缩比 1.97×）**，论证见 §4.1；逐字节 tar 对账列为可选复核项；
3. ✅ 导入耗时 **51.6 秒**（10:15:30→10:16:22）；导入前空闲物理内存 11.94 GiB；**未复现** `E_UNEXPECTED/E_ABORT`（高水位一次成功，无失败指纹可记；不构成内存阈值证据）；
4. ✅ 验收五项：`wsl -l -v` 在列且为 WSL2、默认星标保持在 `podman-machine-default`；`/etc/os-release` = openKylin 3.0 (huanghe)；默认用户 `openkylin` UID 1000；`df -h /` 13G/1.0T；软件包 **1900**（`dpkg-query -W | wc -l`，较最小镜像 405 包 **+1495**）；`/etc/wsl.conf` 含 `[user] default=openkylin` 与 `[boot] systemd=true`；
5. ✅ xrdp 桌面链路（**全链路含交互桌面，已闭环**）：eth0 IPv4 = **172.25.189.68**，`--terminate` 重启后 IP 未变；`ss -lnt` 见 `*:3390` LISTEN；Windows 侧 `127.0.0.1:3390` TCP 转发测试成功，实测 `mstsc /v:localhost:3390` 可连（绕开 IP 漂移）；mstsc → Session xorg → openkylin 登录，**首登纯黑屏**经 §5.1 定位（KWin 冷启动不驻留，根因 `XDG_RUNTIME_DIR` 被 startwm.sh 清掉）并以用户级 `~/.xsession` 修复，**重登后稳定进入完整 UKUI 桌面**（壁纸/任务栏/开始菜单/图标齐全，kwin 父进程链与会话环境正确）；残留观察项：整机 `wsl --shutdown` 后 IP 是否漂移（用 localhost 接入可规避，不影响结论）；
6. ✅ `systemctl --failed` 全机**仅 1 个**失败单元 `systemd-binfmt`（良性：WSL 宿主预置 WSLInterop 注册致重复注册退出 1，自带 drop-in 恢复注册，证据见 §6）；未见硬件相关服务失败；`xrdp`/`xrdp-sesman` 均 enabled+active；
7. ✅ VHD 逻辑大小＝真实占用 = **13,971,226,624 字节（13.01 GiB，`GetCompressedFileSizeW` 对账）**；VHD/ext4 有效数据 = **1.044**、VHD/tar(k=3) ≈ **1.075**——**修正 1.17 旧系数**（单点观测非常数）；
8. ✅ 稀疏 VHD：导入产物默认非稀疏且逻辑＝真实占用，全新桌面系统"当下无洞可回收"再次验证，未执行 `--set-sparse`（无收益且承担 `--allow-unsafe` 风险）；后续在 WSL 内删除大文件后再按实测指南 §5 决策；
9. ⚪ 卸载清理：用户保留该发行版，未执行 `wsl --unregister`；命令与回收验证留待将来弃用时执行。

---

## 8. I 阶段：核心洞察（四元组）

### I-1　两个按钮同源同构，差异是"内容载荷"而非"安装机制"

- **陈述**：两镜像同为 gzip tar rootfs、同日构建、文件名同源、同一篇官方文档、同一条 `wsl --import` 路径、同一默认账号；机制层零差异，全部差异集中在载荷（是否含 xrdp + UKUI 全桌面）与 18.7 倍的下载体积。
- **证据**：F-046（魔数与头部条目同构）、F-045（命名、构建日期与下载条目）、F-048（官方文档同章同导入路径与账号体系）。F 编号对应知识包 [index.md H 组](../index.md)。
- **反常识**："Desktop WSL"听起来像另一个产品或另一套安装器；实测它没有任何安装机制上的新东西，选型问题因此可简化为纯业务问题——"要不要完整图形桌面会话"。
- **行动**：按 §6 决策表二选一即可，不必为"桌面版会不会更难装"预留额外学习成本（2026-10-08 实测同一条 import 路径 51.6 秒成功，机制零差异再获证据）；包数差已量化（405→1900，+1495），但逐包包含关系仍未 diff，勿把"同源"表述成"桌面镜像 = 最小镜像 + 桌面包"的事实等式。

### I-2　6.1G 下载只是冰山一角，且大镜像恰好让 gzip ISIZE"秒查解压大小"的技巧失效

- **陈述**：真实下载 6.14 GiB，而导入后还要叠加 VHD 长期占用与同盘 `.wsl` 共存峰值（手动解压排障路径另有完整 tar，分层口径见 §4.2）；用于廉价估算解压体积的 gzip ISIZE 字段在 >4 GiB 后回绕，本案例读出 98.5 MiB 的荒谬小值，头尾信息只能给出 8.1/12.1/16.1/20.1 GiB 离散候选（k≥6 时 ≥24.1 GiB）。**2026-10-08 落机后真值落定：k=3（tar 12.1 GiB）、VHD 13.01 GiB、同盘峰值 19.2 GiB——事前规划区间正确包裹真值，点估（k=4 参考列）偏差约 3 GiB，再次验证"区间规划、不押单点"的必要性。**
- **证据**：F-045（精确 Content-Length）、F-047（ISIZE 回绕与候选区间）、最小镜像实测的 VHD/tar 1.17 与临时占用构成；2026-10-08 实测（df 有效数据夹逼 k=3、VHD 13.01 GiB、峰值 19.2 GiB、51.6 秒流式导入）。
- **反常识**：直觉按下载页"6.1G"预留空间；真正失败模式是盘备好 7 GiB 却在导入途中盘满，留下半成品 VHD；更隐蔽的是网上常用的"读 gzip 末 4 字节估大小"技巧在大文件上静默给出错误答案而不报错。
- **行动**：大归档下载前一律走[零下载远程预检](../../../../retrospective/patterns/code-patterns/large-archive-remote-preflight.md)五步；磁盘按 §4.2 三档口径依部署路径（跨盘/同盘/排障）规划，而非按下载体积或单一上限；**全量解压并非消歧 ISIZE 的唯一手段——导入后用 ext4 有效数据双向夹逼即可在整数 k 级定档，省一份 ~12 GiB 临时 tar**。

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
| 🟢 五轮回填（落机实测，2026-10-08） | 实测可能推翻事前推断：1.17 系数、分钟级导入、流式假设、k 值四点均需对账；且实测者容易把"服务 active"夸大成"桌面好用" | §4.2 增实测对账表（系数修正为 1.04～1.08、导入 51.6 秒、峰值 19.2 GiB）；§4.1 以 ext4 有效数据夹逼 k=3 并保留残余不确定性声明；流式写入由"假设"改为"已证实"；全文唯一保留的【待实测】收敛为交互 GUI 登录观感，服务级与桌面会话级显式分开表述 |
| 🔴 六轮实战（首登黑屏，2026-10-08） | 服务 active 后果然 ≠ 桌面可用：用户首登纯黑屏。攻击点：①勿凭"黑屏"二字猜 GL/重装/重启；②勿把手动救活该 WM 当成根治；③看门狗若反复拉起会制造多 WM 竞态 | 先取四类日志+进程证据，区分"会话没起/WM 没起/GL 起不来"，钉死为 WM(KWin) 没起；沿父进程链与 ukuismserver 日志定位到 `XDG_RUNTIME_DIR` 被 unset 的冷启动根因；修复用用户级 `~/.xsession`（补环境变量+幂等看门狗，备份可回滚），重登后以父进程链证实"会话自起 WM、看门狗仅兜底"，新增 §5.1；未改系统文件、未装包 |

V 门结论：4 视角全覆盖，实质意见 11 条，全部采纳；另完成三轮用户驱动修正（二/三/四轮）与两轮落机回填——五轮：四项事前推断逐条对账（1 修正、3 证实）；**六轮：首登黑屏实战，证据驱动定位 KWin 冷启动根因并用户级修复、重登验证，桌面链路从服务到交互全通**。无遗留未决故障项（仅 `--shutdown` IP 漂移、内存失败下界、unregister 回收为可选的长期观察项）。

---

## 10. 局限声明

1. ~~桌面镜像未落机导入~~（2026-10-08 已落机）：导入耗时（51.6 秒）、真实 VHD（13.01 GiB）、包数（1900）、xrdp 服务态均已实测；~~交互 GUI 登录观感未确认~~（同日已确认可进入完整 UKUI）；**残留**：内存失败阈值下界未测定（11.94 GiB 空闲一次成功，无失败指纹）；
2. ~~ISIZE 候选未消歧/流式未证实~~（2026-10-08 已关闭）：k=3 由 ext4 有效数据双向夹逼定档，但未做整份纯 tar 的逐字节对账（残差小数量级，整数 k 判定不受影响）；VHD 系数已由 1.17 单点修正为 1.04～1.08 区间观测，随内容分布变化，仍非常数；
3. 事实时点：文件级事实 2026-09-30 取得、2026-10-08 复核未变（镜像仍为 2026-08-28 构建）；官方今后可能更新镜像，下载前应以页面当时的字节数与 MD5 重新核验；
4. 社区零实测的检索结论受检索词与平台覆盖限制（bbs.openkylin.top 站内检索 + 公开搜索引擎），不排除有未被收录的个人博客记录；
5. ~~黑屏等桌面会话故障仅作排查方向~~（2026-10-08 已在本镜像实际命中并闭环，见 §5.1）：该结论基于**单次首登+一次重登验证**，黑屏根因（`startwm.sh` unset `XDG_RUNTIME_DIR` → KWin 冷启动不驻留）与用户级修复在本镜像/本 WSL 版本证据充分；不同 openKylin/WSL 版本的 startwm 脚本若变化，修复仍需按 §5.1 的判别三步重新取证；systemd 唯一失败单元为良性 `systemd-binfmt`。

---

## 11. 参考资料

- [openKylin 桌面启动与日常使用教程（一键启动器/登录/关闭/FAQ）](wsl-desktop-startup-tutorial.md)
- [openKylin 3.0 WSL 安装与稀疏 VHD 实操指南（Windows 10 实测）](wsl-install-sparse-vhd-guide.md)
- [openKylin 官方下载中心](https://www.openkylin.top/downloads/index-cn.html)
- 官方文档《openKylin-WSL版本安装》：Gitee `openkylin/docs` → `1入门与参与/1_3系统下载与安装指南/05_openKylin-WSL版本安装.md`
- [大归档零下载远程预检法（模式）](../../../../retrospective/patterns/code-patterns/large-archive-remote-preflight.md)
- [WSL 导入内存分诊与稀疏 VHD 决策模式](../../../../retrospective/patterns/code-patterns/wsl-import-memory-triage-sparse-vhd.md)
- [xrdp 黑屏三层分诊法（连接/会话/窗口管理器）](../../../../retrospective/patterns/code-patterns/xrdp-black-screen-window-manager-triage.md)
- [03 安装路径全景与选型](../concepts/03-install-paths.md)

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20260930-openkylin-desktop-wsl | msg=知识沉淀：Desktop WSL 双形态对照 | ctx={"scenario":"knowledge","chain":"R-I-E-V-C"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G3 | event=GATE_PASSED | session=sc-20260930-openkylin-desktop-wsl | msg=模式「大归档零下载远程预检法」L1单案例，5反模式，含跨域迁移
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V9 | event=GATE_PASSED | session=sc-20260930-openkylin-desktop-wsl | msg=4视角11意见全部采纳
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261008-openkylin-desktop-wsl-install | msg=落机安装：执行§7待实测清单 | ctx={"scenario":"problem","chain":"R-I-F-V-C"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C1 | event=DOWNLOAD_VERIFIED | session=sc-20261008-openkylin-desktop-wsl-install | msg=6592986686字节+MD5 df559..精确匹配，约3分钟
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C2 | event=IMPORT_OK | session=sc-20261008-openkylin-desktop-wsl-install | msg=流式导入51.6秒零失败，1900包，VHD 13.01GiB
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261008-openkylin-desktop-wsl-install | msg=§7清单8/9闭环；待实测项收敛为GUI观感
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I1 | event=ROOTCAUSE_FOUND | session=sc-20261008-openkylin-desktop-wsl-install | msg=首登黑屏根因：startwm.sh unset XDG_RUNTIME_DIR→KWin冷启动不驻留；证据=四类日志+父进程链
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C3 | event=FIX_VERIFIED | session=sc-20261008-openkylin-desktop-wsl-install | msg=用户级~/.xsession补XDG_RUNTIME_DIR+WM看门狗(已备份)，重登进入完整UKUI；会话自起WM、看门狗仅兜底
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V9 | event=GATE_PASSED | session=sc-20261008-openkylin-desktop-wsl-install | msg=六轮实战：桌面链路服务→交互全通，无遗留未决故障；新增§5.1黑屏排障
[CMD-LOG] | level=INFO | cmd=extraction | step=S6 | event=PATTERN_STORED | session=extr-20261008-xrdp-black-screen-wm-triage | msg=新模式「xrdp黑屏三层分诊法」入库 code-patterns，L1单案例/6反模式/跨域迁移，toctree登记+双向回链 | ctx={"maturity":"L1","validation_count":1}
```
