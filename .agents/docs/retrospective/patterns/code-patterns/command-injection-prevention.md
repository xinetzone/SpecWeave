---
id: "command-injection-prevention"
source: "../../../../../.agents/insights/infrastructure/dev-env-adversarial-review-20260709/code-patterns.md"
domain: "code"
layer: "code"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "standard"

[bindings]
rules = []
references = []
skills = []
---
# 命令构造防注入：列表形式优先，shlex.quote 兜底

## 模式概述

用户输入拼接到 shell 命令会导致命令注入漏洞。优先使用 `subprocess.run(cmd_list)` 列表形式（不经 shell 解释）；必须经过 shell 时，对每个嵌入变量单独使用 `shlex.quote()` 转义。

## 问题现象

用户输入拼接到 shell 命令字符串中导致命令注入：
- 容器名、路径、用户名等参数直接拼接到 docker/ssh 命令
- 攻击者通过特殊字符（`;`、`|`、`$()`、`&&`、空格等）注入任意命令
- `shell=True` 是高危标志，shell 会解释其中的所有特殊字符——这不是"安全建议"，是 shell 的**设计功能**

## 解决方案

```python
import shlex
import subprocess

# ❌ 错误做法：shell=True+字符串拼接
subprocess.run(f"docker exec {name} mkdir -p {path}", shell=True)

# ✅ 正确做法：列表形式（不经shell解释）
subprocess.run(
    ["docker", "exec", name, "mkdir", "-p", str(path)],
    check=True,
)

# ✅ 必须经过shell时（如bash -c），对每个嵌入变量单独quote
safe_name = shlex.quote(name)
safe_path = shlex.quote(str(path))
subprocess.run(
    f"docker exec {safe_name} bash -c 'mkdir -p {safe_path}'",
    shell=True,
    check=True,
)
```

## 命令构造安全层级

| 层级 | 方式 | 安全性 | 说明 |
|------|------|--------|------|
| L1（最佳） | 列表形式 `subprocess.run([...])` | ✅ 安全 | 不经 shell 解释，参数直接传递给 execve |
| L2（可接受） | `shell=True` + 所有嵌入变量 `shlex.quote()` | ⚠️ 需谨慎 | 每个外部输入必须单独 quote |
| L3（危险） | `shell=True` + f-string/字符串拼接 | ❌ 注入漏洞 | 禁止用于包含任何外部输入的命令 |

## 关键检查点

1. **优先使用列表形式** `subprocess.run(cmd_list)` 不经 shell
2. **必须用 shell 时**，每个嵌入变量都要 `shlex.quote()`
3. **永远不要把用户输入直接拼接到 shell 命令字符串中**
4. **设置 `check=True`**：命令失败时抛出异常而非静默继续

## shlex.quote 正确用法

```python
import shlex

# ✅ 正确：每个变量单独quote
safe_name = shlex.quote(name)
safe_path = shlex.quote(str(path))
cmd = f"docker exec {safe_name} bash -c 'mkdir -p {safe_path}'"

# ❌ 错误：整体quote（嵌套shell时引号会冲突）
cmd = f"docker exec {shlex.quote(f'bash -c mkdir -p {path}')}"

# ❌ 错误：部分quote
cmd = f"docker exec {name} bash -c {shlex.quote(f'mkdir -p {path}')}"  # name未quote!
```

## 正反例

### 正例

```python
# ✅ 列表形式：最安全
subprocess.run(
    ["docker", "exec", container_name, "mkdir", "-p", str(target_path)],
    check=True,
    capture_output=True,
    text=True,
)

# ✅ 需要shell管道时：用subprocess.PIPE连接
p1 = subprocess.Popen(["ls", "-la"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["grep", ".py"], stdin=p1.stdout, stdout=subprocess.PIPE, text=True)
p1.stdout.close()
output = p2.communicate()[0]
```

### 反例

```python
# ❌ 直接拼接：name="container; rm -rf /" 会执行危险命令
subprocess.run(f"docker exec {name} ls", shell=True)

# ❌ format拼接：同样危险
subprocess.run("docker exec {} mkdir -p {}".format(name, path), shell=True)

# ❌ 列表形式但仍用shell=True：列表第一个元素作为命令，剩余作为$0,$1...，仍有注入风险
subprocess.run(["docker exec {} bash -c 'mkdir -p {}'".format(name, path)], shell=True)
```

## 适用场景

- 调用外部命令（docker、ssh、git、cmake 等）
- 接受用户输入的参数（容器名、路径、文件名等）
- 构建系统、CI/CD 脚本
- 任何使用 subprocess 且参数包含外部输入的场景

## 注意事项

1. **`check=True` 默认添加**：不添加时命令失败不会抛出异常，可能导致后续操作在错误状态下继续
2. **`capture_output=True` + `text=True`**：Python 3.7+ 可用，替代 `stdout=PIPE, stderr=PIPE` 并自动解码
3. **路径参数转字符串**：`pathlib.Path` 对象传给列表形式时，用 `str(path)` 或直接传（subprocess 接受 PathLike）
4. **避免 shell 特性**：如果需要管道、通配符、重定向等 shell 特性，优先用 Python 代码实现，而非 `shell=True`
5. **Docker exec 特殊注意**：`docker exec container bash -c 'command'` 中的内层 bash -c 是新的 shell 层，传入的变量必须在这层也被正确 quote
