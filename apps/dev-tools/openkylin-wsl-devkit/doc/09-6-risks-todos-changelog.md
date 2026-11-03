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
| **v2.1.0-draft（补记 3）** | **2026-11-03** | **旧库备份与拆分中间件清理**：删前校验 `import tvm`（0.19.0 + `llvm`/`ccompiler` 两个 Target）、`import xmnn`（1.0.1.dev120）、`podman --remote --connection remote-ai ps -a` 与 `info` 均正常，并确认 `libtvm.so.bak-llvm21` 未被 `profile.d`/脚本/rpath 引用；随后删除该备份（79,231,568 B，sha256 `9dfa9a66…`）与 `split-doc09.ps1`（19,711 B）。删后回归：`import tvm`/`import xmnn` rc=0、`remote-ai info` → 5.6.2/rootless/overlay、`ssh BatchMode whoami` → `ai`(1006)。XFS 可用 316,398,936,064 → 316,478,189,568 B（+75.6 MiB）；D: 保持 34.00 GB。**保留** `.temp/doc09-atomize/original-backup.md`（拆分前原文唯一副本）与 `.temp/npu-toolchain`（被 `run.sh`/`verify.sh`/`all-in-one.sh` 硬编码引用） |

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [验收与实测证据](09-5-acceptance-and-evidence.md)
- [v1.x 归档（已废弃）](09-7-appendix-v1-wsl-deprecated.md)