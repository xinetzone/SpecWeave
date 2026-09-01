---
id: "insight-xmnn-export-entrypoint-fix-20260718"
title: "XMNN 镜像导出修复洞察萃取"
date: 2026-07-18
type: "insight-extraction"
source: "retrospective-xmnn-export-entrypoint-fix-20260718/README.md"
scope: "task"
participants: ["orchestrator", "developer"]
status: "completed"
tags: ["docker", "entrypoint", "shell-scripting", "sticky-bit", "set-e", "whl", "gate", "export"]
---

# XMNN 镜像导出修复洞察萃取

## 洞察总览

| 编号 | 洞察 | 类型 | 可复用性 |
|------|------|------|---------|
| I1 | `docker commit --change` 在 entrypoint 覆盖场景下静默失效 | 反直觉行为 | 高（所有 Docker 镜像导出场景） |
| I2 | sticky bit + `set -e` 组合导致脚本在关键时刻静默退出 | 隐性陷阱 | 高（所有 shell 脚本） |
| I3 | whl 内 so 直替换方案：免 Nuitka 重编译 | 效率优化 | 中（C++ 库迭代场景） |
| I4 | 发布门禁是导出流程的必需品，非可选项 | 流程设计 | 高（所有发布流程） |
| I5 | 导出脚本中 rm 清理操作应是非阻塞的 | 容错设计 | 高（所有 shell 脚本） |

---

## I1：`docker commit --change` 在 entrypoint 覆盖场景下静默失效

### 现象

`docker commit --change='ENTRYPOINT []'` 执行后无报错，但镜像的 ENTRYPOINT 仍为 `[/bin/bash]`，导致 `docker run <img> bash` 实际执行 `/bin/bash bash`，报 `cannot execute binary file`。

### 根因

Docker 引擎设计中，`docker commit` 会保留容器运行时的 entrypoint 状态。当容器以 `--entrypoint /bin/bash` 覆盖启动时，这个运行时覆盖优先于 `--change` 指令。`--change` 不会覆盖运行时设置，且**没有任何警告**。

### 验证方法

```bash
# 复现
docker run -d --name test --entrypoint /bin/bash img -c "sleep 300"
docker commit --change='ENTRYPOINT []' --change='CMD ["/bin/bash"]' test test:bad
docker inspect test:bad --format '{{json .Config.Entrypoint}}'  # → ["/bin/bash"]，非 null

# 正确做法：两步法
docker commit test test:raw
cat > Dockerfile <<'EOF'
FROM test:raw
ENTRYPOINT []
CMD ["/bin/bash"]
EOF
docker build -t test:good .
docker inspect test:good --format '{{json .Config.Entrypoint}}'  # → null
```

### 影响范围

所有通过 `docker commit --change` 修改 ENTRYPOINT 的导出流程，尤其是容器以 `--entrypoint` 覆盖启动的场景。

### 建议

- 导出脚本中 ENTRYPOINT 修改使用两步法（commit + Dockerfile），避免依赖 `--change`
- 导出后自动验证 `docker inspect` 确认 ENTRYPOINT 为空

---

## I2：sticky bit + `set -e` 组合导致脚本在关键时刻静默退出

### 现象

`do_export.sh` 中 `rm -f /tmp/xmnn-*.whl` 在 Step 5 失败，导致脚本在 `docker commit` 和 `docker save` 之前退出，白白浪费了 whl 安装的 5 分钟。

### 根因

三道防线同时失效：
1. **`rm -f` 不保证成功**：`/tmp` 有 sticky bit（`drwxrwxrwt`），只有文件所有者或 root 能删除文件。`docker cp` 从容器拷贝的文件保留 root uid，ai 用户无权删除。
2. **`set -e` 使任何命令失败立即退出**：`rm -f` 返回非零 → 脚本退出。
3. **清理操作放在了关键路径上**：`rm` 在 commit 和 save 之前，且是阻塞性操作。

### 影响范围

所有在 `/tmp` 或任何 sticky bit 目录下操作 root 文件的 shell 脚本，尤其是使用 `set -e` 的脚本。

### 建议

- 清理操作应是非致命的（`|| true` 或 `2>/dev/null || true`）
- 关键路径上的清理操作放在 commit/save 之后
- 最终清理由 root 执行（`docker exec ... rm`）

---

## I3：whl 内 so 直替换方案：免 Nuitka 重编译

### 场景

TVM C++ 库（`libtvm.so`、`libtvm_runtime.so`）更新后，需要将新 so 打入 whl 包。传统做法是重新运行 Nuitka 编译（6 分钟），但构建环境（`nuitka-gcc-llvm` Docker 镜像）可能不可用。

### 方案

直接在宿主机解压 whl → 替换 so 文件 → 更新 RECORD hash → 重新打包。85 行 Python 脚本完成，秒级执行。

关键步骤：
1. 解压 whl 到临时目录
2. 替换 `tvm/_libs/libtvm.so` 和 `tvm/_libs/libtvm_runtime.so`
3. 删除已废弃的 `tvm/_libs/libtvm_allvisible.so`
4. 重新计算 RECORD 中对应条目的 SHA256 hash
5. 重新打包为 zip

### 适用条件

- 仅 C++ 库有变化，Python 代码未变
- 新 so 与 whl 内 Python 绑定的 ABI 兼容

### 限制

- 不适用于 Python 代码变更（需要 Nuitka 重编译）
- 不适用于新增/删除 Python 模块
- 需要确认 ABI 兼容性（同名函数签名未变）

---

## I4：发布门禁是导出流程的必需品，非可选项

### 洞察

ENTRYPOINT 错误在之前的导出中已存在（`/usr/bin/bash: cannot execute binary file`），但一直未被发现，因为用户总是用 `--entrypoint ''` 绕过。缺少自动化验证意味着每次导出都依赖人工记忆，缺陷会持续积累。

### 建议的门禁检查项

1. tar.gz 可正常 `docker load`
2. ENTRYPOINT 为 null 或 `[]`
3. CMD 为 `["/bin/bash"]`
4. 默认启动可进入 bash（无参 `docker run`）
5. `docker run <img> bash -c '...'` 正常执行（回归测试）
6. libtvm.so 版本匹配
7. libtvm_allvisible.so 已移除
8. TVM 符号可见性（Registry 可注册）
9. relay.build 正常
10. xmnn API 可导入

### 实现

[verify_final_image.sh](../../../../../../external/xmhub/xmnn/tests/verify_final_image.sh)（88 行），从 tar.gz 加载镜像后逐项验证，输出 PASS/FAIL 报告。

---

## I5：导出脚本中 rm 清理操作应是非阻塞的

### 原则

清理操作（`rm`、`rmdir`）的本质是"尽力而为"的收尾工作，不应成为阻塞性操作。如果清理失败，用户可以在事后手动清理，但导出流程本身不应因此中断。

### 设计模式

```bash
# 模式 A：非致命清理
rm -f /tmp/*.whl 2>/dev/null || true

# 模式 B：延迟清理（由 root 执行）
docker exec $CONTAINER rm -f /tmp/*.whl

# 模式 C：清理放在 commit/save 之后
# 即使清理失败，镜像已导出，用户可以手动清理
```

### 适用场景

所有 shell 脚本中的清理操作，尤其是使用 `set -e` 的脚本。

<!-- changelog -->
- 2026-07-18 | feat | 初始版本：5 条洞察萃取