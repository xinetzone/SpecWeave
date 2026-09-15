---
id: jupyter-podman-rootless-changelog
title: jupyter-podman-rootless 变更日志
source: 从 apps/containers/jupyter-podman-rootless/AGENTS.md 拆分归档
---

# 变更日志

## 2026-09-15

| 类型 | 变更 |
|------|------|
| feat | **`invoke save` 镜像归档任务——Windows 原生保存路径补齐（七概念场景5 F→V→I→C，session sc-20260915-inv-save-image）**：此前镜像保存仅 `bash bin/jpman save`（WSL/Linux bash，`bin/jpman.ps1` 无 save、load 时提示 "Run 'jpman save' first (inside WSL)"），Windows 原生宿主存在能力空洞。新增 `tasks/image_cache.py`：① 两层后端——SDK（podman-py `image.save(chunk_size=2MiB, named=tag)` 流式，**named 必须传 tag 否则 load 后仓库标签变 `<none>:<none>`**）→ CLI 兜底（`podman save -o <相对项目根路径>` 落临时 tar 再 Python gzip；**禁止 `podman save |` pwsh 管道**——对象管道损坏二进制；已实证 Windows 远程客户端 `-o` 落本机文件系统）；② 产物契约与 bin/jpman 完全同构——`.image-cache/jupyter-podman-rootless-<id12>-<YYYYMMDD-HHMMSS>.tar.gz`、`manifest.txt` 七字段（IMAGE_NAME/IMAGE_ID/IMAGE_FILE/SIZE/SHA256/SAVED/SAVE_TOOK）、latest 指针；Windows 普通用户无 symlink 权限（WinError 1314）故 latest 用 `os.link` 硬链接，并对旧 drvfs 坏 reparse 点无条件 unlink、对 Defender/索引短暂锁做 0.5/1.5/3.0s 退避重试+copyfile 兜底；③ 可靠性——落盘前磁盘空间预算预检（TAR_BUDGET 1.05）、每 100MiB 进度打点、`.tmp-save-*` 原子 `os.replace`、gzip CRC 通读自证 + 归档 SHA256；④ 四选项 `-t/--tag`（参数>IMAGE_TAG env>.env>配置）、`-o/--output`（自定义路径不污染 manifest/latest）、`-n/--no-compress`、`-f/--force`；缺镜像在 `inspect` 阶段识别 `image not known` 秒回中文指引（exit 1）。根命名空间注册于 build-toolbx 之后、run 之前（不经 container.py 聚合，无 container.save 别名）。V 真机验证（默认镜像 534272b90067，虚拟 1.19GB→gzip 354.7M/70s）：V-1 CLI 全链路成功；V-3 `podman load -i *latest.tar.gz` 回环 `Loaded image: localhost/jupyter-podman-rootless:latest` 标签/ID 一致；V-4 缺镜像秒回；V-5 二次 save latest 硬链接正确切换；V-6 `--no-compress -o` 自定义路径 106.4M tar 回环成功且无 manifest/latest 污染；V-7 空间预检双向；shared 97 项单测无回归。诚实记录：本机 SDK 本就降级（P2-machine AttributeError，shared 连接层既有状态），CLI 为实际主力路径，SDK 分支未真机执行（字节处理与 CLI 共用同一 `_write_stream`）。同步 docs/02-invoke-reference.md（核心命令+save 参数节）、docs/16-image-cache.md（双路径同构叙述+硬链接说明）、AGENTS.md 镜像缓存条、.agents/rules/invoke-tasks.md（目录结构/命名空间表/验证清单）、README 命令速查（预防措施：跨平台能力补齐先实证远程客户端文件落盘语义与本机权限模型，再定产物契约；字节流禁走 pwsh 管道） |
| feat | **SSH host key 持久化 named volume（同日「第三次复发」条目的根治，七概念场景3 I→F→A→C→V）**：host key 生命周期脱离容器可写层——① entrypoint.sh 新增常量 `HOST_KEY_DIR=/var/lib/jpman/ssh-host-keys`，`generate_host_keys()` 以 `mountpoint -q`（非目录存在性，挂载点已烘焙进镜像）为唯一判据双模式分流：持久模式缺失才生成 ed25519/RSA-4096、已存在原样复用并打 `Reusing persisted ...`，私钥 600/公钥 644/目录 700，清空 `/etc/ssh/ssh_host_*` 防默认路径加载旧 key；回退模式（裸 `podman run`/Toolbx 未挂卷）保留 `ssh-keygen -A` 容器层旧行为并打 `WILL rotate on rebuild` 警告。`configure_sshd()` 在 `sshd -t` 前按模式整行 sed 重写两条 `HostKey`（整行匹配、重入幂等）。② Containerfile Layer 3 烘焙挂载点目录 700。③ 三路挂同一 named volume `jupyter-podman-rootless_ssh-host-keys`（对齐 compose project 与 registry-data 命名先例）：compose.yaml 服务卷+顶层声明、`tasks/manage.py::_run_via_cli()` 的 `-v`、`tasks/client.py::sdk_run_kwargs()` 的 volumes；卷名/路径常量 `HOST_KEY_VOLUME`/`HOST_KEY_DIR` 定义于 client.py，manage.py 导入共用。④ Access info 提示文案改为「持久化，重建不再轮换」。V 对抗验证（真机四组）：空卷首启生成 F1=`SHA256:57JzDq…`（卷内 600/644、目录 700、sshd_config 指向卷、/etc/ssh CLEAN、healthy）；`--force` 删除重建后容器 ID 变化但 F2==F1 且日志两行 Reusing；known_hosts 更新一次后第三次 `--force` 重建，`StrictHostKeyChecking=yes`+BatchMode 直连直接越过主机校验（到达密码认证阶段）——证明指纹永久稳定；无卷临时容器回退分支实测 key 落 `/etc/ssh`、WARN 正确。升级代价：旧容器层密钥不迁移，首次启用需接受一次新指纹；主动轮换路径 `invoke stop` → `podman volume rm jupyter-podman-rootless_ssh-host-keys` → `invoke run`。同步规则 `.agents/rules/entrypoint.md` §[2/7]§[3/7]、docs/13-faq.md 专条改写（预防措施：有状态凭据生成于无状态容器层——身份材料必须显式挂载持久卷；回退兼容性以挂载点探测而非全局开关保留） |
| fix | **容器重建后 SSH host key 校验失败第三次复发（REMOTE HOST IDENTIFICATION HAS CHANGED，七概念 I→F→V→C，session sc-20260915-ssh-hostkey-rotated-again）**：根因——sshd host key 生成于容器可写层，删除重建（`--force`/停止态对账重建/手动 rm）必轮换，宿主 known_hosts 旧指纹致 strict checking 拒绝；本次先以容器内 `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key` 取真实指纹（`SHA256:zZO0qM…`）与客户端所见逐项比对排除 MITM，再 `ssh-keygen -R "[localhost]:2222"` + accept-new 入库核验。预防（信息层，不改镜像）：`run` task 新增 `_print_host_key_rotation_hint()`，新建容器的两处 Access info（compose / SDK·CLI）均直接打印轮换原因与修复命令，幂等命中不打印（未重建不轮换）；docs/13-faq.md 新增专条（轮换触发条件、一条命令修复、指纹核验安全提示）。未做 key 持久化卷方案（需改 entrypoint + 重建镜像，留待后续裁决）（预防措施：同一反复故障只做即时恢复、未在成功路径输出可执行恢复指引） |
| fix | **`inv run` name already in use（exit 125）+ 幂等语义缺失（七概念 I→F→V→C，session sc-20260915-inv-run-stale-container）**：根因为 2026-09-10 记载的 invoke/pwsh 引号问题在**隐藏探测命令上的再现**——invoke 在 Windows 以 `pwsh.exe /c "<整条命令>"` 包装执行，探针内嵌的双引号 Go 模板（`--format "{{.Names}}"`）提前截断外层引用，残片被 pwsh 解析为自身参数（实证 `unknown shorthand flag: 'i' in -inputFormat` / `'e' in -encodedarguments`），含引号的 `podman ps` 探针在该通道**必然 rc=1**，被 `warn=True` 静默吞掉；旧 `container_exists()` 布尔探测把「命令失败」与「容器不存在」合并为 False，builder 跳过对账裸跑 `podman run` 撞同名残留 exit 125，且早期版本还会把用户**正在运行的健康容器**无提示重建（unknown 被误判 absent 的直接后果）。修复四层：① shared `containers.py` 新增四态模型 `container_phase()`（running/stopped/absent/unknown，unknown 与 absent 显式分离），探针全部改为**零引号** `ps -q --filter name=^NAME$ [--filter status=running]`（-q 输出 ID，非空即命中，name regex 锚定保证唯一），旧 `container_exists/container_running` 同步换芯保留兼容；② `run` task 启动前对账（`reconcile_before_run`）：running→幂等 no-op 并从现存容器 `inspect` 回读**真实** USER_PASSWORD/JUPYTER_TOKEN 展示（`_read_container_env`，Go 模板改单引号），stopped→`rm -f` 后重建，unknown→放行交自愈兜底（不擅删运行中容器）；③ 新增 `inv run --force`（运行中也重建）与 already-in-use 文本命中/相位裁决后的**单次**自愈重试（`_run_via_cli_self_heal`）；④ 密钥生成移至对账之后（幂等分支不再打印用不上的新密钥）。顺手修复同款双引号地雷：`inv status` 的 table 模板（并修非 hide 路径 stdout 被流式打印+print 两次的重复输出）。验证：shared 97 项单测全过（新增四态/短路/零引号断言）；真机 E2E 四路径——运行中 `inv run` 幂等零重建且容器 ID 不变、Exited 残留自动 rm 重建、`--force` 重建、status 单行表格；重建后刷新 `[localhost]:2222` known_hosts（accept-new，ED25519 指纹核验）并 healthy。**client 侧双引号经实证非缺陷（同日补验，推翻初稿「遗留」判断）**：client 的 invoke 不覆盖 shell，Windows 走 COMSPEC（cmd.exe），实测其 `env_in_container.py`（images/digest 共 2 处）与 `client_core.py`（images/ps，2 处）的 `--format "..."` 在 cmd.exe 下全部正确展开（含 `|` 分隔模板）；改单引号反而使引号成为字面量（输出 `'sha256:...'`）污染解析。两条通道规则相反、禁止跨包照搬，已在 client `.agents/rules/invoke-tasks.md` §3.4 固化（预防措施：外部 shell 引用边界假设未在隐藏调用点验证 + 布尔探测把「探测失败」错误降级为「否定结论」+ 静默 warn 掩盖基础层失效） |
| refactor | **组内共享包 jpman-common 接线（apps/containers OKF 容器知识包重构的 builder 侧）**：平台/进程/容器只读工具与 SDK 连接层的唯一实现上移至兄弟包 `apps/containers/shared`（jpman_common 0.1.0：`proc.py`/`platform_paths.py`/`containers.py` + `connection.py`）；`tasks/utils.py` 改为 `jpman_common` 再导出垫片（仅保留 builder 专属 `MIRROR_CHOICES`），`tasks/client.py` 再导出 `get_client`/`sdk_available`/`podman_sock_path`/`APIError`/`PodmanNotFound`（保留 builder 专属 compose 探测 `compose_available`/`compose_unavailable_reason` 与 `sdk_run_kwargs`/`sdk_build_kwargs`）；pyproject 新增依赖 `jpman-common`，安装顺序先 shared 后本包（editable 必须 `--no-build-isolation`）。同步：AGENTS.md 组内共享包条与文件地图、.agents/README.md、.agents/rules/invoke-tasks.md 与 entrypoint.md 符号定位、docs/08-directory-structure.md 共享包章节、docs/09-three-tier-backend.md 实现位置、README 项目结构（移除已不存在的 CMakeLists.txt 行）。验收：daemon-free 静态等价（连接行为零变化，垫片保持原导入路径）；真机 E2E 后置清单项见 client `.agents/CHANGELOG.md` 2026-09-15 条目第 5 项（`invoke --list` + 垫片符号来源 import 冒烟）。规格 `.trae/specs/infra-env/containers-okf-refactor/` |

## 2026-09-12

| 类型 | 变更 |
|------|------|
| fix | **桥接在真实 SSH 会话失效（同日第二轮故障，env-only 桥接的覆盖盲区）**：上一条 feat 落地后真实 SSH 终端仍报 newuidmap EPERM。七概念 F 链路实证：`podman exec` 继承容器 config env 故桥接生效，而 **sshd+PAM 派生的 SSH 登录 shell 环境被清洗**（`env -i` 复现：`HOST_PODMAN_SOCK`/`CONTAINER_HOST`/`XDG_RUNTIME_DIR` 三变量全空），env-only 守卫不满足而 no-op。修复：桥接脚本升级为四级解析——显式 `CONTAINER_HOST` ＞ `HOST_PODMAN_SOCK` env ＞ `/etc/podman-host-sock.path` 事实文件（entrypoint B-scheme 分支写入解析后的挂载路径，644，兼覆盖非标准挂载点）＞ `/run/user/$(id -u)/podman/podman.sock` 标准路径自探测；逃生语义收敛为「显式 CONTAINER_HOST 是唯一覆盖手段」。启动文件五通道覆盖全部 shell 形态：profile.d（登录）+ .bashrc（交互）+ 容器 ENV BASH_ENV（podman exec 子进程）+ /etc/environment 的 BASH_ENV（pam_env 注入，覆盖 `bash script.sh`/cron）+ **entrypoint 运行时写 sshd_config `SetEnv CONTAINER_HOST`（写后 sshd -t 校验失败回滚，回退分支同步删除）——经 F1/F2/F3 对照实证 bash 只在执行脚本文件时读 BASH_ENV，`bash -c "cmd"`（`ssh host "cmd"`/sshd 最外层）不读任何启动文件，SetEnv 是唯一不经 shell 启动文件的注入点**。验证纪律固化进 entrypoint.md：独立 shell 行为必须经真实 SSH/`env -i` 复核（且用 `printenv` 而非引号展开读变量，避免外层 shell 提前展开的测量假象），禁止只验 podman exec。真实 SSH key 免密四形态（ssh cmd / -lic / -lc / ssh -t 交互）+ podman-compose up/down 端到端验证通过（预防措施：规则新增验证纪律 + 事实文件双信息源 + PAM 通道补全） |
| feat | **B-scheme 桥接扩展至独立 shell（修复终端内 podman/podman-compose 的 newuidmap EPERM）**：根因经七概念 F→V 链路实证——entrypoint.sh 的 `CONTAINER_HOST` 导出只存活于 supervisord→jupyter 进程子树，SSH/`podman exec`/Jupyter·IDE 终端等独立 shell 仅继承容器配置 env 的 `HOST_PODMAN_SOCK`，落回容器内 rootless 后在三层 userns 嵌套下结构性失败（中间 ns root 能力集 `0x800405fb` 无 CAP_SYS_ADMIN，setuid newuidmap 写多行 uid_map 必被拒；改 /etc/subuid 区间 100000→524288 的假设已被对照实验证伪）。修复双层：① Containerfile Layer 3 烘焙 `/etc/profile.d/80-podman-host-socket.sh`（条件式 `HOST_PODMAN_SOCK`→`CONTAINER_HOST` 桥接，含构建期 `bash -n` 校验）并让 devuser `~/.bashrc` source 同一文件以覆盖非登录交互 shell，并以 `ENV BASH_ENV` 覆盖非交互非登录 bash（`podman exec ... bash -c`/cron，V7 矩阵实测的第三类缺口）；② entrypoint.sh 在导出 XDG 前对 GUI 透传注入的 inherited `XDG_RUNTIME_DIR`（/tmp/runtime-user，podman 自动建为 root:0755）只 chown 目录本身（禁 -R，wayland-0 单文件挂载红线），消除独立 shell 的二级失败 `mkdir .../libpod: permission denied`。守卫语义：显式 CONTAINER_HOST 优先（远程 daemon 逃生舱）、`HOST_PODMAN_SOCK= <cmd>` 强制本地、socket 缺失 no-op（回退分支零影响）。对照实验另证：podman remote 流式上传构建上下文，宿主无需 /workspace 同名软链。`.agents/rules/entrypoint.md` §[4/7] 同步两条契约 |

## 2026-09-11

| 类型 | 变更 |
|------|------|
| fix | **devuser 固定 UID/GID 1000**（对齐上游 toolbox `images/ubuntu/26.04/Containerfile` 的 `userdel --remove ubuntu`）：基础镜像 ubuntu:26.04 自带 `ubuntu(1000)`，原 Layer 3「UID 被占则自动分配」分支使 devuser 实际漂移到 **1001**（与 AGENTS/docs 长期声称的 1000 不符，且 Toolbx init-container 按宿主 UID 1000 同步用户时连续撞 useradd/usermod）。修复：Layer 3 先 userdel ubuntu + 兜底 groupdel 1000，再 `useradd -u 1000 -U` 固定创建（保留 devuser 已存在时的 UID 断言分支）；Layer 5 新增 3 条硬断言（id/getent）；头部注释、`.agents/rules/containerfile.md`、`entrypoint.md`、docs/07、client README/Containerfile.client 注释同步。实测：新镜像 `id -u devuser`=1000、`getent passwd 1000`=devuser、ubuntu 不存在 |
| feat | **Toolbx 宿主变体 `Containerfile.toolbx`（tag `:toolbx`）+ `invoke build-toolbx`**：薄覆盖层（FROM :latest，秒级）解决三大直接 create 障碍——①Toolbx 只覆盖 Cmd 不清 ENTRYPOINT（tini+entrypoint.sh 抢先执行，实测 `exec: --: invalid option`）→ `ENTRYPOINT []`；②精简 podman machine 无 systemd 用户实例致 HEALTHCHECK 定时器注册失败 → `HEALTHCHECK NONE`；③init-container 按宿主同名用户同步 UID1000 与 devuser 冲突（`useradd: UID 1000 is not unique`）→ `userdel devuser`（不 -r，1000:1000 数字属主文件由新用户承接），sudoers 改 `%sudo` 组 NOPASSWD。两条实测裁决写入文件头注释：wrapper 影子保留（TOOLBOX_PATH 非空即转发容器内原生二进制）；用户名模型必须释放 UID。构建任务 `build_toolbx` 带基底存在性中文预检。端到端实测（podman machine Fedora 43）：create 退出 0、`uid=1000(user) groups=sudo`、HOME/cwd/`/run/host` 透传、Python 3.14.7、sudo -n、podman 5.7.0、重复 create 幂等；`flatpak-spawn --host` 因 VM 无 D-Bus 门户不可用（环境天花板，装法与上游一致）。docs/07 新增完整宿主流程章节 |
| fix | **B-scheme socket 属主穿透事故修复**（UID 修复联调中暴露的潜伏缺陷）：entrypoint.sh 对 `/run/user/1000` 整体及 `podman/` 目录的 `chown -R` 会跟随**单文件 bind-mount 的宿主 podman.sock** 穿透修改宿主 inode 属主——实测宿主 socket 被改成 subuid 映射值 `525287:525287`，sshd 以 user(1000) 转发 unix socket 即被拒（`ssh: rejected: connect failed (open failed)`，Windows podman CLI/API 全断）。修复：两处 `chown -R` 降级为只 chown 目录本身，递归白名单仅保留 `libpod/`；并补 `ln source==target` 同一性幂等判断（UID 固定 1000 后挂载点与运行时路径天然相同，GNU ln 对同文件即使 -f 也报错致 set -e 中止启动）。修复后实测容器重启宿主 socket 保持 `user:user 0660`、remote API 5.7.1 连通、Jupyter HTTP 200。规范固化到 `.agents/rules/entrypoint.md`（预防措施：挂载点路径与宿主文件 inode 不隔离时，递归 chown 等价于直接改宿主） |

## 2026-09-10

| 类型 | 变更 |
|------|------|
| feat | 新增 `invoke registry.up/down`（`src/jpman_builder/tasks/registry.py`）：本地 OCI registry 的 **SDK→CLI 两层**实现，取代此前唯一的 `podman-compose --profile registry up -d`——后者在 Windows 原生宿主上已被工具层门禁，导致该服务在 Windows 上**没有启动路径**（`model.push/pull/pack/extract` 的默认目标 `localhost:5000` 因而不可用）。关键参数与 `compose.yaml` 的 `model-registry` 服务**对齐**：容器名 `<CONTAINER_NAME>-registry`、镜像 `registry:2`、宿主端口解析优先级（`--port` > `REGISTRY_PORT` 环境变量 > `.env` > 默认 5000）、环境变量 `REGISTRY_STORAGE_DELETE_ENABLED`/`REGISTRY_HTTP_ADDR`、重启策略 `unless-stopped`；数据卷直接采用 podman-compose 的生成名 `jupyter-podman-rootless_registry-data`，使两条启动路径**共享同一份数据**。compose 项目网络存在时自动加入并挂 `model-registry` 别名（`--network-alias` 不允许用于默认网络，故按网络存在性条件添加，缺失时打印提示）。实测：`registry.up` → `curl http://localhost:5000/v2/_catalog` 返回 **HTTP 200**、卷名与 compose 一致；重复 `up` 幂等替换；`down` 删容器保留卷、`--volumes` 连卷删除。同步 `AGENTS.md`、`.agents/rules/invoke-tasks.md`（目录结构/命名空间/验证清单 13→15 命令）、`.agents/rules/ml-models.md`、`.agents/rules/compose.md`、`.agents/rules/build-test.md`、`docs/02-invoke-reference.md`、`docs/08-directory-structure.md`、`docs/00/01/04/06`、`.env.example`；**并修正文档中「zot 镜像」的失实描述**（`ghcr.io/project-zot/zot-linux-amd64` → 实际的 `registry:2`，涉及 docs/04、docs/06、.agents/rules/compose.md、.agents/rules/ml-models.md）与 `container_name`/缺失环境变量的陈旧片段（预防措施：能力声明未覆盖全部目标平台 + 文档与可执行配置源不一致） |
| fix | invoke 的 Windows shell 配置修正（**既有阻断性缺陷**）：`__init__.py` 原用 `config["run"]["shell"] = shutil.which("pwsh") or shutil.which("powershell")`，在 Store 版 PowerShell 上返回 `C:\Program Files\WindowsApps\...\pwsh.EXE`。invoke 以 `Popen(cmd, shell=True, executable=shell)` 启动 shell，Windows 下 Python 拼成 `f'{shell} /c "{cmd}"'` 且 **`executable` 不能被引号包裹**（实测加引号 → `OSError [WinError 123]`；写裸名 `pwsh` → `FileNotFoundError [WinError 2]`），于是含空格的路径被拆断，**所有** `c.run` 命令均失败；该失败在 `warn=True` 调用点被静默吞掉，症状表现为「CLI 兜底层整条不可用、容器永远报不存在」（`invoke status` 的 CLI 分支即长期如此）。修复：新增 `_resolve_space_free_pwsh()`，优先取无空格的 App Execution Alias 路径 `%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe`，取不到则不设 shell 覆盖（回退 COMSPEC）。保留 PowerShell 7 而非改回 cmd.exe 的原因：`run_cmd` 构造的是 POSIX 风格命令（单引号包裹 `--format '{{.Names}}'`、`bash -c 'cd X && ...'`），cmd.exe 会把单引号当普通字符、把 `&&` 当命令分隔符而静默破坏。实测：修复前 `Context().run('podman --version')` 的 `ok=False` 且 stderr 为 pwsh 用法帮助；修复后 `ok=True`，且 `'echo A && echo B'` 原样保留；`invoke registry.up` 端到端成功。同步 `.agents/rules/invoke-tasks.md`（新增「Windows shell 配置（硬约束）」章节 + 验证清单新增 CLI 兜底层连通性检查）（预防措施：外部依赖的宿主相关行为改动未随代码一并验证 + 静默兜底掩盖了基础层失效） |
| fix | 宿主透传挂载源**禁止自动创建**（long syntax + `bind: {create_host_path: false}`）：`compose.yaml`（`HOST_PODMAN_SOCK`）、`compose.dev.yaml`（SSH agent / gitconfig / `.ssh` / X11 / pip cache 共 5 处）、`compose.passthrough.yaml`（D-Bus）、`compose.passthrough.gui.yaml`（Wayland）共 **8 处**宿主绝对路径挂载源由 short syntax 改为 long syntax 并加该字段。**动因**：podman-compose 的 short syntax 只填 `bind.propagation`（`podman_compose.py:209`），故 `assert_volume()` 必走 `os.makedirs()` 分支——Windows 下 `/run/...` 被 `ntpath` 按盘符解析为 `D:\run\...` 后即尝试在宿主建目录。实测**加固前**手敲 `podman-compose -f compose.yaml -f compose.dev.yaml up` 会在宿主留下 `D:\run`、`D:\dev`、`D:\home` 等错误目录；**加固后**同一命令（`--dry-run`）直接抛 `ValueError: invalid mount config for type 'bind': bind source path does not exist: <path>`，宿主零残留。**行为变更（显式声明）**：原先依赖自动创建的源（尤指 `~/.cache/pip`）须由宿主预先具备，否则该报错会命中它；`./workspace` 等相对路径源保持不变（自动创建仍启用）。已实证 `create_host_path` 在 4 种叠加组合的 `config` 合并结果中逐层保留；同步 `.agents/rules/compose.md`（基础约定 + 分层硬约束 + 验证清单 2 项）、`docs/07-toolbx-passthrough.md`、`docs/09-three-tier-backend.md`（预防措施：以「静默修补」代替「显式失败」的隐式副作用未收敛 + 第三方组件的默认值语义未在配置层显式化） |
| fix | `podman-compose` 后端在 Windows 原生宿主**从「文档标注」升级为「工具层门禁」**（承接同日 docs 条目）：`tasks/client.py::compose_available()` 改为宿主感知——新增 `_COMPOSE_HOST_SUPPORTED = os.name != "nt"`，Windows 原生恒返回 `False`，使全部 `_should_use_compose()` 判据失效，三层降级自动落到 Tier 2 SDK / Tier 3 CLI（二者把 Linux 绝对路径原样交给 podman，Windows 上 podman 为远程客户端、路径由 machine 内 daemon 解析，**路径语义才一致**）；新增 `compose_unavailable_reason()` 并在 `invoke build` 跳过 Tier 1 时输出一行可执行原因（含 WSL / `podman machine ssh` 两条替代路径）。**根因**：`podman-compose` 是运行在宿主进程内的路径处理器——Windows 下 `ntpath` 把以 `/` 开头的组件当作「驱动器根」，`/run/user/1000/bus` 被解析为当前盘符下的 `D:\run\user\1000\bus`；随后 `assert_volume()`（1.6.0 `podman_compose.py` L591 做 `os.path.join`/`abspath`、L600 调 `os.makedirs`）见该路径不存在便试图在宿主创建目录，实测 `PermissionError [WinError 5]` 并触发沙箱 `Not allow operate files: D:\run`；该失败被 `except OSError: pass` 吞掉后 podman 仍收到被篡改的挂载源（宿主残留风险：`D:\run`、`D:\dev`、`D:\home`、`D:\tmp`）（预防措施：跨平台路径语义假定未收敛到单一判据 + 第三方组件的宿主耦合行为未在工具层门禁化） |
| fix | 修正 toolbox 验证探针假阳性与能力声明过宽：Containerfile aux 阶段与 Layer 5 两处探针由 `toolbox --help >/dev/null 2>&1`（cobra 在 `PersistentPreRunE` 前短路 `--help`，且重定向吞掉 stderr，致使容器内裸跑 `toolbox` 报 `Error: TOOLBOX_PATH not set` 时仍打印 [OK]）改为**无重定向**的 `toolbox --version` 活性探针，标签由 "available" 改为 "binary present (liveness only)"；同步 docs/17-upstream-tools.md、docs/04-image-architecture.md、.agents/rules/containerfile.md、.agents/rules/build-test.md，明确 toolbox 的容器创建/进入能力由宿主侧 Toolbx 启动器提供，普通 podman 会话中裸跑 `toolbox` 按上游设计报错，镜像内仅声明二进制活性（预防措施：验证探针类型=假阳性探针 + 声明-事实不一致） |
| fix | toolbox 运行时错误优雅降级 + 对齐官方镜像：补装 `flatpak-xdg-utils` 并提供 `/usr/bin/flatpak-spawn` symlink（`ForwardToHost` 宿主回调前提，对齐官方 `images/ubuntu/26.04/Containerfile`）；真二进制移位至 `/usr/local/libexec/toolbox`，`/usr/local/bin/toolbox` 改由新增的 `scripts/toolbox-wrapper.sh` 承担——有 `TOOLBOX_PATH` 时 `exec` 真二进制、`-h/--help/--version` 短路透传（注意 `-v` 是上游 verbose 计数标志，不属短路型，故不透传），其余情况输出中文可执行指引并保持退出码 1（不再暴露上游裸错误 `Error: TOOLBOX_PATH not set`）；Layer 4/5 [VALIDATE] 6→7 项，Layer 5/5 [OK] 23→25 项（新增 `flatpak-spawn` 存在性与裸跑降级双向断言）；同步 AGENTS.md、docs/04-image-architecture.md、docs/07-toolbx-passthrough.md、docs/17-upstream-tools.md、.agents/rules/containerfile.md、.agents/rules/build-test.md（预防措施：能力声明的运行前提未随资产一并搬运 + 裸错误无可执行指引） |
| fix | 构建上下文排除宿主缓存目录：`.containerignore` 新增 `.wsl-cache/`、`.temp/`、`.image-cache/`、`.ipynb_checkpoints/`——podman 构建上下文**不读取 `.gitignore`**，此前约 15.3G 缓存被全量上传（`.wsl-cache` 11.7G + `.temp` 3.2G + `.image-cache` 355M），`invoke build` 事实上不可用；排除后构建上下文降至约 121M（预防措施：构建忽略清单与 `.gitignore` 语义不同步） |
| fix | Miniforge3 安装包解析改为「本地缓存优先 + 镜像优先多源回退」：新增 `local-cache/miniforge/`（Containerfile `COPY` 至 `/tmp/local-cache/`，命中即跳过全部网络下载，支持离线构建）；显式指定 tuna/aliyun 时按 首选镜像 → 备用镜像 → USTC → GitHub 排序（原实现恒将 GitHub 置于首位，国内大文件下载实测 120s 仅收 9.9MB/124MB 即超时或连接重置，镜像源紧随其后遇瞬时抖动即双源全灭）；curl 增加 `--retry-all-errors`、单源 `--max-time` 由 900s 收紧至 600s、失败打印 curl 退出码，全灭时输出可执行 `[HINT]`（预防措施：外部下载源单点依赖 + 镜像源未按可达性排序） |
| feat | 运行时透传分层覆盖与专用镜像 tag：新增 `compose.passthrough.yaml`（主层 `network_mode: host` + `ports: !reset []` + D-Bus 会话总线，镜像切至 `jupyter-podman-rootless:passthrough`）与 `compose.passthrough.{gui,gpu,usb}.yaml` 三个独立开关，替代原先散落于 `compose.yaml`/`compose.dev.yaml` 的注释式 opt-in（预防措施：交付物形态与运行时约束不匹配——5 项均为运行期参数，无法烘焙进镜像层，且 podman 对缺失挂载源/设备节点硬失败（退出码 125、不自动创建），故各覆盖文件头部内置前置检查命令） |
| fix | 新增 `SSHD_PORT` 环境变量支持：entrypoint `configure_sshd()` 读取 `SSHD_PORT`（默认 22、非法值报错退出）并重写 `sshd_config` 的 `Port`，主层透传覆盖设 2222。host 网络模式下 rootless Podman 容器 root 映射为宿主非特权 UID，绑定特权端口 22 被拒绝（实测 `Bind to port 22 on 0.0.0.0 failed: Permission denied`，sshd 随即 FATAL 退出），原文档承诺的 `localhost:22` 不成立（同场景 Jupyter 8888 正常返回 HTTP 200）（预防措施：能力声明未校验其运行前提在目标网络模式下是否成立） |
| docs | 标注 `podman-compose` 执行环境边界：`docs/07-toolbx-passthrough.md` 与 `.agents/rules/compose.md` 补充说明该命令须在 WSL / podman machine 内执行——Windows 原生 shell 下 podman-compose 会把 Linux 绝对挂载源（`/run/user/1000/bus` 等）按当前盘符解析为 `D:\run\...` 并操作本地文件，报 `Not allow operate files: D:\run`（对照测试确认仅基座 + `compose.dev.yaml` 即已复现，非分层覆盖引入） |
| fix | `olot_car.py` 构建期探针假阳性修正：Layer 5 原用 `python /usr/local/bin/olot_car.py --help >/dev/null 2>&1` 断言 "CLI functional"，但该脚本把 `from olot.basics` / `from olot.backend.oras_py` 置于 `cmd_pack()`/`cmd_extract()` 函数体内**延迟导入**，`--help` 走完 argparse 即退出、从未触达真实依赖，且重定向吞掉 stderr，致使依赖缺失时仍打印 `[OK]`；改为同构于 toolbox 探针修正的**无重定向**实质探针——断言 `olot` + `oras_py.is_oras_py()` 可导入并校验 `--help` 声明 `pack`/`extract` 子命令（预防措施：验证探针类型=假阳性探针） |

## 2026-09-09

| 类型 | 变更 |
|------|------|
| fix | jpman `rebuild`/`rebuild-all` 补 `--format docker`：OCI 格式忽略 SHELL 指令，导致 Stage 2 的 bash 数组语法在 dash 下报 Syntax error |
| fix | 宿主 socket 直通 B-scheme：entrypoint `setup_podman()` 用 `stat -Lc '%G'` 读取宿主直通 socket 属组并以 `usermod -aG` 叠加（须早于 `exec /usr/bin/supervisord`），解决容器内 devuser 访问宿主 socket 报 EACCES（C-I2）；严禁 `chmod 666`/`chown` 宿主 socket |
| fix | Jupyter devuser 与 libpod/tmp 目录准备：容器内 podman 运行所需运行时目录在启动阶段创建 |
| fix | 宿主直连 socket 挂载绕开嵌套 userns 映射带来的权限错位 |
| chore | vendor/ 三上游子模块 pin commit 更新 |

## 2026-09-08

| 类型 | 变更 |
|------|------|
| feat | vendor/ 登记三个容器编排上游 third_party 子模块并 pin commit（github.com/containers/*）：podman-compose `e3df10472`、podman-py `5dd81b49`、toolbox `81401f64`（gitlink 固定，禁止本地修改） |
| feat | 镜像内嵌三容器编排工具：新增 toolbox-builder aux 阶段（golang:1.26-bookworm + libsubid-dev，go build `/out/toolbox`，仅二进制 COPY 进 final 的 /usr/local/bin/toolbox）；conda-builder 内以本地源 pip 安装 podman-py/podman-compose 进 main env（cp314t 直装失败降级 mamba deps + pip --no-deps）；最终验证块新增三项内嵌工具 [OK] 检查（共 23 项） |
| feat | 构建前置 stage 机制：src/jpman_builder/tasks/stage_upstream.py 将 SpecWeave 根 vendor/ 三子模块源树复制到 `<app>/upstream/<name>`（git-ignored 临时目录；.containerignore 反白放行其根 README.md），Containerfile 据此 COPY 本地安装/构建 |
| feat | invoke build 与 jpman rebuild/rebuild-all 构建前自动 stage 上游源树；invoke build 构建上下文根改为向上查找含 Containerfile 的应用根（修复任意 cwd 下上下文与 upstream/ 定位错误） |
| docs | 新增 docs/17-upstream-tools.md（上游工具引入/升级流程/stage 机制/容器内用法）；同步 .agents/rules/containerfile.md、build-test.md、docs/04、08、README.md、AGENTS.md、.agents/README.md 等（构建架构章节由 7 层改述为 3 阶段 + aux + final 运行时分层） |

## 2026-08-29

| 类型 | 变更 |
|------|------|
| feat | passt 固化进 Containerfile（Stage 1 apt 清单 + 版本回显 + Layer 5 最终验证），修复 DinP 场景 rootless 网络命名空间 pasta 缺失报错 |
| fix | jpman rebuild-all/rebuild 补 `--format docker`：OCI 格式忽略 SHELL 指令导致 Stage 2 bash 数组语法在 dash 下报 Syntax error |
| fix | Containerfile Miniforge 下载 `--max-time` 300s→900s：慢速链路（~200KB/s）拉取 124MB 安装包双源 4 次尝试全部超时 |
| refactor | 合并 Containerfile.hidden 至主 Containerfile 并删除：Layer 4 吸收 root 配置权限与 allow_hidden 校验（VALIDATE 5/5→6/6）；jpman rebuild 改为主 Containerfile 层缓存构建（配置变更仅重建 Layer 4/5）；同步 AGENTS/README/docs/14/16、.agents/README、jpman-podman-ops SKILL.md 共 8 处引用 |

## 2026-08-28

| 类型 | 变更 |
|------|------|
| feat | jupyter-podman-rootless 任务系统 Windows 环境适配：任务定义适配 pwsh shell、构建与容器任务补充环境变量传递、manage 任务兼容 Windows 路径、build/container 增加运行时检测；xmnn 四模型组验证 |

## 2026-08-27

| 类型 | 变更 |
|------|------|
| feat | jpman `-w/--workspace` 自定义工作区挂载：支持CLI参数覆盖.env配置，Windows路径自动转换为WSL/mnt/路径 |
| feat | jpman .env安全加载：逐行解析（非source），剥离CRLF，支持引号值，反斜杠路径不被破坏 |
| feat | jpman 短变量名兼容：CONTAINER_NAME/SSH_PORT/IMAGE_TAG/USER_PASSWORD 自动fallback到JUPYTER_*前缀 |
| feat | jpman WORKSPACE优先级链：-w CLI > WORKSPACE env > JUPYTER_WORKSPACE env > .env > 默认workspace |
| fix | jpman: 移除podman create错误的-d标志（create本身不启动，-d是run的选项） |
| fix | jpman: CRLF行结尾导致bash语法错误（脚本转为LF，.env加载自动剥离\r） |
| fix | jpman: cmd_restart参数透传丢失（"$@"透传给cmd_start） |
| fix | jpman: bash source破坏Windows反斜杠路径（重写为安全逐行解析） |
| docs | 更新docs/14-jpman-cli.md：补充-w参数、短名兼容表、WORKSPACE优先级、路径自动转换说明 |
| docs | 更新.env.example：补充jpman路径自动转换说明和短名兼容注释 |
| docs | 里程碑复盘+4个L2模式入库（bash-safe-dotenv-loading/wsl-windows-path-autoconvert/multi-entrypoint-config-unification/cross-platform-bash-preflight-checklist） |
| feat | jpman零依赖CLI：跨平台bash/cmd/ps1脚本，无需Python依赖 |
| feat | 镜像缓存：jpman save/load，pigz多线程压缩，manifest元数据，latest软链接 |
| feat | WSL2一键导出：jpman wsl-export，自动配置wsl.conf+Conda激活+冒烟测试验证 |
| feat | 增量重建：Containerfile.hidden + jpman rebuild，配置变更<10秒完成 |
| feat | WSL保活：jpman keepalive自动启动sleep infinity防止容器退出 |
| feat | jpman install：全局命令安装symlink到~/.local/bin |
| refactor | 文档更新：README.md、AGENTS.md、docs/README.md更新，新增3个文档（共17个） |
| docs | 新增docs/14-jpman-cli.md：jpman CLI完整参考 |
| docs | 新增docs/15-wsl-export.md：WSL2发行版导出与使用指南 |
| docs | 新增docs/16-image-cache.md：镜像缓存与增量重建指南 |
| fix | .agents/README.md父级路径修正（4级向上而非3级） |
| refactor | AGENTS.md精简为路由入口，约束迁移至.agents/rules/（7个主题文件）；README.md原子化至docs/（14个文档） |
| feat | R5/Toolbx集成：Toolbx兼容标记(LABEL+/run/host+markers+capsh)、compose.dev.yaml透传覆盖文件、注释式透传文档 |
| feat | R4/OLOT集成：KServe ModelCar标准镜像打包(model.pack/extract)、olot_car.py辅助脚本 |
| feat | R3/OMLMD集成：ML模型OCI artifact分发(model.push/pull/config)、model-registry compose service(profile:registry) |
| feat | R2/podman-compose集成：声明式compose.yaml编排、.env配置管理、compose_backend.py |
| feat | R1/podman-py SDK集成：三层exec后端架构、client.py封装 |

## 2026-08-26

| 类型 | 变更 |
|------|------|
| feat | 完整实现：Containerfile(7层)、entrypoint.sh(7步)、config/配置、invoke任务、healthcheck |
| feat | 初始化项目结构：AGENTS.md、目录结构、pyproject.toml、.containerignore、README.md |
