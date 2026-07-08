---
id: "script-generator-pattern"
source: ".agents/insights/notebook-nuitka-build-retrospective-20260704.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/architecture-patterns/script-generator-pattern.toml"
---
# 脚本生成器模式：Python 拼接 + Shell 执行的混合架构

## 模式概述

需要在不同环境（容器/远程/本地）执行复杂命令序列时，不在 Python 中一步步调用 subprocess，而是**动态生成完整的 shell 脚本再执行。Python 负责"组装逻辑，Shell 负责"执行流程"，各司其职。

## 问题现象

在 Python 中用 subprocess 一步步执行命令时，常见问题：

1. **调试困难**：Python 拼出来的命令串无法单独拿出来运行
2. **错误定位难**：不知道哪一步挂的，日志混在一起
3. **代码丑陋**：大量 subprocess.run 链式调用，可读性差
4. **幂等难做**：每步都要自己判断跳过条件
5. **环境隔离差**：Python 进程环境变量传递给 shell 容易出错

## 解决方案

用 Python 函数生成完整的 shell 脚本，再统一执行：

```python
def build_xxx_script(
    src_dir: str,
    output_dir: str,
    cache_dir: str,
    extra_args: str = "",
) -> str:
    """生成 xxx 步骤的 bash 脚本。"""
    return "\n".join([
        "set -e",                              # 失败即停
        "# 幂等检查：已存在则跳过",
        f"if ls {output_dir}/output.so >/dev/null 2>&1; then",
        f"  echo 'output already exists, skipping'",
        f"  exit 0",
        "fi",
        f"cd {src_dir}",                       # 切换工作目录
        f"./configure --prefix={output_dir} {extra_args}",  # 配置
        f"make -j$(nproc)",                    # 构建
        f"make install",                       # 安装
        f"echo 'Build complete'",                 # 验证输出
    ])
```

## 使用方式

```python
# 生成脚本
script = build_xxx_script(
    src_dir="/work/src",
    output_dir="/work/dist",
    cache_dir="/var/cache/xxx",
)

# 在容器内执行
container.exec(script)

# 或者写入文件调试
Path("debug_script.sh").write_text(script)
# $ bash debug_script.sh   ← 单独运行
```

## 模式优势

| 优势 | 说明 |
|------|------|
| **可调试性强** | 生成的脚本可以独立保存为 .sh 文件，手动运行复现 |
| **失败即停** | `set -e` 保证任何一步失败立即退出，不会继续执行 |
| **幂等简单** | 脚本开头用 `if ls ...; then exit 0; fi` 实现跳过 |
| **可读性好** | 生成逻辑是纯字符串拼接，一目了然 |
| **环境清晰** | shell 脚本里的环境变量、工作目录都是显式的 |
| **跨环境** | 同一份脚本可以在容器/远程/本地执行 |

## 多步骤编排

当有多个步骤时，可以用数组组织，统一执行：

```python
def run_pipeline(container, steps):
    """steps: [(label, script), ...]"""
    for label, script in steps:
        try:
            container.exec(script)
        except Exception as e:
            raise RuntimeError(f"{label} 失败:\n{e}") from e

# 使用
steps = [
    ("TVM", build_tvm_script(...)),
    ("VTA", build_vta_script(...)),
    ("XMNN", build_xmnn_script(...)),
    ("Wheel", package_wheel_script(...)),
]
run_pipeline(container, steps)
```

每步独立 label，失败时知道是哪一步挂的。

## 脚本头部标准结构

推荐每个生成的脚本都遵循统一结构：

```bash
set -e                                    # 1. 失败即停
if [ 已完成判断 ]; then exit 0; fi       # 2. 幂等跳过
cd /work/xxx                             # 3. 切换目录
export XXX=yyy                           # 4. 环境变量
command1                                 # 5. 实际命令
command2
...
echo "DONE"                              # 6. 完成标记
```

## 适用场景

- 容器内多步构建（编译+打包+测试）
- 远程服务器部署脚本生成
- CI/CD 流水线步骤编排
- 需要反复调试的命令序列
- 跨环境（本地/容器/远程）执行相同流程

## 注意事项

1. **路径转义**：Python f-string 拼接时注意 shell 特殊字符需要转义
2. **空格问题**：路径中有空格的路径要用引号包裹
3. **安全注入**：如果参数来自用户输入，要做合法性检查
4. **set -e 陷阱**：管道命令在某些情况下 set -e 不生效（如 if 条件中）
5. **调试技巧**：开发时加上 `set -x` 跟踪执行过程

## 正反例

### 正例

```python
# ✅ 脚本生成器，清晰可调试
def build_script(src, out):
    return "\n".join([
        "set -e",
        f"cd {src}",
        f"make -j$(nproc)",
        f"cp output {out}",
    ])
```

### 反例

```python
# ❌ Python 中一步步 subprocess，丑陋难调试
def build(src, out):
    subprocess.run(["cd", src], check=True)  # cd 没用，子进程不影响父进程
    subprocess.run(["make", "-j4"], check=True, cwd=src)
    subprocess.run(["cp", "output", out], check=True)
    # 每步都要 try/except，代码臃肿
    # 出问题时没法单独拿出命令行跑
```

## 与其他模式的关系

- **Docker 容器会话 RAII（docker-container-session-raii）**：
  脚本生成器负责"生成什么"，容器会话负责"在哪里执行"，两者配合使用

- **生命周期三阶段（lifecycle-protocol-three-phase）**：
  脚本生成器是"执行"层面的模式，生命周期是"流程"层面的模式

- **三层解析生成器（three-layer-parser-generator）**：
  脚本生成器是更简单的一层版本，适用于 shell 场景
