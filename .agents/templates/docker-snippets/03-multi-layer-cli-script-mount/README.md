# 模式3：多层命令脚本挂载（Multi-Layer-CLI-Script-Mount）

> **核心原则**：超过2层CLI嵌套时，将验证/执行逻辑写入脚本文件，通过挂载/COPY传入容器执行，禁止使用内联字符串+转义。
>
> **经验法则**：引号嵌套层数 = N层shell + 1层目标语言。N+1 > 3时必须用脚本文件挂载。
>
> **源洞察**：PowerShell→WSL→docker run→bash -c→python -c 共5层嵌套，3次因引号转义失败，每次浪费5+分钟调试

---

## 嵌套层数判定表

| 场景 | 层数 | 策略 |
|------|:----:|------|
| bash → python -c "print('ok')" | 2 | ✅ 内联可用 |
| bash → docker run → python -c "..." | 3 | ⚠️ 可用但脆弱，推荐脚本 |
| PowerShell → WSL → docker → python -c "..." | 4 | ❌ 必须脚本挂载 |
| PowerShell → WSL → docker → bash -c → python -c "..." | 5 | ❌ 必须脚本挂载 |
| CI (GitHub Actions) → docker → bash → python | 4 | ❌ 必须脚本挂载 |

---

## 片段A：PowerShell/WSL 环境下的容器验证模板

```powershell
# ============================================================
# Multi-Layer CLI Script Mount Pattern
# 场景：Windows+WSL+Docker 多层嵌套环境中的容器验证
# ============================================================

# ---- 配置区 ----
$IMAGE_NAME = "{{IMAGE_NAME}}"       # 如 "xmnn-runtime:1.2.2"
$CONTAINER_WORKSPACE = "/workspace"

# ---- Step 1: 生成临时Python验证脚本 ----
$verifyScript = Join-Path $env:TEMP "docker_verify_$(Get-Random).py"
@'
import sys
import importlib

def verify():
    errors = []

    # 1. 核心模块导入
    modules = {{MODULE_LIST}}  # 如 ['tvm', 'vta', 'xmnn']
    for mod in modules:
        try:
            m = importlib.import_module(mod)
            print(f"  [OK] import {mod} -> {getattr(m, '__file__', 'built-in')}")
        except ImportError as e:
            errors.append(f"import {mod} failed: {e}")
            print(f"  [FAIL] import {mod}: {e}", file=sys.stderr)

    # 2. 功能验证（TE计算）
    try:
        import tvm
        from tvm import te
        import numpy as np
        n = te.var("n")
        A = te.placeholder((n,), name="A")
        B = te.compute((n,), lambda i: A[i] * 2.0, name="B")
        s = te.create_schedule(B.op)
        mod = tvm.build(s, [A, B], "llvm", name="double_array")
        ctx = tvm.cpu(0)
        a = tvm.nd.array(np.array([1.0, 2.0, 3.0], dtype="float32"), ctx)
        b = tvm.nd.array(np.zeros(3, dtype="float32"), ctx)
        mod(a, b)
        result = b.numpy().tolist()
        assert result == [2.0, 4.0, 6.0], f"Expected [2,4,6], got {result}"
        print("  [OK] TVM TE compute (double_array) -> result correct")
    except Exception as e:
        errors.append(f"TVM compute failed: {e}")
        print(f"  [FAIL] TVM compute: {e}", file=sys.stderr)

    # 3. 包版本验证（使用标准API，不用__version__）
    from importlib.metadata import version, PackageNotFoundError
    for pkg in {{PYPI_PACKAGES}}:  # 如 ['numpy', 'scipy', 'xmnn']
        try:
            v = version(pkg)
            print(f"  [OK] {pkg}=={v}")
        except PackageNotFoundError:
            errors.append(f"Package {pkg} not installed")
            print(f"  [FAIL] {pkg}: NOT INSTALLED", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("\nAll verifications PASSED")

verify()
'@ | Set-Content -Path $verifyScript -Encoding UTF8

# ---- Step 2: 通过WSL路径转换挂载脚本到容器执行 ----
# 将Windows路径转换为WSL路径（如 C:\Users\... → /mnt/c/Users/...）
$wslScriptPath = wsl -e wslpath "$verifyScript"

try {
    # Step 3: docker run 挂载脚本文件执行（而非内联 -c "..."）
    wsl -e bash -c @"
docker run --rm \
    -v "${wslScriptPath}:/tmp/verify.py:ro" \
    -v "`$(pwd):${CONTAINER_WORKSPACE}" \
    ${IMAGE_NAME} \
    python /tmp/verify.py
"@
    $exitCode = $LASTEXITCODE
}
finally {
    # Step 4: 清理临时文件
    Remove-Item $verifyScript -Force -ErrorAction SilentlyContinue
}

if ($exitCode -ne 0) {
    Write-Error "Verification failed with exit code $exitCode"
    exit $exitCode
}
Write-Host "`nVerification complete!"
```

### 占位符替换表

| 占位符 | 替换为 | XMNN项目示例 |
|--------|--------|-------------|
| `{{IMAGE_NAME}}` | 镜像名:tag | xmnn-runtime:1.2.2 |
| `{{MODULE_LIST}}` | 要import的模块列表 | `['tvm', 'vta', 'xmnn']` |
| `{{PYPI_PACKAGES}}` | 要验证版本的PyPI包名 | `['numpy', 'scipy', 'xmnn']` |

---

## 片段B：Bash/Linux 环境下的通用函数

```bash
#!/bin/bash
# docker_exec_script.sh — 通过挂载脚本文件在Docker容器中执行
# 用法: docker_exec_script <image> <script_file> [docker_args...]
set -euo pipefail

docker_exec_script() {
    local image="$1"
    local script="$2"
    shift 2

    if [ ! -f "$script" ]; then
        echo "Error: script file not found: $script" >&2
        return 1
    fi

    local script_name
    script_name=$(basename "$script")
    local ext="${script_name##*.}"

    local cmd=""
    case "$ext" in
        py)      cmd="python /tmp/scripts/$script_name" ;;
        sh|bash) cmd="bash /tmp/scripts/$script_name" ;;
        *)       cmd="/tmp/scripts/$script_name" ;;
    esac

    docker run --rm \
        -v "$(realpath "$script"):/tmp/scripts/$script_name:ro" \
        "$@" \
        "$image" \
        $cmd
}

# ---- 使用示例 ----
# # 1. Python验证脚本
# docker_exec_script xmnn-runtime:1.2.2 ./verify.py
#
# # 2. 带额外挂载
# docker_exec_script xmnn-runtime:1.2.2 ./verify.py \
#     -v "$(pwd)/models:/workspace/models"
#
# # 3. Shell脚本
# docker_exec_script xmnn-runtime:1.2.2 ./test_env.sh
```

---

## 片段C：快速生成临时验证脚本的辅助函数

```bash
#!/bin/bash
# with_docker_verify.sh — 内联创建验证脚本并在容器中执行
# 适用于一次性快速验证，不创建持久脚本文件
set -euo pipefail

with_docker_python() {
    local image="$1"
    shift
    local script_body="$1"
    shift

    local tmpdir
    tmpdir=$(mktemp -d)
    trap "rm -rf $tmpdir" EXIT

    cat > "$tmpdir/verify.py" << 'PYEOF'
import sys
PYEOF

    # 将script_body追加到文件
    echo "$script_body" >> "$tmpdir/verify.py"

    docker run --rm \
        -v "$tmpdir/verify.py:/tmp/verify.py:ro" \
        "$@" \
        "$image" \
        python /tmp/verify.py
}

# ---- 使用示例 ----
# with_docker_python xmnn-runtime:1.2.2 '
# import tvm
# print("tvm version:", tvm.__version__ if hasattr(tvm, "__version__") else "N/A")
# '
```

---

## 片段D：CI/GitHub Actions 中的正确做法

```yaml
# .github/workflows/docker-verify.yml
# ❌ 错误做法：run中用多层嵌套引号
# - name: Verify (WRONG)
#   run: |
#     docker run --rm myimage python -c "import tvm; print('OK')"
#     # 如果需要更复杂的验证，引号嵌套会爆炸

# ✅ 正确做法：先写脚本文件，挂载执行
- name: Create verify script
  run: |
    cat > /tmp/verify.py << 'PYEOF'
    import sys
    import importlib
    # ... 验证逻辑（无引号转义问题）
    modules = ['tvm', 'vta', 'xmnn']
    for mod in modules:
        m = importlib.import_module(mod)
        print(f"OK: {mod}")
    print("All imports passed")
    PYEOF

- name: Run verification in container
  run: |
    docker run --rm \
      -v /tmp/verify.py:/tmp/verify.py:ro \
      ${{ env.IMAGE_NAME }} \
      python /tmp/verify.py
```

---

## 片段E：快速冒烟测试一行命令（2层嵌套可用，不超过3层）

```bash
# 简单冒烟测试：2层嵌套（bash→docker→python），可内联但需注意引号
# 规则：python代码中只用单引号，外层用双引号
docker run --rm xmnn-runtime:1.2.2 python -c "
import tvm; print('tvm:', tvm.__file__ if hasattr(tvm, '__file__') else 'builtin')
from importlib.metadata import version; print('xmnn:', version('xmnn'))
"

# 3层及以上嵌套必须使用脚本文件
# ❌ 失败案例（PowerShell→wsl→docker→python，4层）:
# wsl -e docker run --rm xmnn-runtime:1.2.2 python -c "import tvm; print('OK')"
# PowerShell和wsl都会对引号做额外解析，单双引号在多层传递中语义丢失
```

---

## 反模式速查（Do NOT）

| ❌ 反模式 | 嵌套层数 | 失败模式 | ✅ 正确做法 |
|-----------|:--------:|---------|-----------|
| `wsl docker run img python -c "import x; print('a b')"` | 4层 | PowerShell和wsl各自解析引号，字符串被截断 | 脚本挂载 |
| `docker run img bash -c "python -c 'import x'"` | 3层 | 内层单引号与外层单引号冲突 | 脚本挂载 |
| 用`\"`转义多层双引号 | 任意>2层 | 每层shell解析方式不同，转义在某层失效 | 脚本挂载 |
| heredoc嵌套（`bash -c "cat <<EOF ... EOF"`） | 3层+ | heredoc终止符被某层shell提前匹配 | 脚本挂载 |
| 在Dockerfile RUN中写超过5行的python -c | 2层但复杂 | 可读性差、调试困难、`\n`转义 | COPY .py文件后执行 |
