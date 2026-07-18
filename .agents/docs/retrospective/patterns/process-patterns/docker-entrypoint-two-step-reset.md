---
id: "docker-entrypoint-two-step-reset"
title: "Docker 镜像 ENTRYPOINT 两步安全重置模式"
type: "process-pattern"
date: 2026-07-18
maturity: "L1 实验性"
maturity_note: "单案例验证（XMNN Runtime 镜像导出），待第二个独立案例验证后升级 L2"
source: "../../reports/task-reports/retrospective-xmnn-export-entrypoint-fix-20260718/README.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/process-patterns/docker-entrypoint-two-step-reset.toml"
related_patterns:
  - "../code-patterns/docker-commit-config-reset.md"
  - "../code-patterns/compiled-wheel-runtime-image-build.md"
tags: ["docker", "entrypoint", "cmd", "commit", "export", "image", "shell"]
validation_count: 1
reuse_count: 0
---

# Docker 镜像 ENTRYPOINT 两步安全重置模式

> **注意**：本模式是对 `docker-commit-config-reset.md` 的修正——该模式推荐使用 `docker commit --change='ENTRYPOINT []'`，但此方案在容器以 `--entrypoint` 覆盖启动时**静默失效**（无报错但未生效）。本模式提供两步法（commit + Dockerfile）作为可靠替代。

## 触发场景

- 需要导出/发布 Docker 镜像，且需要清除运行时的 ENTRYPOINT 覆盖
- 容器以 `--entrypoint` 参数启动（如 `docker run --entrypoint /bin/bash`），`docker commit --change` 无法重置 ENTRYPOINT
- 镜像的 CMD 被保活命令（如 `sleep infinity`）污染，需要重置为交互式 shell

**识别信号**：
- `docker inspect` 显示 ENTRYPOINT 为 `["/bin/bash"]` 而非 `null` 或 `[]`
- `docker run <img> bash` 报 `cannot execute binary file`（实际执行 `/bin/bash bash`）
- `docker commit --change='ENTRYPOINT []'` 执行后无报错，但 `docker inspect` 验证未生效

**不适用场景**：
- 容器未以 `--entrypoint` 覆盖启动（`--change` 可能正常工作）
- 使用 Dockerfile 从头构建镜像（直接用 `ENTRYPOINT []` 指令）
- 镜像不需要修改 ENTRYPOINT/CMD

## 问题背景

### `docker commit --change` 的静默失效

`docker commit --change='ENTRYPOINT []'` 在以下条件下**静默失效**（无任何警告或错误）：

1. 容器以 `docker run --entrypoint /bin/bash` 覆盖启动
2. Docker 引擎将运行时的 entrypoint 覆盖持久化到容器配置中
3. `docker commit` 时，`--change` 指令无法覆盖运行时已设置的 entrypoint
4. 结果：镜像的 ENTRYPOINT 仍为 `["/bin/bash"]`，CMD 为 `["/bin/bash"]`（原始 CMD 与新 entrypoint 拼接）

### 核心矛盾

```
docker commit --change='ENTRYPOINT []'  →  期望 null  →  实际 ["/bin/bash"]
原因：运行时 --entrypoint 覆盖的优先级高于 --change 指令
```

## 核心步骤（两步法）

### 步骤1：提交不含配置修改的中间镜像

```bash
docker commit $CONTAINER_NAME "$NEW_IMAGE-raw"
```

**为什么**：先保存容器当前状态，此时 ENTRYPOINT/CMD 可能不正确，但后续 Dockerfile 会修正。

### 步骤2：用临时 Dockerfile 重置 ENTRYPOINT/CMD

```bash
EPFIX_DIR=$(mktemp -d)
cat > "$EPFIX_DIR/Dockerfile" <<'EOF'
FROM <image>:<tag>-raw
ENTRYPOINT []
CMD ["/bin/bash"]
EOF
docker build -q -t "$NEW_IMAGE" "$EPFIX_DIR"
```

**为什么**：Dockerfile 中的 `ENTRYPOINT []` 和 `CMD ["/bin/bash"]` 是声明式配置，不受运行时覆盖影响，且 Docker 构建引擎会正确处理。

### 步骤3：清理中间镜像

```bash
docker rmi "$NEW_IMAGE-raw" >/dev/null 2>&1 || true
rm -rf "$EPFIX_DIR"
```

**为什么**：中间镜像仅用于配置重置，最终镜像已生成，清理避免磁盘浪费。

### 步骤4：验证

```bash
docker inspect "$NEW_IMAGE" --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
# 预期：Entrypoint=null  Cmd=["/bin/bash"]
```

**为什么**：自动化验证是防止配置错误的最后一道防线。`docker commit --change` 的教训是：没有验证的配置修改是不可靠的。

## 完整脚本示例

```bash
#!/bin/bash
set -euo pipefail

CONTAINER_NAME="my-container"
NEW_IMAGE="my-app:latest"

# 1. 停止容器
docker stop "$CONTAINER_NAME"

# 2. 提交中间镜像
docker commit "$CONTAINER_NAME" "$NEW_IMAGE-raw"

# 3. 用 Dockerfile 重置 ENTRYPOINT/CMD
EPFIX_DIR=$(mktemp -d)
cat > "$EPFIX_DIR/Dockerfile" <<'EOF'
FROM my-app:latest-raw
ENTRYPOINT []
CMD ["/bin/bash"]
EOF
docker build -q -t "$NEW_IMAGE" "$EPFIX_DIR"

# 4. 清理
docker rmi "$NEW_IMAGE-raw" >/dev/null 2>&1 || true
rm -rf "$EPFIX_DIR"

# 5. 验证
EP=$(docker inspect "$NEW_IMAGE" --format '{{json .Config.Entrypoint}}')
CM=$(docker inspect "$NEW_IMAGE" --format '{{json .Config.Cmd}}')
echo "ENTRYPOINT=$EP  CMD=$CM"

# 6. 回归测试
docker run --rm "$NEW_IMAGE" bash -c 'echo "OK: entrypoint fixed"'
```

## 反模式（不要这么做）

### ❌ 反模式1：依赖 `docker commit --change` 修改 ENTRYPOINT

- **错误**：`docker commit --change='ENTRYPOINT []' --change='CMD ["/bin/bash"]' $CONTAINER $IMAGE`
- **后果**：容器以 `--entrypoint` 覆盖启动时静默失效，镜像 ENTRYPOINT 仍为 `["/bin/bash"]`
- **为何危险**：无任何报错或警告，只有运行时才会暴露问题
- **正确做法**：使用两步法（commit + Dockerfile）

### ❌ 反模式2：不验证 ENTRYPOINT 配置

- **错误**：提交后不运行 `docker inspect` 验证
- **后果**：配置错误在导出后才发现，需要重新导出整个镜像（数分钟到数十分钟）
- **正确做法**：提交后立即 `docker inspect` 验证，确认后再 `docker save`

### ❌ 反模式3：用 `docker run --entrypoint ''` 绕过而非修复

- **错误**：每次使用镜像时加 `--entrypoint ''` 参数
- **后果**：对下游用户不透明，且容易遗忘
- **正确做法**：修复镜像本身的 ENTRYPOINT 配置

## 检验标准

- [ ] `docker inspect` 显示 ENTRYPOINT 为 `null` 或 `[]`
- [ ] `docker inspect` 显示 CMD 为 `["/bin/bash"]`
- [ ] `docker run --rm <img> bash -c 'echo OK'` 正常执行
- [ ] 默认 `docker run -i --rm <img>` 进入交互式 bash

## 迁移示例

### 场景1：XMNN Runtime 镜像导出（本项目，源案例）

- **问题**：`docker commit --change='ENTRYPOINT []'` 静默失效，导致 `docker run <img> bash` 报 `cannot execute binary file`
- **修复**：改为两步法（commit + Dockerfile）
- **结果**：ENTRYPOINT=null，CMD=["/bin/bash"]，回归测试通过

### 场景2：CI/CD 中基于运行容器生成发布镜像（推断，待验证）

- **类似问题**：CI 中 `docker run --entrypoint /bin/sh` 执行测试后 commit 发布镜像，ENTRYPOINT 被污染
- **对应策略**：测试容器 commit 后使用两步法重置 ENTRYPOINT
- **差异**：CI 环境可能使用 `docker build` 而非 `docker commit`

### 场景3：热修复镜像（推断，待验证）

- **类似问题**：生产环境 `docker exec` 修复后 commit 新镜像，保活命令成为 ENTRYPOINT
- **对应策略**：commit 后使用两步法重置

## 与相关模式的关系

- **[docker-commit-config-reset.md](../code-patterns/docker-commit-config-reset.md)**：该模式推荐 `--change` 方案，本模式是其修正版——在 `--entrypoint` 覆盖场景下，`--change` 不可靠，必须使用两步法
- **[compiled-wheel-runtime-image-build.md](../code-patterns/compiled-wheel-runtime-image-build.md)**：该模式的导出步骤可使用本模式确保 ENTRYPOINT 正确

## Changelog

- **2026-07-18** (v1.0.0): 初始版本，从 XMNN Runtime 镜像导出修复复盘萃取，单案例验证，标记 L1 实验性