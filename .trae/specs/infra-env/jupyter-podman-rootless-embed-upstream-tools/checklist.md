# Checklist：jupyter-podman-rootless 嵌入 containers 上游工具

## Task 1：vendor/ submodule 注册
- [x] `.gitmodules` 包含三个条目（podman-compose/podman-py/toolbox，路径 `vendor/<name>`，URL `git@github.com:containers/<name>.git`）
- [x] `vendor/AGENTS.md` 子模块路由表与边界声明含三行 `third_party` 条目；`python .agents/scripts/check-vendor.py` 通过（vendor/README.md、VERSION.md 已再生成，无孤儿目录）
- [x] `git submodule status` 三个条目 commit 与 spec 固定值一致（`e3df1047`/`5dd81b49`/`81401f64`），无前缀 `-`；`git status --short` 无泄漏
- [x] `external/dao/action/Containers/` 历史 untracked 快照未改动、未产生任何入库条目（保持原样）

## Task 2：stage 机制
- [x] python stage 逻辑可解析 SpecWeave root 并复制 `vendor/<name>` 至 `<project_root>/upstream/<name>`（跳过 `.git`；实跑两次幂等成功）
- [x] `invoke build`（build.py 头部）与 jpman `rebuild/rebuild-all`（cmd_rebuild/cmd_rebuild_all）构建前自动触发 stage，幂等
- [x] submodule 未初始化时构建中止并输出含 `git submodule update --init vendor/<name>` 的修复提示（python 模块级实测非 0 退出）
- [x] 应用 `.gitignore` 含 `upstream/`；`.containerignore` 允许 `upstream/` 且保留两仓库 README.md（反白），generic `.git/` 覆盖 `upstream/*/.git`
- [x] 路径探测用 `.gitmodules` 祖先查找（bash/python），不硬编码盘符；WSL 9p 路径下 stage 产物可直接被 podman build 消费

## Task 3：Containerfile
- [x] toolbox 经 Go builder 阶段（golang:1.26-bookworm aux stage）编译、final COPY `/usr/local/bin/toolbox`（755，devuser PATH 可达）
- [x] podman-py/podman-compose 由 `vendor/` 本地源 pip 装入 `/opt/conda/envs/main`，builder 内源树已 `rm -rf` 清理
- [x] 最终验证块新增三项内嵌工具检查（podman-compose --version / python import podman / toolbox --help）；实为 23 项 [OK]
- [x] 镜像构建成功（WSL podman 5.7.1 rootless，real 3m14s，TUNA + GO_PROXY=goproxy.cn）；容器内以 root 与 devuser(1001) 两身份实测 `podman-compose version 1.6.0`、`python import podman -> 5.8.0`、`toolbox --help exit 0` 全部通过
- [x] final 镜像无 Go 工具链（实测 `command -v go` 为空）；镜像 1.17 GB，toolbox COPY 层 11.22MB（体积增量记录在案）

## Task 4：规则与文档
- [x] `.agents/rules/containerfile.md` 与 `build-test.md` 描述与实际实现一致（aux 阶段、本地源安装、三项内嵌工具检查、submodule 前置、upstream/ 语义）
- [x] `.agents/CHANGELOG.md` 追加 2026-09-08 feat 记录
- [x] 新增 `docs/17-upstream-tools.md`；`docs/README.md`/`docs/04-image-architecture.md`/`docs/08-directory-structure.md`/AGENTS.md/`.agents/README.md`/README.md/docs 00/01 已同步，无"podman-compose 仅宿主机"类过期表述
- [x] docs 相对链接检查通过（check-links 排除 upstream 后无新增断链；docs/16 的 1 处为改动前既有断链且文件不在白名单）

## Task 5：端到端
- [x] checklist 全项核对完成；runtime-conditional 遗留已显式标注并有记录（见下）

## 验证记录（runtime-conditional 遗留）
- `toolbox --help` 可用（exit 0，`flatpak-spawn not found` 仅为 stderr 噪音）；`toolbox list`（uid 1001）返回 `Error: flatpak-spawn(1) not found` —— 镜像含 Toolbx 标记，toolbox 视自身已在 toolbox 容器内、需宿主 flatpak-spawn 互操作；属 DinP/宿主会话级限制，不阻塞镜像构建验收（与 spec 注记一致）。
- 完整服务态（supervisord + sshd + jupyter + HEALTHCHECK）需在有 systemd 用户会话/dbus 或 `podman machine ssh` 完整会话的宿主上冒烟（本 rootless 宿主无 systemd 用户会话，裸 run 需 `--no-healthcheck`）。
- devuser 实际 UID=1001（ubuntu:26.04 自带 ubuntu 用户占 1000）——既有条件，非本次引入；硬编码 UID=1000 的脚本/文档如需校准可另行治理。
- 建议用户后续在常规环境执行 `bash bin/jpman rebuild-all`（Windows 侧用 jpman.ps1/cmd）与 entrypoint 全流程冒烟复核。
