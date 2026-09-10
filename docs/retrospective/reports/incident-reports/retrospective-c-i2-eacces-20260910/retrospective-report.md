---
id: "retrospective-c-i2-eacces-20260910"
title: "容器内 Podman socket EACCES（C-I2）根因修复复盘"
source: "apps/containers/client 消费端 SDK 与 apps/containers/jupyter-podman-rootless 构建端 B-scheme socket 通道透传诊断 (2026-09-10)"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/incident-reports/retrospective-c-i2-eacces-20260910/retrospective-report.toml"
type: incident-report
scope: task
status: completed
related_patterns:
  - "rootless-socket-group-membership-adaptation"
  - "host-channel-pass-through"
---

# 容器内 Podman socket EACCES（C-I2）根因修复复盘

## 事件概述

**发生时间**：2026-09-10
**影响范围**：容器内 `devuser` 经 B-scheme 宿主 socket 通道调用 podman（`PodmanClient.from_env()` 与 `!podman images` 两条路径同时受阻）
**严重程度**：P2（容器内 podman 功能完全不可用，但宿主侧不受影响，可定位修复）
**根因类别**：通道实现缺陷（B-scheme 只覆盖 socket「可达性」维度，未覆盖 POSIX 权限位「可访问性」维度）+ 验证方法缺陷（`su -` 登录 shell 剥离环境变量，伪造失败信号）
**新增诊断编号**：**C-I2**（EACCES，socket 存在但无权限），与既有 C-I1（ENOENT，socket/目录不存在）语义分离

## 事实时间线

| # | 事件 |
|---|------|
| F-01 | 容器内 `devuser` 的 UID 由基础镜像 `useradd` 动态分配，本次为 **1001**（非 1000） |
| F-02 | Notebook `with PodmanClient.from_env() as client: client.containers.list(...)` 抛 `PermissionError: [Errno 13] Permission denied`，栈顶 `podman/api/uds.py:41 super().connect(netloc)` |
| F-03 | 上述异常被 urllib3 `connectionpool.py:788 self._make_request(...)` 二次包装为 `APIError`，掩盖了底层 `PermissionError` |
| F-04 | 同一 Notebook `!podman images` 输出 `dial unix /run/user/1001/podman/podman.sock: connect: permission denied` |
| F-05 | 两处报错均为 EACCES（permission denied）而非 ENOENT，属既有 C-I1 之外的新类别 → 新增 **C-I2** |
| F-06 | 宿主 rootless podman socket `/run/user/1000/podman/podman.sock` 权限为 `srw-rw---- 1 root root`（**0660**） |
| F-07 | B-scheme 将宿主 socket bind-mount 进容器同一路径 `/run/user/1000/podman/podman.sock`，并在 devuser 可控目录建符号链接 `/run/user/1001/podman/podman.sock -> /run/user/1000/podman/podman.sock` |
| F-08 | rootless userns 映射下，宿主 socket 的数值属主/属组进入容器后被压扁为容器 `root:root`（gid 0） |
| F-09 | 修复前 `entrypoint.sh` B-scheme 分支**无任何 socket 属组处理**；旧 base 镜像内 `socket group` 关键字命中 **0** |
| F-10 | 容器内 `usermod -aG root devuser` 后，jupyter 进程获得 gid 0 补充组，socket 变为可读写 |
| F-11 | supervisord 4.3.0 `drop_privileges` 在 spawn 子进程时经 `grp.getgrall()` 派生补充组 → `os.setgroups()` → `setgid` → `setuid` |
| F-12 | 由 F-11 推出硬时序约束：`usermod -aG` 必须发生在 `exec supervisord` **之前**，晚于此则已 spawn 的子进程不继承新组 |
| F-13 | `config/supervisor/conf.d/jupyter.conf` 修复前硬编码 `/run/user/1001` 路径 → 存在 UID 漂移隐患 |
| F-14 | 实测 `su - devuser`（登录 shell）丢弃 `CONTAINER_HOST`/`XDG_RUNTIME_DIR`，子 shell 内两者均为空 |
| F-15 | 无 `CONTAINER_HOST` 时 podman 退化为本地 in-container 模式，触发 WSL 三层 userns 嵌套限制 `newuidmap: write to uid_map failed: Operation not permitted` |
| F-16 | 修复：`entrypoint.sh` B-scheme 分支新增 **socket 属组自适应**——`stat -Lc '%G'`/`'%g'` 取宿主 socket 属组 → `usermod -aG` 加入非 root 用户 → 复验可读写 |
| F-17 | `%G` 解析不出属组名（空或 `UNKNOWN`）时回退使用 `%g` 数值 gid，避免静默跳过属组衔接 |
| F-18 | `stat` 失败时必打 `log_warn`（不静默返回），并显式提示 `${NON_ROOT_USER}` 存在 EACCES 风险 |
| F-19 | 修复同时新增自验证：`su - devuser -c "test -r ... && test -w ..."`，仅告警不阻断（属组映射不匹配时仍可能失败） |
| F-20 | `bash -n entrypoint.sh` 语法校验通过 |
| F-21 | base 镜像重建 → `701c2e509fd8`，镜像内 `socket group` 关键字命中 **5**（旧镜像基线 0） |
| F-22 | client 层重建 → `5ed156783148`，`User=root` 且 `jpman_client` editable 安装成功 |
| F-23 | 容器重建 → `41d46c351352` |
| F-24 | entrypoint 启动日志：`[B-scheme] Added devuser to socket group 'root' (gid 0)` + `[B-scheme] [OK] devuser can read/write host podman socket` |
| F-25 | 容器内 `/proc/<jupyter>/status` 的 `Groups: 0 27 997 1001`，证明 gid 0 已注入 jupyter 进程 |
| F-26 | `PodmanClient.from_env()` 修复后成功：podman **5.7.1**、列出 **3** 个容器、**无 PermissionError** |
| F-27 | devuser 侧在显式 `CONTAINER_HOST` 下 `podman images` 列出 11 镜像；`podman info` 显示 `rootless=true`、`RemoteSocket=unix:///run/user/1000/podman/podman.sock` |
| F-28 | 反证：无 `CONTAINER_HOST` 时稳定复现 `newuidmap: write to uid_map failed` —— 证明 `su -` 丢环境变量是历史误判来源，**非** C-I2 修复失败 |
| F-29 | 读 `/proc/<jupyter>/environ` 报 Permission denied —— setuid 后内核清除 dumpable 标志，root 无 `CAP_SYS_PTRACE` 亦不可读，反证提权剥离正常 |
| F-30 | 镜像构建链为两层：`entrypoint.sh` 经 `COPY --chmod=755` 烘焙进 base 镜像 → `Containerfile.client` 单层叠加，故 C-I2 修复**须重建两层镜像**才生效 |
| F-31 | 消费端代码改动：`utils.py` `podman_sock_path()` 默认 `PODMAN_RUNTIME_UID=1000` 且支持环境变量覆盖（严禁硬编码容器内 UID）；`windows_diagnose_hint()` 新增 C-I2 匹配，与 C-I1（ENOENT）语义分离 |
| F-32 | 文档闭环共 8 处：`README.md` §5.4 新增 C-I2 条目、`.agents/rules/windows-wsl.md` §5 速查表、`AGENTS.md`、`.agents/README.md`、`.agents/rules/entrypoint.md` 等 |
| F-33 | 代码修复与文档闭环随根仓库提交 `52084da68` 入库（11 files changed, 106 insertions(+), 20 deletions(-)） |
| F-34 | CHANGELOG 回填 2026-09-07 条目对应提交 `91c29c240` 并登记 C-I2 条目，随提交 `4e47126a0` 入库 |
| F-35 | V 阶段对抗审查共采纳 5 条意见：自验证 / `%G` 空回退 `%g` / 代价与红线声明 / `stat` 失败必 warn / C-I2 分支先于平台守卫 |

## 根因分析（5Why）

```
为什么容器内 PodmanClient.from_env() / !podman images 报 permission denied？
├─ 为什么？→ devuser 对宿主 podman socket 的 connect() 返回 EACCES（F-02/F-04）
│   └─ 为什么？→ socket 本体 mode 0660 且属组为 root，devuser（UID 1001）不在其许可属组内（F-06/F-01）
│       └─ 为什么？→ 宿主 socket 经 rootless userns 映射进入容器后数值属主/属组被压扁为容器 root:root，
│          而镜像基线从未把 devuser 加入 root 组（F-08/F-09）
│           └─ 为什么？→ entrypoint.sh B-scheme 分支只实现了「socket 路径暴露」（符号链接 + CONTAINER_HOST 导出），
│              未实现「调用方属组衔接」（F-07/F-09）
│               └─ 为什么（系统根因）？→ 通道透传设计把「可达性」等同于「可访问性」：
│                  只验证了 socket 存在且路径正确（可排除 ENOENT），
│                  未覆盖 POSIX 权限位维度（EACCES 成为盲区）（F-05）
├─ 为什么修复后一度被误判为"仍未修好"？
│   └─ 为什么？→ 复测命令 `su - devuser` 是登录 shell，剥离了 CONTAINER_HOST/XDG_RUNTIME_DIR（F-14）
│       └─ 为什么？→ 环境变量缺失使 podman 退化为本地 in-container 模式，
│          撞上 WSL 三层 userns 嵌套限制并抛 newuidmap 错误（F-15）
│           └─ 为什么？→ 验证命令的执行上下文与生产上下文（supervisord 继承 entrypoint 导出值）不一致（F-11/F-24）
```

## 洞察

| # | 陈述 | 证据 | 反常识 | 行动 |
|---|------|------|--------|------|
| I1 | socket 透传必须同时覆盖「路径可达」与「权限可访问」两个维度，缺一即故障 | F-05/F-06/F-09 | 排除 ENOENT **不代表**通道可用；EACCES 是独立故障类别，诊断文案必须与 C-I1 分列，否则会把属组问题误诊为路径问题 | 诊断表新增 C-I2；entrypoint 增加属组自适应；README §5.4 与 rules 三处同步 |
| I2 | 跨 userns 边界判断可访问性，必须以**容器视角的映射结果**为准，不能用宿主 `ls -l` 结果推理 | F-06/F-07/F-08/F-10 | 宿主 `root:root` 经 userns 压扁后在容器内**仍显示** `root:root`，但语义已变；"在宿主上把 devuser 加组"无效，正确解是**容器内** `usermod -aG root` | entrypoint 用容器内 `usermod -aG`；规则明确禁止硬编码 1000/1001 |
| I3 | 依赖「补充组继承」的修复，其生效时机被钉死在守护进程 `exec` 之前——晚一步即静默失效 | F-11/F-12/F-24/F-25 | `usermod` 返回码 0 只说明"加组成功"，不说明"进程已生效"；这是一个**成功但无效**的修复陷阱 | 属组衔接置于 `setup_podman()`（exec supervisord 之前）；用 `/proc/<pid>/status` 的 `Groups:` 反查实际继承 |
| I4 | 验证命令自身的语义会伪造失败信号——必须用与生产一致的执行上下文复测 | F-14/F-15/F-28 | `su -` 以"提供干净环境"为设计目标，恰恰因此**不适合**复现任何依赖环境变量的场景；误判成本是"把已修好的问题当成没修好" | 复测脚本显式 `export CONTAINER_HOST/XDG_RUNTIME_DIR`；反证实验固化为诊断资产 |

## 修复措施与验证

- **A1（构建端 · 已随 `52084da68` 入库）**：[entrypoint.sh](../../../../../apps/containers/jupyter-podman-rootless/entrypoint.sh) `setup_podman()` B-scheme 分支新增 socket 属组自适应
  - `stat -Lc '%g'` / `'%G'` 读取宿主 socket 属组，`%G` 空或 `UNKNOWN` 时回退 `%g` 数值 gid
  - 已属该组则跳过；否则 `usermod -aG` 把 `${NON_ROOT_USER}` 加入；`stat` 失败或加组失败一律 `log_warn`（不静默）
  - 新增自验证 `su - ${NON_ROOT_USER} -c "test -r ... && test -w ..."`，仅告警不阻断
- **A2（构建端 · 已随 `52084da68` 入库）**：[jupyter.conf](../../../../../apps/containers/jupyter-podman-rootless/config/supervisor/conf.d/jupyter.conf) 移除硬编码 `/run/user/1001`，改 `%(ENV_CONTAINER_HOST)s` / `%(ENV_XDG_RUNTIME_DIR)s` 继承 entrypoint 动态导出值，消除 UID 漂移
- **A3（消费端 · 已随 `52084da68` 入库）**：[utils.py](../../../../../apps/containers/client/src/jpman_client/tasks/utils.py) `windows_diagnose_hint()` 新增 C-I2 匹配；[client_core.py](../../../../../apps/containers/client/src/jpman_client/tasks/client_core.py) 失败汇总表叠加 C-I2 文案；`get_client()` 失败路径不回归
- **验证（verify 全绿）**：
  - `bash -n entrypoint.sh` ✅（F-20）
  - base 镜像重建 `701c2e509fd8`（`socket group` 命中 5 vs 旧基线 0）✅（F-21）
  - client 层重建 `5ed156783148`（`User=root`、editable 安装 OK）✅（F-22）
  - 容器重建 `41d46c351352` ✅（F-23）
  - entrypoint 日志确认加组成功且自验证通过 ✅（F-24）
  - `/proc/<jupyter>/status` → `Groups: 0 27 997 1001` ✅（F-25）
  - `PodmanClient.from_env()` 成功（v5.7.1、3 容器、无 PermissionError）✅（F-26）
  - devuser 侧 `podman images`（11 镜像）/ `podman info`（rootless=true）成功 ✅（F-27）
  - 反证：无 `CONTAINER_HOST` 时复现 newuidmap 错误 ✅（F-28）

## 预防行动项

| # | 行动 | 验收标准 | 状态 |
|---|------|----------|------|
| A1 | entrypoint.sh 新增 socket 属组自适应 + 自验证 | 容器启动日志出现 `Added devuser to socket group` 与 `[OK] ... read/write host podman socket` | ✅ `52084da68` |
| A2 | jupyter.conf 去硬编码 UID，改 `%(ENV_x)s` 继承 | 全文件无 `/run/user/1001` 字面量 | ✅ `52084da68` |
| A3 | 消费端新增 C-I2 诊断分支（与 C-I1 分离） | `windows_diagnose_hint()` 对 EACCES 命中 C-I2 文案 | ✅ `52084da68` |
| A4 | 文档闭环 8 处（README §5.4 / windows-wsl §5 / AGENTS.md / .agents/README.md / entrypoint.md 等） | 三处口径 1:1 对应，共 5 条（W-I1~W-I3 + C-I1 + C-I2） | ✅ `52084da68` |
| A5 | CHANGELOG 回填 2026-09-07 提交哈希 + 登记 C-I2 条目 | CHANGELOG 无 `<TBD>` 残留，C-I2 条目引用 `52084da68` | ✅ `4e47126a0` |
| A6 | 沉淀模式 `rootless-socket-group-membership-adaptation` | 模式文档 + index.md（toctree）+ README.md（模式清单表）+ .meta/toml 四处登记 | ✅ 本复盘收尾 |
| A7 | 本复盘报告落盘并登记 incident-reports 双索引 | index.md（toctree）+ README.md（报告索引表）+ .meta/toml | ✅ 本复盘收尾 |

## 质量门记录

- **V 门（强制对抗审查，不可跳过）**：对 F 的根因假设与修复方案执行 4 视角 + 5 攻击者角色审查，**采纳 5 条**：① 增加属组自验证实验；② `%G` 空值回退 `%g` 数值 gid；③ 补代价与红线声明（不改宿主权限、不 chmod socket、不引入 `--privileged`）；④ `stat` 失败必须 `log_warn` 不得静默跳过；⑤ C-I2 匹配分支置于平台守卫之前（否则 Windows 分支先返回会吞掉 C-I2）。不采纳项（V-4/V-5/V-7）已在 V 阶段记录理由
- **G1（事实无因果）**：F-01~F-35 全部为命令输出、日志、`/proc` 实测与 git 记录，无"应该/可能"类推断
- **G2（洞察四元组）**：I1~I4 均含【陈述 / 证据（引用 F 编号）/ 反常识 / 行动】四项
- **G3（模式可迁移）**：萃取 `rootless-socket-group-membership-adaptation`，可迁移至任何"跨 userns/跨用户边界的 socket 或设备透传 + 属组授权"场景，非 jpman 专有
- **G4（行动项原子化）**：A1/A2/A3 为三块可独立 revert 的代码改动；A4/A5 为文档与日志；A6/A7 为知识沉淀；本次 C 阶段提交 `4e47126a0` 单一职责（仅 CHANGELOG 回填与登记）
