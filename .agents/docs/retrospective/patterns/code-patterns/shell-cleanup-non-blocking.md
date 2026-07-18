---
id: "shell-cleanup-non-blocking"
title: "Shell 脚本清理操作非阻塞模式"
type: "code-pattern"
date: 2026-07-18
maturity: "L1 实验性"
maturity_note: "单案例验证（XMNN do_export.sh /tmp sticky bit 清理失败），待第二个独立案例验证后升级 L2"
source: "../../reports/task-reports/retrospective-xmnn-export-entrypoint-fix-20260718/README.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/shell-cleanup-non-blocking.toml"
related_patterns:
  - "idempotent-shell-config.md"
tags: ["shell", "bash", "set-e", "cleanup", "rm", "sticky-bit", "permissions", "docker", "error-handling"]
validation_count: 1
reuse_count: 0
---

# Shell 脚本清理操作非阻塞模式

## 触发场景

- Shell 脚本中在关键路径（commit/save/export 之前）执行文件清理操作
- 清理操作可能因权限、sticky bit、只读文件系统等原因失败
- 脚本使用了 `set -e`（任何命令失败立即退出）
- 清理的文件由其他用户（如 root）创建，当前用户无权删除

**识别信号**：
- `rm -f` 看似安全但返回非零退出码
- 脚本在 `docker commit` 或 `docker save` 之前意外退出
- `/tmp` 目录下的文件无法被非 root 用户删除（sticky bit + 文件归属 root）

**不适用场景**：
- 清理失败会导致安全问题（如密钥泄露）——此时清理必须是阻塞的
- 脚本未使用 `set -e`
- 清理操作在 commit/save 之后

## 问题背景

### 三道防线同时失效

1. **`rm -f` 不保证成功**：`/tmp` 有 sticky bit（`drwxrwxrwt`），只有文件所有者或 root 能删除文件。`docker cp` 从容器拷贝的文件保留 root uid，非 root 用户无权删除。
2. **`set -e` 使任何命令失败立即退出**：`rm -f` 返回非零 → 脚本退出。
3. **清理操作放在关键路径上**：`rm` 在 commit 和 save 之前，且是阻塞性操作。

## 核心步骤

### 模式 A：非致命清理（推荐用于非关键路径）

```bash
rm -f /tmp/*.whl 2>/dev/null || true
```

**何时使用**：清理操作失败不影响核心流程，文件可后续手动清理。

### 模式 B：延迟清理（推荐用于 commit/save 之前）

```bash
# 先 commit/save，再清理
docker commit $CONTAINER "$IMAGE"
docker save "$IMAGE" | gzip > output.tar.gz

# 现在清理——即使失败，镜像已导出
rm -f /tmp/*.whl 2>/dev/null || true
```

**何时使用**：清理操作在 commit/save 之前，但清理失败不应阻塞核心流程。

### 模式 C：root 级清理（推荐用于 root 拥有的文件）

```bash
docker exec $CONTAINER rm -f /tmp/*.whl
```

**何时使用**：清理的文件由 root 拥有，非 root 用户无法删除。

### 决策树

```
需要清理文件？
├─ 清理失败是否影响安全？ ──是──→ 阻塞式清理（set -e 下允许失败退出）
├─ 文件是否在 commit/save 之前？ ──是──→ 延迟清理（模式 B）或 root 级清理（模式 C）
├─ 文件由 root 拥有？ ──是──→ root 级清理（模式 C）
└─ 其他 ──→ 非致命清理（模式 A）
```

## 反模式（不要这么做）

### ❌ 反模式1：在 commit/save 之前执行阻塞性清理

```bash
# 错误
rm -f /tmp/*.whl          # 可能失败
docker commit $C "$IMG"   # 永远不会执行
docker save "$IMG" | gzip > out.tar.gz  # 永远不会执行
```

- **后果**：清理失败导致整个流程白跑，浪费之前的安装/配置时间
- **正确做法**：先 commit/save，再清理

### ❌ 反模式2：依赖 `rm -f` 一定成功

```bash
# 错误（在 set -e 脚本中）
rm -f /tmp/*.whl
```

- **后果**：sticky bit、权限、只读文件系统等可使 `rm -f` 失败
- **正确做法**：`rm -f /tmp/*.whl 2>/dev/null || true`

### ❌ 反模式3：所有清理操作不加 `|| true`

- **错误**：`set -e` 脚本中每个 `rm` 都是潜在的退出点
- **正确做法**：区分关键清理（失败必须退出）和非关键清理（失败可容忍），非关键清理加 `|| true`

## 检验标准

- [ ] 非关键清理操作使用 `|| true` 或 `2>/dev/null || true`
- [ ] commit/save 之前的清理操作已移至 commit/save 之后
- [ ] root 拥有的文件清理使用 `docker exec` 或 `sudo`
- [ ] 关键清理（安全相关）保持阻塞，失败时脚本退出

## 迁移示例

### 场景1：XMNN do_export.sh 修复（本项目，源案例）

- **问题**：`rm -f /tmp/xmnn-*.whl` 因 sticky bit + root 归属失败，`set -e` 导致脚本在 commit 前退出
- **修复**：`rm` 改为 `|| true` + Step 6 增加 `docker exec ... rm` root 级清理
- **结果**：清理失败不再阻塞导出流程

### 场景2：CI/CD 构建脚本中的临时文件清理（推断，待验证）

- **类似问题**：CI runner 的 `/tmp` 可能被其他 job 污染，清理失败不应中断构建
- **对应策略**：非关键清理使用 `|| true`

### 场景3：Docker 构建中 `docker cp` 后的临时文件清理（推断，待验证）

- **类似问题**：`docker cp` 从容器拷贝的文件保留 root uid
- **对应策略**：使用 `docker exec ... rm` 在容器内清理

## Changelog

- **2026-07-18** (v1.0.0): 初始版本，从 XMNN do_export.sh sticky bit 修复复盘萃取，单案例验证，标记 L1 实验性