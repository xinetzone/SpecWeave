---
id: "dockerfile-python-code-safe-embedding"
domain: "code"
layer: "code"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "standard"
source: "sc-20260722-docker-template 方法论编排复盘"

[bindings]
rules = []
references = ["../../templates/docker-snippets/skeleton/Dockerfile", "../../templates/docker-snippets/skeleton/CONFIG.md"]
skills = []
---

# Dockerfile 中 Python 代码的安全嵌入模式

## 触发场景

- 需要在 Dockerfile 的 `RUN` 指令中嵌入多行 Python 验证代码
- 构建时执行 `python -c "..."` 进行安装后验证（ldd检查/import测试/功能测试）
- 编写 Dockerfile 模板，其中包含用户可替换的 Python 验证代码段

**识别信号**：
- Dockerfile 构建失败，错误信息为 `unknown instruction: import` 或 `unknown instruction: from`
- 错误行号指向 Python 代码的第二行（`from tvm import te` 被误解析为 `FROM` 指令）
- `RUN` 指令中使用 `python -c "` 后跟多行缩进代码块

**不适用场景**：
- Python 代码少于 5 行（直接用 `python -c "..."` 单行格式即可）
- 使用 `RUN python /path/to/script.py` 挂载脚本文件（不涉及内联代码）
- 使用 `COPY` + `RUN` 分离脚本的方式

## 问题现象

Dockerfile 解析器在 `RUN` 的 shell 形式中，`\` 续行后的内容仍被解析器检查语法。当 Python 代码块使用多行格式时：

```dockerfile
# 错误写法：多行 Python 代码直接嵌入
RUN set -eux; \
    echo "Verifying..."; \
    python -c "
import tvm
from tvm import te      # ← 此行被 Docker 解析器误判为 FROM 指令
import numpy as np
"
```

Docker 解析器将第二行的 `from` 误认为 `FROM` 指令，报错 `unknown instruction: import`。错误信息不直观，排查耗时。

**实际案例**：XMNN Runtime 镜像构建（2026-07-22），首次构建时 Dockerfile 第 99 行 TVM TE compute 验证代码包含多行 Python，导致构建失败。修复方法是将 15 行 Python 代码转为单行 `python -c "..."` 格式。

## 解决方案

### 原则：RUN 中永远不使用多行 Python 代码块

**方案一：单行格式（推荐，代码 ≤ 15 行）**

```dockerfile
RUN set -eux; \
    echo "Verifying..."; \
    python -c "import tvm; from tvm import te; import numpy as np; \
n = te.var('n'); A = te.placeholder((n,), name='A'); \
B = te.compute((n,), lambda i: A[i] * 2.0, name='B'); \
s = te.create_schedule(B.op); mod = tvm.build(s, [A, B], 'llvm'); \
print('OK')"
```

**方案二：写入临时脚本（推荐，代码 > 15 行）**

```dockerfile
RUN set -eux; \
    cat > /tmp/verify.py << 'PYEOF'
import tvm
from tvm import te
import numpy as np
# ... 任意多行代码 ...
PYEOF
    python /tmp/verify.py && rm /tmp/verify.py
```

**方案三：COPY + RUN 分离（推荐，代码可复用）**

```dockerfile
COPY docker/verify.py /tmp/verify.py
RUN python /tmp/verify.py && rm /tmp/verify.py
```

### 模板中的标注

在模板 CONFIG.md 中显式标注此约束，防止模板使用者踩坑：

```markdown
注意：`RUN` 中多行命令必须用 `\` 续行，Python 代码必须在同一行
或使用 `python -c "..."` 单行格式。禁止使用多行缩进 Python 代码块。
```

## 反模式

1. **在 `RUN` 中直接使用 `python -c "` 后跟多行缩进代码**——Docker 解析器会将 `from`/`import` 误判为指令
2. **使用 `python << 'EOF' ... EOF` heredoc**——部分 shell（如 Alpine 的 ash）不兼容
3. **在模板中不标注此约束**——模板使用者会重复踩坑，增加排查成本

## 迁移验证

| 场景 | 验证方式 |
|------|---------|
| 其他需要 Dockerfile 内嵌 Python 的项目 | 使用方案一/二/三均可 |
| 非 Python 语言（Node.js/Bash） | 同样适用：`node -e "..."` 单行格式，或 `cat > /tmp/script.js << 'EOF'` |
| CI/CD 流水线中的 Dockerfile | 将验证脚本独立为文件，COPY 进镜像执行 |

## 相关模式

- [docker-build-network-resilience](../process-patterns/docker-build-network-resilience.md) — Docker 构建时的网络韧性问题
- [compiled-wheel-runtime-image-build](../code-patterns/compiled-wheel-runtime-image-build.md) — C扩展wheel的运行时镜像构建