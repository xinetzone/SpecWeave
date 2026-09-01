---
id: "nested-engine-storage-externalize"
title: "嵌套引擎存储卷外置模式（Nested Engine Storage Externalize）"
type: "process-pattern"
maturity: "L1-实验性"
maturity_note: "案例1（正向+反向）：C盘治理 20260828，jupyter 容器内嵌套 podman 默认存储写可写层形成 21GB 黑洞（反模式实证），清理后可写层归零但卷外置方案尚待下一次构建任务验证"
created: "2026-08-28"
last_updated: "2026-08-28"
source:
  - "retrospective-c-drive-vhdx-recovery-20260828（模式2，洞察1）"
related_patterns:
  - "vhdx-two-phase-recovery-sop.md"
  - "docker-cross-os-internal-build.md"
tags: ["nested-containers", "podman-in-podman", "docker-in-docker", "writable-layer", "storage-volume", "build-cache", "disk-space"]
validation_count: 1
---

# 嵌套引擎存储卷外置模式（Nested Engine Storage Externalize）

## 触发场景

- 需要在容器内运行嵌套容器引擎（podman-in-podman、docker-in-docker）执行构建任务
- 嵌套构建会产生大量镜像层、构建缓存（本案例：91 个镜像合计 21GB）
- 外层容器生命周期长于单次构建任务（如常驻开发容器 jupyter-podman）
- 宿主磁盘空间敏感（vhdx 所在盘紧张，或需精确控制容器磁盘配额）

**适用于**：常驻容器内的重复构建任务、CI 流水线 docker-in-docker 构建器、嵌套引擎镜像积累监控。

**不适用于**：一次性构建容器（用完即删，见反目标1）、无嵌套引擎的容器（可写层天然稳定）。

## 问题本质

外层容器的可写层（overlay upperdir）对宿主而言是**不透明黑盒**：

1. **双重不可见**：宿主侧 `podman system df` 只显示可写层总量（22.76GB）不见内部构成；容器内普通用户 `du` 因权限只见 7.3GB（实际 32GB，F-006）——排查时需 root 视角 + 宿主 `podman inspect ... .GraphDriver.Data.UpperDir` 双路定位
2. **只增不减**：嵌套引擎默认存储路径（`/var/lib/containers`）落在可写层，vhdx 随之膨胀且不会自动归还（需配合 [VHDX 二相回收 SOP](vhdx-two-phase-recovery-sop.md)）
3. **僵尸态不可入**：外层容器主进程死亡后（本案例 F-021），`podman exec` 失败，只能宿主侧分析 overlay diff 目录

## 核心步骤

1. **存储外置**：嵌套引擎存储根指向命名卷或显式挂载：
   ```bash
   # 容器启动时预挂载（推荐）
   podman run -v nested-storage:/var/lib/containers ...
   # 或嵌套引擎指定存储根
   podman --root /mnt/buildcache/storage --runroot /mnt/buildcache/run ...
   ```
2. **产物即时导出**：构建产物（wheel/镜像 tar）写出到 `/workspace` 类 bind mount，不留在嵌套存储
3. **结束即 prune**：构建会话结束执行 `podman rmi -af --force`（注意：`system prune` 对运行中容器引用的镜像报 image in use，F-015）
4. **监控验收**：`podman system df` 中外层容器 SIZE 长期稳定（不随嵌套构建增长）

## 排查路径（当黑洞已形成）

```bash
# 宿主侧定位可写层真实构成（root）
wsl -d podman-machine-default -u root -- \
  podman inspect <容器> --format {{.GraphDriver.Data.UpperDir}}
du -xh --max-depth=2 <UpperDir> | sort -rh | head -10
```

## 反模式

| 反模式 | 后果 | 实证 |
|--------|------|------|
| ❌ 嵌套引擎默认存储路径直接写可写层 | 21GB 黑洞，宿主 vhdx 膨胀 | F-009 |
| ❌ 依赖普通用户 du 排查容器占用 | 权限遮蔽，7.3GB vs 32GB 严重低估 | F-006 |
| ❌ 构建完成不清理（xmnn 系列镜像滞留） | 镜像积累 91 个，回收需提权攻坚 | F-010 |
| ❌ 僵尸容器内 exec 排查 | 主进程已死 exec 必失败，浪费排障时间 | F-021 |
| ❌ `system prune` 清理被容器引用的镜像 | 报 image in use 静默跳过，需先 rm 容器或 rmi --force | F-015 |

## 失败案例（20260828 真实实证，防成功偏误）

| # | 失败尝试 | 现象 | 教训 |
|---|---------|------|------|
| 1 | 未外置存储直接嵌套构建 | 可写层 22.76GB，其中 21GB 嵌套镜像，宿主 C盘耗尽 | 默认路径即反模式，本模式存在的理由 |
| 2 | 普通用户 du 评估容器占用 | 仅见 7.3GB（root-only 目录不可见），低估 4 倍 | 排查必须 root + 宿主 UpperDir 双路 |
| 3 | `podman system prune -a -f` 清理 | "image in use" 报错，镜像未删 | 改 `podman rm -af` + `rmi -af --force` 才清空（21GB→764KB） |
| 4 | 容器僵尸态后 exec 排查 | exec 卡死/失败 | 僵尸容器只能宿主侧 inspect UpperDir 分析 |
| 5 | 清理后 boot ID 缓存不一致 | 嵌套 podman 拒绝服务 | 删 `/run/containers/storage` 与 `/run/libpod` 后恢复（F-017） |

> 注：本案例是**反模式实证 + 清理验证**，卷外置的正向实施尚待下次构建任务应用后升 L2。

## 不适用/反目标/边界场景（≥3类，防确认偏误）

| 类别 | 场景 | 不适用原因 |
|------|------|-----------|
| 反目标1 | 一次性构建容器（CI 每任务新起，用完即删） | 容器销毁即释放可写层，卷外置徒增复杂度 |
| 反目标2 | 无嵌套引擎的普通容器 | 可写层增长源于应用日志/上传文件，应走日志轮转/应用层治理 |
| 反目标3 | 跨 OS bind mount 作存储卷（Windows 9p → Linux） | 9p 文件系统 IO 极慢（项目记忆实证），构建会慢一个数量级；应选命名卷或容器原生 FS |
| 边界1 | 嵌套引擎需 rootful 而外层是 rootless | 存储/运行时权限模型冲突，需验证嵌套引擎在容器内的 uid 映射 |
| 边界2 | 构建缓存跨任务复用需求强 | 命名卷生命周期管理需额外设计（否则缓存无限增长，问题换了个位置） |
| 边界3 | 磁盘配额严格的共享环境 | 卷外置后可写层可控，但卷本身仍需配额监控（`podman volume df`） |

## 早期预警信号（≥5个）

| 信号 | 判定阈值 | 含义 |
|------|---------|------|
| `podman system df` 容器 SIZE >10GB | 可写层异常膨胀 | 疑似嵌套引擎/缓存写可写层 |
| 宿主 vhdx 增长与挂载卷内容不匹配 | 差值持续扩大 | 可写层有隐形写入源 |
| 容器内 df 与普通用户 du 差异 >2倍 | 权限遮蔽 | 存在 root-only 大目录，需提权排查 |
| 构建任务后容器 SIZE 只增不减 | 单任务增长 >2GB | 构建产物/镜像滞留可写层 |
| `podman exec` 无响应但 ps 显示 running | 主进程死亡 | 僵尸容器，走宿主侧 UpperDir 排查 |

## 跨场景迁移

| 场景 | 嵌套引擎 | 外置方法 |
|------|---------|---------|
| CI docker-in-docker | dockerd | `-v /var/lib/docker` 命名卷（业界标准做法 GitLab CI/Kaniko 均此思路） |
| Kubernetes 构建 Pod | docker sidecar | emptyDir/PVC 挂 `/var/lib/containers` |
| Codespaces/devcontainer | 嵌套 podman | devcontainer.json 挂命名卷 |
| 本地 rootless podman 嵌套 | podman | `--root/--runroot` 指向外置路径（本模式主案例） |

**本质**：可写层是给运行时状态（进程临时文件、配置变更）的，不是给数据存储的——任何"数据"（镜像、缓存、产物）都应显式选择落点（卷/挂载/导出），否则就是黑洞。

## 关联文档

- 复盘报告：[retrospective-c-drive-vhdx-recovery-20260828](../../reports/environment-setup/retrospective-c-drive-vhdx-recovery-20260828/README.md)
- 姊妹模式：[vhdx-two-phase-recovery-sop.md](vhdx-two-phase-recovery-sop.md)（黑洞形成后的回收方案，本模式是预防方案）
- 相关模式：[docker-cross-os-internal-build.md](docker-cross-os-internal-build.md)（构建目录放容器原生 FS 的同类思想）
