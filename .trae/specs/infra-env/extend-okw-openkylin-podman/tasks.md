---
title: "为 okw 增加 openKylin WSL rootless Podman 支持 - 实施计划"
status: "draft"
methodology: "seven-concepts-cmd: F→V→I→C"
content-sensitivity: "public"
source: ".trae/specs/infra-env/extend-okw-openkylin-podman/spec.md"
---

# 为 okw 增加 openKylin WSL rootless Podman 支持 - 实施计划

## Task 1: 增加 Podman 只读预检

- **Status**: `done`（提交 8a26c5d0f / 544b4c6a6，47 场景测试）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在现有 `okw` 命令树中增加 `podman preflight <发行版>`。
  - 复用 `okw.distro` 的发行版检查与 WSL 调用封装；明确区分以默认用户执行的探测与发行版内 root 探测。
  - 检查 WSL2、openKylin、非 root 默认用户、APT/dpkg、`podman`/`uidmap`/`slirp4netns`/`fuse-overlayfs` 包候选和 UID/GID 映射；对缺失/过期 APT 索引导致的未知状态单独报告并输出中文行动建议。
  - 预检不得调用 APT 更新/安装，不得写入目标发行版或改变 WSL 状态。
  - 输出中对 APT 三类常见问题（候选不可达 / 网络错误 / 哈希校验失败）给出可区分的失败阶段标签与中文描述。
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `rule` TR-1.1：发行版不存在、WSL1、非 openKylin、默认 root、缺少 APT、候选不可用/未知/三类 APT 常见失败模式及全通过场景均有测试并返回预期结果。
  - `rule` TR-1.2：预检所有 WSL 子进程调用均为只读；APT 命令参数中无 update/install，映射文件及默认发行版前后快照不变。
  - `rubric` TR-1.3：APT 索引未知状态输出中的行动建议文案完整且中文；三类 APT 失败模式的阶段标签互不相同。

## Task 2: 安全安装 Podman 并配置 rootless 用户映射

- **Status**: `done`（install --yes + subuid/subgid 单次联合原子脚本；207 测试通过，podman 模块覆盖率 98%）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 实现 `okw podman install <发行版> --yes`；无 `--yes` 时在任何安装、索引更新或配置写入前退出。
  - 通过现有 WSL 封装在指定发行版内执行 root 操作；不得对默认发行版或其他发行版执行操作。
  - 在显式确认后刷新目标发行版 APT 索引，复查四个直接包候选，再以单次包管理安装流程安装；Podman 的传递依赖由 APT 解析，不添加或改写软件源。
  - 增加可隔离测试的 subuid/subgid 管理逻辑：使用「左闭右开 [start, start+count)」区间算法判定重叠；只有目标用户同时满足「缺映射、标准区间 [100000, 165536) 与其它账户不重叠、行格式可解析」才追加；冲突、解析异常、off-by-one 边界或写入失败时保护原文件、输出冲突对比，并提供可操作中文错误。
  - 安装失败时明确区分「包不在源里」「APT 网络错误」「哈希校验失败」三类失败阶段并报告已完成阶段和可能的部分变更；不宣称事务回滚或自动卸载。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8
- **Test Requirements**:
  - `rule` TR-2.1：未提供 `--yes`、前置条件失败或依赖包无候选时，断言没有安装命令或映射写入。
  - `rule` TR-2.2：确认安装只针对目标发行版；APT 索引更新发生在 `--yes` 之后；不出现软件源修改、默认发行版变更或 `/etc/wsl.conf` 写入命令。
  - `rule` TR-2.3：映射缺失、有效映射、重复执行两遍幂等、UID/GID 区间重叠（含 off-by-one 边界 A.end == B.start 判不重叠）、同名多行区间冲突、行字段非正整数（无效映射）、畸形三列解析失败、写入只读文件共 8 类路径均有隔离测试；每类测试用前后快照断言不得改动其它账户记录或文件原除目标追加行外的其它字节。
  - `rubric` TR-2.4：三类 APT 失败输出中的阶段标签互不相同，失败文案为中文且分别指向「包候选缺失」「网络可达性」「镜像源校验」三类修复方向。

## Task 3: 增加 rootless 验收与本地镜像冒烟

- **Status**: `done`（verify 只读矩阵 + root 强制守卫 + --smoke-image 禁拉取；提交 20cbe98fb，244 测试）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 实现 `okw podman verify <发行版>`，以发行版默认非 root 用户执行 Podman 版本、rootless 状态、subuid/subgid 和用户命名空间检查。
  - 增加可选 `--smoke-image <本地镜像>`；仅用户显式提供镜像时运行临时容器，并禁止拉取。
  - 输出逐项 PASS/FAIL 和中文失败指引；失败时使用非零退出码。
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-3.1：Podman 缺失、rootless false、映射错误、unshare 失败和全通过输出矩阵均被测试覆盖；root 身份不可得到 rootless PASS。
  - `rule` TR-3.2：默认 verify 不运行容器；显式冒烟使用禁止拉取参数；缺少本地镜像时失败且测试不产生网络请求。

## Task 4: 完成 CLI 回归、包构建与用户文档

- **Status**: `done`（提交 70a1309a4 映射回滚加固 + 5f56a8140 help/README/索引/wheel；247 测试通过，TOTAL 95%、podman 98%、cli 86%；wheel `openkylin_wsl_devkit-0.1.0-py3-none-any.whl` 零 Requires-Dist）
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**:
  - 完善 `okw --help`、`okw podman --help`、`okw podman install --help` 的错误码和中文错误输出；保持既有命令参数与行为兼容。
  - 更新 `apps/dev-tools/openkylin-wsl-devkit/README.md`，新增「Podman 入门」「常见问题 FAQ」章节，覆盖：① rootless vs sudo podman 的区别与推荐理由；② `--yes` 一次性确认的副作用清单（≥4 条）；③ 如何查询发行版名（`okw list` / `wsl -l -v`）；④ `--smoke-image` 前置条件（先手动 pull 镜像，默认 verify 不联网）；⑤ 三类 APT 失败原因与修复指引。
  - 更新 `apps/AGENTS.md` 与 `apps/README.md` 中现有 `okw` 描述；不新增重复应用条目。
  - 运行完整测试、覆盖率检查、wheel 构建和链接检查。
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-4.1：完整测试通过；总覆盖率 ≥80%，新增关键 Podman 模块覆盖率 ≥90%；wheel 构建成功且运行时依赖未增加。
  - `rule` TR-4.2：既有 `okw` 子命令回归测试通过；README 命令、`okw podman --help` 与 `install --help` 三处对 rootless/--yes/发行版名查询/--smoke-image 的说明一致；apps 索引仍只登记一个 `openkylin-wsl-devkit`。
  - `rule` TR-4.3：新增/修改 Markdown 本地链接检查通过；README FAQ 章节对三类 APT 失败修复指引各有至少 1 条独立条目。

## Task 5: 在可用 openKylin WSL2 环境执行分层验收

- **Status**: `done（仅只读层）`——真实只读 preflight/verify 已执行并留存证据；安装/映射写入/容器冒烟经用户授权范围限定标记 `blocked`（见下，TR-5.1），未伪造实测
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 先确认目标 openKylin 3.0 WSL2 发行版存在且可执行；检查其现有软件源是否提供规格要求的包，不得为通过验收而添加第三方源。
  - 在不触碰用户日常发行版的前提下，优先使用专用/可丢弃测试发行版验证预检、安装、映射幂等和 rootless verify。
  - 只有在用户明确授权对其指定发行版执行安装时，才运行实际包安装；容器冒烟必须使用本地镜像。
  - 若发行版或包候选不可用，保留静态与 mock 验收证据，并在任务证据中标记真实环境项 `blocked`，记录解除条件，不得伪造实测结果。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-5.1：真实执行记录覆盖发行版身份、包候选、安装结果、默认用户 rootless 结果和映射；任何未执行步骤明确注明 blocked 及原因。
  - `rule` TR-5.2：真实验证不改变 WSL 默认发行版、不触及其他发行版、不增加软件源；可选冒烟无远程拉取。

### 真实验收证据（2026-10-08，Windows 宿主，py314 源码直跑 `python -m okw`）

**环境清单（`wsl -l -v` / `okw list`，验收前后各一次，星标无变化）**：

```text
* podman-machine-default    Stopped  WSL2   # 默认发行版，全程未触碰
  openKylin-3.0-desktop     Stopped  WSL2   # 本次唯一目标发行版
  PCMClawUbuntu             Stopped  WSL2   # 他人发行版，全程未触碰
```

- 任务交接时提及的最小镜像 `openKylin-3.0` 验收时已不存在（注销/回收），故真实对象仅
  `openKylin-3.0-desktop`；mock 层双发行版场景仍由 247 个单测覆盖。
- 只读探测会临时唤醒发行版，命令结束后 WSL 自行回到 Stopped，不构成配置变更。

**① 发行版身份（只读，TR-5.1/AC-1）**：`/etc/os-release` =
`NAME="openKylin" VERSION="3.0 (huanghe)" ID=openkylin VERSION_ID="3.0"`；
默认用户 `openkylin` / uid 1000（非 root）。

**② `okw podman preflight openKylin-3.0-desktop`（只读，退出码 2）**：

```text
[PASS] WSL 版本
[PASS] openKylin 身份
[PASS] 默认用户非 root          默认用户=openkylin uid=1000
[PASS] APT/dpkg 能力
[UNKNOWN] 包候选 podman / uidmap / slirp4netns / fuse-overlayfs
        （APT索引未知：索引缺失或过期，建议先手动 sudo apt update 后重跑；只读预检未执行 apt update）
[PASS] subuid 映射
[PASS] subgid 映射
```

**③ 包候选（只读，AC-2 前置）**：当前 APT 索引为空（`apt-cache policy podman uidmap
slirp4netns fuse-overlayfs` 仅输出包名头、无 Candidate 行），与 preflight 4 项 UNKNOWN
一致；未添加/修改任何软件源。候选是否由 openKylin 官方源提供须待 `apt update` 后确认
（属 install --yes 的授权范围，本次 blocked）。

**④ 映射现状（只读，TR-5.1）**：`/etc/subuid` 与 `/etc/subgid` 均已存在且仅有一行
`openkylin:100000:65536`——正是安装器的标准区间 [100000, 165536)；真实环境验证了
「目标用户已有映射 → install 跳过写入」的幂等路径（写入路径本身由 mock 单测 8 类场景覆盖）。
`unshare --user --map-root-user /bin/true` 实测通过（UNSHARE_OK）。

**⑤ `okw podman verify openKylin-3.0-desktop`（只读、无 --smoke-image，退出码 1）**：

```text
[PASS] WSL 版本 / 默认用户非 root(openkylin,1000) / subuid 映射 / subgid 映射 / unshare 用户命名空间
[FAIL] podman 版本   podman: 未找到命令（中文指引：先 okw podman install <发行版> --yes）
[FAIL] rootless 状态 podman info 失败：podman: 未找到命令
# 存在前置 FAIL，容器冒烟自动跳过 → 无任何容器创建、无网络请求
```

podman 二进制确未安装（rootless 尚无法成立），FAIL 与真实状态一致；AC-4 的失败矩阵
（podman 缺失、rootless false）在真实环境得到对应观测，PASS 矩阵由 mock 单测覆盖。

**⑥ blocked 项与解除条件（TR-5.1，未执行、未伪造）**：

| blocked 项 | 原因 | 解除条件 |
|---|---|---|
| 实际 APT 安装 `install --yes`（AC-2/AC-3 真实层） | 用户本次仅授权只读验收；且当前 APT 索引为空，候选需 apt update 后确认 | 用户明确授权对 `openKylin-3.0-desktop` 执行 `okw podman install openKylin-3.0-desktop --yes`（其内部先 apt update 复查候选再装 4 包；映射已存在将跳过写入） |
| 映射真实写入/幂等二跑（AC-3 真实层） | 随安装授权；且现状映射已是目标行，无缺失可追加 | 同上授权后观察 install 输出「映射已存在/跳过」；或另备缺失映射的可丢弃发行版 |
| rootless PASS 真实矩阵 + `--smoke-image` 冒烟（AC-4/AC-5 真实层） | podman 未安装；本地无已 pull/load 镜像 | 安装完成后重跑 `okw podman verify`；冒烟须先在发行版内 `podman pull/load` 本地镜像，再 `verify --smoke-image <本地镜像>`（固定 --pull=never） |

**TR-5.2 合规声明**：全过程仅执行 `wsl -l -v`、`okw list`、`okw podman preflight`、
`okw podman verify`（无 --smoke-image）与 `cat/grep/id/unshare/apt-cache policy` 只读命令；
默认发行版星标验收后仍为 `podman-machine-default`；未触 PCMClawUbuntu；未改软件源、
未写任何文件、未执行 apt update/install、未创建容器、无远程拉取。

## Task Dependencies

- Task 1 是只读预检基础；Task 2 与 Task 3 可在 Task 1 完成后并行实施。
- Task 4 依赖 Task 2 和 Task 3。
- Task 5 依赖 Task 4 的可运行实现与文档。
