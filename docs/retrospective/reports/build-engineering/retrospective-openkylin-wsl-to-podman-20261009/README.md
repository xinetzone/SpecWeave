---
id: "milestone-openkylin-wsl-to-podman-20261009"
title: "openKylin WSL 导出转 podman 镜像里程碑复盘报告"
date: "2026-10-09"
completion_date: "2026-10-09"
type: "Report"
description: "openKylin 3.0 WSL 导出文件转 podman 镜像（导入+验证+归档+压缩）任务里程碑复盘：podman machine WSL 空闲回收根因定位、执行通道选择、三层验证闭环"
status: "stable"
source: "D:/spaces/SpecWeave/.docker-cache/wsl-exports/openKylin-3.0-wsl-amd64.wsl"
milestone-name: "openKylin WSL→podman 镜像转换"
time-range: "2026-10-09（单会话）"
methodology: "七概念方法论（R→I→E→V→C 链路，里程碑复盘场景）"
quality-gates:
  G1: "事实无因果词 ✅（28 条事实）"
  G2: "洞察四元组完整 ✅（3 条洞察）"
  G3: "模式可迁移验证 ✅（wsl-rootfs-oci-image-export，L1-draft）"
  G4: "交付物验证通过 ✅（结构/链接/计数三查）"
tags: ["里程碑复盘", "七概念", "wsl", "podman", "镜像转换", "keep-alive", "docker-archive", "gzip", "验证闭环", "vm-idle-timeout"]
generated:
  by: "process:seven-concepts-cmd"
  at: "2026-10-09T00:00:00Z"
verified:
  by: "process:artifact-verification（三查法）"
  at: "2026-10-09T00:00:00Z"
stale_after: "2027-10-09"
---

<!-- meta_type: retrospective -->

# openKylin WSL 导出转 podman 镜像里程碑复盘报告

> **方法论编排**：七概念 R→I→E→V→C 链路（里程碑复盘场景）
> **复盘对象**：`D:\spaces\SpecWeave\.docker-cache\wsl-exports\openKylin-3.0-wsl-amd64.wsl` 转为 podman 镜像并归档压缩
> **时间范围**：2026-10-09（单会话完成）
> **复盘日期**：2026-10-09
> **session**：sc-20261009-openkylin-wsl2podman
> **用户原始需求**："D:\spaces\SpecWeave\.docker-cache\wsl-exports\openKylin-3.0-wsl-amd64.wsl 转为 podman 镜像" → "保存镜像" → "归档并压缩" → "里程碑复盘+洞察+萃取+导出报告+编写文档"

---

## 一、里程碑总览

### 1.1 交付成果

| 指标 | 结果 |
|---|---|
| 转换产物 | podman 镜像 `localhost/openkylin:3.0`（ID `e828c412099a`，1.18 GB） |
| 运行验证 | ✅ `podman run --rm openkylin:3.0 cat /etc/os-release` 输出 `openKylin 3.0 (huanghe)` |
| 归档产物 | `openKylin-3.0-podman-docker-amd64.tar`（1,182,614,528 字节） |
| 压缩产物 | `openKylin-3.0-podman-docker-amd64.tar.gz`（351,873,468 字节，压缩比 3.36x） |
| 归档验证 | ✅ tar 结构完整，manifest RepoTags/Config 与镜像 ID 一致，gzip 解压后逐字一致 |
| 根因定位 | ✅ podman machine（WSL 后端）虚拟机空闲回收（对照实验证实） |
| 可复用模式 | 1 个（[wsl-rootfs-oci-image-export](../../../patterns/code-patterns/wsl-rootfs-oci-image-export.md)，L1-draft） |

### 1.2 关键决策节点

| 节点 | 决策 | 依据 |
|---|---|---|
| D1 文件格式判定 | 以魔数判定为 gzip tar，而非信任扩展名 | 前 16 字节 `1F 8B 08` |
| D2 执行通道 | 在虚拟机内以 `/mnt/d/...` 路径导入 | 客户端直传连接不稳 + `/mnt/d` 挂载可见 |
| D3 存活性对策 | 常驻 `sleep` 进程保持虚拟机活跃 | 对照实验：有 keep-alive 间隔 30s 两次 ssh 均成功 |
| D4 归档格式 | docker-archive（非 OCI） | podman/docker load 双兼容 |
| D5 压缩方式 | 整档 gzip（.NET GZipStream） | podman docker-archive 层未压缩，二次压缩有 3.36x 收益 |

---

## 二、R 阶段：事实清单

> G1 质量门：✅ 通过（28 条事实均为客观陈述，无因果推断词，数据可追溯）

| 编号 | 事实 |
|------|------|
| F-001 | 源文件 `D:\spaces\SpecWeave\.docker-cache\wsl-exports\openKylin-3.0-wsl-amd64.wsl` 存在 |
| F-002 | 源文件大小 352,431,812 字节，修改时间 2026-10-09 07:27:33 |
| F-003 | 源文件前 16 字节魔数 `1F 8B 08`，判定为 gzip 压缩格式 |
| F-004 | 本机 podman 客户端版本 5.7.0-rc3，provider=wsl，OS=windows/amd64 |
| F-005 | `podman system connection list` 显示 `podman-machine-default`（ssh://user@127.0.0.1:60432）与 `podman-machine-default-root` 两个连接 |
| F-006 | `podman machine list` 显示 `podman-machine-default`（wsl 类型，8 CPU/2GiB/100GiB，创建于 3 周前） |
| F-007 | 首次 `podman machine start` 输出 "Machine started successfully" |
| F-008 | 启动后 `podman info` 返回 OS=linux arch=amd64，存储路径 /home/user/.local/share/containers/storage |
| F-009 | `podman machine ssh` 可访问 `/mnt/d/`，源文件位于 `/mnt/d/spaces/SpecWeave/.docker-cache/wsl-exports/` |
| F-010 | wsl-exports 目录内含 `jupyter-podman-rootless-20260908-091604.tar`（6,486,487,040 字节）、`podman-machine-default-20260908-091604.tar`（8,373,760,000 字节）与 `ok-rootfs/` 目录 |
| F-011 | Windows 客户端 `podman import D:\...` 返回 "Cannot connect to Podman socket: dial tcp 127.0.0.1:60432 refused" |
| F-012 | 机器启动后约数十秒内再次停止，`podman machine list` LAST UP 保持 "11 days ago" |
| F-013 | 启动后立即 ssh 输出 "Connection to localhost closed by remote host" |
| F-014 | `wsl -l -v` 显示 `podman-machine-default`、`openKylin-3.0-desktop`、`PCMClawUbuntu` 三个 WSL2 发行版，均为 Stopped |
| F-015 | `C:\Users\xinzo\.wslconfig` 存在且内容为空 |
| F-016 | `wsl -d podman-machine-default -- echo DIRECT_OK` 输出 DIRECT_OK |
| F-017 | 保持 `wsl -d podman-machine-default -- sleep 600` 常驻进程时，间隔 30 秒两次 `podman machine ssh -- echo` 均成功（SSH_ONE/SSH_TWO） |
| F-018 | 未保持常驻进程时，同一次调用内第二条 ssh 输出 "Connection to localhost closed by remote host" |
| F-019 | 保持常驻后 `podman machine ssh -- podman import /mnt/d/.../openKylin-3.0-wsl-amd64.wsl openkylin:3.0` 输出镜像 ID `sha256:e828c412099a26f21946e6ee89b7216624e0f21f6d4da958d60b0ad4c514e1d8` |
| F-020 | `podman images` 显示 `localhost/openkylin:3.0`（e828c412099a，1.18 GB） |
| F-021 | `podman run --rm openkylin:3.0 cat /etc/os-release` 输出 `NAME="openKylin" VERSION="3.0 (huanghe)" ID=openkylin PRETTY_NAME="openKylin 3.0"` |
| F-022 | `podman run --rm openkylin:3.0 cat /etc/openkylin-release` 输出 "No such file or directory" |
| F-023 | `podman save --format docker-archive -o D:\...\openKylin-3.0-podman-docker-amd64.tar openkylin:3.0` 生成 1,182,614,528 字节归档 |
| F-024 | `tar -xOf` 归档 `manifest.json` 输出 `RepoTags:["localhost/openkylin:3.0"]`，Config 为 `e828c412...`（与镜像 ID 一致），单层 `c6553af0...` |
| F-025 | 用 .NET GZipStream（Optimal）压缩生成 `openKylin-3.0-podman-docker-amd64.tar.gz`，351,873,468 字节 |
| F-026 | `tar -xzf` 解压 tar.gz 后 `manifest.json` 内容与压缩前逐字一致 |
| F-027 | 压缩比计算：1,182,614,528 / 351,873,468 ≈ 3.36 |
| F-028 | 既有模式 `oci-image-wsl-rootfs-bridge.md` 将「WSL 发行版打包为镜像」列为场景5 反向操作，未展开实现细节 |

---

## 三、I 阶段：核心洞察

> G2 质量门：✅ 通过（3 条洞察，四元组完整，证据引用 F 编号）

### 洞察 1：podman machine 的"存活性"是 Windows 自动化操作的首要前置条件

- **陈述**：Windows 上 podman machine（wsl 后端）的虚拟机在命令间隙空闲即被回收，"start 成功"与"持续可用"是两个独立事实；跨命令自动化必须先确认存活、并在操作窗口内保持活跃。
- **证据**：F-011（客户端连接被拒）、F-012（机器再次停止）、F-013/F-018（ssh 连接被远端关闭）、F-017（keep-alive 对照成功）、F-015（.wslconfig 为空=默认空闲回收行为）。
- **反常识**：直觉认为"podman machine start 返回成功 = 环境就绪"；实际连接失败的第一现象是 socket 拒绝，极易被误判为端口转发故障，而根因是虚拟机本身已被 WSL 回收——直到对照实验才证实。
- **行动**：把「存活检查 + keep-alive」固化为模式 Step 2；后续所有 podman machine 相关自动化以"单次调用内连续执行"为设计约束。

### 洞察 2：执行通道选择决定成败——客户端直传 vs 虚拟机内直读

- **陈述**：podman machine 连接下"本地文件"路径在客户端与虚拟机两侧语义不同；源文件位于 `/mnt/<盘符>/` 时，在虚拟机内以 WSL 路径直接执行导入是更稳定的通道。
- **证据**：F-011（客户端 `D:\` 路径导入连接被拒）、F-009（虚拟机内可见 `/mnt/d/...`）、F-019（虚拟机内导入成功且与客户端共享同一存储）。
- **反常识**：podman 客户端在 Windows 上"看起来原生可用"，但 import/save 等文件类操作的真实执行边界在虚拟机内；跨路径体系操作不确认通道就执行，成败依赖环境状态。
- **行动**：转换/导入类命令统一走 `podman machine ssh -- podman ...` + `/mnt/<盘符>/` 路径；命令模板已写入模式 Step 3。

### 洞察 3：镜像转换任务的成功是"三层验证"的叠加，缺一层都不能宣称完成

- **陈述**：转换任务的成功 = 导入注册（有镜像 ID）∩ 元数据一致（manifest/tag/ID 对得上）∩ 运行可用（冒烟命令真实执行）；归档任务还要叠加"压缩可逆"验证。
- **证据**：F-019/F-020（导入与注册）、F-024（manifest 校验）、F-021/F-022（运行冒烟与发行版专属文件缺失并存）、F-026（压缩后解压一致）。
- **反常识**："podman import 输出镜像 ID + 退出码 0"常被当作成功终点；本例中 `/etc/openkylin-release` 缺失说明 rootfs 内容可与"发行版应有文件"存在差异——结构校验与运行冒烟是互补维度，不可互相替代。
- **行动**：模式检验标准固化为三层（导入/元数据/运行）；归档压缩后追加解压校验步骤。

---

## 四、V 阶段：对抗审查（轻量）

> 里程碑复盘场景 V 为可选；本报告执行轻量三视角审查并采纳修正。

| 视角 | 攻击点 | 修正 |
|---|---|---|
| 🔴 魔鬼代言人 | 洞察 1 的根因可能是本机 WSL 版本/配置特有（`.wslconfig` 为空=默认 60s 空闲回收）；调大 `vmIdleTimeout` 的环境不成立 | 模式 Step 2 与"已知限制"中标注为**环境相关前置条件**，写明适用边界 |
| 🟢 新人视角 | 新人可能用 `wsl -d podman-machine-default` 直接进入，导致环境变量未初始化（既有模式已记录该陷阱） | 模式 Step 3 反模式中明确"客户端直传不可用"，并交叉引用 wsl-podman-build-bridge Troubleshooting |
| 🟠 老板/未来 | 单案例 L1 结论推广风险：openKylin 桌面发行版与 devcontainer 类镜像在 boot/文件结构上差异大 | 模式明确标注 L1-draft 与升级路径（他发行版复用→L2），未宣称已验证 |

---

## 五、E 阶段：模式萃取

> G3 质量门：✅ 通过（触发/步骤/反模式/检验/迁移齐全，L1-draft 单案例标注）

**产出**：[wsl-rootfs-oci-image-export.md](../../../patterns/code-patterns/wsl-rootfs-oci-image-export.md)（WSL发行版镜像化导出模式，code-pattern）

**重复性比对结论**：
- 既有 `oci-image-wsl-rootfs-bridge.md`（OCI→WSL 正向）已把反向列为"场景5"但未展开 → 本模式为其**反向互补实现**，非重复创建
- 既有 `docker-image-offline-export-distribution.md`（导出-验证-分发六步法）覆盖 docker 侧 → 本模式补充 podman 侧差异（docker-archive 未压缩、VM 内通道、keep-alive）
- 既有 `wsl-podman-build-bridge.md` Troubleshooting 已记录 ssh 不稳与 keepalive → 与本模式 Step 2 相互印证

**成熟度**：L1-draft（单案例：openKylin 3.0；升级建议见模式"已知限制与待验证"）

---

## 六、C 阶段：原子提交

> G4 质量门：✅ 通过（单一职责、UTF-8 提交、提交后验证）

| 项 | 值 |
|---|---|
| 提交类型 | `docs(retrospective)` |
| 提交信息 | 新增 openKylin WSL→podman 镜像转换里程碑复盘与"WSL镜像化导出"L1 模式（沉淀 WSL 空闲回收根因与三层验证闭环） |
| 变更文件 | 报告 README.md + index.md、模式文档、build-engineering 索引、oci-image-wsl-rootfs-bridge 交叉引用（详见提交 stat） |
| 提交验证 | `git show --stat HEAD` + `git cat-file -p HEAD` 中文无乱码 + 工作区无残留 |

---

## 七、导出环节：改进建议与行动计划

> 导出报告类型：retrospective / 格式：Markdown（本文件即导出产物，`formats=["md"]`）

### 7.1 改进建议

| 问题 | 改进措施 | 优先级 | 预期效果 | 状态 |
|------|---------|--------|---------|------|
| podman machine 空闲回收致连接反复失效 | 自动化脚本内建「存活检查+keep-alive」前置步骤 | 高 | 消除偶发连接失败，命令可重复执行 | 已制定预案（模式 Step 2 固化） |
| 客户端直传路径歧义 | 文件类操作统一走 VM 内 `/mnt/` 通道 | 中 | 减少路径体系歧义导致的失败 | 已制定预案（模式 Step 3 固化） |
| 验证不足风险 | 强制三层验证 + 压缩解压校验 | 高 | 交付前拦截结构/运行缺陷 | 已执行（本次任务全量执行） |
| 镜像无默认 CMD | 如需默认 shell，补 `--change CMD` 或基于镜像构建 | 低 | 提升容器开箱可用性 | 待规划 |
| 未压缩 tar 占用 1.1GB | 确认归档稳定后删除未压缩版 | 低 | 释放磁盘空间 | 待规划（涉及删除，需用户确认） |

### 7.2 行动计划

| 优先级 | 改进项 | 具体措施 | 建议时间 | 状态 |
|--------|--------|---------|---------|------|
| 中 | keep-alive 检查脚本化 | 评估将存活检查+keep-alive 封装为 `.agents/scripts/` 可复用脚本（先与现有脚本库比对防重复） | 2026-10-16 | 待规划 |
| 中 | 模式成熟度升级 | 下次他发行版（Ubuntu/Alpine）WSL→镜像任务复用本模式并回填验证记录，L1→L2 | 按需触发 | 已制定预案 |
| 低 | `.wslconfig` 评估 | 由用户决策是否调大 `vmIdleTimeout`（系统级配置，需用户确认后执行） | 2026-10-16 | 待规划 |
| 低 | 归档清理决策 | 由用户确认后删除未压缩 tar（涉及删除操作） | 2026-10-16 | 待规划 |

### 7.3 模式成熟度更新

| 模式 ID | 成熟度变化 | 触发原因 | 更新时间 | 验证/复用次数 |
|---------|-----------|---------|---------|-------------|
| wsl-rootfs-oci-image-export | 新建（L1-draft） | 本任务单案例验证 | 2026-10-09 | 验证 1 / 复用 0 |
| oci-image-wsl-rootfs-bridge | 不变（L1-draft） | 新增反向互补模式交叉引用 | 2026-10-09 | 复用 0 |

---

> **报告编制**：本文档基于本会话完整执行轨迹（CMD-LOG + 工具输出）编制，全部事实有工具输出佐证；报告遵循"事实→分析→洞察→建议"结构，采用 Markdown 格式。状态语义遵循项目规范（已执行/已制定预案/已评估/已暂缓）。
