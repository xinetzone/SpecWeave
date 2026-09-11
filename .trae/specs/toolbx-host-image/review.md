# Toolbx 宿主镜像变体与 devuser UID 修复 - Independent Review

- [x] CP-R1: devuser 固定 UID/GID 1000（AC-1）
  - **Type**: `rule`
  - **Covers**: AC-1 / TR-1.x / TR-3.2
  - **Evidence（R1 独立复核）**: `id devuser`=`uid=1000(devuser) gid=1000(devuser) groups=1000,27(sudo),997(docker)`；passwd 1000 行锚定匹配；ubuntu 三重确认不存在。R2 随 remediation 镜像（5f37aa7746ed）重验：见 Review History R2。

- [x] CP-R2: :toolbx 变体宿主可用（AC-2）
  - **Type**: `rule`
  - **Covers**: AC-2 / TR-2.x / TR-4.x
  - **Evidence（R1）**: history 仅 17.9kB 实层（userdel/sudoers）+ HEALTHCHECK NONE + ENTRYPOINT [] + flavor LABEL；`toolbox run id`=`uid=1000(user) groups=...,27(sudo)`；HOME/cwd//run/host/Python 3.14.7/sudo -n/podman 5.7.0/幂等全过；flatpak-spawn --host 按备案为环境限制。

- [x] CP-R3: 普通模式零回归（AC-3）
  - **Type**: `rule`
  - **Covers**: AC-3 / TR-5.1
  - **Evidence（R1）**: jupyter+sshd RUNNING；HTTP 200（原 token）；宿主 socket user:user 0660 未穿透；devuser 1000；workspace 挂载正确；B-scheme 日志含 skip symlink + can read/write socket。

- [x] CP-R4: client 联动与指纹一致（AC-4）
  - **Type**: `rule`
  - **Covers**: AC-4 / TR-5.2
  - **Evidence（R1）**: label 与基底 digest 71 字符逐字符一致（IDENTICAL）；remediation 轮更新为 sha256:720d4ba6…，R2 复核新值。

- [x] CP-R5: 文档与事实一致（AC-5）
  - **Type**: `rule`
  - **Covers**: AC-5 / FR-4 / FR-5 / TR-6.1
  - **Evidence**: R1 FAIL（F1-F4）；remediation 后 R2 复核 grep 零命中（合法 :latest 普通服务引用除外），镜像内 wrapper 文案已含 :toolbx。

- [x] CP-U1: 变体最小侵入度（AC-6）
  - **Type**: `rubric`
  - **Covers**: AC-6 / TR-2.3
  - **Scale**: 1-5；R1 独立评分 **5/5**（仅 4 条必要差异、未碰运行模型、构建入口一行注册、裁决注释完整）。

- [x] CP-R6: 静态安全/正确性（shell 链/chown/ln 边界）
  - **Type**: `rule`
  - **Covers**: NFR（修复正确性回归）
  - **Evidence（R1）**: set -e/pipefail 链分析通过；chown 白名单实测充分；ln readlink -f 幂等实测；无遗漏同类挂载点。advisory F5-3（userdel 兜底）已在 remediation 采纳。

## Review History

### Review R1（2026-09-11，fresh context 子代理）
- **Result**: `fail`
- **Evidence**: 功能项 CP-R1~R4、CP-U1、CP-R6 全部独立实测 PASS；CP-R5 FAIL。
- **Findings（全部 actionable，文档/注释层，无运行时风险）**:
  - F1（中）：`scripts/toolbox-wrapper.sh` 烘焙进镜像的指引仍指向 `:latest`（必败路径）。
  - F2（中）：docs/01、docs/13、docs/17、README（2 处）、docs/00、docs/README、compose.md 残留"直接对 :latest toolbox create"表述。
  - F3（低）：`config/supervisor/conf.d/jupyter.conf:14` 残留"UID 动态分配/1001"注释（AC-5 字面判据命中，且 tasks.md Task 6 grep 自述失实）。
  - F4（低）：`.agents/rules/entrypoint.md:50` 与同文件 L60 自相矛盾（动态 UID vs 固定 1000）。
- **Advisory（非阻断）**: LABEL usage 措辞；build_toolbx 自检/指纹/引号；userdel 半成功兜底；~/.local chown 前提注释；docs/13 conda activate base 旧误；docs/07 补 9p 构建约定。
- **Remediation（已实施并级联重建）**:
  - F1：wrapper 指引改 `:toolbx` + 说明 :latest 不可用 → 镜像内实测文案更新。
  - F2：8 个文件 9 处全部改为 :toolbx 并链接 docs/07。
  - F3：jupyter.conf 注释改为"固定 UID 1000 + id -u 派生路径"。
  - F4：entrypoint.md L50 改"非 root UID（固定 1000，≠0）"。
  - 连带（Review 复扫 client 侧新发现）：client `utils.py:703` C-I2 诊断文案、`windows-wsl.md:117` 同步修正。
  - 采纳 advisory F5-3：`userdel ... || userdel ... || true` + Layer 5 getent 断言兜底。
  - 级联重建：:latest 5f37aa7746ed → :toolbx 1f4ae77767ca → client:latest（新基底指纹 sha256:720d4ba6…）；jupyter-podman 重启后 jupyter/sshd RUNNING、HTTP 200、socket user:user 660；jupyter-dev 用新变体重建后 id=uid1000(user)/sudo、Python 3.14.7。

### Review R2（2026-09-11，fresh context 子代理，差异复审）
- **Result**: `pass`（无新增 actionable/advisory）
- **Evidence**:
  - F1：容器内 wrapper 文案实测含 :toolbx 与":latest 不能直接 create"；容器内二进制与工作树 sha256 一致（6991c41b…，烘焙一致性证明）。
  - F2：全部 `toolbox create -i` 命令均指 :toolbx；"直接 create"命中 4 处均为否定句；38 处 :latest 命中逐条判定合法（普通服务/缓存/ARG/CHANGELOG）。
  - F3/F4/连带项：`动态分配|动态 UID|可能为 1000|auto-assign` 全仓零命中；1001 的 9 处命中全部合法；jupyter.conf/entrypoint.md/utils.py/windows-wsl.md 口径一致。
  - 级联产物 6/6：devuser=1000、双服务 RUNNING、HTTP 200、基底指纹 sha256:720d4ba6… 逐字符一致、宿主 socket user:user 660、jupyter-dev（镜像 1f4ae77767ca）id=uid1000(user)/sudo + HOME//run/host/Python 3.14.7/sudo/podman 全过。
  - F5-3：`A || B || true` 在 set -e/pipefail 下安全，Layer 5 三断言构成失败关闭兜底；相对链接零断链；脚本 bash -n 全过；容器内 entrypoint 与工作树 sha256 一致。
  - 测量假象排除：嵌套引号中 HOME=C:Usersxinzo 为 PowerShell 展开假象，printenv HOME=/home/user 权威证据无回归。
- **结论**：AC-1~AC-6 全部有独立证据通过，队列 drain，项目结项。
