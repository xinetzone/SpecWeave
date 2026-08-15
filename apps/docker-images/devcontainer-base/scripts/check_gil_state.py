#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jupyter kernel / 任意 Python 进程的 GIL 状态诊断器。

检测当前解释器是否因加载了未声明 free-threading 支持的 C 扩展
（如 _brotli 等 jupyter 生态间接依赖）而被迫启用了 GIL，
并通过「金丝雀子进程」逐个审计已加载的 C 扩展，定位肇事模块。

背景（PEP 703）：free-threading 构建中，C 扩展需在模块定义的
Py_mod_gil slot 里声明自己可安全无 GIL 运行。import 未声明的
模块时，解释器会发出 RuntimeWarning 并拉起 GIL（进程级一次性
保险丝，之后无法关闭）。

用法：
    python check_gil_state.py                  # 诊断当前进程
    %run scripts/check_gil_state.py -v         # 在 Jupyter kernel 里诊断
    python check_gil_state.py --pre brotli     # 先 import 指定模块再诊断（复现 jupyter 状态）
    python check_gil_state.py --audit numpy,brotli   # 只审计指定模块

退出码：0 = GIL 禁用（健康）；1 = GIL 被迫启用；2 = 非 free-threading 构建
"""

from __future__ import annotations

import argparse
import importlib
import os
import subprocess
import sys
import sysconfig

# 审计子进程里默认跳过的重量级模块（避免 GPU/图形栈初始化副作用与超时）
DEFAULT_SKIP = {
    "torch", "torchvision", "tensorflow", "cv2", "cupy",
    "matplotlib", "matplotlib.pyplot", "PIL", "IPython",
}

CANARY_CODE = (
    "import sys, importlib\n"
    "try:\n"
    "    importlib.import_module(sys.argv[1])\n"
    "    print(1 if sys._is_gil_enabled() else 0)\n"
    "except ImportError:\n"
    "    print('skip')\n"
)


def is_free_threading_build() -> bool:
    """当前解释器是否为 free-threading（nogil）构建。"""
    return bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


def gil_enabled() -> bool:
    return sys._is_gil_enabled()


def loaded_c_extensions() -> dict[str, str]:
    """收集当前进程已加载的 C 扩展模块（name -> 文件路径）。"""
    exts: dict[str, str] = {}
    suffixes = importlib.machinery.EXTENSION_SUFFIXES
    for name, mod in list(sys.modules.items()):
        if "." in name:  # 只审计顶层包名，子模块归属父包
            continue
        path = getattr(mod, "__file__", None) or ""
        if path and any(path.endswith(s) for s in suffixes):
            exts[name] = path
    return exts


def canary_audit(modules: list[str], skip: set[str], timeout: float = 12.0
                 ) -> tuple[list[str], list[str], list[str]]:
    """金丝雀审计：在干净子进程（GIL 初始禁用）里逐个 import 模块，
    观察是否触发 GIL 拉起。返回 (肇事模块, 安全模块, 跳过/失败模块)。"""
    culprits, safe, skipped = [], [], []
    for name in modules:
        if name in skip or name.split(".")[0] in skip:
            skipped.append(name)
            continue
        try:
            # 注意：金丝雀子进程必须以默认行为运行（不设 PYTHON_GIL=0）——
            # 否则会屏蔽"未声明模块拉起 GIL"这一待检测机制本身
            env = {k: v for k, v in os.environ.items() if k != "PYTHON_GIL"}
            r = subprocess.run(
                [sys.executable, "-c", CANARY_CODE, name],
                capture_output=True, text=True, timeout=timeout, env=env,
            )
            out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        except subprocess.TimeoutExpired:
            skipped.append(name)
            continue
        if out == "1":
            culprits.append(name)
        elif out == "0":
            safe.append(name)
        else:
            skipped.append(name)
    return culprits, safe, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description="GIL 状态诊断器（free-threading Python）")
    ap.add_argument("-v", "--verbose", action="store_true", help="列出所有已加载 C 扩展")
    ap.add_argument("--pre", default="", help="诊断前先 import 的模块（逗号分隔），用于复现 kernel 状态")
    ap.add_argument("--audit", default="", help="只审计指定模块（逗号分隔）；默认审计全部已加载 C 扩展")
    ap.add_argument("--no-audit", action="store_true", help="只报状态，不做子进程审计")
    args = ap.parse_args()

    print("=" * 62)
    print("GIL 状态诊断")
    print("=" * 62)
    print(f"Python        : {sys.version.split()[0]} ({sys.executable})")
    print(f"构建          : {'free-threading (Py_GIL_DISABLED=1)' if is_free_threading_build() else '常规 GIL 构建'}")
    if not is_free_threading_build():
        print("\n[!] 非 free-threading 构建，本工具的 nogil 诊断不适用。")
        return 2

    if args.pre:
        for m in [x.strip() for x in args.pre.split(",") if x.strip()]:
            importlib.import_module(m)
            print(f"[pre] 已导入: {m}")

    enabled = gil_enabled()
    print(f"GIL 当前状态  : {'已启用' if enabled else '禁用（nogil 生效）'}")

    exts = loaded_c_extensions()
    if args.verbose:
        print(f"\n已加载 C 扩展（{len(exts)} 个）：")
        for name, path in sorted(exts.items()):
            print(f"  - {name:24s} {path}")

    if not enabled:
        print("\n[OK] GIL 处于禁用状态 —— 多线程 CPU 密集任务可并行扩展。")
        return 0

    # ---- GIL 已被拉起：定位肇事模块 ----
    print("\n[!] GIL 已被启用 —— 本进程多线程并行已退化为 ~1x。")
    print("    开始金丝雀审计（每个 C 扩展在干净子进程中重新 import）...")
    if args.audit:
        modules = [x.strip() for x in args.audit.split(",") if x.strip()]
    else:
        modules = sorted(exts)

    culprits, safe, skipped = canary_audit(modules, DEFAULT_SKIP)

    if culprits:
        print(f"\n肇事模块（会触发 GIL 拉起，共 {len(culprits)} 个）：")
        for name in culprits:
            print(f"  [X] {name}")
    else:
        print("\n未在已加载 C 扩展中定位到肇事模块（可能已卸载或来自 .pth 钩子）。")

    if safe:
        print(f"\n已验证安全（声明了 free-threading 支持，{len(safe)} 个）：")
        print("  " + ", ".join(safe))
    if skipped:
        print(f"\n跳过（超时/缺依赖/黑名单，{len(skipped)} 个）：{', '.join(skipped)}")

    print("\n建议：")
    print("  1. CPU 密集任务移到独立子进程执行（spawn），保持本 kernel 仅做交互/展示")
    print("  2. 剔除或替换肇事模块（等待上游发布声明 Py_mod_gil 的版本）")
    print("  3. 重启 kernel 后先跑本脚本确认状态，再决定工作流")
    return 1


if __name__ == "__main__":
    sys.exit(main())
