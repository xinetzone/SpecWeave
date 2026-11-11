---
id: "extraction-xmnn-export-entrypoint-fix-20260718"
title: "XMNN 镜像导出修复模式萃取"
date: 2026-07-18
type: "pattern-extraction"
source: "retrospective-xmnn-export-entrypoint-fix-20260718/insight-extraction.md"
scope: "task"
status: "completed"
maturity: "candidate"
tags: ["docker", "entrypoint", "shell-scripting", "gate", "export", "pattern"]
---

# XMNN 镜像导出修复模式萃取

## 萃取说明

本次萃取源于单次任务（XMNN 镜像导出修复），按萃取规范，单案例模式标记为"候选洞察"（Candidate），待第二个独立案例验证后升级为 L1 正式模式。

共萃取出 3 个候选模式。

---

## 候选模式 A：Docker 镜像 ENTRYPOINT 安全重置模式

- **成熟度**：Candidate（单案例已验证）
- **类型**：流程模式（Process Pattern）
- **抽象层次**：L2（方法）

### 触发场景

需要修改已有 Docker 镜像的 ENTRYPOINT/CMD 配置（如导出发布镜像时清理运行时覆盖的 entrypoint）。

### 问题背景

`docker commit --change='ENTRYPOINT []'` 在以下条件下**静默失效**（无报错但未生效）：
- 容器以 `--entrypoint` 参数覆盖了镜像默认 entrypoint
- Docker 引擎保留运行时覆盖，`--change` 无法覆盖运行时设置

### 核心步骤

```bash
# Step 1: 提交不含 ENTRYPOINT 修改的中间镜像
docker commit $CONTAINER_NAME "$NEW_IMAGE-raw"

# Step 2: 用临时 Dockerfile 重置 ENTRYPOINT/CMD
EPFIX_DIR=$(mktemp -d)
cat > "$EPFIX_DIR/Dockerfile" <<'EOF'
FROM <image>:<tag>-raw
ENTRYPOINT []
CMD ["/bin/bash"]
EOF
docker build -q -t "$NEW_IMAGE" "$EPFIX_DIR"

# Step 3: 清理中间镜像
docker rmi "$NEW_IMAGE-raw" >/dev/null 2>&1 || true
rm -rf "$EPFIX_DIR"

# Step 4: 验证
docker inspect "$NEW_IMAGE" --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
# 预期：Entrypoint=null Cmd=["/bin/bash"]
```

### 适用条件

- 容器以 `--entrypoint` 覆盖启动
- 需要修改最终镜像的 ENTRYPOINT/CMD
- 目标镜像大小适中（Dockerfile build 仅需秒级，不增加显著耗时）

### 反模式

- **直接用 `--change` 修改 ENTRYPOINT**：在 `--entrypoint` 覆盖场景下静默失效，无警告
- **用 `docker run --entrypoint ''` 绕过而非修复**：每次使用都需要记住加参数，且对下游用户不透明

### 迁移验证

- 已验证场景：XMNN Runtime 镜像导出（`do_export.sh` + `export_runtime.sh`）
- 待验证场景：其他 Docker 镜像发布流程

### 与已有模式的关系

- 关联模式：Docker 构建网络韧性模式（`docker-build-network-resilience`，已有 L1 模式）
- 区别：本模式关注导出阶段（commit + save），非构建阶段

---

## 候选模式 B：Shell 脚本清理操作非阻塞模式

- **成熟度**：Candidate（单案例已验证）
- **类型**：编码模式（Code Pattern）
- **抽象层次**：L2（方法）

### 触发场景

Shell 脚本中需要在关键路径（commit/save/export 之前）执行文件清理操作，但清理可能因权限、sticky bit 等原因失败。

### 问题背景

`set -e` 下任何命令失败都会导致脚本立即退出。如果清理操作（如 `rm -f /tmp/*.whl`）在 commit/save 之前且可能因权限问题失败，会导致整个流程在关键时刻中断，浪费之前的所有工作。

具体案例：`/tmp` 的 sticky bit 导致非 root 用户无法删除 root 拥有的文件，`docker cp` 保留容器内 root uid。

### 核心步骤

```bash
# 模式 A：非致命清理（推荐用于非关键路径）
rm -f /tmp/*.whl 2>/dev/null || true

# 模式 B：延迟清理（推荐用于 commit/save 之前）
# 先 commit/save，再清理
docker commit $CONTAINER "$IMAGE"
docker save "$IMAGE" | gzip > output.tar.gz
# 现在清理——即使失败，镜像已导出
docker exec $CONTAINER rm -f /tmp/*.whl

# 模式 C：root 级清理（推荐用于 root 拥有的文件）
docker exec $CONTAINER rm -f /tmp/*.whl
```

### 反模式

- **在 commit/save 之前执行阻塞性清理**：清理失败导致整个流程白跑
- **依赖 `rm -f` 一定成功**：sticky bit、权限、只读文件系统等可能使 `rm -f` 失败
- **不加 `|| true` 的清理在 `set -e` 脚本中**：任何失败都会终止脚本

### 迁移验证

- 已验证场景：`do_export.sh` Step 5 清理 `/tmp/xmnn-*.whl`
- 待验证场景：其他 `set -e` shell 脚本中的清理操作

---

## 候选模式 C：发布门禁检查模式

- **成熟度**：Candidate（单案例已验证）
- **类型**：流程模式（Process Pattern）
- **抽象层次**：L2（方法）

### 触发场景

任何软件发布流程的最后一步——导出产物（镜像/包/二进制）后，需要自动化验证产物完整性。

### 问题背景

ENTRYPOINT 错误在之前的 XMNN 镜像导出中已存在（`/usr/bin/bash: cannot execute binary file`），但一直未被发现，因为用户每次都用 `--entrypoint ''` 绕过。缺少自动化验证意味着缺陷会持续积累，直到被下游用户发现。

### 核心步骤

1. **从最终产物加载**（而非从本地 Docker 缓存验证）
   ```bash
   docker load -i output.tar.gz
   ```

2. **配置检查**：ENTRYPOINT、CMD、环境变量等
   ```bash
   docker inspect "$IMAGE" --format '{{json .Config.Entrypoint}}'
   ```

3. **回归测试**：之前失败的用例必须通过
   ```bash
   docker run --rm "$IMAGE" bash -c 'echo OK'
   ```

4. **内容完整性**：关键文件的版本/哈希校验
   ```bash
   docker run --rm "$IMAGE" -c 'sha256sum /path/to/key/file'
   ```

5. **功能冒烟测试**：核心 API 可调用
   ```bash
   docker run --rm "$IMAGE" -c 'python -c "import core_module; print(\"OK\")"'
   ```

6. **输出 PASS/FAIL 报告**，非零退出码表示门禁未通过

### 反模式

- **只验证本地 Docker 缓存中的镜像**：本地缓存可能和导出产物不一致
- **手动逐项检查**：不可重复，容易遗漏，每次发布都需重新记忆
- **门禁脚本放在不同仓库**：维护者找不到，门禁形同虚设

### 迁移验证

- 已验证场景：XMNN Runtime 镜像导出（10 项检查，10/10 通过）
- 待验证场景：其他 Docker 镜像/包发布流程

### 参考实现

[verify_final_image.sh](../../../../../../external/xmhub/xmnn/tests/verify_final_image.sh)（88 行，10 项检查，独立可运行）

<!-- changelog -->
- 2026-07-18 | feat | 初始版本：3 个候选模式（Candidate），待第二个独立案例验证后升级为 L1