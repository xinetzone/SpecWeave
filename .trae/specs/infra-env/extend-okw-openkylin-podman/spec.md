---
title: "为 okw 增加 openKylin WSL rootless Podman 支持"
status: "draft"
methodology: "seven-concepts-cmd: F→V→I→C"
content-sensitivity: "public"
source: "docs/knowledge/tech/openkylin-docs-wiki/; apps/dev-tools/openkylin-wsl-devkit/; apps/containers/AGENTS.md"
---

# 为 okw 增加 openKylin WSL rootless Podman 支持

## Overview

- **Summary**：扩展现有 `apps/dev-tools/openkylin-wsl-devkit`（CLI `okw`），为指定的 openKylin 3.0 WSL2 发行版提供 Podman 只读预检、rootless 安装与验收；不创建新的并列应用。
- **Purpose**：现有 `okw` 管理和验收 openKylin WSL，但不负责在发行版内部准备容器开发运行时。将 Podman 能力纳入同一入口，让开发者可以先确认软件源和 rootless 条件，再显式安装并验证。
- **Target Users**：在 Windows + WSL2 中使用 openKylin 3.0 开发、并希望在该发行版内以非 root 用户运行 Podman 的开发者。

## Goals

- G1：新增 `okw podman preflight <发行版>`、`okw podman install <发行版> --yes` 与 `okw podman verify <发行版>` 命令。
- G2：在安装前检查指定发行版、openKylin 身份、WSL2、默认非 root 用户、APT 能力及 rootless 前置条件。
- G3：安装 Podman 与必要的 rootless 支持；在显式确认后，为发行版默认用户安全、幂等地补齐 `/etc/subuid` 和 `/etc/subgid` 映射。
- G4：验收 Podman 以指定发行版默认用户运行且 rootless；容器运行冒烟仅在用户指定本地镜像时执行。
- G5：复用现有 `okw` 的 WSL 调用封装和零第三方运行时依赖，不复制 `apps/containers` 的容器工作负载管理能力。

## Non-Goals

- 不新建另一个 openKylin、Podman 或容器管理应用；不改变 `okw` 的包名和入口。
- 不把 openKylin WSL rootfs 转换成 OCI 镜像，也不涉及 `podman save/load` 镜像桥接。
- 不在 Windows 原生环境运行 Podman；Podman 命令只在显式指定的 openKylin WSL2 发行版中执行。
- 不添加或修改 APT 软件源，不导入第三方仓库，不自动下载或导入 WSL 发行版。
- 不设置 WSL 默认发行版或发行版默认用户，不修改 `/etc/wsl.conf`，不启用 systemd 用户服务或 Podman socket。
- 不使用 `--privileged`、不配置嵌套容器，不实现 `apps/containers` 的镜像构建、Compose 栈、工作负载或离线交付功能。
- 不执行需要联网拉取镜像的隐式容器冒烟测试。

## Background & Context

- 用户已确认系统形态为 **openKylin WSL 开发环境**，Podman 能力归入现有 `okw`，不新建并列应用。
- 已有 `.trae/specs/openkylin-wsl-devkit/` 变更已完成；原规格将发行版内开发排除在范围外。本变更是新增能力，不复开或改写其已验收范围。
- openKylin 知识库记录了 3.0 WSL2 最小镜像的默认用户、systemd 与发行版验收经验；软件源中 Podman 及 rootless 支持包的实时可用性尚未验证，因此必须在目标发行版内探测，不能把包可用当作既定事实。
- 本期预检和安装的直接包集合固定为 `podman`、`uidmap`、`slirp4netns`、`fuse-overlayfs`；Podman 声明的传递依赖由 APT 解析，不自行固定 `conmon`、`crun` 等底层包版本。
- `apps/containers/AGENTS.md` 中 `/dev/fuse`、`label=disable`、`cgroupns=host` 是该组 OCI 容器启动契约，不是 WSL 发行版内安装 Podman 的通用配置；本变更不复制或套用该容器启动参数。
- 现有 `okw` 以标准库 `argparse`/`subprocess` 实现，WSL 调用经 `okw.distro` 统一封装；Podman 安装所需的 root 权限须通过 WSL 对目标发行版执行 root 命令，不得另建绕过封装的 Windows 调用路径。

## Functional Requirements

### Requirement: 只读预检目标 openKylin 发行版

`okw` SHALL 对用户显式指定的发行版执行只读预检，并检查 `podman`、`uidmap`、`slirp4netns`、`fuse-overlayfs` 四个直接包的候选可用性。预检 SHALL NOT 更新 APT 索引、安装软件包、修改配置文件或更改 WSL 状态。

#### Scenario: 预检满足基础条件

- **WHEN** 用户运行 `okw podman preflight <发行版>`
- **AND** 目标已注册、为 WSL2、`/etc/os-release` 可识别为 openKylin，且默认用户非 root
- **THEN** `okw` SHALL 检查发行版内 APT/dpkg 能力、上述四个直接包的候选可用性，以及默认用户的 subuid/subgid 映射
- **THEN** `okw` SHALL 输出逐项可读的通过、失败或未知结果；软件包索引缺失或过期导致无法确认时 SHALL 明确标为未知
- **THEN** 当 APT 索引缺失/过期导致候选状态为未知时，`okw` SHALL 在对应项下方额外输出中文行动建议：`未知：发行版 APT 索引缺失或已过期，建议在发行版内先手动执行 sudo apt update 后重跑 preflight`
- **THEN** 预检 SHALL 保持发行版配置、软件包状态与默认发行版不变，仍不得自动执行 apt update

#### Scenario: 发行版或运行条件不符合

- **WHEN** 用户指定的发行版不存在、不是 WSL2、不是 openKylin，或默认用户为 root
- **THEN** `okw` SHALL 给出失败项和可执行的修复指引，并以非零状态结束
- **THEN** `okw` SHALL NOT 自动创建用户、修改默认用户或继续安装

### Requirement: 显式确认后安装 rootless Podman

`okw` SHALL 仅在用户显式确认后，向指定 openKylin WSL2 发行版安装上述四个直接包及 APT 解析出的传递依赖。安装 SHALL 使用该发行版当前配置的软件源，且 SHALL NOT 添加或改写软件源。

#### Scenario: 安装前置检查通过且用户已确认

- **WHEN** 用户运行 `okw podman install <发行版> --yes`
- **AND** 只读前置检查通过
- **THEN** `okw` SHALL 在指定发行版中更新本地 APT 索引、确认四个直接包均存在候选版本，并通过发行版内包管理器一次安装直接包及传递依赖
- **THEN** `okw` SHALL 在安装结束后执行 rootless 验收并报告逐项结果
- **THEN** `okw` SHALL NOT 对其他发行版执行命令，也 SHALL NOT 改变 WSL 默认发行版

#### Scenario: 缺少用户确认或软件包不可用

- **WHEN** 用户未提供 `--yes`，或目标发行版内所需软件包在现有软件源中没有可安装候选
- **THEN** `okw` SHALL 在安装软件包或改写用户映射前拒绝继续，并给出明确原因和建议
- **THEN** `okw` SHALL NOT 添加第三方软件源或静默改用未经用户选择的软件源

#### Scenario: 安装中途失败

- **WHEN** APT 安装、映射配置或后续验收任一步骤失败
- **THEN** `okw` SHALL 返回非零状态，指出失败阶段，并报告可能已完成的变更
- **THEN** `okw` SHALL NOT 宣称安装成功或自动卸载软件包；规格不要求跨 APT 与系统文件变更提供事务回滚

### Requirement: 安全配置 rootless 用户映射

安装流程 SHALL 使用目标发行版当前默认的非 root 用户作为 rootless Podman 用户。只有在目标用户映射缺失且标准 `100000:65536` 范围对 UID 与 GID 均无重叠时，系统才可追加该映射。

**定义（判定矩阵）**：
- 一条映射行 `name:start:count` 的区间定义为 `[start, start+count)`（左闭右开，不含结束端点）。
- "区间重叠"：任意两条映射的区间有交集（一条的 start 在另一条的区间内即视为重叠；端点恰好相等 `A.end == B.start` 不算重叠）。
- "目标用户的有效映射"：`/etc/subuid`（或 `/etc/subgid`）中存在至少一行 `name=<默认用户名>` 且 `start` 与 `count` 均为正整数、区间与其它行不与其它任何用户区间重叠、区间跨度 ≥ 65536 的映射；满足以上全部条件方判定为"已有有效映射"。
- "无效映射"：出现以下任一情形即判为无效——目标用户名存在但 `start/count` 不是正整数、目标用户同名多行区间互相冲突、目标用户区间与其它用户区间重叠、映射文件无法按 `name:start:count` 三列格式解析。

#### Scenario: 映射缺失且范围可安全使用

- **WHEN** 安装已获 `--yes` 确认，目标默认用户为非 root，且 `/etc/subuid` 或 `/etc/subgid` 缺少有效映射
- **AND** 标准区间 `[100000, 165536)` 与现有任一条其它账户映射的区间均无重叠
- **THEN** `okw` SHALL 只为缺失的文件（subuid 缺补 subuid，subgid 缺补 subgid，均缺则两者都补）在文件末尾追加目标用户的 `<默认用户名>:100000:65536` 行
- **THEN** 重复执行 SHALL 识别已有有效映射并跳过追加；重复执行两遍后文件内容逐字节不变（幂等）

#### Scenario: 映射冲突或现状不明确

- **WHEN** 目标用户现有映射无效、标准区间 `[100000, 165536)` 与其他账户区间存在重叠，或映射文件无法安全解析/写入
- **THEN** `okw` SHALL 在改写映射前中止该配置步骤，输出冲突对比（列出已存在的冲突用户名与其区间），并给出"请手动编辑 /etc/subuid 与 /etc/subgid 为目标用户选择不冲突的区间段后重跑 install"的中文建议
- **THEN** `okw` SHALL 保留已有映射原文，不得覆盖、重排或删除任何已有行；中止后目标映射文件前后内容逐字节一致

### Requirement: 验收 rootless Podman

`okw podman verify <发行版>` SHALL 只读检查 Podman 可执行性、版本、目标默认用户、rootless 模式、subuid/subgid 映射与 rootless 用户命名空间能力。

#### Scenario: rootless 环境验收通过

- **WHEN** 用户运行 `okw podman verify <发行版>`
- **AND** Podman 可由发行版默认非 root 用户运行，Podman 报告 rootless，且映射及用户命名空间检查通过
- **THEN** `okw` SHALL 输出逐项 PASS 结果并以零状态结束
- **THEN** `okw` SHALL NOT 以 root 身份冒充 rootless 验收结果

#### Scenario: 可选的本地镜像容器冒烟

- **WHEN** 用户显式通过 `--smoke-image <本地镜像>` 请求容器冒烟
- **THEN** `okw` SHALL 仅使用指定发行版内已存在的该镜像运行一次临时容器，并禁止隐式拉取镜像
- **THEN** 镜像不存在或容器启动失败时 SHALL 报告失败，不得自动访问远程 registry

### Requirement: 保持 okw 既有调用与应用边界

Podman 能力 SHALL 作为现有 `okw` 的子命令实现，并复用统一的 WSL 结果处理与错误提示。新增运行时实现 SHALL 保持零第三方依赖，并更新用户文档及 apps 应用索引中的既有应用说明。

#### Scenario: 既有命令不回归

- **WHEN** 新版 `okw` 执行既有发行版管理、五步验收、脚手架和知识参考命令
- **THEN** 既有命令参数、默认发行版保护、退出状态和行为 SHALL 保持兼容
- **THEN** `okw --help` 与 README SHALL 展示一致的 Podman 子命令及确认/副作用边界

## Non-Functional Requirements

- **NFR-1（运行时依赖）**：继续使用 Python 标准库和现有 `scikit-build-core` 包构建，不增加第三方运行时依赖。
- **NFR-2（WSL 调用）**：发行版命令 SHALL 复用 `okw.distro` 的 `wsl.exe` 定位、`WSL_UTF8=1` 注入、超时和受控错误归一；需要 root 权限时显式指定目标发行版内的 root 用户。
- **NFR-3（测试）**：单元测试不得真实安装软件或改写系统文件；Podman 子进程与映射文件操作须可注入/隔离测试。应用整体覆盖率不低于 80%，新增关键 Podman 模块不低于 90%。
- **NFR-4（输出）**：命令错误 SHALL 以中文说明失败阶段与后续操作；不得将敏感环境内容或无关发行版数据写入文件。
- **NFR-5（兼容）**：Windows + WSL2 为宿主支持范围；目标为 openKylin 3.0 WSL2。软件源包可用性作为运行时探测结果，不作为静态假设。

## Constraints

- **Technical**：目标发行版需提供 APT/dpkg；所需 rootless 包的精确可用性取决于其现有软件源和索引状态。安装前先检查，安装中刷新索引后再次检查。
- **Security**：`preflight` 与默认 `verify` 只读；`install` 必须要求 `--yes`；全部变更必须限定于显式指定的发行版和目标默认用户。
- **Compatibility**：不将容器组的 OCI 启动契约误用于发行版宿主 Podman，也不要求 `/dev/fuse`、`--privileged`、systemd 用户服务或远程镜像拉取作为基础安装条件。
- **Dependencies**：Windows WSL2、已导入的 openKylin 3.0 WSL2 发行版及该发行版现有 APT 软件源；实际安装验证还依赖所需包有可用候选。

## Assumptions

- 本期面向知识库记录的 openKylin 3.0 WSL2 最小镜像，桌面镜像不增加独立适配逻辑。
- `podman`、`uidmap`、`slirp4netns`、`fuse-overlayfs` 由目标发行版当前软件源提供；若任一直接包探测不到，工具安全停止而不引入外部源。
- `/etc/subuid` 与 `/etc/subgid` 的标准映射范围采用 `100000:65536`；若与现存配置冲突，交由用户处理。
- 容器实际运行冒烟需要用户提供本地镜像；默认验收不联网、不拉取镜像。

## Acceptance Criteria

### AC-1：预检为只读且目标明确

- **Type**：`rule`
- **Given**：模拟目标发行版不存在、WSL1、非 openKylin、root 默认用户、APT 能力缺失、软件包候选未知/缺失及全部通过等情况
- **When**：执行 `okw podman preflight <发行版>`
- **Then**：每种情况均输出可区分的逐项结果和正确退出状态；命令不执行安装、索引更新、映射写入或默认发行版变更
- **Pass Condition**：隔离测试断言调用序列、退出码和文件系统前后快照全部通过
- **Evidence**：Podman 预检单元测试与副作用哨兵断言

### AC-2：安装有显式确认和发行版边界

- **Type**：`rule`
- **Given**：符合条件的 openKylin WSL2 发行版
- **When**：无 `--yes` 执行安装，或有 `--yes` 执行安装
- **Then**：无确认时零安装/配置写入；确认后只在指定发行版中执行包管理与 root 映射命令；不改软件源、其他发行版、WSL 默认发行版或 `/etc/wsl.conf`
- **Pass Condition**：mock WSL 命令序列及配置文件快照断言通过
- **Evidence**：安装流程单元测试与 CLI 集成测试

### AC-3：subuid/subgid 更新安全且幂等

- **Type**：`rule`
- **Given**：映射缺失、已有有效映射、重复运行、范围重叠、畸形文件、文件不可写等输入
- **When**：安装流程配置 rootless 用户映射
- **Then**：只追加缺失且安全的 `100000:65536` 映射；有效既有内容保持不变；冲突或异常时停止且不覆盖其他用户记录
- **Pass Condition**：临时文件系统中的表驱动和重复执行测试通过
- **Evidence**：映射管理模块测试、原始文件逐字节对比

### AC-4：Podman 验收确认真实 rootless 上下文

- **Type**：`rule`
- **Given**：Podman 不存在、版本读取失败、rootless 为 false、映射无效、unshare 失败和全部通过等输出
- **When**：执行 `okw podman verify <发行版>`
- **Then**：结果准确反映每项状态，root 身份下不得报告 rootless PASS，失败返回非零状态
- **Pass Condition**：mock 输出矩阵覆盖每一项判断，实际 openKylin 环境可用时以默认用户运行验收
- **Evidence**：verify 模块单元测试；目标 WSL 可用时的只读执行记录

### AC-5：容器冒烟不隐式拉取镜像

- **Type**：`rule`
- **Given**：用户未请求冒烟、指定的本地镜像存在或不存在
- **When**：执行默认 verify 或 `verify --smoke-image <镜像>`
- **Then**：默认 verify 不执行容器；显式冒烟仅用本地镜像并禁止拉取；镜像缺失时清晰失败
- **Pass Condition**：命令参数断言包含禁止拉取语义，且测试中无网络调用
- **Evidence**：冒烟参数构造测试及无网络测试守卫

### AC-6：既有 okw 能力与包构建无回归

- **Type**：`rule`
- **Given**：现有 `okw` 测试与包配置
- **When**：运行完整测试及 wheel 构建
- **Then**：既有子命令通过，新增 Podman 命令可从安装入口调用，运行时依赖未增加，wheel 构建成功
- **Pass Condition**：全量测试通过、总体覆盖率 ≥80%、关键 Podman 模块覆盖率 ≥90%、wheel 构建成功
- **Evidence**：pytest/coverage 与 wheel 构建记录

### AC-7：文档和区域索引一致

- **Type**：`rule`
- **Given**：新版 CLI help、README 和 apps 索引
- **When**：核对三个入口
- **Then**：命令名称、`--yes` 确认条件、rootless 行为、软件源限制和冒烟边界一致；apps/AGENTS.md 与 apps/README.md 更新既有 `okw` 描述而非新增重复应用
- **Pass Condition**：文档命令与 `okw --help` 逐项对应且链接有效
- **Evidence**：文档核对记录与链接检查

### AC-8：源不可达与首次使用场景的用户体验

- **Type**：`rubric`
- **Given**：干净 openKylin 3.0 WSL2 发行版（APT 索引为空或未刷新）、或现有软件源中缺失 4 个直接包中任一个
- **When**：首次运行 `okw podman preflight`、以及 `install --yes` 在复查候选阶段命中包不可达
- **Then**：预检输出不伪装 PASS，对未知/不可达项附带中文行动建议；安装失败时明确区分「包不在源里」「APT 网络错误」「哈希校验失败」三类常见原因，分别给出对应建议，并标注「禁止添加第三方源，如需启用官方 backports 或 proposed 组件请手动编辑 sources.list」
- **Pass Condition**：三类失败原因的输出均可被用户独立识别为「环境问题」而非「okw 内部错误」，退出码仍为非零；文档 README 的「常见问题」章节收录三者对应说明
- **Evidence**：预检/安装的 mock 输出矩阵与 README FAQ 章节核对

### AC-9：新用户入门与副作用说明完备

- **Type**：`rubric`
- **Given**：首次接触 okw podman 子命令的开发者
- **When**：阅读 `okw podman --help`、`okw podman install --help` 与 README 的「Podman 入门」段落
- **Then**：三个入口共同明确以下事实且无矛盾：① rootless Podman 与 sudo podman 的区别与为什么推荐 rootless；② `--yes` 一次性确认的副作用清单（≥4 条：apt update、安装 4 个直接包、追加 subuid/subgid 映射行、事后运行 rootless verify）；③ 如何查询发行版名（通过 `okw list` 或 `wsl -l -v`）；④ `--smoke-image` 前置条件（必须先在目标发行版内手动 `podman pull <镜像>`，默认 verify 不联网不拉镜像）
- **Pass Condition**：任意一条缺失或三入口不一致即判不通过
- **Evidence**：三入口文档逐字段对照表

## Open Questions

- 产品范围无待决项。目标发行版当前软件源是否提供所需包，是安装前/安装时的运行时门禁；若本机没有可用的 openKylin 3.0 发行版，真实安装验收须如实记录为 `blocked`，不得用 mock 结果替代。
