"""三命名空间注册表面黄金清单（T4 AC-1：任务名/参数/短选项/命名空间不回归）。

直接验证生产入口 ``jpman_client.tasks.ns``（invoke Collection），等价于
``invoke --list`` + ``invoke <task> --help`` 的程序化快照，无需起子进程。
"""
from __future__ import annotations

import inspect

from invoke import Task

from jpman_client.tasks import monetize as monetize_mod
from jpman_client.tasks import quant as quant_mod
from jpman_client.tasks import xmnn as xmnn_mod
from jpman_client.tasks import xmnnrt as xmnnrt_mod
from jpman_client.tasks import ns

SIX = ("build", "down", "logs", "ps", "smoke", "up")


def _col(name: str):
    return ns.collections[name]


def _params(task: Task) -> list[str]:
    return [p for p in inspect.signature(task.body).parameters if p != "c"]


def test_namespace_task_sets():
    assert set(_col("quant").tasks) == set(SIX)
    assert set(_col("xmnn").tasks) == {*SIX, "build-tvm", "wheel"}
    assert set(_col("monetize").tasks) == {*SIX, "build-native", "wheel"}
    assert set(_col("xmnnrt").tasks) == set(SIX)


def test_root_and_alias_namespaces_intact():
    # 根 7 命令 + container/env 别名命名空间不被栈重构影响
    assert set(ns.tasks) >= {
        "load", "images", "save", "run", "stop", "status", "clean",
    }
    assert set(_col("container").tasks) == {
        "load", "images", "save", "run", "stop", "status", "clean",
    }
    assert set(_col("env").tasks) == {"build-layer", "run-cmd", "shell"}


def test_docstrings_golden():
    q, x, m = _col("quant"), _col("xmnn"), _col("monetize")
    assert q.tasks["build"].__doc__.startswith("构建 ONNX 量化叠加镜像")
    assert q.tasks["smoke"].__doc__ == "运行 3 个纯 ONNX 冒烟（动态 INT8 / FP16 / 静态 QDQ）。"
    assert x.tasks["build-tvm"].__doc__.startswith("栈内编译 TVM C++ 原生库")
    assert x.tasks["wheel"].__doc__.startswith("栈内执行 Nuitka 全流程打包")
    assert m.tasks["build-native"].__doc__.startswith("栈内 clang++ 编译")
    assert m.tasks["wheel"].__doc__.startswith("栈内 setuptools 打 agent-monetize")
    r = _col("xmnnrt")
    assert r.tasks["build"].__doc__.startswith("暂存 wheel 后构建 xmnn-runtime")
    assert r.tasks["up"].__doc__.startswith("渲染并启动 xmnn-runtime 栈")
    assert r.tasks["smoke"].__doc__ == "运行 xmnn-runtime 守卫：已装 wheel 与内置 torch CPU 的干净环境 10 项验证。"


def test_signatures_golden():
    q, x, m = _col("quant"), _col("xmnn"), _col("monetize")
    # build 参数集（xmnn 多 conda_mirror）
    assert _params(q.tasks["build"]) == ["tag", "base_image", "pip_mirror", "no_cache"]
    assert _params(x.tasks["build"]) == [
        "tag", "base_image", "pip_mirror", "conda_mirror", "no_cache",
    ]
    assert _params(m.tasks["build"]) == ["tag", "base_image", "pip_mirror", "no_cache"]
    # xmnnrt build 多 --wheel 暂存参数（whl 显式指定）
    assert _params(_col("xmnnrt").tasks["build"]) == [
        "tag", "base_image", "pip_mirror", "wheel", "no_cache",
    ]
    # up/smoke：仅 quant 暴露 gpu
    assert _params(q.tasks["up"]) == ["gpu", "skip_build"]
    assert _params(x.tasks["up"]) == ["skip_build"]
    assert _params(m.tasks["up"]) == ["skip_build"]
    assert _params(_col("xmnnrt").tasks["up"]) == ["skip_build"]
    assert _params(q.tasks["smoke"]) == ["gpu"]
    assert _params(x.tasks["smoke"]) == []
    assert _params(m.tasks["smoke"]) == []
    assert _params(_col("xmnnrt").tasks["smoke"]) == []
    # 其余四任务
    for col in (q, x, m, _col("xmnnrt")):
        assert _params(col.tasks["down"]) == ["volumes"]
        assert _params(col.tasks["logs"]) == ["tail"]
        assert _params(col.tasks["ps"]) == []
    # 长任务
    assert _params(x.tasks["build-tvm"]) == []
    assert _params(x.tasks["wheel"]) == ["jobs", "clean", "tvm_flags"]
    assert _params(m.tasks["build-native"]) == []
    assert _params(m.tasks["wheel"]) == []


def test_auto_shortflags_quant_on_others_off():
    for name in SIX:
        assert _col("quant").tasks[name].auto_shortflags is True
        assert _col("xmnn").tasks[name].auto_shortflags is False
        assert _col("monetize").tasks[name].auto_shortflags is False
        assert _col("xmnnrt").tasks[name].auto_shortflags is False
    assert _col("xmnn").tasks["wheel"].auto_shortflags is False
    assert _col("monetize").tasks["wheel"].auto_shortflags is False


def test_modules_bounded_and_declarative():
    """T4 AC-5：声明模块 ≤160 行，且不再内嵌同构编排函数。"""
    for mod in (quant_mod, xmnn_mod, monetize_mod, xmnnrt_mod):
        assert len(inspect.getsource(mod).splitlines()) <= 160, mod.__name__
        src = inspect.getsource(mod)
        for forbidden in ("def _gate_platform", "def _compose_argv", "def _run_compose",
                          "def _reconcile_stale_containers", "def _prepare_env"):
            assert forbidden not in src, (mod.__name__, forbidden)
