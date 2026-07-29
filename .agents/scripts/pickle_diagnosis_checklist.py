#!/usr/bin/env python3
"""
DataLoader Pickle 序列化问题诊断检查清单脚本

基于诊断 SOP 文档：.agents/docs/knowledge/best-practices/dataloader-pickle-diagnosis-sop.md

功能：
1. 诊断模式：运行完整的5步诊断流程
2. 检测模式：检测代码中是否存在不可序列化模式
3. 验证模式：验证对象是否可序列化
4. 检查清单模式：运行代码审查检查项
5. 跨模式验证：测试fork/forkserver/spawn三种启动方式
"""

import os
import sys
import pickle
import subprocess
import multiprocessing
from pathlib import Path
from typing import Any, Callable, List, Optional

try:
    import typer
    from typing_extensions import Annotated
except ImportError:
    print("错误：需要安装 typer 和 typing-extensions")
    print("请运行: pip install typer typing-extensions")
    sys.exit(1)

app = typer.Typer(
    name="pickle-diagnosis",
    help="DataLoader Pickle 序列化问题诊断检查清单脚本",
    no_args_is_help=True,
)


def test_pickle(obj: Any, name: str = "object") -> bool:
    """测试对象是否可序列化"""
    try:
        pickle.dumps(obj)
        print(f"✅ {name} 可序列化")
        return True
    except Exception as e:
        print(f"❌ {name} 序列化失败: {type(e).__name__}: {e}")
        return False


def print_step(title: str, step_num: int = None):
    """打印步骤标题"""
    if step_num:
        print(f"\n{'='*60}")
        print(f"Step {step_num}: {title}")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")


def print_checkbox(item: str, checked: bool = False):
    """打印检查项"""
    status = "✅" if checked else "⬜"
    print(f"  {status} {item}")


@app.command("diagnose", help="运行完整的5步诊断流程")
def diagnose():
    """运行完整的5步诊断流程"""
    print_step("5步诊断流程", 0)

    print_step("Step 1: 复现问题", 1)
    print_checkbox("在 spawn 模式下复现（最快暴露序列化问题）", False)
    print_checkbox("设置 num_workers=2（单进程不会触发序列化）", False)
    print_checkbox("启用调试日志 (XMN_DEBUG_PICKLE=1)", False)
    print_checkbox("记录完整错误堆栈，找到第一个 PicklingError", False)

    print_step("Step 2: 定位不可序列化对象", 2)
    print_checkbox("使用 pickle.dumps() 逐级测试可疑对象", False)
    print_checkbox("如果整体对象失败，逐组件拆分测试", False)
    print_checkbox("确认是哪个具体类/函数/对象导致失败", False)

    print_step("Step 3: 识别不可序列化模式", 3)
    patterns = [
        "Lambda 函数",
        "闭包（嵌套函数捕获局部变量）",
        "局部类定义（函数内部的 class）",
        "打开的文件句柄 / IO 对象",
        "网络连接 / 数据库连接 / Socket",
        "CUDA 张量 / GPU 资源",
    ]
    for i, pattern in enumerate(patterns, 1):
        print_checkbox(f"3.{i} {pattern}", False)

    print_step("Step 4: 应用修复方案", 4)
    print_checkbox("方案 A: 模块级命名类（最推荐）", False)
    print_checkbox("方案 B: 模块级命名函数", False)
    print_checkbox("方案 C: functools.partial（谨慎使用）", False)

    print_step("Step 5: 验证修复", 5)
    print_checkbox("单元测试：pickle.dumps() + pickle.loads()", False)
    print_checkbox("集成测试：DataLoader 以 num_workers=2 完整迭代", False)
    print_checkbox("跨模式测试：fork / forkserver / spawn", False)
    print_checkbox("功能等价性测试：修复前后输出完全一致", False)
    print_checkbox("日志验证：XMN_DEBUG_PICKLE=1", False)

    print("\n提示：请根据实际情况手动勾选上述检查项")


@app.command("detect", help="检测代码中是否存在不可序列化模式")
def detect(
    path: Annotated[str, typer.Argument(help="要检测的目录或文件路径")] = ".",
):
    """检测代码中是否存在不可序列化模式"""
    target_path = Path(path)
    if not target_path.exists():
        print(f"❌ 路径不存在: {path}")
        sys.exit(1)

    print_step(f"检测路径: {target_path.resolve()}")

    if target_path.is_file():
        files = [target_path]
    else:
        files = list(target_path.rglob("*.py"))

    print(f"\n发现 {len(files)} 个 Python 文件")

    issues = []

    for pyfile in files:
        try:
            content = pyfile.read_text(encoding="utf-8")

            if "transforms.Lambda(lambda" in content:
                issues.append((pyfile, "Lambda 函数", "transforms.Lambda(lambda"))

            if "lambda x:" in content or "lambda " in content:
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "lambda " in line and "def " not in line:
                        issues.append((pyfile, "Lambda 函数", f"第{i}行: {line.strip()}"))

            if "class " in content:
                lines = content.split("\n")
                indent_level = 0
                for i, line in enumerate(lines, 1):
                    stripped = line.lstrip()
                    if stripped.startswith("def "):
                        indent_level = len(line) - len(stripped)
                    elif stripped.startswith("class ") and len(line) - len(stripped) > indent_level:
                        issues.append((pyfile, "局部类定义", f"第{i}行: {line.strip()}"))

            if "open(" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "open(" in line and "__init__" in content:
                        issues.append((pyfile, "打开的文件句柄", f"第{i}行: {line.strip()}"))

            if "socket.socket(" in content or "requests.Session(" in content:
                issues.append((pyfile, "网络连接", "包含 socket 或 requests.Session"))

            if ".cuda()" in content or ".to('cuda')" in content or ".to(\"cuda\")" in content:
                issues.append((pyfile, "CUDA 张量", "包含 CUDA 操作"))

        except Exception as e:
            print(f"⚠️ 读取文件失败 {pyfile}: {e}")

    if issues:
        print("\n❌ 发现不可序列化模式：")
        for file, pattern, detail in issues:
            rel_path = file.relative_to(target_path) if target_path.is_dir() else file.name
            print(f"  - [{pattern}] {rel_path}: {detail}")
    else:
        print("\n✅ 未发现不可序列化模式")


@app.command("validate", help="验证对象是否可序列化")
def validate(
    module: Annotated[str, typer.Argument(help="要导入的模块路径")],
    object_name: Annotated[str, typer.Argument(help="要验证的对象名称")],
):
    """验证对象是否可序列化"""
    print_step(f"验证对象: {module}.{object_name}")

    try:
        sys.path.insert(0, os.getcwd())
        mod = __import__(module.replace("/", ".").replace(".py", ""), fromlist=[object_name])
        obj = getattr(mod, object_name)

        print(f"\n正在测试 {object_name} 的序列化...")
        success = test_pickle(obj, object_name)

        if success:
            print("\n✅ 对象可序列化")
        else:
            print("\n❌ 对象不可序列化")
            sys.exit(1)

    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        sys.exit(1)
    except AttributeError as e:
        print(f"❌ 对象不存在: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 验证失败: {type(e).__name__}: {e}")
        sys.exit(1)


@app.command("checklist", help="运行代码审查检查项")
def checklist(
    path: Annotated[str, typer.Argument(help="要检查的目录或文件路径")] = ".",
):
    """运行代码审查检查项"""
    target_path = Path(path)
    if not target_path.exists():
        print(f"❌ 路径不存在: {path}")
        sys.exit(1)

    print_step(f"代码审查检查项: {target_path.resolve()}")

    if target_path.is_file():
        files = [target_path]
    else:
        files = list(target_path.rglob("*.py"))

    results = []

    for pyfile in files:
        try:
            content = pyfile.read_text(encoding="utf-8")
            rel_path = pyfile.relative_to(target_path) if target_path.is_dir() else pyfile.name

            checks = []

            if "transforms.Lambda(lambda" in content:
                checks.append("❌ 存在 transforms.Lambda(lambda ...) 调用")
            else:
                checks.append("✅ 无 transforms.Lambda(lambda) 调用")

            if "__init__" in content:
                if "open(" in content:
                    checks.append("⚠️ __init__ 中可能有打开文件操作")
                else:
                    checks.append("✅ __init__ 中无打开文件操作")

                if ".cuda()" in content or ".to('cuda')" in content:
                    checks.append("⚠️ __init__ 中可能有 CUDA 张量创建")
                else:
                    checks.append("✅ __init__ 中无 CUDA 张量创建")

            if "lambda " in content:
                checks.append("⚠️ 代码中存在 lambda 函数")

            if "print(" in content and "logging" not in content:
                checks.append("⚠️ 使用 print 而非 logging")

            results.append((rel_path, checks))

        except Exception as e:
            print(f"⚠️ 读取文件失败 {pyfile}: {e}")

    print("\n检查结果:")
    for file_path, checks in results:
        print(f"\n📄 {file_path}")
        for check in checks:
            print(f"  {check}")


@app.command("cross-validate", help="跨启动模式验证")
def cross_validate(
    script: Annotated[str, typer.Argument(help="要测试的脚本路径")],
):
    """跨启动模式验证（fork/forkserver/spawn）"""
    script_path = Path(script)
    if not script_path.exists():
        print(f"❌ 脚本不存在: {script}")
        sys.exit(1)

    print_step(f"跨启动模式验证: {script_path.resolve()}")

    start_methods = ["fork", "forkserver", "spawn"]
    results = []

    for method in start_methods:
        print(f"\n🔧 测试 {method} 模式...")

        env = os.environ.copy()
        env["XMN_MP_START_METHOD"] = method
        env["XMN_DEBUG_PICKLE"] = "1"

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print(f"✅ {method} 模式: 成功")
                results.append((method, "SUCCESS", result.stdout.strip()[:200] if result.stdout else ""))
            else:
                print(f"❌ {method} 模式: 失败 (退出码: {result.returncode})")
                error_msg = result.stderr.strip()[:300] if result.stderr else result.stdout.strip()[:300]
                results.append((method, "FAILED", error_msg))

        except subprocess.TimeoutExpired:
            print(f"⏱️ {method} 模式: 超时")
            results.append((method, "TIMEOUT", "脚本执行超时"))
        except Exception as e:
            print(f"❌ {method} 模式: 异常 - {e}")
            results.append((method, "EXCEPTION", str(e)))

    print("\n" + "=" * 60)
    print("跨启动模式验证结果")
    print("=" * 60)
    print(f"{'模式':<12} {'状态':<10} {'备注'}")
    print("-" * 60)
    for method, status, note in results:
        print(f"{method:<12} {status:<10} {note}")


@app.command("env-check", help="检查当前环境配置")
def env_check():
    """检查当前环境配置"""
    print_step("环境配置检查")

    print("\n📊 Python 版本:")
    print(f"  {sys.version}")

    print("\n🔧 multiprocessing 配置:")
    try:
        ctx = multiprocessing.get_context()
        print(f"  当前启动方式: {ctx.get_start_method()}")
        print(f"  可用启动方式: {ctx.get_all_start_methods()}")
    except Exception as e:
        print(f"  获取配置失败: {e}")

    print("\n🌐 环境变量:")
    env_vars = ["XMN_MP_START_METHOD", "XMN_DEBUG_PICKLE", "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"]
    for var in env_vars:
        value = os.environ.get(var, "未设置")
        print(f"  {var}: {value}")

    print("\n📦 关键依赖:")
    try:
        import torch
        print(f"  torch: {torch.__version__}")
    except ImportError:
        print("  torch: 未安装")

    try:
        import numpy as np
        print(f"  numpy: {np.__version__}")
    except ImportError:
        print("  numpy: 未安装")


@app.command("quick-test", help="快速测试脚本的序列化兼容性")
def quick_test(
    script: Annotated[str, typer.Argument(help="要测试的脚本路径")],
):
    """快速测试脚本的序列化兼容性（使用 spawn 模式）"""
    script_path = Path(script)
    if not script_path.exists():
        print(f"❌ 脚本不存在: {script}")
        sys.exit(1)

    print_step(f"快速序列化测试: {script_path.resolve()}")
    print("使用 spawn 模式（最严格的序列化测试）")

    test_script = f"""
import multiprocessing
import os

os.environ['XMN_DEBUG_PICKLE'] = '1'
multiprocessing.set_start_method('spawn', force=True)

exec(open('{script_path.resolve()}').read())
"""

    try:
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            print("\n✅ spawn 模式测试通过")
            if result.stdout:
                print("输出:")
                print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        else:
            print("\n❌ spawn 模式测试失败")
            if result.stderr:
                print("错误信息:")
                print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
            sys.exit(1)

    except subprocess.TimeoutExpired:
        print("\n⏱️ 测试超时")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()