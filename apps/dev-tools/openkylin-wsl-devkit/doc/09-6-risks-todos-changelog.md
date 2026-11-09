---
type: "Spec"
title: "npu-toolchain 远程后端：风险、回退、待确认与版本历史"
frontmatter_spec_version: "v2.1.0-draft"
status: "implemented-draft（阶段 0–4 已实施，2026-11-03 实测）"
owner: "未指定"
part_of: "09-npu-toolchain-windows-host.md"
---

# npu-toolchain 远程后端：风险、回退、待确认与版本历史

> **本篇职责**：记录风险矩阵、回滚方案、分阶段实施与状态、待确认问题 Q1–Q6，以及与服务器侧 `all-in-one.sh` 的差异和版本历史。
> **本篇不负责**：技术方案与决策依据见[架构与决策](09-1-backend-and-decision.md)；验收判定见[验收与实测](09-5-acceptance-and-evidence.md)；v1.x 归档见[归档篇](09-7-appendix-v1-wsl-deprecated.md)。

## 7. 风险、回退与分阶段实施

### 7.1 风险矩阵

| # | 风险 | 影响 | 缓解 |
|---|---|---|---|
| R1 | XFS 仅剩 298 GB（99% 已用） | 构建中途写满 | A9 门禁 50 GB；构建前 `df` 检查；必要时 `podman system prune`（需用户批准） |
| R2 | 容器内 LLVM 22 安装失败（conda 通道抖动） | A3 无法达成 | 备选：宿主 conda 缓存离线包 `podman cp` 进容器安装 |
| R3 | Python 包层安装失败（3.14 过新、缺 wheel） | A4/A5 无法达成 | 先补 `scikit-build-core`/`setuptools-scm`；仍失败则仅用宿主 py314 构建纯 Python 层作为兜底 |
| R4 | Docker Hub 不可达 | 无法 pull 新镜像 | 使用远程本地镜像，Containerfile 本地构建 |
| R5 | `podman --remote` 连接切换影响既有 WSL 默认连接 | 既有工作流受影响 | 先不设默认，用 `--remote <name>` 显式调用 |
| R6 | SSH 断线中断长构建 | 构建失败 | 一律 `tmux` + `nohup`，日志留存 |
| R7 | 端口冲突（8890/8892 已占） | Jupyter 无法发布 | 先 `ss -lnt` 与 `Test-NetConnection` 双检，选用 8888/8889 等空闲端口 |
| R8 | 容器 UID 与宿主不一致（现状 `private`） | 新建文件属主错乱 | 重建容器使用 `--userns=keep-id`；或在已验证 777 权限下只读复用 |
| R9 | `podman system df` 报 infra-container 缺失 | 无法统计存储 | 用 `du -sh`/`df` 替代；必要时重建 infra 容器 |

### 7.2 回滚方案

| 触发 | 回滚动作 |
|---|---|
| 容器内 LLVM 22 引入构建失败 | 改用 `/opt/build/llvm21`（21.0.0）重编，规格临时降级到 A3=21.x，并在附录记录偏差 |
| 新建容器异常 | `podman rm -f` 后按 `scripts/run.sh` 以原参数重建（原容器配置已记录于本规格基线表） |
| 镜像重建失败 | 回退到 `localhost/openkylin-npu-toolchain:3.0`（镜像 ID `e7244a0c...`，创建时间 2026-11-02） |
| Windows 侧连接配置污染 | `podman system connection rm remote-ai`；既有 4 条 `podman-machine-*` 不变 |

### 7.3 分阶段实施计划

| 阶段 | 内容 | 完成判据 | 状态（2026-11-03） |
|---|---|---|---|
| 0 | 规格确认（v2.0.0-draft） | 用户批准 | ✅ 已批准（Q1/Q2/Q5 放行） |
| 1 | 预检（本轮已做，只读） | 本规格基线表全部落表 | ✅ 已完成 |
| 2 | 方案 A 连接落地（`podman system connection add`，暂不改默认） | `podman --remote info` 通过 | ✅ 连接条目已注册（`default=false`）；`--connection` 形式受客户端缺陷阻断，`--url` 直连通过（偏差 D1） |
| 3 | 容器内补 LLVM 22 + Python 包层 | A3、A8、A6 PASS | ✅ LLVM 22.1.8；容器内 uid=1006；A6/A8 实测通过 |
| 4 | 两库构建（若需换 LLVM 22 则重编 npu_tvm） | A4、A5 PASS | ✅ A4/A5 PASS（复用既有 `libtvm.so`，未重编；偏差 D2） |
| 5 | 端口按需发布与 Windows 访问验证 | A7 PASS | ⏸ 未执行（按默认不发布端口，A7 记 N/A） |
| 6 | 端到端复核与容量复核 | A1–A9 全 PASS；`df` 余量 ≥ 50 GB | ✅ A1–A6、A8、A9 PASS；A7 N/A；余量 293 GB |
| 7 | 文档定稿（v2.1.0）与验证脚本更新 | `verify.sh` 与规格一致 | ⏳ 本文档为 v2.1.0-draft，`verify.sh` 更新未启动 |

## 8. 待确认问题清单

| # | 问题 | 阻塞级别 | 建议决策 | 现状 |
|---|---|---|---|---|
| Q1 | 是否允许在远程安装 `llvmdev=22.1.*`（占用少量 XFS 空间，约 0.5–1 GB） | 中（阻塞 A3） | 推荐允许；属镜像内依赖，不污染宿主 | **已决（用户放行并已执行）**：`/opt/build/llvm22` 装成 **22.1.8**，含 clang-22 / lld 23.1.4；见 §9 |
| Q2 | 是否重建 `npu-toolchain` 容器（改用 `--userns=keep-id`） | 中（影响 A8 严格判定） | 推荐重建；原容器仅 22h，无长任务在跑 | **已决（用户放行并已执行）**：同名容器已重建，`--userns=keep-id` 生效（容器内 `uid=1006(ai)`）；`/opt/build` 卷内容完整保留 |
| Q3 | 是否将 `podman-machine-default` 默认连接切换为 `remote-ai` | 低（不阻塞，但影响 UX） | 建议**不切默认**，用 `--connection remote-ai` 显式调用 | **已决（保持不切默认）**：`podman system connection ls` 实测 `podman-machine-default` 为 `default=true`、`remote-ai` 为 `default=false`；`podman --remote --connection remote-ai info` → `5.6.2` / `rootless=true` / `overlay`，显式调用链路可用。如需切换，命令为 `podman system connection default remote-ai`（会改变 WSL 既有工作流，须另行批准） |
| Q4 | Jupyter 是否需要、发布在哪个端口 | 低（非目标默认关闭） | 需要时用 8888→8890 之外的空闲端口，先做占用双检 | **已决（选定宿主 8888 → 容器 8888）**：远程 `ss -lnt` 仅 `8890`、`8892` 在听；Windows `Test-NetConnection` 对 8888/8889/8894 均 `False`（空闲）、对 8890 为 `True`（对照）。备用 8894。按目标 6 仍**不发布**端口——容器端口不可后加，启用时须重建容器并加 `-p 0.0.0.0:8888:8888` |
| Q5 | XFS 99% 已用是否需要在构建前清理（`podman system prune` 可回收约 14 GB 悬空镜像） | 中（影响 R1） | 建议先只读 `podman images` 复核悬空镜像，再经用户批准执行 | **已决（用户放行并已执行）**：执行 `podman image prune -f`，**回收 0 GB**；两个 dangling 条目（13.7 GB / 1.19 GB）为 tagged 镜像的祖先层，prune 无权移除；严格未使用 `-a` |
| Q6 | 是否保留 v1.x 的 `scripts-host/preflight-wsl.sh` | 低 | 保留文件、在规格标注废弃，不删除 | 已定为保留（本轮未动该文件） |

> **注（Q1 历史表述订正，2026-11-03）**：上表 Q1 行的「含 clang-22 / lld 23.1.4」为实施当日的原始记录，为保留决策链的可追溯性，原文不动，仅在此追加订正。经复核，该表述中的 `lld` 自始即 **23.1.4**（22 系 `lld` 从未安装），属偏差 G3 的混装构件；该批 23 系包（`libllvm23`、`lld`、`llvm-openmp` 23.1.4）已隔离移出 `/opt/build/llvm22`，隔离副本（268 MB / 48 文件）随后删除。XFS 可用字节 315,729,219,584 → **316,010,168,320**（+280,948,736 B，约 268 MiB），prefix 内现仅余 22 系。处置证据见[验收与实测 D7](09-5-acceptance-and-evidence.md)。

## 9. 已评估未采纳的决策：13 GiB 基镜像最小化（2026-11-04）

> **结论**：评估结论为「技术上可行、但与风险不匹配」，用户于 2026-11-04 改判 **路径 A（维持现状）**——不建 `openkylin:3.0-minimal`，不裁剪、不 `export`/`import`，新旧镜像与悬空镜像一概不动；原计划 P1–P5 全部取消。

> **二次复核（2026-11-04，只读）**：`S:\.agents\wsl-images\` 侧来源文件的格式与结构已实测，据此订正 §9.1 的来源判断：「官方最小 rootfs 不可得」仅在 registry / apt 仓库 / ISO 三类入口成立；同盘另有官方 `.wsl` 精简 rootfs 归档与两个 `podman export` 归档在场。**该复核只修正事实层与依据，不改变路径 A 决策**；详见 §9.5。

| 项 | 记录 |
|---|---|
| 决策 | 路径 A：维持 `localhost/openkylin:3.0`（单层 13 GiB，tarball 导入）现状 |
| 日期 | 2026-11-04 |
| 决策人 | 用户（自「路径 B：最小 rootfs」改判） |
| 影响面 | 零：本轮结束时 `podman images --all` 24 条与评估前一致；XFS 可用 293 GB 未变 |

### 9.1 rootfs 来源的实测结论（2026-11-04，含同日晚间二次复核）

| 来源 | 判定 | 实测证据 |
|---|---|---|
| 官方最小 rootfs 包（经 registry / apt 仓库 / ISO 入口） | **限定范围内不可得** | `https://registry.openkylin.top/v2/` → `000`；`https://mirrors.openkylin.top/` → 无响应；`https://mirrors.tuna.tsinghua.edu.cn/openkylin/dists/` → `403`；`https://mirrors.aliyun.com/openkylin/iso/` → `404`；`https://mirrors.aliyun.com/openkylin-docker/` → `404`。**原判断（2026-11-04）**：官方最小 rootfs 包不可得。**订正（同日二次复核）**：上述 5 条探测只覆盖 registry、apt 镜像站、ISO 目录三类入口，未覆盖发行版下载页直链，故只能限定为「经上述入口不可得」；同盘已实测存在官方 WSL 精简 rootfs 归档（下表第 4 行、§9.5.2） |
| debootstrap | **不可行（本机远端）** | 远端 `which debootstrap` 无输出；`sudo -n true` → `sudo: a password is required`；rootless 用户命名空间下 `chroot`/`mknod` 受限；`huanghe` 仓库组件为 `main/cross/pty`，非标准三件套，且无 openKylin 专用 debootstrap 脚本。**附注（同日二次复核）**：官方 `.wsl` 归档内含 `./debootstrap/` 目录残留（仅记录目录存在，未据此判断制作者与构建环境）；即便其上游用 debootstrap 构建，也不改变本机远端「不可行」——本机约束是无 sudo 与 rootless 命名空间限制 |
| 从现有 rootfs 裁剪 | **可行但属派生法** | **原判断（2026-11-04）**：原始 tarball 已不在（`/media/pc/data` `-maxdepth 3` 搜索 `*openkylin*.tar*` / `*.wsl` 无命中），唯一可行路径为容器内裁剪 → `podman export` → `podman import` 为新 tag。**订正（同日二次复核）**：① 文件实际位于 `/media/pc/data/ai/.agents/wsl-images/`，相对 `/media/pc/data` 为第 **4** 层，而首轮用 `-maxdepth 3`，差一层即漏检——真因是**检索口径缺陷，不是文件缺失**；`S:` 即 `\\10.16.11.3\ai` 的映射，落点仍是 `/media/pc/data/ai`，不是另一处存储。② 现存两件 tar 均为 `podman export` 产物（pax 扩展头含 `user.overlay.origin` / `user.overlay.uuid` / `user.overlay.impure` 与 `user.crtime_usec` 等仅容器快照导出才带的 xattr），**不是最初 `podman import` 的源 tar**；原始导入源在现存目录清单中未见留存。③「唯一可行路径」不成立：另有官方 `.wsl` 精简 rootfs 归档（下表第 4 行）。裁剪结论本身不变——产物是**派生最小根文件系统**，不能称「官方 minimal」 |
| **官方 WSL 精简发行包（新发现来源）** | **可用来源候选（结构上成立，本轮未实际 import）** | `openKylin-3.0-wsl-amd64.wsl` 352,431,812 B（336.13 MiB）；外层 gzip（`1F 8B 08 00 00 00 00 00 00 03`）+ 内层 GNU tar（`./` 起始，偏移 257 `ustar`）；27,930 条目、解压 1,182,607,360 B（1.10 GiB）；`./usr/` 988.8 MiB；无 `/usr/lib/firmware`、`/usr/lib/modules`，无桌面组件；`/usr/lib/os-release` → `NAME="openKylin"` / `VERSION="3.0 (huanghe)"` / `VERSION_ID="3.0"` / `VERSION_CODENAME=huanghe`；归档内无 `wsl-distribution.conf` / `oobe.sh` / `install.tar` / `icon.ico` / `terminal_profile.json`（不属新版 `.wsl` 单文件发行包形态，而是 `tar.gz` rootfs 归档）。详见 §9.5.2 |

### 9.2 可回收空间测算（因选择 A 而放弃）

容器内 `du` 实测：`/usr/lib/firmware` 1.9 G、`/usr/share/kylin-ai` 1.8 G、`/usr/libexec/ukui-air-gesture` 974 M、`/usr/share/fonts` 653 M、`/usr/share/locale` 528 M、`/usr/share/icons` 367 M、`/usr/share/backgrounds` 340 M、`/var/opt` 709 M、`/usr/lib/modules` 277 M、`/usr/src` 214 M、`kylin-software-center` 216 M、`kylin-user-guide` 150 M、`/usr/share/doc` 70 M。

- 合计可回收 **约 7.0 GiB**；目标基镜像 **5–6.5 GiB**，上限 7.0 GiB（现状 13 GiB，容器内 `du -sh /` = 13G）。
- 峰值额外占用约 **16 GiB**（临时 tar ≤ 7.0 GiB + 新基 ≤ 7.0 GiB + 重建 toolchain 应用层约 1.5 GiB），可用 294 → 278 GiB；该盘长期 99%，不改变告警档位。

### 9.3 关键结构性事实（与是否采纳无关，长期有效）

`openkylin:3.0` 的 13 GiB 层被 `openkylin-npu-toolchain:3.0` 引用。**仅删除基镜像 tag 不释放任何空间**；省空间必须「新基 → 在其上重建 toolchain → 旧 toolchain 退役」三步齐全。

### 9.4 测量口径异常（后续一律按此复核）

`podman image inspect` 对同一镜像两次返回 `12,988,161,159` 与 `25,976,321,159` B，而容器内 `du -sh /` 稳定为 13G、`storage/overlay` 实测 34 G。口径不一致，今后涉及体积增减**一律以 `df` 前后字节差复核**，不采信单一体积字段。

- 归档内文件净和统计另有一处工具级陷阱：`printf "%d"` 对超过 2³¹ 的值会截到 `2147483647`，须用 `%.0f` 或直接取字节数；§9.5.3 的净值即按 `%.0f` 重算。

### 9.5 来源事实的二次实测与订正（2026-11-04，只读）

> **范围**：本节只回答「有哪些来源、各是什么」，不重开方案 B。全部测量只读：`tar -tf` / `tar -xOf` / `file -b` 输出到 stdout，未解压落盘、未 `podman import`、未写 `S:`、未删除任何文件。

#### 9.5.1 必须分开的两件事

| 问题 | 本轮结论 |
|---|---|
| ① 最初 `podman import` 用的**原始源 tar** 是否仍存在 | **未见留存**。`/media/pc/data/ai/.agents/wsl-images/`（即 `S:\.agents\wsl-images\`）目录清单已逐条核对，9 个条目中没有任何原始导入源 tar；现存两件 tar 均为 `podman export` 产物（确证见 §9.5.3） |
| ② 是否存在**可用等效来源** | **存在**：官方 `.wsl` 精简 rootfs 归档（最佳候选）与两件 `podman export` 归档（结构可用、质量不划算） |

> **口径**：「等效来源存在」不等于「原始 tarball 失而复得」。首轮「原始 tarball 已不在」的真因是 `-maxdepth 3` 少了一层（文件位于第 4 层），属检索口径缺陷；订正后只能表述为「未找到」，不能反过来断言它存在。

#### 9.5.2 官方 `.wsl` 精简包：格式判定与结构

| 项 | 实测值 |
|---|---|
| 文件 | `S:\.agents\wsl-images\openKylin-3.0-wsl-amd64.wsl`；352,431,812 B（336.13 MiB）；mtime 2026-11-04 15:52:36。**完整性校验（2026-11-04 补充实测）**：官方**只发布 MD5**——官网下载页「MD5 校验码」给出 `3c5717cfde5c032c69122fb14fa8e2fa`，其校验码页全文无 `sha256` / `SHA-256` 字样（命中数 0），官方 releases 目录亦未提供 `SHA256SUMS`；本地实测 MD5 与该值**逐位一致**，官方目录列示同名文件字节数 352,431,812，与本地一致。本地自算 SHA-256 `d6d0d708c54bbc643961aba21d74c0b18270715bdf2266ecec3bc55f486d07d4` **无官方对照值**，不得表述为「官方 SHA-256」 |
| 外层头 16 字节 | `1F 8B 08 00 00 00 00 00 00 03` → **gzip**（CM=08 deflate，FLG=00 无 FNAME/FEXTRA/FCOMMENT，OS=03 Unix） |
| 内层 | 解压流首块为 `./` 条目头，偏移 257 处 `ustar` → **GNU tar**；`file -b` 独立确认 `gzip compressed data, from Unix` |
| 归档可读性 | 全流 `tar -tf` rc=0，条目计数 27,930，无截断报错；此项只证明归档可遍历、未截断，**不构成校验和意义上的完整性结论**（校验和结论见上「文件」行） |
| 条目构成 | 普通文件 22,478 / 目录 2,882 / 符号链接 2,560 / 硬链接 2；解压后 1,182,607,360 B（1.10 GiB） |
| 顶层 | `./usr/` 988.8 MiB（约 85%）、`./var/` 118.8 MiB、`./etc/` 0.7 MiB，另有 `./boot ./dev ./proc ./sys ./run ./tmp ./home ./root ./srv ./media ./mnt ./debootstrap`；根层 `bin→usr/bin`、`sbin→usr/sbin`、`lib→usr/lib`、`lib64→usr/lib64`（usr-merge 形态） |
| 发行版标识 | `/etc/os-release` 是软链 `→ ../usr/lib/os-release`，内容：`NAME="openKylin"`、`VERSION="3.0 (huanghe)"`、`ID=openkylin`、`PRETTY_NAME="openKylin 3.0"`、`VERSION_ID="3.0"`、`VERSION_CODENAME=huanghe` |
| 裁剪潜力 | 已无 `/usr/lib/firmware`、`/usr/lib/modules`，无桌面组件（对照 §9.2：`openkylin:3.0` 容器内 firmware 1.9 G、`kylin-ai` 1.8 G 等） |
| 形态判别 | `wsl-distribution.conf`、`oobe.sh`、`install.tar`、`icon.ico`、`terminal_profile.json` 命中数全为 0 → **不是**新版 WSL 单文件发行包，而是 `tar.gz` 形式的 rootfs 归档 |

> 关于 `./debootstrap/`：归档内该目录存在（含 `debootstrap` 脚本与 `debootstrap.log` 等），可视为构建残留；本轮**未**据此判断制作者与构建环境，仅记录目录存在。

#### 9.5.3 两件 export tar：确证为导出产物，且是「脏」基

| 项 | `export-20261021` | `export-20261030` |
|---|---|---|
| 文件字节 | 10,224,732,160 B（9.52 GiB） | 21,470,699,520 B（20.00 GiB） |
| 格式 | `file -b` → `POSIX tar archive`，**未压缩** | 同左 |
| 首块 | `./` + 偏移 257 `ustar` | 同左 |
| 条目数（全流遍历） | 392,439 | 396,258 |
| 普通文件净和 | **9.27 GiB** | **19.91 GiB** |
| `./usr` | 1582.3 MiB | 1583.0 MiB |
| `./var` | 300.9 MiB | **10,403.4 MiB** |
| `./home` | 7608.7 MiB | 8401.4 MiB |
| `/etc/os-release` | 存在（3.0 / huanghe） | 存在 |
| 桌面组件 / firmware | 无（`ukui` 1–2 条、字体 3 MiB、图标 13 MiB、firmware 0、backgrounds 0） | 同左 |

**确证为 `podman export` 产物**：GNU tar 反复报 `Ignoring unknown extended header keyword 'LIBARCHIVE.xattr.user.overlay.origin'`、`user.overlay.uuid`、`user.overlay.impure`、`user.crtime_usec`——`user.overlay.*` 只有容器快照导出才会携带；叠加文件名中的 `export` 标注，两点足以排除「最初 `podman import` 的源」这一可能。

**为何不划算**：

- `export-20261030` 的 `./var/tmp/podman910947893` 单文件 **10,224,732,160 B**，与 `export-20261021.tar` 的字节数完全相同——导出过程把上一次导出的临时 tar 自包含进了归档；
- `./home/openkylin` 8.20 GiB 内含**嵌套 podman 存储**（同一份 165 MB `pandoc` 在 `overlay/*/diff/opt/conda/envs/main/bin/` 下重复 7 份）；
- 剔除 `home` 与 `var/tmp` 后，两件的系统内核都约 1.55 GiB（`usr` 1.58 GiB + `etc` 0.8 MiB + `debootstrap` 0.2 MiB）。

**能否作为 `podman import` 来源**：技术上成立（POSIX tar、完整 rootfs、`./` 前缀规范、单层无压缩、含 `/etc/os-release`）；但 1021 导入约 9.27 GiB、1030 导入约 **20 GiB 脏镜像**（含约 10.2 GB 的 `/var/tmp/podman*` 遗留与约 8.2 GiB 嵌套存储），比现状（13 GiB 基）更差——**仅具「裁剪后可用」潜力，不具备「现成最小基」价值**。

#### 9.5.4 与容器存储的关系及尺寸账（仅陈述，不改变决策）

- `S:` 实测为 `\\10.16.11.3\ai` 的映射（`Get-SmbMapping`：`S:` → `\\10.16.11.3\ai`，`Status=OK`；`Win32_LogicalDisk` DriveType=4、NTFS、可用 310,432,460,800 B ≈ 289 GiB），服务端落点即 `/media/pc/data/ai/.agents/wsl-images/`，与 podman graphroot 同在一块 XFS 上；故远端 `podman import` 可直接读取该 `.tar.gz`，**无需传输，且支持 gzip 直读**。
- 尺寸账（估算，非实测）：`.wsl` 压缩 336.13 MiB → 树 1.10 GiB → `podman import` 后镜像报约 1.1–1.2 GB；若日后重启，重建 toolchain 峰值额外约 3 GB；对照现状（`openkylin:3.0` 13 GiB + `npu-toolchain:3.0` 14 GB），换基后估算可回收约 **11 GiB**。§9.2 的 7.0 GiB 是「在现有镜像内裁剪」的口径，两者口径不同，不可相加或互替。
- **若日后重启方案 B，应优先 `import` `.wsl`，不使用这两件 export**：前者残留为零，后者自带 10 GB 级垃圾。

#### 9.5.5 同目录体积现状（治理待办，处置需用户批准）

2026-11-04 16:17:52 只读复核，`S:\.agents\wsl-images\` 共 9 个条目，放大文件合计 **43,014,463,190 B（40.06 GiB）**：

| 文件 | 字节 | 备注 |
|---|---|---|
| `openKylin-3.0-export-20261030.tar` | 21,470,699,520 | export 产物，20.00 GiB |
| `openKylin-3.0-export-20261021.tar` | 10,224,732,160 | export 产物，9.52 GiB |
| `openKylin-3.0-desktop-wsl-amd64-old.wsl` | 6,592,986,686 | 6.14 GiB，桌面 WSL 发行版包（旧），非容器导入源 |
| `未确认 317733.crdownload` | 4,373,610,496（16:17 读数） | 15:52 为 2.60 GB、16:12 为 3.60 GB、16:17 为 4.37 GB，**仍在增长**，属另一路下载中断/进行中残留 |
| `openKylin-3.0-wsl-amd64.wsl` | 352,431,812 | 336.13 MiB，§9.5.2 判定对象 |
| `dl-segments.ps1` / `dl-progress.log` / `dot.xsession` | 2,172 / 79 / 265 | 历史分段下载脚本、进度日志与 xsession 配置 |

- 该目录与 99% 已用的 XFS 同盘（可用约 289 GiB），单目录 40 GiB 量级占用值得单列；`.crdownload` 仍在增长这一点本身也需确认。
- **本轮处置为零**：删除/迁移任何文件均需用户批准；按任务要求只读，不读 `.crdownload` 内容、不删、不续传。

## 附录 A：与服务器侧 `all-in-one.sh` 的差异点

| 差异点 | 服务器侧（既有） | v2 远程后端 |
|---|---|---|
| 宿主 | Ubuntu 22.04.5（`ai@10.16.11.3`） | **同一台机器**，即服务器侧方案即目标方案 |
| 访问入口 | 本地终端 | Windows 经 SSH / `podman --remote` |
| LLVM | 系统 `/usr/lib/llvm-21` 或 `/usr/lib/llvm-20` | 宿主 py314 的 **22.1.2**，容器内补同版本 |
| Python | 容器内 conda `main`（3.14.x） | 不变 |
| 挂载 | bind `/media/pc/data/ai` | 不变 |
| 存储 | rootless overlay，graphroot 在 XFS | 不变 |

> 结论：v2 **没有新增构建逻辑**，只是把入口从「Windows 本地 WSL」换成「Windows → SSH → 同一台服务器」，目标环境与服务器侧完全一致。

## 附录 C：版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0.0-draft | 2026-11-01 | 首版：WSL + OpenKylin + rootless Podman 本地后端规格 |
| v1.2.0-draft | 2026-11-02 | LLVM 21/22 兼容性结论、A8/A9、分层落盘 |
| v1.3.0-draft | 2026-11-02 | D: 盘方案、容量基线、Q9、阶段 1a/1b、I2 通道 B 纠错 |
| **v2.0.0-draft** | **2026-11-03** | **方案切换为远程后端**：放弃 WSL 本地发行版（D: 容量与系统服务独占锁双因），改为 Windows 经 SSH 使用 10.16.11.3 上的 rootless Podman；重写目标/验收 A1–A9、架构图、挂载与 UID、LLVM 22 供给、方案 A/B、端口策略、构建复用；新增 py314 与 LLVM 22 事实卡；v1.x 全文归档至附录 D |
| **v2.1.0-draft** | **2026-11-03** | **落地实施**：新增 §9「实施结果与实测证据」（A1–A9 判定、偏差 D1–D6、容器配置与产物、遗留问题）；§7.3 阶段表补状态列；Q1/Q2/Q5 标记已决，Q3 记录「按用户指示不切默认」；frontmatter 状态改为 implemented-draft |
| **v2.1.0-draft（补记）** | **2026-11-03** | **缺陷修复与重编**：定位并修复 `--connection` 主机名丢失缺陷（`~/.ssh/config` 的 `Host 10.16.11.3` 改为 `Match host 10.16.11.3`，根因与隔离实验见 09-1 §4.1）；以 `-DUSE_LLVM=/opt/build/llvm22/bin/llvm-config` 重编 `libtvm.so`（854 目标 rc=0，`ldd` 链接 `libLLVM.so.22.1`，旧产物备份 `libtvm.so.bak-llvm21`）；A2/A4 证据与 D1/D2 处置同步更新 |
| **v2.1.0-draft（补记 2）** | **2026-11-03** | **临时产物清理与 Q3/Q4 定案**：清理前复验 `import tvm` rc=0、`ldd` 命中 `libLLVM.so.22.1`；断言后删除 `.temp/npu-toolchain-run`（6,904 文件 / 3,001,480,000 B）与 `.temp/npu-toolchain-spec-v2`（2 文件 / 97,370 B），以及 Windows `~/.ssh/config.bak-20261103-split`，XFS 可用 **292 GB → 295 GB**；`libtvm.so.bak-llvm21`（79 MB）当时主动保留为 LLVM 21 回滚点。Q3 定为保持不切默认连接、Q4 选定 8888→8888（备用 8894） |
| **v2.1.0-draft（补记 3）** | **2026-11-03** | **旧库备份与拆分中间件清理**：删前校验 `import tvm`（0.19.0 + `llvm`/`ccompiler` 两个 Target）、`import xmnn`（1.0.1.dev120）、`podman --remote --connection remote-ai ps -a` 与 `info` 均正常，并确认 `libtvm.so.bak-llvm21` 未被 `profile.d`/脚本/rpath 引用；随后删除该备份（79,231,568 B，sha256 `9dfa9a66…`）与 `split-doc09.ps1`（19,711 B）。删后回归：`import tvm`/`import xmnn` rc=0、`remote-ai info` → 5.6.2/rootless/overlay、`ssh BatchMode whoami` → `ai`(1006)。XFS 可用 316,398,936,064 → 316,478,189,568 B（+75.6 MiB）；D: 保持 34.00 GB。**保留** `.temp/doc09-atomize/original-backup.md`（拆分前原文整档副本；2026-11-03 已迁入 `.agents/archive/doc09-atomize-20261103/` 并删源）与 `.temp/npu-toolchain`（被 `run.sh`/`verify.sh`/`all-in-one.sh` 硬编码引用） |
| **v2.1.0-draft（补记 4）** | **2026-11-03** | **G3 处置收口**：§8 Q1 行保留实施当日原文（含 clang-22 / lld 23.1.4）以维持决策链可追溯，其后追加注记——`lld` 自始即 23.1.4、22 系 `lld` 从未安装，该批 23 系包（`libllvm23`/`lld`/`llvm-openmp` 23.1.4）已隔离移出，隔离副本（268 MB / 48 文件）已删除，XFS 可用 315,729,219,584 → 316,010,168,320 B。同步订正 09-3 容器现状表与注、09-5 A3 行/偏差 D7/§9.3/§9.4 第 5 条 |
| **v2.1.0-draft（补记 5）** | **2026-11-04** | **基镜像最小化评估收口（未采纳）**：新增 §9，记录三条 rootfs 来源实测（官方包不可得 / debootstrap 不可行 / 裁剪导入属派生法）、可回收约 7.0 GiB 测算与目标 5–6.5 GiB、13 GiB 层被 toolchain 引用故删 tag 不释放空间、以及 `podman image inspect` 体积口径异常（`12,988,161,159` vs `25,976,321,159` B，`du` 稳定 13G）。用户 2026-11-04 改判路径 A 维持现状，P1–P5 取消，未改动任何镜像 |
| **v2.1.0-draft（补记 6）** | **2026-11-04** | **§9 来源判断二次实测订正（决策不变）**：新增 §9.5（`.wsl` 魔数/结构判定与 27,930 条目、两件 export tar 全流遍历（392,439 / 396,258 条目）与 `user.overlay.*` pax 头确证其为导出产物、原始源与等效来源的分辨、同目录 40.06 GiB 体积现状）；订正 §9.1 第 1 行「官方最小 rootfs 不可得」的适用范围（仅 registry / apt / ISO 三类入口）、第 3 行「原始 tarball 已不在 / 唯一路径为导出裁剪」（真因为 `-maxdepth 3` 少一层、export 产物非原始源、新增官方 `.wsl` 候选），并新增第 4 行「官方 WSL 精简发行包」来源；§9.4 补记 `printf "%d"` 截断口径陷阱。路径 A 维持现状的决定未变，未执行 `import` / `build` / 删除，未写 `S:` |
| **v2.1.0-draft（补记 7）** | **2026-11-04** | **§9.5.2 校验口径订正**：官方 `.wsl` 包**只发布 MD5**（`3c5717cfde5c032c69122fb14fa8e2fa`），官网校验码页全文无 `sha256` / `SHA-256` 字样（命中 0），releases 目录亦无 `SHA256SUMS`；本地实测 MD5 与该值**逐位一致**，字节数 352,431,812 与官方目录列示一致。本地自算 SHA-256 `d6d0d708c54bbc643961aba21d74c0b18270715bdf2266ecec3bc55f486d07d4` **无官方对照值**，不得表述为「官方 SHA-256」。同时把 §9.5.2 原「完整性」行改名为「归档可读性」（该行仅记 `tar -tf` rc=0 与 27,930 条目，与校验和语义无关）。路径 A 维持现状，未执行 `import` / `build` / 删除，未写 `S:` |

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [验收与实测证据](09-5-acceptance-and-evidence.md)
- [v1.x 归档（已废弃）](09-7-appendix-v1-wsl-deprecated.md)