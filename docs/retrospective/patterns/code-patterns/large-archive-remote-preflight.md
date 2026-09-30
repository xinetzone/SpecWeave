---
type: Pattern
id: "large-archive-remote-preflight"
title: 大归档零下载远程预检法
version: 1.0
date: 2026-09-30
maturity: L1
validation_count: 1
reuse_count: 0
tags: [HTTP-Range, gzip, tar, preflight, checksum, magic-bytes, storage-planning, WSL, large-file, powershell]
source: "openKylin 3.0 Desktop WSL 镜像（6.14 GiB）下载前远程核验实操（方法论编排 session sc-20260930-openkylin-desktop-wsl）"
related_patterns:
  - "pretrained-model-download-validation"
  - "wsl-import-memory-triage-sparse-vhd"
  - "wsl-distro-install-migration-guide"
  - "docker-image-layered-verification"
---

# 大归档零下载远程预检法

> 面对 GB 级归档/镜像（系统镜像、容器 rootfs、数据集、虚拟机模板），在**磁盘不足、带宽昂贵或仅需做选型决策**时，不下载全量，仅用 HTTP 元信息与 Range 请求（通常消耗 KB～数十 MB 流量）完成容器级事实核验：真实下载地址、精确字节数、官方校验值、文件格式、解压体积区间、归档内部结构。

## 适用边界

**适用于**：

- 单文件体积巨大（数百 MB 起），全量下载成本高，而决策只需要格式/体积/校验值/顶层结构；
- 目标盘剩余空间紧张，下载前必须先算出"下载 + 解压/导入膨胀"的总占用再决定是否开始；
- 下载页是跳转链接（`download.php?id=...`），需要还原 CDN 真实文件名与大小；
- 归档格式自带尾部元数据（gzip 流的 ISIZE、ZIP 的中央目录等），可用极小流量读出解压规模线索；
- 需要把"远程可证事实"与"必须本机实测的运行时事实"分层记录的调研场景。

**不适用于**：

- 小文件（直接下载再校验，比构造 Range 请求更省事；下载后校验链路见 [pretrained-model-download-validation.md](pretrained-model-download-validation.md)）；
- 需要验证运行时行为（能否导入启动、服务是否正常、性能如何）——任何远程手段都无法替代，必须落机实测；
- 服务器不支持 Range（首次请求先看响应是否含 `Accept-Ranges: bytes`，不支持则放弃尾部读取）；
- 加密/私有格式且无公开头尾结构文档的归档。

## 核心步骤（五步）

1. **HEAD 跟跳转，拿真实 URL 与精确字节数**
   ```powershell
   curl.exe -sIL "https://example.com/download.php?id=127" |
     Select-String -Pattern "HTTP/|location:|content-length:|accept-ranges:" -CaseSensitive:$false
   ```
   记录三段事实：302 跳转链末端真实 URL、最终响应 `Content-Length`（精确字节，勿用页面上的"6.1G"近似值）、是否支持 Range。页面展示体积常用十进制 GB（÷1000），磁盘/GiB 规划用二进制（÷1024³），两个口径都要算。

2. **从官方页面数据取校验值，不靠猜接口**
   下载页的校验码常由页内 JavaScript 数据结构提供（本案例为 `md5ById` 映射，直接抓页内脚本即可按下载 id 取出 MD5）；另有站点提供独立 `/md5.html`。校验值与下载物**分别取证**，避免同源被篡改时失去校验意义。

3. **Range 取头部小块，二进制方式验魔数**
   ```powershell
   curl.exe -s -r 0-3 "<真实URL>" -o head.bin
   Format-Hex head.bin   # gzip 应为 1F 8B 08 00
   ```
   **必须落盘后用 `Format-Hex` 读，禁止经控制台文本管道看二进制**：本机实测同一次核验走文本管道时，`0x8B` 被控制台编码替换成 UTF-8 替换符的三字节序列 `EF BF BD`，魔数看起来"差一字节"，实为传输毁码而非文件问题。

4. **Range 取 gzip 尾 4 字节读 ISIZE，并强制做 4GiB 回绕判别**
   ```powershell
   $size = 6592986686; $start = $size - 4
   curl.exe -s -r "$start-$($size-1)" "<真实URL>" -o tail.bin
   $isize = [BitConverter]::ToUInt32([IO.File]::ReadAllBytes("tail.bin"), 0)
   ```
   ISIZE 是 gzip 成员**解压后大小对 2³² 取模**的小端 32 位整数。真实解压大小 = `k × 4 GiB + ISIZE`（k 为非负整数）。判别规则：
   - ISIZE 与压缩体积同量级或更大 → k=0，读数即真实值；
   - ISIZE 远小于压缩体积（本案例读出 0.10 GiB，压缩包却有 6.14 GiB）→ **已回绕**，真实值是候选序列 `ISIZE + n×4GiB` 中的某个，头尾信息无法消歧；
   - 消歧依据只能是：同系列小镜像的实测压缩比外推（本案例最小镜像 3.4×，桌面镜像候选中 17.28 GiB ≈ 2.6× 最可能，但**保持为推断**）或全量解压实测；
   - 磁盘规划按候选**上限加余量**给保守值，不采用推断中位数。

5. **取头部小流量块流式解压 + 归档列目，验内容结构**
   ```powershell
   curl.exe -s -r 0-20971519 "<URL>" -o probe.bin   # 仅取前 20 MiB
   # 用 .NET GzipStream 流式解压截断流（流末尾抛异常属预期，try/finally 关句柄即可）
   tar.exe -tf probe.tar | Select-Object -First 40  # 看顶层条目形态
   ```
   tar.gz 类归档的条目从流头部顺序排列，前数十 MB 足以分辨"标准 rootfs 目录（`./dev ./bin ./usr`）""单层 tar 包目录""嵌套压缩包"等结构差异，从而判断能否套用同一套导入工具链。截断解压必然在尾部报错，正常现象。

**产出纪律**：每条结论标注证据等级——【远程核验】（上述步骤直接取得）、【官方口径】（页面/文档声明）、【推断】（压缩比外推等，附依据与不确定性）、【待实测】（运行时行为）。四级不可混写。

## 反模式（均来自本案例实操）

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 用下载页展示体积（"6.1G"）直接做磁盘规划 | 十进制/二进制口径差 + 完全漏掉解压膨胀，实际需要量可达展示值 3 倍以上，导入中途盘满留下半成品 VHD | 步骤 1 取精确字节数，步骤 4 估算解压大小，按"压缩包 + 解压体 + 临时余量"合计规划 |
| 2 | 读到 gzip ISIZE 是个很小的值就当作真实解压大小 | >4 GiB 的归档 ISIZE 必然回绕，0.1 GiB 的读数对应真实 8.7～21.6 GiB 区间，按 0.1 GiB 规划必然失败 | 步骤 4 强制回绕判别，给候选区间与保守上限 |
| 3 | 二进制头经过 shell 文本管道肉眼判读 | 控制台编码把非 ASCII 字节替换为 `EF BF BD`，误判文件损坏/格式不符 | Range 结果一律落盘，`Format-Hex` 读取 |
| 4 | 归档"能远程确认格式"就写"该镜像可正常导入使用" | 文件级事实（格式/大小/校验值/结构）与运行时事实（可启动/服务正常/性能可用）是两个证据层级，混用会让文档给出未经证实的可用性承诺 | 产出纪律四级标注；运行时项进"待实测清单"，不提前下结论 |
| 5 | 只取 `Content-Length` 不验魔数与结构就认定与同系列镜像同构 | 同名后缀可能换容器（rootfs tar / 内含 VHD / 多成员 gzip 形态各异），导入工具链并不通用 | 步骤 3+5 用极小流量确认格式与顶层结构后再迁移工具链结论 |

## 检验标准

- 不下载全量即可回答五问：真实 URL 与精确字节数？官方校验值？格式魔数？解压大小区间与保守规划值？归档顶层结构？
- 所有体积数字同时给出字节数与 GiB 换算，页面口径与实测口径分列；
- 每条结论可回溯到具体 HTTP 响应/页面字段/命令输出；
- 报告显式区分远程可证事实与待实测运行时事实，后者有验收清单承接。

## 跨域迁移

- **容器镜像 tar.gz / OCI bundle**：导入前预检架构目录（`manifest.json`、`repositories` 是否在头部条目中出现）与解压规模；
- **数据集归档（GB～TB 级 tar.gz）**：下载前估算落盘峰值、判断是否需要流式管道（边解压边处理，不落全量）；
- **虚拟机模板（OVA/QCOW2 压缩包）**：选型对比多个模板时，零下载先取得体积/格式清单，再决定下哪一个；
- **模型仓库大权重文件**：与 [pretrained-model-download-validation.md](pretrained-model-download-validation.md) 衔接——本模式负责下载前决策，后者负责下载后多源校验与加载验证。

## 成熟度

**L1（单案例待验证）**：本模式首次完整应用于 openKylin 3.0 Desktop WSL 镜像（6.14 GiB gzip tar）核验，五步全部走通且步骤 3 的反模式在同一案例中真实触发。升级 L2 需在非同构场景（如数据集 tar.gz 或容器镜像仓库）再完整应用一次并验证步骤 4 之外的归档尾部元数据读法（ZIP EOCD 等）。
