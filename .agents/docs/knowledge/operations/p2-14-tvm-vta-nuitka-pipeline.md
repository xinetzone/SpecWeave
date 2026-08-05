---
id: p2-14-tvm-vta-nuitka-pipeline
title: TVM VTA 容器构建与 Nuitka 打包流水线说明
source: d:\spaces\chaos\hub\sync\AGENTS.md
source_type: file
category: operations
tags:
  - tvm
  - vta
  - podman
  - nuitka
  - build-pipeline
  - workspace-operations
archive_status: archived
archive_priority: P2
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T12:00:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 hub/sync/AGENTS.md 与 notebook/AGENTS.md、正文为流水线说明提炼、元数据与 operations 分类映射核对通过
summary: hub/sync 本地附加分析说明，覆盖 TVM VTA 构建容器（Podman + Invoke）与 Nuitka wheel 打包流水线的目录导航、命令入口、跨平台连接方式与报告约定。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p2-14-tvm-vta-nuitka-pipeline.md
archived_at: 2026-08-02T03:27:43Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:27:43Z archived from d:\spaces\chaos\.agents\knowledge\temp\operations\p2-14-tvm-vta-nuitka-pipeline.md to D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p2-14-tvm-vta-nuitka-pipeline.md
---

# TVM VTA 容器构建与 Nuitka 打包流水线说明

## 来源

- 根说明：[hub/sync/AGENTS.md](../../../../external/chaos/npuusertools/AGENTS.md)
- 子项目说明：[hub/sync/notebook/AGENTS.md](../../../../external/chaos/npuusertools/AGENTS.md)
- 上游分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`operations`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\operations\`

## 正文摘要

`hub/sync/` 是本地 TVM 相关附加分析容器，不直接在根目录操作，所有工作在子目录中进行。核心子项目：`notebook/`（TVM VTA 构建任务）、`npu_tvm/`（TVM NPU 分支源码）、`npuusertools/`（NPU 用户工具集）。

### notebook 子项目流水线

通过 Podman 运行 TVM VTA 构建容器的 Invoke 任务与 Nuitka 打包流水线：

| 路径 | 用途 |
|---|---|
| `tasks.py` | Invoke 任务入口（`inv build` / `inv nuitka`） |
| `utils/build.py` | 容器编排与 4 阶段脚本执行 |
| `utils/nuitka_scripts.py` | Nuitka 编译参数与 wheel 打包脚本生成 |
| `xmnn/` | scikit-build-core 打包配置（pyproject.toml + CMakeLists.txt） |
| `.agents/` | AI Agent 工作手册（architecture / constraints / commands / roles） |

### 关键操作约束

- Windows 平台：通过 `taolib.flowkit.podman_win.PodmanSSHClient` 连接远程 Podman
- Linux 平台：使用 `podman.PodmanClient` 本地连接
- 所有编译/打包操作在容器内执行，宿主机仅做编排
- 容器 I/O 使用 `sys.stdout.buffer.write()` 处理 bytes 输出，避免 Windows GBK 编码问题
- 报告与复盘文档统一存放 `.agents/postmortems/`，命名 `task-summary-YYYYMMDD.md`，不散落根目录

## 动作边界

本轮为 P2 专题抽样条目。正式归档时以流水线入口、目录导航与跨平台约束为核心正文，不搬运 `.agents/` 工作手册的完整架构与约束明细。
