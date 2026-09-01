---
id: "retrospective-xmnn-export-entrypoint-fix-20260718"
title: "XMNN Runtime 镜像导出 ENTRYPOINT 修复与发布门禁复盘"
date: 2026-07-18
type: "task-retrospective"
source: "XMNN Runtime 1.2.1-fix-cp314 镜像导出流程修复（2026-07-18）"
scope: "task"
participants: ["orchestrator", "developer"]
status: "completed"
tags: ["xmnn", "docker", "entrypoint", "export", "symbol-visibility", "whl", "repack", "verify", "gate"]
---

# XMNN Runtime 镜像导出 ENTRYPOINT 修复与发布门禁复盘

## 执行摘要

任务目标：在符号可见性修复（`HIDE_PRIVATE_SYMBOLS=ON` + `-Wl,--exclude-libs,ALL`）完成后，重新导出包含最新 `libtvm.so` 的 Docker 镜像，并修复 ENTRYPOINT 配置错误。

**关键成果**：
- 镜像 tar.gz 重新导出：2.08 GB，SHA256 `0bceaf10...`
- whl 免 Nuitka 重编译直接替换 libtvm.so（85 行 `repack_whl.py`）
- 发现并修复 ENTRYPOINT 配置缺陷（`docker commit --change` 静默失效）
- 发现并修复导出脚本 sticky `/tmp` 中断缺陷
- 建立发布门禁检查脚本 `verify_final_image.sh`（88 行，10 项检查，10/10 通过）
- 生成操作文档 `EXPORT_AND_VERIFY_GUIDE.md`（172 行）
- 同步 `export_runtime.sh` 至两步法

**关键数据**：
- 修复脚本数：4（`do_export.sh`、`export_runtime.sh`、`repack_whl.py`、`verify_final_image.sh`）
- 新增文件数：3（`repack_whl.py`、`verify_final_image.sh`、`EXPORT_AND_VERIFY_GUIDE.md`）
- whl 大小：126 MB → 95.2 MB（移除 `libtvm_allvisible.so` 30.8 MB）
- 镜像大小：2.08 GB
- libtvm.so SHA256 前缀：`80845b8e5e17024d`
- Registry 符号可见数：3310
- 验证通过率：10/10（100%）

## 1. 事实时间线

| 时间 | 事件 | 类型 |
|------|------|------|
| 14:00 | 用户询问镜像是否就绪，确认产物状态 | 启动 |
| 14:05 | 梳理导出流水线：`whl → do_export.sh → tar.gz` | 分析 |
| 14:08 | 确认 whl 内 `libtvm.so` 为旧版（06:06），缺少 11:46 符号修复 | 发现 |
| 14:10 | 确认 WSL 中无 `nuitka-gcc-llvm` 构建镜像，无法重跑 Nuitka | 决策 |
| 14:15 | 编写 `repack_whl.py`（85 行），宿主机直接替换 whl 内 `libtvm.so`/`libtvm_runtime.so`，删除 `libtvm_allvisible.so`，更新 RECORD | 实现 |
| 14:19 | whl 重打包完成：126 MB → 95.2 MB | 构建 |
| 14:20 | 首次执行 `do_export.sh`：Step 5 的 `rm -f /tmp/xmnn-*.whl` 因 sticky bit 失败，`set -e` 导致脚本在 commit 前退出 | 失败 |
| 14:25 | 修复 `do_export.sh`：`rm` 改为非致命 + Step 6 增加 root 级清理 | 修复 |
| 14:28 | 第二次执行 `do_export.sh`：导出成功，2.0 GB | 构建 |
| 14:30 | 发现 ENTRYPOINT 仍为 `[/bin/bash]`——`docker commit --change` 因为容器以 `--entrypoint` 启动而静默失效 | 发现 |
| 14:35 | 编写 `ep_fix_test.sh` 复现 `--change` 失效问题，确认两步法（commit + Dockerfile）有效 | 诊断 |
| 14:38 | 重写 `do_export.sh` Step 7：commit → 临时 Dockerfile 重置 ENTRYPOINT/CMD | 修复 |
| 14:40 | 第三次执行 `do_export.sh`：导出成功，ENTRYPOINT=null，CMD=["/bin/bash"] | 构建 |
| 14:42 | 编写 `verify_final_image.sh`（88 行，10 项检查），从 tar.gz 加载验证 | 验证 |
| 14:44 | 10/10 全部通过 | 验证 |
| 14:48 | 同步 `export_runtime.sh` 至两步法 | 同步 |
| 14:54 | 生成 `EXPORT_AND_VERIFY_GUIDE.md`（172 行） | 文档 |

## 2. 关键决策

| 决策 | 理由 | 结果 |
|------|------|------|
| 宿主机直接替换 whl 内 so，而非重跑 Nuitka | WSL 中无 `nuitka-gcc-llvm` 镜像，且仅 C++ 库有变化，Python 代码未变 | 85 行 Python 脚本完成，免 6 分钟 Nuitka 编译 |
| `rm` 失败改为非致命 | `/tmp` sticky bit 下 root 文件无法被 ai 删除，`set -e` 导致脚本在 commit 前退出 | 首次导出失败，修复后正常 |
| ENTRYPOINT 两步法（commit + Dockerfile） | `docker commit --change='ENTRYPOINT []'` 在容器以 `--entrypoint` 覆盖启动时静默失效 | 镜像 ENTRYPOINT 正确重置为 null |
| 创建发布门禁脚本而非手动验证 | 手动验证不可重复，每次导出需重新确认 | 10 项自动化检查，可复用 |

## 3. 问题根因（5-Whys 分析）

### 3.1 根因 1：`docker commit --change` 静默失效

| 层级 | 追问 | 答案 |
|------|------|------|
| Why 1 | 为什么 ENTRYPOINT 未清除？ | `--change='ENTRYPOINT []'` 未生效 |
| Why 2 | 为什么 `--change` 未生效？ | 容器以 `--entrypoint /bin/bash` 覆盖启动 |
| Why 3 | 为什么覆盖启动会影响 commit？ | Docker 引擎设计中，commit 时会保留运行时的 entrypoint 覆盖，`--change` 无法覆盖运行时设置 |
| Why 4 | 为什么之前没发现？ | 之前导出流程中 ENTRYPOINT 错误被 `--entrypoint ''` 绕过，未做自动化验证 |
| Why 5 | 为什么没有自动化验证？ | 导出流程缺少发布门禁检查环节 |

### 3.2 根因 2：`rm -f /tmp/xmnn-*.whl` 导致脚本中断

| 层级 | 追问 | 答案 |
|------|------|------|
| Why 1 | 为什么脚本在 commit 前退出？ | `set -e` 下 `rm` 失败返回非零 |
| Why 2 | 为什么 `rm -f` 会失败？ | `/tmp` 有 sticky bit，root 拷贝的文件无法被 ai 用户删除 |
| Why 3 | 为什么 whl 是 root 拥有的？ | `docker cp` 从容器拷贝的文件保留容器内 uid/gid |
| Why 4 | 为什么不用 `rm` 的 `|| true` 容错？ | 脚本未考虑 sticky bit 场景 |
| Why 5 | 为什么脚本缺少容错设计？ | 导出脚本在单一环境（无 sticky bit /tmp）开发，未做跨环境测试 |

## 4. 改进建议

| 编号 | 建议 | 优先级 | 验收标准 | 状态 |
|------|------|--------|---------|------|
| ACT-1 | whl 重打包工具 `repack_whl.py` 已建立 | 高 | 脚本可独立运行，替换 whl 内 so 并更新 RECORD | 完成 |
| ACT-2 | 导出脚本 sticky bit 容错已修复 | 高 | `do_export.sh` 中 rm 非致命 + root 清理 | 完成 |
| ACT-3 | ENTRYPOINT 两步法已落地 | 高 | `do_export.sh` + `export_runtime.sh` 均使用两步法 | 完成 |
| ACT-4 | 发布门禁脚本 `verify_final_image.sh` 已建立 | 高 | 10 项检查全部通过，可从 tar.gz 加载验证 | 完成 |
| ACT-5 | 操作文档 `EXPORT_AND_VERIFY_GUIDE.md` 已生成 | 中 | 包含导出/验证/常见问题，后续维护者可参考 | 完成 |
| ACT-6 | 将 `verify_final_image.sh` 集成到 CI/CD 流程 | 中 | 每次导出后自动运行门禁检查 | 待定 |
| ACT-7 | `repack_whl.py` 增加 `libtvm.so` 版本一致性校验 | 低 | 替换前确认源文件与目标 hash 不同，防止误操作 | 待定 |

<!-- changelog -->
- 2026-07-18 | feat | 初始版本：XMNN 镜像导出 ENTRYPOINT 修复与发布门禁复盘