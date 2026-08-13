#!/usr/bin/env python3
"""specweave-bridge 一键部署 / 启用 / 验证脚本（零第三方依赖）。

用法:
    python install.py install      # deploy + enable（幂等，自动备份 config.yaml）
    python install.py enable       # 仅幂等启用（改写 config.yaml plugins.enabled）
    python install.py deploy       # 仅拷贝骨架到 HERMES_HOME/plugins/
    python install.py verify       # 校验：插件加载 + 工作区检测 + 路由 + 协议注入
    python install.py all          # install + verify（默认）

设计原则（七概念方法论证）:
    - 面向「结果」而非复刻手动步骤：只有 install 与 verify 两个结果。
    - 复用插件自身的 detector/_handle_specweave_route，避免双份逻辑漂移。
    - 幂等：重复执行无副作用、不重复注入 enabled 列表。
    - enable 前备份 config.yaml，可回滚。
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional

PLUGIN_NAME = "specweave-bridge"
DEFAULT_HERMES_HOME = Path.home() / ".hermes"
# 本脚本所在目录即插件规范源码根目录
SOURCE_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# 路径解析
# ---------------------------------------------------------------------------

def get_hermes_home() -> Path:
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    return DEFAULT_HERMES_HOME


def get_plugin_dir(home: Path) -> Path:
    return home / "plugins" / PLUGIN_NAME


def get_config_path(home: Path) -> Path:
    return home / "config.yaml"


# ---------------------------------------------------------------------------
# deploy — 拷贝骨架到插件目录
# ---------------------------------------------------------------------------

def deploy(home: Path) -> Path:
    target = get_plugin_dir(home)
    # 排除自身安装脚本与文档，仅拷贝运行时必需文件
    for name in ("__init__.py", "_constants.py", "detector.py", "plugin.yaml", "skills"):
        src = SOURCE_DIR / name
        if src.is_dir():
            shutil.copytree(src, target / name, dirs_exist_ok=True)
        elif src.is_file():
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target / name)
    return target


# ---------------------------------------------------------------------------
# enable — 幂等改写 config.yaml（备份 + 仅追加缺失项，保留注释）
# ---------------------------------------------------------------------------

def _is_enabled(lines: List[str], plugin: str) -> bool:
    marker = f"- {plugin}"
    for line in lines:
        if line.strip() == marker:
            return True
    return False


def _top_level_indices(lines: List[str]) -> List[int]:
    """返回所有列 0 顶层键所在行号（跳过空行与注释）。"""
    return [i for i, l in enumerate(lines) if l and not l.startswith((" ", "\t", "#"))]


def enable_plugin(config_path: Path, plugin: str = PLUGIN_NAME) -> str:
    if not config_path.is_file():
        raise FileNotFoundError(f"config.yaml 不存在: {config_path}")

    lines = config_path.read_text(encoding="utf-8").splitlines()

    # 幂等：已启用则直接返回
    if _is_enabled(lines, plugin):
        return "already-enabled"

    # 备份
    backup = config_path.with_name(f"config.yaml.bak-{time.strftime('%Y%m%d%H%M%S')}")
    shutil.copy2(config_path, backup)

    # 定位 plugins 顶层块
    top = _top_level_indices(lines)
    top_keys = {i: lines[i].rstrip(":") for i in top}
    plugins_idx = next((i for i in top if lines[i].startswith("plugins:")), None)

    if plugins_idx is None:
        # 无 plugins 块：在 model 块之后 / providers 之前插入
        insert_idx = next((i for i in top if lines[i].startswith("providers:")), len(lines))
        block = ["", "plugins:", "  enabled:", f"  - {plugin}"]
        new_lines = lines[:insert_idx] + block + lines[insert_idx:]
        _write(config_path, new_lines)
        return "created-block"

    # 有 plugins 块：定位其块内 enabled
    block_end = next((i for i in top if i > plugins_idx), len(lines))
    block = lines[plugins_idx + 1 : block_end]
    enabled_idx = next(
        (i for i, l in enumerate(block) if l.strip().startswith("enabled:")), None
    )

    if enabled_idx is None:
        # 块内无 enabled：在块末尾追加
        new_lines = lines[:block_end] + ["  enabled:", f"  - {plugin}"] + lines[block_end:]
        _write(config_path, new_lines)
        return "added-enabled"

    # 块内有 enabled：追加到列表末尾
    # 找 enabled 之后的第一个顶层键前插入；若块内 enabled 是最后一项则追加到 block_end
    list_items_end = block_end
    for i in range(plugins_idx + 1 + enabled_idx + 1, block_end):
        if block[i - (plugins_idx + 1)].strip().startswith("- "):
            list_items_end = i + 1
        else:
            break
    new_lines = (
        lines[:list_items_end] + [f"  - {plugin}"] + lines[list_items_end:]
    )
    _write(config_path, new_lines)
    return "appended-item"


def _write(config_path: Path, lines: List[str]) -> None:
    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# verify — 复用插件真实逻辑做校验
# ---------------------------------------------------------------------------

def _load_plugin(plugin_dir: Path):
    init = plugin_dir / "__init__.py"
    if not init.is_file():
        raise FileNotFoundError(f"插件 __init__.py 不存在: {init}")
    name = PLUGIN_NAME.replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, init)
    mod = importlib.util.module_from_spec(spec)
    # 作为包加载：注册到 sys.modules 并设置 __path__，以支持 `from . import detector`
    sys.modules[name] = mod
    mod.__path__ = [str(plugin_dir)]
    spec.loader.exec_module(mod)
    return mod


def verify(home: Path, cwd: Optional[str] = None) -> dict:
    cwd = cwd or os.getcwd()
    plugin_dir = get_plugin_dir(home)
    result = {
        "plugin_dir": str(plugin_dir),
        "plugin_yaml_exists": (plugin_dir / "plugin.yaml").is_file(),
        "enabled_in_config": False,
        "workspace_root": None,
        "subregion": None,
        "route_ok": None,
        "hook_injection": None,
    }

    # 1. 配置已启用
    config_path = get_config_path(home)
    if config_path.is_file():
        result["enabled_in_config"] = _is_enabled(
            config_path.read_text(encoding="utf-8").splitlines(), PLUGIN_NAME
        )

    # 2. 复用插件逻辑做工作区 / 路由 / 协议注入校验
    if result["plugin_yaml_exists"]:
        try:
            mod = _load_plugin(plugin_dir)
            result["workspace_root"] = mod.detector.find_specweave_root(cwd)
            if result["workspace_root"]:
                result["subregion"] = mod.detector.detect_subregion(
                    cwd, result["workspace_root"]
                )
                route = mod._handle_specweave_route({"task": "复盘", "cwd": cwd})
                result["route_ok"] = '"ok": true' in route
                result["hook_injection"] = mod._on_pre_llm_call() is not None
        except Exception as exc:  # pragma: no cover - 校验失败也返回，不崩溃
            result["plugin_error"] = str(exc)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    argv = list(argv) if argv else sys.argv[1:]
    cmd = (argv[0] if argv else "all").lower()
    home = get_hermes_home()

    if cmd in ("install", "enable", "deploy"):
        if cmd in ("install", "deploy"):
            target = deploy(home)
            print(f"[deploy] 已拷贝插件到 {target}")
        if cmd in ("install", "enable"):
            config_path = get_config_path(home)
            status = enable_plugin(config_path)
            print(f"[enable] {status}: plugins.enabled 含 {PLUGIN_NAME}")
        if cmd == "install":
            print("[install] 完成。重启 Hermes 会话生效。")
        return 0

    if cmd == "verify":
        result = verify(home)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        ok = (
            result["plugin_yaml_exists"]
            and result["enabled_in_config"]
            and result["route_ok"] is True
        )
        print("\n[verify]", "PASS ✅" if ok else "FAIL ❌")
        return 0 if ok else 1

    if cmd == "all":
        if install_return := main(["install"]):
            return install_return
        return main(["verify"])

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
