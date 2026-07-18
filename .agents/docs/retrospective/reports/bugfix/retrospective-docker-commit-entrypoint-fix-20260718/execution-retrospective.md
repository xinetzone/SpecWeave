# 执行复盘：docker commit ENTRYPOINT 泄漏问题修复

## 一、事实数据收集

### 1.1 时间线

| 时间 | 事件 |
|------|------|
| 2026-07-18 | 用户执行 `docker run -it --rm xmnn-runtime:1.2.1-fix-cp314 bash` 报错 `/usr/bin/bash: /usr/bin/bash: cannot execute binary file` |
| 2026-07-18 | 诊断：通过 `docker inspect` 发现镜像 Entrypoint=["/bin/bash"], Cmd=["-c","while true; do sleep 3600; done"] |
| 2026-07-18 | 根因定位：`docker commit` 保留了临时保活容器的入口配置 |
| 2026-07-18 | 用户询问"改Dockerfile会不会更好" |
| 2026-07-18 | 修复：两个导出脚本(do_export.sh/export_runtime.sh)的docker commit添加--change重置ENTRYPOINT/CMD |
| 2026-07-18 | 验证：修复现有镜像并测试bash/python3/默认shell三种启动方式均通过 |

### 1.2 问题现象复现

```
$ docker run -it --rm xmnn-runtime:1.2.1-fix-cp314 bash
/usr/bin/bash: /usr/bin/bash: cannot execute binary file
```

错误含义：bash试图把/usr/bin/bash（一个二进制可执行文件）当作shell脚本来解释执行，失败。

### 1.3 根因链路

```
导出脚本启动临时容器（用于安装新wheel）
  → 使用 --entrypoint /bin/bash + sleep CMD 作为保活机制
  → docker exec 安装新wheel包
  → docker commit 保存容器为新镜像
  → docker commit 默认保存容器当前所有Config（包括ENTRYPOINT和CMD）
  → 新镜像继承了临时保活配置: Entrypoint=["/bin/bash"], Cmd=["-c","while true; ..."]
  → 用户 docker run IMAGE bash → 实际执行 /bin/bash bash → bash尝试执行bash二进制文件 → 报错
```

### 1.4 Docker ENTRYPOINT vs CMD 机制

Docker容器启动命令的组合规则：`[ENTRYPOINT] [CMD]`

- 当ENTRYPOINT=["/bin/bash"]时，用户传入的任何参数都作为bash的参数
- `docker run IMAGE bash` → `/bin/bash bash` → bash把"bash"当作脚本文件名
- `docker run IMAGE python3 -c "..."` → `/bin/bash python3 -c "..."` → bash尝试执行python3脚本，同样失败
- `docker run IMAGE`（无参数）→ `/bin/bash -c "while true; do sleep 3600; done"` → 容器假死

### 1.5 变更清单

| 文件 | 变更前 | 变更后 |
|------|--------|--------|
| do_export.sh L111 | `docker commit $CONTAINER_NAME "$NEW_IMAGE"` | `docker commit --change='ENTRYPOINT []' --change='CMD ["/bin/bash"]' $CONTAINER_NAME "$NEW_IMAGE"` |
| export_runtime.sh L77 | `docker commit $CONTAINER_NAME "$NEW_IMAGE"` | 同上 |

### 1.6 镜像修复

除了修复脚本，还对已存在的 `xmnn-runtime:1.2.1-fix-cp314` 镜像进行了修复：
- 启动临时容器 → 使用 `--change` 参数重新commit → 验证通过

## 二、过程分析

### 2.1 为什么这个Bug会发生？

1. **docker commit的隐式行为**：`docker commit` 默认会保存容器的所有运行时配置（包括Entrypoint、Cmd、Env、WorkingDir等），不做任何重置。这在"快速保存容器状态"场景是合理的，但在"基于容器做增量更新"场景下是陷阱。

2. **保活配置被误用为永久配置**：导出脚本中 `--entrypoint /bin/bash -c "while true; do sleep 3600; done"` 是临时保活机制（让容器持续运行以便docker exec安装wheel），但被commit固化为镜像的永久入口。

3. **缺乏镜像配置验证**：镜像导出后，没有验证步骤检查Entrypoint/Cmd是否合理。

### 2.2 为什么错误信息令人困惑？

`/usr/bin/bash: /usr/bin/bash: cannot execute binary file` 这个错误看起来像是bash文件损坏或权限问题，但实际上是命令组合错误导致的语义错误。用户看到这个错误第一反应是"镜像坏了"或"bash有问题"，而不是"入口配置错了"。

### 2.3 对比正确的客户端镜像

项目中存在一个正确构建的客户端镜像 `notebook/xmnn/client/Containerfile`，其ENTRYPOINT设置为 `["/bin/bash", "/home/ai/entrypoint.sh"]`，CMD为 `["python"]`。这个配置是通过Dockerfile显式声明的，有明确的设计意图（UID/GID自适应）。而 `xmnn-runtime` 镜像通过docker commit构建，没有显式配置ENTRYPOINT/CMD，导致临时配置泄漏。
