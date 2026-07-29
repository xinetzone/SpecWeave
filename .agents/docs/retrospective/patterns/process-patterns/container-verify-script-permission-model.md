---
id: "container-verify-script-permission-model"
title: "容器验证脚本的权限安全模型"
type: "process-pattern"
date: 2026-07-22
maturity: "L2"
maturity_note: "双案例验证（XMNN Runtime verify.sh + run_redlines.py）"
source: "sc-20260722-docker-template 方法论编排复盘"
related_patterns:
  - "../code-patterns/dockerfile-python-code-safe-embedding.md"
  - "./docker-entrypoint-two-step-reset.md"
tags: ["docker", "verify", "permission", "entrypoint", "conda", "gosu", "tempfile"]
validation_count: 2
reuse_count: 0
---

# 容器验证脚本的权限安全模型

## 触发场景

- 编写通过 `docker run -v` 挂载临时脚本的容器验证工具
- 验证的镜像包含 entrypoint（含 `gosu` 降权逻辑）或 conda 环境
- 需要以非 root 用户运行验证脚本，但容器内用户 UID 与宿主机不一致

**识别信号**：
- 验证脚本报告 `Permission denied`，但手动 `docker run` 进入容器执行相同命令正常
- 错误信息为 `python: can't open file '/tmp/test/xxx.py': [Errno 13] Permission denied`
- 容器 entrypoint 包含 `gosu ai` 或 `exec gosu` 降权逻辑
- 临时文件在宿主机默认权限为 `600`，属主为宿主机用户

**不适用场景**：
- 镜像无 entrypoint 或 entrypoint 不涉及用户切换（直接用 `docker run python` 即可）
- 验证脚本以 root 运行（可直接读取挂载文件）
- 使用 `docker exec` 而非 `docker run` 的验证方式

## 问题背景

### 权限不匹配的根因

Docker 的 `-v` 挂载保留宿主机文件的权限和属主。当验证脚本通过 `tempfile.NamedTemporaryFile` 创建临时文件时：

1. 文件默认权限为 `600`（仅属主可读写）
2. 文件属主为宿主机当前用户（如 UID=1000）
3. 容器 entrypoint 执行 `gosu ai` 降权后，容器内用户为 `ai`（UID 可能 ≠ 1000）
4. 容器内 `ai` 用户无权读取宿主机 UID=1000 的 `600` 权限文件

**实际案例**：
- XMNN Runtime 验证（2026-07-22）：首次 `verify.sh` 运行时，entrypoint 的 `gosu ai` 导致 R1-R3 全部误报失败（Permission denied），实际镜像的 ldd/import/TE compute 均正常
- run_redlines.py 首次运行时，`nobody`(uid=65534) 用户无法读取 `NamedTemporaryFile` 创建的临时文件，R4-1 失败

## 解决方案

### 原则：验证脚本必须显式管理临时文件权限

**核心代码模式**：

```python
import os, tempfile, shutil

def docker_py(image, script, user=None, timeout=60):
    """安全地在容器中执行 Python 脚本"""
    # 1. 创建专用临时目录（而非 NamedTemporaryFile）
    work_dir = tempfile.mkdtemp(prefix="dkrtest_")
    os.chmod(work_dir, 0o755)  # 确保目录可遍历

    # 2. 写入脚本并显式设置权限
    script_path = os.path.join(work_dir, "test.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)
    os.chmod(script_path, 0o644)  # 确保所有用户可读

    try:
        # 3. 绕过 entrypoint 降权逻辑
        cmd = ["docker", "run", "--rm", "--entrypoint", ""]
        if user:
            cmd.extend(["-u", user])
        cmd.extend(["-v", f"{work_dir}:/tmp/scripts:ro"])
        cmd.extend([image, python_cmd, "/tmp/scripts/test.py"])
        return subprocess.run(cmd, ...)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
```

**Shell 等效模式**：

```bash
TMPDIR=$(mktemp -d)
chmod 755 "$TMPDIR"
cat > "$TMPDIR/test.py" << 'PYEOF'
# ... 验证代码 ...
PYEOF
chmod 644 "$TMPDIR/test.py"

docker run --rm --entrypoint "" \
    -v "$TMPDIR:/tmp/test:ro" \
    "$IMAGE" python /tmp/test/test.py

rm -rf "$TMPDIR"
```

### 验证脚本设计原则

1. **区分错误类型**：基础设施错误（权限/路径）应报告为 SKIP，镜像质量错误（依赖/功能）应报告为 FAIL
2. **提供 `--entrypoint-override` 参数**：允许绕过 entrypoint 的降权逻辑
3. **提供 `--python` 参数**：允许指定 conda 环境中的 Python 路径
4. **提供 `--env` 参数**：允许注入必要的环境变量（如 `TVM_LIBRARY_PATH`）

## 反模式

1. **依赖 `NamedTemporaryFile` 的默认权限**——默认 `600` 权限在容器内非属主用户无法读取
2. **假设容器内用户 UID 与宿主机一致**——entrypoint 的 `gosu` 会改变 UID
3. **不区分"基础设施错误"和"镜像质量错误"**——导致 CI 门禁误报，阻塞流水线
4. **硬编码 `python` 路径**——conda 环境镜像的 `python` 可能不在 `PATH` 中

## 迁移验证

| 场景 | 验证方式 |
|------|---------|
| 任意 conda 环境镜像 | 使用 `--python /opt/conda/envs/<name>/bin/python` |
| 任意含 gosu entrypoint 的镜像 | 使用 `--entrypoint-override` 或 `--user root` |
| 任意非 root 用户镜像 | 使用 `--user <uid>:<gid>` 指定用户 |
| CI/CD 流水线 | 将验证脚本作为独立步骤，区分 EXIT_CODE 含义 |

## 相关模式

- [docker-entrypoint-two-step-reset](./docker-entrypoint-two-step-reset.md) — ENTRYPOINT 两步安全重置
- [dockerfile-python-code-safe-embedding](../code-patterns/dockerfile-python-code-safe-embedding.md) — Dockerfile 中 Python 代码嵌入