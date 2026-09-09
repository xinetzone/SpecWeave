---
id: "retrospective-invload-invalid-tar-20260909"
title: "inv load 镜像缓存损坏复盘"
date: "2026-09-09"
source: "../../reports/incident-reports/retrospective-invload-invalid-tar-20260909/retrospective-report.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/reports/incident-reports/retrospective-invload-invalid-tar-20260909/retrospective-report.toml"
type: incident-report
scope: task
status: completed
---

# inv load 镜像缓存损坏复盘

## 事件概述

**发生时间**：2026-09-09
**影响范围**：`apps/containers/client/.image-cache/`
**严重程度**：P2（功能不可用，可快速修复）
**根因类别**：工具误用（PowerShell Compress-Archive 生成 ZIP 而非 gzip）

## 事实时间线

| # | 时间（UTC+8） | 事件 |
|---|-------------|------|
| F1 | ~14:00 | 执行 `podman save` 生成原始 `.tar`（rootless 1.12 GB, client 1.83 GB） |
| F2 | ~14:17 | 执行 `podman save localhost/jupyter-podman-client:latest -o client.tar` |
| F3 | 14:17 | 使用 `Compress-Archive` 将两个 `.tar` 压缩为 `.tar.gz` 放入 `.image-cache/` |
| F4 | ~14:30 | 更新 `.image-cache/manifest.txt`，指向新的 `.tar.gz` 文件 |
| F5 | 用户执行 `inv load` | 报错：`invalid tar header`（oci-archive 和 docker-archive 格式均不支持） |
| F6 | 根因诊断 | `Compress-Archive` 是 PowerShell ZIP 工具，不是 gzip；扩展名 `.tar.gz` 掩盖了底层 ZIP 格式 |
| F7 | 修复执行 | 用 Python `gzip.open()` 重新生成有效的 `.tar.gz`（571 MB + 357 MB） |
| F8 | 验证 | 两个新 `.tar.gz` 均通过 `podman load -i` 测试 |

## 根因分析（5Why）

```
为什么 inv load 失败？
├─ 因为 .image-cache 中的 .tar.gz 文件格式无效
│   └─ 因为文件是用 Compress-Archive 生成的（ZIP 格式）
│       └─ 因为执行者不知道 Compress-Archive 生成的是 ZIP 而非 gzip
│           └─ 因为 .tar.gz 扩展名具有误导性，工具行为与命名直觉不符
│               └─ 因为没有在 image-cache 文档中明确记录压缩规范
└─ 为什么 manifest.txt 没有阻止这个问题？
    └─ 因为 manifest 只有引用信息，没有格式校验逻辑
```

**系统性根因**：
1. **工具误用**：`Compress-Archive` 与 `gzip` 在 Windows 上功能相似但输出格式不同
2. **缺乏显式约束**：`.image-cache/` 目录下没有说明如何正确生成 `.tar.gz`
3. **缺少完整性校验**：manifest.txt 记录了元数据但没有预校验机制

## 洞察（3条）

| # | 洞察 | 证据 | 反常识 | 下次行动 |
|---|------|------|--------|---------|
| I1 | Windows PowerShell `Compress-Archive` 生成的是 ZIP，不是 gzip | 文件扩展名 `.tar.gz` 掩盖了底层格式问题，`podman load` 报 `invalid tar header` | 用户看扩展名以为是 gzip tar，实际是 ZIP；Podman 的错误信息也没有直接说"文件格式错误" | **新增 `.image-cache/README.md`**：明确禁止使用 `Compress-Archive`，指定 Python gzip 或 WSL tar 方案 |
| I2 | `manifest.txt` 没有校验 .tar.gz 完整性 | manifest 记录了 IMAGE_FILE、SIZE、SHA256，但没有校验流程；损坏的文件被当作有效缓存使用 | 缓存命中逻辑只检查文件是否存在，不检查格式有效性 | **在 `tasks.py` 的 load 任务中加入文件大小/SHA256 预校验**，不匹配时自动删除重建 |
| I3 | `podman save` 和 `podman load` 之间的格式契约未显式文档化 | 同一镜像在不同位置保存为原始 `.tar` vs `.tar.gz`，两者 `podman load` 都能接受；但 `.tar.gz` 必须是真正的 gzip | 扩展名 `.tar.gz` 暗示了格式契约，但工具链没有强制验证 | **建立镜像缓存格式规范**：`podman save --format docker` 输出 `.tar`，再用 `gzip` 命令行工具压缩 |

## 已萃取模式

### `win-powershell-compress-archive-gzip-mismatch`（L1 实验性）

- **触发场景**：Windows 环境下需要将容器镜像或大型 tar 文件压缩为 `.tar.gz`
- **核心规则**：禁止使用 PowerShell `Compress-Archive`；改用 Python `gzip.open()` 或 WSL `tar -czf`
- **反模式**：用 `Compress-Archive` 生成 .tar.gz → `podman load` 报 invalid tar header
- **已沉淀至**：[docs/retrospective/patterns/process-patterns/win-powershell-compress-archive-gzip-mismatch.md](../../patterns/process-patterns/win-powershell-compress-archive-gzip-mismatch.md)

## 行动项（A1-A3）

| # | 行动项 | 负责人 | 优先级 | 状态 | 验收标准 |
|---|--------|--------|--------|------|---------|
| A1 | 在 `.image-cache/` 下创建 `README.md`，明确禁止使用 `Compress-Archive`，指定 Python gzip 方案 | Agent | P1 高 | ⏳ 待执行 | README 存在且内容准确 |
| A2 | 在 `tasks.py` 的 load 任务中加入文件大小/SHA256 预校验，不匹配时提示重建 | Agent | P2 中 | ⏳ 待执行 | 损坏缓存自动检测并报错 |
| A3 | 提交变更到 git（含模式文档 + 复盘报告 + toml 元数据） | Agent | P1 高 | ⏳ 待执行 | commit message 符合 Conventional Commits |

## 质量门

- [x] G1 事实无因果词
- [x] G2 洞察四元组完整
- [x] G3 模式可迁移（Win 压缩工具误用场景可迁移至其他容器/归档工具）
- [x] G4 行动项原子化
