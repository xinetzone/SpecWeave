# Toolbx 宿主镜像变体与 devuser UID 修复 - 产品需求规格

## Overview

- **Summary**：修复 `jupyter-podman-rootless` 镜像 devuser 实际 UID 为 1001（文档声称 1000）的事实性缺陷，并新增一个可被宿主机 Toolbx（`toolbox create/enter`）直接使用的专用镜像变体 `:toolbx`。
- **Purpose**：2026-09-11 在 podman-machine-default（Fedora 43 rootless VM）端到端验证宿主侧 `toolbox create` 流程时实证：①基础镜像自带 `ubuntu(1000)` 致 devuser 落 1001，Toolbx 按宿主用户 UID 同步时连续撞 useradd/usermod；②镜像 tini+entrypoint.sh 入口链与 HEALTHCHECK 使镜像无法直接作为 Toolbx 容器（Toolbx 只覆盖 Cmd 不覆盖 ENTRYPOINT）。
- **Target Users**：在 WSL2/podman machine/Linux 宿主机上希望用 `toolbox create -i ...` + `toolbox enter` 获得透传开发体验的用户；以及所有消费 `:latest` 普通镜像的既有用户（UID 修复的间接受益者）。

## Goals

- devuser 在镜像内**确定地**占用 UID/GID 1000（与全部既有文档承诺、Linux 主机默认用户 UID 对齐）。
- 提供 `localhost/jupyter-podman-rootless:toolbx` 变体：零定制即可 `toolbox create -i <tag> -c <name>` → `toolbox enter/run`，用户身份/UID/HOME/cwd/`/run/host` 透传可用。
- 普通模式（`:latest` + entrypoint/supervisord + client 叠加层）零行为回归。
- Toolbx 使用路径、宿主前置条件与 WSL 限制有权威文档。

## Non-Goals

- 不改变普通模式的进程模型（root 跑 supervisord → jupyter/sshd 降权 devuser）、DinP/rootless 三必需、compose/client 编排方式。
- 不在 WSL 精简 VM 内解决 `flatpak-spawn --host` D-Bus 门户缺失（VM 环境天花板；仅文档如实说明）。
- 不把 toolbox/p11-kit-server 安装进 podman machine VM（VM 非本仓库管理资产；仅文档给出 `dnf install` 路径）。
- 不修改 vendor/toolbox 上游源码（只读 submodule）。
- 不做镜像发布/推送（仅本地 tag）。

## Background & Context

- 上游权威实现 [vendor/toolbox/images/ubuntu/26.04/Containerfile](../../../vendor/toolbox/images/ubuntu/26.04/Containerfile) 第 41 行显式 `userdel --remove ubuntu`（注释：uid 1000 会与宿主用户冲突），第 37 行 flatpak-spawn symlink 装法与我方一致。
- Toolbx create 机制（[vendor/toolbox/src/cmd/create.go](../../../vendor/toolbox/src/cmd/create.go) L412-L480）：入口为 PATH 解析的 `toolbox init-container ...`；挂载宿主 toolbox 到 `/usr/bin/toolbox` 并注入 `TOOLBOX_PATH`；`--privileged --network host --pid host --ipc host` + `/:/run/host`；只设 Cmd 不清镜像 ENTRYPOINT。
- 当前 Containerfile Layer 3（[Containerfile L560-L567](../../../apps/containers/jupyter-podman-rootless/Containerfile)）在 UID 1000 被占时走"自动分配"分支 → devuser=1001。
- 实测证据（2026-09-11，session sc-20260911-host-toolbox-create-verify）：VM 内用临时派生镜像（userdel ubuntu+用户收编 1000+`ENTRYPOINT []`+`HEALTHCHECK NONE`）成功 `toolbox create/run`，容器内 `uid=1000(user) groups=sudo,docker`、HOME/cwd 透传、`/run/host` 完整、Python 3.14.7 可用。
- entrypoint.sh 全部以 `${NON_ROOT_USER}` 名字操作属主（无硬编码 UID），UID 固定 1000 与其兼容。
- 既有预防机制：client 叠加层基底指纹（2026-09-11 早些时候交付）会在基底更新后提示重建，本变更须联动重建 client:latest。

## Functional Requirements

- **FR-1**：主 Containerfile 在创建 devuser 前删除基础镜像自带的 ubuntu 用户（含家目录），devuser 固定以 UID/GID 1000 创建；"UID 被占自动分配"分支移除。
- **FR-2**：新增 `Containerfile.toolbx`（FROM 主镜像）：清空 ENTRYPOINT、关闭 HEALTHCHECK；wrapper 遮蔽问题以实测裁决（优先保留 wrapper 借 TOOLBOX_PATH 转发容器内原生二进制；不通则删 wrapper 影子），并在文件注释记录裁决结论。
- **FR-3**：构建入口可产出 `:toolbx` tag（invoke 任务与/或 jpman CLI，按 Plan 选定的最小路径），构建上下文/缓存策略与主镜像一致。
- **FR-4**：文档（docs/07-toolbx-passthrough.md）新增"宿主机 Toolbx 流程"章节：变体镜像名、宿主前置（toolbox/libsubid/p11-kit-server）、首次 `toolbox create` 触发 `podman system migrate` 会停掉运行中容器的警告、WSL socket 通道（CONTAINER_HOST/无 systemd 用户实例/HEALTHCHECK）、flatpak-spawn --host 的 WSL 限制。
- **FR-5**：所有声称 devuser UID 的文档/注释与修复后事实一致（UID 1000 固定；"动态分配 1000/1001"表述删除或改写）。
- **FR-6**：client 叠加层基于修复后的基底重建，jupyter-podman 容器以新镜像重启且既有 token/密码可沿用。

## Non-Functional Requirements

- **NFR-1**：每个镜像交付结论必须有可观测证据（构建日志、容器内命令输出），禁止无证据宣称成功。
- **NFR-2**：构建在 WSL 原生文件系统执行（9p 构建极慢，项目既有约定）；仅失效层重建，apt/conda 层缓存命中。
- **NFR-3**：变更原子化、可独立回滚（UID 修复与 toolbx 变体为不同提交粒度）。
- **NFR-4**：中文沟通与中文 commit 主体；遵循应用 AGENTS.md 与 containerfile/build-test 规则。

## Constraints

- **Technical**：Podman 5.7.1 rootless（VM uid=1000 user）；主镜像 ubuntu:26.04；vendor 只读；构建 `--format docker`（OCI 忽略 SHELL/HEALTHCHECK）。
- **Business**：不破坏 `:latest` 既有用户；workspace 是宿主挂载盘数据不丢；重启容器沿用既有凭据。
- **Dependencies**：构建前置 stage（vendor 三子模块）已就绪；client 基底指纹机制已上线。

## Assumptions

- devuser 固定 UID 1000 不影响任何既有消费者（文档从未承诺 1001；client 用 `--chown=devuser:devuser` 名字而非 UID；entrypoint 全用用户名）。
- 保留 wrapper 的变体路径可行（TOOLBOX_PATH 非空 → exec 容器内 `/usr/local/libexec/toolbox`），实测若失败则以删 wrapper 兜底，不影响规格目标。
- `:latest` 重建后 Layer 1/2 缓存仍命中（基础 apt 层与 conda/toolbox COPY 层不变）。

## Acceptance Criteria

### AC-1: devuser 确定为 UID/GID 1000
- **Type**: `rule`
- **Given**: 修复后构建出的 `localhost/jupyter-podman-rootless:latest`
- **When**: 在镜像内执行 `id -u devuser`、`id -g devuser`、`getent passwd 1000`、`getent passwd ubuntu`
- **Then**: uid=1000、gid=1000、passwd 1000 条目为 devuser、ubuntu 用户不存在
- **Pass Condition**: 四条命令输出全部符合
- **Evidence**: `podman run --rm` 实际输出（构建日志 + 命令回显）

### AC-2: :toolbx 变体可被宿主 Toolbx 直接使用
- **Type**: `rule`
- **Given**: podman-machine-default VM（uid=1000 user）内构建并提供 toolbox 二进制
- **When**: 执行 `toolbox create -i localhost/jupyter-podman-rootless:toolbx -c jupyter-dev` 后 `toolbox run -c jupyter-dev id` 及透传检查
- **Then**: create 退出码 0；`id` 输出 uid=1000(user) 且含 sudo 组（上游 init-container 仅经 `GetGroupForSudo` 加入 sudo 组；docker 组非其职责，实施实测修正原"sudo/docker"表述）；HOME=/home/user；`/run/host` 存在且非空；容器内 Python 3.14 可运行；重复 run/create 幂等无 init 错误
- **Pass Condition**: 上述检查项全部通过（flatpak-spawn --host 除外，见 FR-4 文档声明）
- **Evidence**: toolbox 命令回显、inspect（ENTRYPOINT=[]、无 Healthcheck）

### AC-3: 普通模式零回归
- **Type**: `rule`
- **Given**: 用修复后 :latest 以与现网一致参数启动 jupyter-podman
- **When**: 检查 supervisord 服务、端口、容器内 toolbox 指引、workspace 挂载
- **Then**: jupyter+sshd RUNNING；http://localhost:8888 可访问（原 token）；容器内 `toolbox create` 输出中文指引（wrapper 行为不变）；/workspace 内容为宿主工作区
- **Pass Condition**: 全部符合
- **Evidence**: supervisorctl status、curl/HTTP 状态、toolbox 输出、挂载列表

### AC-4: client 叠加层联动完成
- **Type**: `rule`
- **Given**: 修复后 :latest 已构建
- **When**: 重建 client:latest 并重启容器，容器内检查 devuser
- **Then**: 基底指纹 label 与新基底 digest 一致；`invoke run` 无陈旧告警；容器内 `id -u devuser`=1000
- **Pass Condition**: 三条全中
- **Evidence**: inspect label、run 输出、容器内 id 输出

### AC-5: 文档与事实一致且覆盖宿主流程
- **Type**: `rule`
- **Given**: 全部变更文件
- **When**: 逐条核对 UID 表述与镜像事实；按 docs/07 新增章节在 VM 从零走一遍
- **Then**: 仓库内无"devuser 动态分配/常见 1001"残留表述（历史 CHANGELOG 记录除外）；文档步骤可复现 AC-2
- **Pass Condition**: grep 核对 + 文档走查通过
- **Evidence**: grep 结果、走查记录

### AC-6: 变体设计的最小侵入与可维护性
- **Type**: `rubric`
- **Dimension**: 变体与主镜像的重复度、构建集成简洁度、裁决依据可追溯性
- **Scale**: 1-5
- **Anchors**: 1 = 复制整套 Containerfile 或改动主镜像运行模型；3 = 独立变体文件但有较多重复指令、集成方式生硬；5 = 变体仅含必要差异指令、构建入口自然、注释记录实测裁决与上游依据
- **Pass Threshold**: >= 4
- **Evidence**: Containerfile.toolbx 内容、构建任务 diff、review 评阅

## Open Questions

- [x] wrapper 在变体中保留还是删除？→ 实施时以容器实测裁决（优先保留：TOOLBOX_PATH 非空即转发容器内原生二进制），结论写入 Containerfile.toolbx 注释与 tasks 证据。
- [ ] toolbx 变体构建入口形态（invoke `--flavor` vs jpman 子命令 vs 仅文档化 podman build）→ Plan 阶段按最小改动选定并在 tasks 注明。
