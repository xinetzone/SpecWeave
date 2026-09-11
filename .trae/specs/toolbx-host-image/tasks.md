# Toolbx 宿主镜像变体与 devuser UID 修复 - 实施计划

> 规格：[spec.md](spec.md)。任务按依赖序执行；每项完成必须附 Completion Evidence（真实命令输出），禁止无证据宣称完成。

## Task 1: 主镜像 devuser UID 固定 1000（对齐上游 userdel ubuntu）

- **Status**: `completed`
- **Completion Evidence**:
  - Containerfile Layer 3 已改为 userdel ubuntu + 兜底 groupdel + `useradd -u 1000 -U`；auto-assign 分支删除（grep 无残留）；Layer 5 三条断言就位且构建日志出现 `[OK] devuser fixed at UID/GID 1000`、`[OK] passwd entry for UID 1000 is devuser`、`[OK] stock ubuntu account absent`。
  - entrypoint.sh 3 处"动态分配"注释改写；`bash -n` 通过。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 修改 [Containerfile](../../../apps/containers/jupyter-podman-rootless/Containerfile) Layer 3（约 L547-L568）：创建 devuser 前先 `userdel --remove ubuntu`（对齐上游 images/ubuntu/26.04/Containerfile L41，忽略 mail spool 缺失），随后固定 `useradd -m -s /bin/bash -u 1000 -G sudo,docker devuser`；删除"UID 1000 被占→自动分配"分支与 `NON_ROOT_USER ... auto-assigned` 类注释。
  - 同步修正 Containerfile 头部 L8 注释（"UID 1000 if available, auto-assigned otherwise" → 固定 1000）。
  - Layer 3/5 构建期校验追加：`test "$(id -u devuser)" = 1000`、`getent passwd 1000 | cut -d: -f1` 必须为 devuser、`! getent passwd ubuntu`。
  - 同步同文件内 build-info echo（DEVUSER_UID 实际值仍动态采集，保留）。
  - entrypoint.sh L201/L259 等处"devuser UID 动态分配/禁止硬编码 1000"注释改写为"UID 固定 1000，仍以用户名派生日录（不写死数值）"语义；代码逻辑不动。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-1.1: Containerfile grep 不再存在 auto-assign 分支；新增三条构建期断言且构建日志可见 [OK]。
  - `rule` TR-1.2: 构建产物内 `id -u devuser`=1000、`id -g devuser`=1000、`getent passwd 1000` 第一字段=devuser、`getent passwd ubuntu` 退出非 0（在 Task 3 构建后取证）。
- **Notes**: 纯镜像层变更，entrypoint 运行逻辑零改动；历史 CHANGELOG 中 1001 记录属历史事实，不改写。

## Task 2: Toolbx 专用变体 Containerfile.toolbx + invoke build.toolbx 入口

- **Status**: `completed`
- **Completion Evidence**:
  - `Containerfile.toolbx` 落地（LABEL flavor + userdel devuser/%sudo NOPASSWD + HEALTHCHECK NONE + ENTRYPOINT []），文件头含双裁决注释；`inv --list` 出现 `build-toolbx`（根级与 container 集合均可见）；基底缺失分支返回中文指引（逻辑评审，未实际删基底触发）。
  - 裁决一（wrapper 影子）：保留——Task 4 实测 init-container 经 wrapper 转发成功；裁决二（用户名模型）：Task 4 首轮实测 `useradd: UID 1000 is not unique` 后回环追加 `userdel devuser`，第二轮通过（本任务实际经历了 tasks 预案的回环）。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新增 `apps/containers/jupyter-podman-rootless/Containerfile.toolbx`：`ARG BASE_IMAGE=localhost/jupyter-podman-rootless:latest` + `FROM ${BASE_IMAGE}`；`LABEL org.specweave.flavor=toolbx`；`HEALTHCHECK NONE`；`ENTRYPOINT []`。文件头注释写明：①与上游 toolbox 机制依据（create.go 只覆盖 Cmd）；②wrapper 影子裁决结论（实测优先保留 wrapper：TOOLBOX_PATH 非空时 exec 容器内 /usr/local/libexec/toolbox；实测不通则追加 `RUN rm -f /usr/local/bin/toolbox` 并记录原因）；③适用命令 `toolbox create -i ...:toolbx`。
  - [build.py](../../../apps/containers/jupyter-podman-rootless/src/jpman_builder/tasks/build.py) 新增任务函数 `build_toolbx(c, tag=None, base_image=None)` 并在任务命名空间暴露为 `build.toolbx`：默认 tag `localhost/jupyter-podman-rootless:toolbx`；前置检查 base 镜像存在（不存在报中文错误指引先 `invoke build`）；固定 `podman build --format docker -f Containerfile.toolbx -t <tag> --build-arg BASE_IMAGE=<base> .`（CLI 直构，秒级薄层，不走三后端/compose/stage）。
  - tasks 命名空间注册处（tasks.py 或包 __init__）登记新任务。
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: `invoke --list` 出现 build.toolbx；base 缺失时退出非 0 且输出可执行指引。
  - `rule` TR-2.2: 构建成功后 inspect：`Config.Entrypoint` 为 `[]`、`Config.Healthcheck` 为空、含 flavor label；镜像历史仅薄层（Size 量级 MB 级）。
  - `rubric` TR-2.3: 最小侵入度 1-5（锚点见 spec AC-6），阈值 >=4；自评证据=变体文件行数/指令数、build.py diff 范围、未触碰三后端与 jpman/Windows 脚本。
- **Notes**: wrapper 裁决在 Task 4 实测落锤；若需 rm wrapper，回到本任务追加一条指令并更新注释。

## Task 3: WSL 原生文件系统构建主镜像与变体（取证 AC-1）

- **Status**: `completed`
- **Completion Evidence**:
  - 上下文 tar 同步 VM `~/build/jpr`（7.4M，排除缓存；含已 stage upstream）；主镜像在工具托管后台任务构建成功（final stage 重建，镜像 065b678a432b；中途排查并弃用 nohup 方案——wsl 会话退出即杀后台进程，旧 /tmp 日志曾造成误判，已记录教训）。
  - AC-1 实测：`id devuser` → `uid=1000(devuser) gid=1000(devuser) groups=1000,27(sudo),997(docker)`；`getent passwd 1000` → `devuser:x:1000:1000:...`；`getent passwd ubuntu` 退出非 0。
  - 变体 history 三条指令确认：`LABEL flavor=toolbx`、`HEALTHCHECK NONE`、`ENTRYPOINT []`；inspect `ep=null`。
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 在 podman-machine-default VM 内 `~/build/jpr/` 准备构建上下文（避开 9p；tar 同步时排除 `.image-cache/.wsl-cache/.temp/upstream/__pycache__`；upstream/ 由 stage 机制在 VM 内基于 /mnt/d 的 vendor 源重新生成，或先在 Windows 侧运行 stage 再随 tar 同步——二选一以实际最短路径执行并记录）。
  - VM 内构建 `:latest`（tuna mirrors，--format docker），确认 Layer 1/2 缓存命中、Layer 3 起重建；构建日志保留 Task 1 三条断言 [OK]。
  - 取证 AC-1 四条命令输出。
  - VM 内构建 `:toolbx`（直接 podman build -f Containerfile.toolbx），取证 TR-2.2。
  - 清理 VM 内临时上下文（~/build/jpr 保留至 Review 结束后由用户决定去留）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-3.1: 构建退出码 0；镜像列表同时出现新 :latest（Created 当日）与 :toolbx。
  - `rule` TR-3.2: AC-1 四命令、TR-2.2 inspect 输出全部附入 Completion Evidence。
- **Notes**: 拉取/网络失败时按既有 Miniforge 多源回退经验处理，不跳过失败断言；构建后台运行并轮询日志。

## Task 4: VM 端到端 Toolbx 流程验证（含 wrapper 裁决）

- **Status**: `completed`
- **Completion Evidence**:
  - `toolbox create -i ...:toolbx -c jupyter-dev` → Created（rc0）；`toolbox run id` → `uid=1000(user) gid=1000(user) groups=1000(user),27(sudo)`；HOME=/home/user、pwd=/home/user；`ls /run/host` 非空（afs/bin/boot/...）；Python 3.14.7；`sudo -n true` 通过（%sudo NOPASSWD）；容器内 podman 5.7.0 可执行；二次 run whoami=user 幂等；`toolbox list` 显示 running；重复 create → `container already exists`（rc1）容器无损。
  - wrapper 路径实证：容器内 `which toolbox` 指向 TOOLBOX_PATH 挂载源，`toolbox --version` 正常；flatpak-spawn --host 按备案失败（D-Bus 门户缺失，环境限制不计失败）。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 复用 2026-09-11 已就位的宿主 toolbox（~/.local/bin/toolbox + compat-lib libsubid 软链；若环境被重置则重新放置并记录）。
  - 清理旧验证容器：`toolbox rm -f jupyter-dev`（派生镜像 jupyter-toolbx-host:latest 验证完毕可删）。
  - `toolbox create -i localhost/jupyter-podman-rootless:toolbx -c jupyter-dev`（经 socket 通道 CONTAINER_HOST=unix:///run/user/1000/podman/podman.sock，HOME/XDG/LD_LIBRARY_PATH 显式导出）。
  - **wrapper 裁决**：首次保留 wrapper 直接验证 `toolbox run`；若 init 失败且证据指向 wrapper 遮蔽（如 `exec: --: invalid option`），回到 Task 2 加 rm wrapper 指令重建变体再验。
  - 验证项：`id`（uid=1000 user、组含 sudo/docker）、`printenv HOME`=/home/user、`pwd`、`ls /run/host` 非空、`/opt/conda/bin/python --version`=3.14.x、二次 run 幂等、`toolbox list` 含 jupyter-dev/created→running。
  - 预期失败项备案：`flatpak-spawn --host`（WSL 无 D-Bus 门户）记录为环境限制，不计失败。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-4.1: spec AC-2 全部检查项有命令回显证据；wrapper 裁决结论与最终 Containerfile.toolbx 内容一致。
  - `rule` TR-4.2: create 幂等（已存在时 toolbox 自身行为正常，不产生半初始化容器）。
- **Notes**: system migrate 已在当日首跑完成（stamp=5.7.1），不应再停容器；若再发生须记录并恢复受影响容器。

## Task 5: 普通模式回归 + client 叠加层联动重建

- **Status**: `completed`
- **Completion Evidence**:
  - 联调中暴露并修复两个回归：①`ln same file`（UID 对齐后挂载路径=运行时路径，entrypoint set -e 中止，容器 start 1s 后 died(1)）；②**B-scheme socket 属主穿透**（entrypoint `chown -R /run/user/1000` 穿透单文件挂载改宿主 socket 为 525287:525287，sshd 拒连、Windows CLI 全断）——`sudo chown user:user` 即时恢复，根因修复（禁递归 + ln 幂等）后级联重建三镜像。
  - 终态：client label base-digest `sha256:2826166e…` == 基底 Digest（DIGEST_MATCH 逐字符）；`inv run` 无陈旧告警；容器内 id -u devuser=1000；supervisorctl jupyter/sshd RUNNING；Jupyter HTTP **200**（原 token）；容器内 toolbox create 中文指引；workspace 可见 Containerfile.toolbx；宿主 socket 保持 user:user 0660；remote API 5.7.1；双容器并存（jupyter-dev + jupyter-podman）。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - Windows 侧（py314）于 apps/containers/client：`inv env.build-layer` 重建叠加层（确认基底指纹输出为新 :latest digest）。
  - `inv stop && inv run --workspace D:/spaces/SpecWeave --jupyter-token <原token> --user-password <原密码>`（沿用 nmXMaAK…/zsb4MNWQ… 现网凭据）。
  - 回归取证：容器内 `id -u devuser`=1000；supervisorctl jupyter/sshd RUNNING；curl http://localhost:8888 HTTP 200/302（带 token /lab 可访问）；容器内 `toolbox create` 仍为 wrapper 中文指引（exit 1）；workspace 挂载与文件可见；`invoke run` 输出无"叠加层基底陈旧"告警。
  - 确认 VM 侧 jupyter-dev 与 jupyter-podman 双容器并存不互扰（端口/命名空间）。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-5.1: AC-3/AC-4 每项有输出证据；Jupyter HTTP 状态码实测。
  - `rule` TR-5.2: client 镜像 base-digest label == 新 rootless digest（逐字符）。
- **Notes**: 若 socket host key/known_hosts 提示属正常刷新，按 run 任务既有输出确认即可。

## Task 6: 文档与规范对齐（UID 表述 + 宿主 Toolbx 章节 + CHANGELOG）

- **Status**: `completed`
- **Completion Evidence**:
  - docs/07 新增"宿主机 Toolbx 流程（:toolbx 变体）"6 节（构建/宿主前置/WSL 环境/实测行为表/限制/命令），步骤与 Task 4/5 实际命令一致。
  - UID 表述：containerfile.md（基础约定+Layer 3+Toolbx 变体专节）、entrypoint.md（含 socket chown 禁令）、docs/07 兼容表、jpr AGENTS.md（概述+变更日志）、client README §10.4/C-I1/C-I2、Containerfile.client 注释全部对齐。
  - 两份 CHANGELOG 追加（jpr 三条：UID fix/变体 feat/socket fix；client 一条联动 chore）。
  - TR-6.1 grep 复核：剩余 1001/动态分配命中均为历史 CHANGELOG 或 windows-wsl.md 宿主多用户场景（与镜像账号无关）。
  - rubric TR-6.2 自评 4/5：零猜测可复现（含 dnf/提取二进制两条安装路径、migrate 停容器警告、socket 通道），扣 1 分因未在干净 VM 从零实走文档（环境为当日已配置状态）。
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - [docs/07-toolbx-passthrough.md](../../../apps/containers/jupyter-podman-rootless/docs/07-toolbx-passthrough.md) 新增"宿主机 Toolbx 流程（:toolbx 变体）"章节：构建（invoke build + build.toolbx）、宿主前置（Fedora: `sudo dnf install toolbox p11-kit-server`；Debian 系 libsubid soname 注意；零安装路径=从容器提取二进制+compat-lib）、首次 create 的 system migrate 停容器警告、WSL socket 通道与无 systemd/HEALTHCHECK 说明、flatpak-spawn --host 限制（与上游装法一致性说明）、完整命令清单（create/enter/list/rm）。
  - UID 表述对齐：docs/00-overview.md、README.md、AGENTS.md（已是 1000 表述，核对即可）、.agents/rules/containerfile.md（L16/L57/L101 增补"固定 1000，userdel ubuntu"）、.agents/rules/entrypoint.md L60（动态分配注释改写）、docs/07 L32（补充上游 userdel 依据）；client 侧 README L377 与 Containerfile.client L14-L16 注释、client AGENTS.md 如涉 UID 表述一并改为"devuser 固定 UID 1000"。
  - 应用 CHANGELOG（jupyter-podman-rootless .agents/CHANGELOG.md）追加本次 fix+feat 条；client CHANGELOG 追加联动重建条（基底指纹首次实战触发记录）。
  - docs README 索引/07 标题如需要同步。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-6.1: `grep -rn "1001\|动态分配" apps/containers/{client,jupyter-podman-rootless}` 仅剩历史 CHANGELOG 记录；新增章节步骤与 Task 4/5 实际命令逐字一致。
  - `rubric` TR-6.2: 文档可复现性 1-5（新人仅按 docs/07 可在干净 VM 完成 create/enter；锚点 1=关键步骤缺失/含过期命令，3=可走通但需猜测，5=零猜测含排障分支），阈值 >=4，自评+Review 复阅。
- **Notes**: 文档 kebab-case 与相对链接遵循开发规范；不新建多余文档文件。

## Task 7: 独立 Review（review.md）

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 队列清空后发起独立审查（fresh context，只读）：按 AC-1~AC-6 逐项复核证据充分性与真实性（重跑关键命令抽检）、文档与镜像事实一致性、变体最小侵入、无遗漏的 UID 硬编码/残留进程/未清理验证物。结果写 review.md；fail 则生成 Issue 回 Implement。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-7.1: review.md 覆盖全部 AC，每个 rule 有独立复核证据；Review Result=pass 方可结项。
