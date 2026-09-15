"""overlay_core 数据驱动编排内核的离线单测（无 daemon、无子进程）。

三栈 SPEC 直接从 quant/xmnn/monetize 模块导入（T4 后唯一事实源在模块），
内核行为以这三份真实声明驱动；任务注册表面另见 test_tasks_surface.py。
"""
from __future__ import annotations

import inspect
import os
import re
from types import SimpleNamespace

import pytest
from invoke import Task
from invoke.exceptions import Exit

from jpman_client.tasks import monetize as monetize_mod
from jpman_client.tasks import overlay_core as oc
from jpman_client.tasks import quant as quant_mod
from jpman_client.tasks import xmnn as xmnn_mod

_QUANT = quant_mod.QUANT_SPEC
_XMNN = xmnn_mod.XMNN_SPEC
_MONETIZE = monetize_mod.MONETIZE_SPEC
ALL_SPECS = (_QUANT, _XMNN, _MONETIZE)


# ---------------------------------------------------------------------------
# 夹具：打桩全部宿主/子进程接触面
# ---------------------------------------------------------------------------


class FakeRunner:
    """记录 run_cmd 调用；按命令内容返回可控结果。"""

    def __init__(self, *, running: bool = False, stale: str = "", image_exists: bool = True):
        self.calls: list[tuple[str, dict]] = []
        self.running = running
        self.stale = stale
        self.image_exists = image_exists

    def __call__(self, c, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        if "ps -a -q" in cmd:
            return SimpleNamespace(ok=True, stdout=self.stale, return_code=0)
        if "ps -q" in cmd:
            return SimpleNamespace(ok=True, stdout="cid" if self.running else "", return_code=0)
        if "image exists" in cmd:
            return SimpleNamespace(ok=self.image_exists, stdout="", return_code=0 if self.image_exists else 1)
        return SimpleNamespace(ok=True, stdout="", return_code=0)

    @property
    def commands(self) -> list[str]:
        return [c for c, _ in self.calls]


@pytest.fixture
def harness(monkeypatch, tmp_path):
    root = tmp_path / "repo" / "apps" / "containers" / "client"
    root.mkdir(parents=True)
    for spec in ALL_SPECS:
        d = root / "overlays" / spec.overlay_subdir
        d.mkdir(parents=True, exist_ok=True)
        (d / spec.containerfile).write_text("# fake\n")
    # xmnn 三源码树（仓库根锚点）
    for rel in ("external/chaos/npu_tvm", "external/chaos/npuusertools", "external/chaos/models"):
        (tmp_path / "repo" / rel).mkdir(parents=True)
    (tmp_path / "repo" / "apps" / "agent-monetize").mkdir(parents=True)

    monkeypatch.setattr(oc, "_project_root", lambda: root)
    monkeypatch.setattr(oc, "_load_env_overrides", lambda r: {})
    monkeypatch.setattr(oc, "detect_runtime", lambda: "podman")
    monkeypatch.setattr(oc, "check_runtime_ready", lambda: (True, ""))
    monkeypatch.setattr(oc, "ensure_workspace_checkpoint_writable", lambda p: None)
    # 只替换 overlay_core 内的 platform 绑定，不污染 jpman_common 的真实平台探测
    # （to_posix_path 依赖 platform.system()=="Windows" 做 /mnt/c 转换）。
    monkeypatch.setattr(oc, "platform", SimpleNamespace(system=lambda: "Linux"))
    monkeypatch.setattr(oc.shutil, "which", lambda name: "/usr/bin/podman-compose")
    monkeypatch.setattr(oc, "run_in_wsl_bridge", lambda *a, **k: None)
    # 清掉三栈 env，避免宿主环境污染
    for spec in ALL_SPECS:
        for key in (spec.workspace_env, spec.image_tag_env, spec.ssh_port_env, spec.jupyter_port_env):
            monkeypatch.delenv(key, raising=False)
        for m in spec.source_mounts:
            monkeypatch.delenv(m.env, raising=False)

    runner = FakeRunner()
    monkeypatch.setattr(oc, "run_cmd", runner)
    return SimpleNamespace(root=root, repo=tmp_path / "repo", runner=runner, tmp=tmp_path)


# ---------------------------------------------------------------------------
# compose_argv 黄金快照
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("spec", ALL_SPECS, ids=lambda s: s.namespace)
def test_compose_argv_common_tails(spec, harness):
    d = harness.root / "overlays" / spec.overlay_subdir
    assert oc.compose_argv(spec, "up", "-d") == [
        "podman-compose", "--project-name", spec.project,
        "--file", str(d / "compose.yaml"), "up", "-d",
    ]
    assert oc.compose_argv(spec, "down")[-1] == "down"
    assert oc.compose_argv(spec, "down", "--volumes")[-2:] == ["down", "--volumes"]
    assert oc.compose_argv(spec, "ps")[-1] == "ps"
    assert oc.compose_argv(spec, "logs", "--follow", "--tail=200")[-3:] == [
        "logs", "--follow", "--tail=200",
    ]
    assert oc.compose_argv(
        spec, "exec", "-T", spec.service, "/bin/python", "/opt/x.py"
    )[-5:] == ["exec", "-T", spec.service, "/bin/python", "/opt/x.py"]


def test_compose_argv_gpu_only_quant(harness):
    d = harness.root / "overlays" / "onnx-quantized"
    argv = oc.compose_argv(_QUANT, "up", "-d", gpu=True)
    assert argv == [
        "podman-compose", "--project-name", "onnx-quantized",
        "--file", str(d / "compose.yaml"),
        "--file", str(d / "compose.gpu.yaml"),
        "up", "-d",
    ]
    # 非 GPU 栈不允许 gpu=True（工厂也不会暴露 --gpu）
    for spec in (_XMNN, _MONETIZE):
        with pytest.raises(RuntimeError, match="gpu_override"):
            oc.compose_argv(spec, "up", "-d", gpu=True)


def test_run_compose_quotes_every_token(harness, monkeypatch):
    """AC-2 反例断言：旧 quant.py 裸 '" ".join(argv)' 遇到含空格路径会断词。"""
    spaced = harness.tmp / "dir with space" / "client"
    (spaced / "overlays" / "onnx-quantized").mkdir(parents=True)
    monkeypatch.setattr(oc, "_project_root", lambda: spaced)
    oc.run_compose(None, _QUANT, "down")
    cmd = harness.runner.commands[-1]
    # shlex.quote 对含空格的路径整体加单引号（旧 quant.py 裸 join 会在此断词）
    assert re.search(r"'[^']*dir with space[^']*'", cmd), cmd
    # extends.file 由 podman-compose 按引用文件目录重写（1.6.0 L2845），无需 cd
    assert cmd.startswith("podman-compose")


# ---------------------------------------------------------------------------
# prepare_env
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("spec", ALL_SPECS, ids=lambda s: s.namespace)
def test_prepare_env_workspace_default_and_checkpoint(spec, harness, monkeypatch):
    called = []
    monkeypatch.setattr(oc, "ensure_workspace_checkpoint_writable", lambda p: called.append(p))
    oc.prepare_env(spec)
    ws_local = (harness.root / "workspace").resolve()
    # 注入子进程环境的是 POSIX 串（/mnt/c/...）；checkpoint 放宽作用于宿主本地路径
    assert os.environ[spec.workspace_env] == oc.to_posix_path(ws_local)
    assert ws_local.exists()
    assert called == [ws_local]
    # POSIX 化（无反斜杠/盘符冒号）
    assert "\\" not in os.environ[spec.workspace_env]


@pytest.mark.parametrize("spec", ALL_SPECS, ids=lambda s: s.namespace)
def test_prepare_env_missing_source_mount_hard_fails(spec, harness, monkeypatch):
    if not spec.source_mounts:
        pytest.skip("quant 无源码挂载")
    monkeypatch.setenv(spec.source_mounts[0].env, str(harness.tmp / "no-such-dir"))
    with pytest.raises(Exit) as ei:
        oc.prepare_env(spec)
    assert ei.value.code == 1


def test_prepare_env_xmnn_mounts_anchor_repo_root(harness):
    oc.prepare_env(_XMNN)
    assert os.environ["NPU_TVM_PATH"].endswith("repo/external/chaos/npu_tvm")
    assert os.environ["NPUUSERTOOLS_PATH"].endswith("npuusertools")
    assert os.environ["MODELS_PATH"].endswith("models")


def test_prepare_env_empty_placeholder_does_not_override(harness, monkeypatch):
    """C9：空字符串 env 占位不得覆盖默认值（or 链穿透空串）。"""
    monkeypatch.setenv("QUANT_SSH_PORT", "")
    monkeypatch.setenv("QUANT_IMAGE_TAG", "")
    env = oc.prepare_env(_QUANT)
    assert oc.image_tag(_QUANT, env) == "localhost/onnx-quantized:latest"
    assert oc._env_port(_QUANT, env, "QUANT_SSH_PORT", "2222") == "2222"


# ---------------------------------------------------------------------------
# 门禁
# ---------------------------------------------------------------------------


def test_gate_platform_linux_noop(harness):
    oc.gate_platform(_QUANT)  # 不抛


def test_gate_platform_windows_bridge_passes_stack_keys(harness, monkeypatch):
    """F-10：桥接透传键来自 spec.bridge_env_keys，utils 不枚举具体栈。"""
    seen = {}

    def fake_bridge(argv=None, extra_env_keys=()):
        seen["keys"] = tuple(extra_env_keys)
        return "podman-machine-default"

    monkeypatch.setattr(oc, "platform", SimpleNamespace(system=lambda: "Windows"))
    monkeypatch.setattr(oc, "run_in_wsl_bridge", fake_bridge)
    with pytest.raises(Exit) as ei:
        oc.gate_platform(_XMNN)
    assert ei.value.code == 0
    assert "NPU_TVM_PATH" in seen["keys"]
    assert "QUANT_IMAGE_TAG" not in seen["keys"]


def test_gate_platform_windows_no_bridge_message(harness, monkeypatch, capsys):
    monkeypatch.setattr(oc, "platform", SimpleNamespace(system=lambda: "Windows"))
    monkeypatch.setattr(oc, "run_in_wsl_bridge", lambda *a, **k: None)
    with pytest.raises(Exit) as ei:
        oc.gate_platform(_MONETIZE)
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "[monetize]" in out
    assert "invoke monetize.up" in out
    assert "COMPOSE_WSL_DISTRO" in out


def test_gate_compose_binary_missing(harness, monkeypatch, capsys):
    monkeypatch.setattr(oc.shutil, "which", lambda name: None)
    with pytest.raises(Exit):
        oc.gate_compose_binary(_QUANT)
    assert "[quant]" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# 标签探测 / reconcile
# ---------------------------------------------------------------------------


def test_container_running_label_filters(harness):
    harness.runner.running = True
    assert oc.container_running(None, _XMNN) is True
    cmd = harness.runner.commands[-1]
    assert f"label={oc.PROJECT_LABEL}=xmnn-dev" in cmd
    assert f"label={oc.SERVICE_LABEL}=xmnn" in cmd


def test_reconcile_no_stale_is_noop(harness):
    harness.runner.stale = ""
    oc.reconcile_stale_containers(None, _QUANT, env={})
    assert not any("down" in c for c in harness.runner.commands)


def test_reconcile_stale_triggers_compose_down(harness):
    harness.runner.stale = "dead-cid"
    oc.reconcile_stale_containers(None, _QUANT, env={})
    cmd = harness.runner.commands[-1]
    assert "podman-compose" in cmd and " down" in cmd
    assert "--project-name onnx-quantized" in cmd


# ---------------------------------------------------------------------------
# 任务工厂表面
# ---------------------------------------------------------------------------


def _param_names(task: Task) -> list[str]:
    return [p for p in inspect.signature(task.body).parameters if p != "c"]


def test_factory_six_tasks_and_docs(harness):
    for spec in ALL_SPECS:
        tasks = oc.make_stack_tasks(spec)
        assert set(tasks) == {"build", "up", "down", "ps", "logs", "smoke"}
        assert all(isinstance(t, Task) for t in tasks.values())
        assert tasks["build"].__doc__ == spec.docs.build
        assert tasks["up"].__doc__ == spec.docs.up
        assert tasks["smoke"].__doc__ == spec.docs.smoke


def test_factory_build_signature_conda_variant(harness):
    q = oc.make_stack_tasks(_QUANT)
    x = oc.make_stack_tasks(_XMNN)
    m = oc.make_stack_tasks(_MONETIZE)
    assert _param_names(q["build"]) == ["tag", "base_image", "pip_mirror", "no_cache"]
    assert _param_names(x["build"]) == [
        "tag", "base_image", "pip_mirror", "conda_mirror", "no_cache",
    ]
    assert _param_names(m["build"]) == ["tag", "base_image", "pip_mirror", "no_cache"]


def test_factory_up_smoke_gpu_params_quant_only(harness):
    q, x, m = (oc.make_stack_tasks(s) for s in (_QUANT, _XMNN, _MONETIZE))
    assert _param_names(q["up"]) == ["gpu", "skip_build"]
    assert _param_names(x["up"]) == ["skip_build"]
    assert _param_names(m["up"]) == ["skip_build"]
    assert _param_names(q["smoke"]) == ["gpu"]
    assert _param_names(x["smoke"]) == []
    assert _param_names(m["smoke"]) == []
    assert _param_names(q["down"]) == ["volumes"]
    assert _param_names(x["logs"]) == ["tail"]


def test_factory_auto_shortflags_quant_on_others_off(harness):
    q = oc.make_stack_tasks(_QUANT)
    x = oc.make_stack_tasks(_XMNN)
    assert all(t.auto_shortflags is True for t in q.values())
    assert all(t.auto_shortflags is False for t in x.values())


def test_bridge_keys_isolated_per_stack():
    """桥接键下沉后，各栈只带自己的前缀，不枚举其他栈（F-10）。"""
    joined = " ".join(_QUANT.bridge_env_keys)
    assert "XMNN_" not in joined and "MONETIZE_" not in joined
    assert "QUANT_WORKSPACE" in _QUANT.bridge_env_keys
    assert "NPU_TVM_PATH" in _XMNN.bridge_env_keys
    assert "MONETIZE_SRC_PATH" in _MONETIZE.bridge_env_keys
    xj = " ".join(_XMNN.bridge_env_keys)
    assert "QUANT_" not in xj and "MONETIZE_" not in xj


# ---------------------------------------------------------------------------
# 端到端：任务体执行（仍全部离线打桩）
# ---------------------------------------------------------------------------


def test_build_task_argv_quant_no_conda(harness):
    tasks = oc.make_stack_tasks(_QUANT)
    tasks["build"].body(None, tag="t:1", base_image="b:1", pip_mirror="tuna", no_cache=True)
    build_cmd = [c for c in harness.runner.commands if " build " in c][0]
    assert "--build-arg BASE_IMAGE=b:1" in build_cmd
    assert "--build-arg PIP_MIRROR=tuna" in build_cmd
    assert "-t t:1" in build_cmd
    assert "--no-cache" in build_cmd
    assert "CONDA_MIRROR" not in build_cmd


def test_build_task_argv_xmnn_includes_conda(harness):
    tasks = oc.make_stack_tasks(_XMNN)
    tasks["build"].body(
        None, tag=None, base_image=_XMNN.default_base_image,
        pip_mirror="aliyun", conda_mirror="tuna", no_cache=False,
    )
    build_cmd = [c for c in harness.runner.commands if " build " in c][0]
    assert "--build-arg CONDA_MIRROR=tuna" in build_cmd
    assert "-t localhost/xmnn-dev:latest" in build_cmd


def test_build_missing_base_image_exits(harness):
    harness.runner.image_exists = False
    with pytest.raises(Exit):
        oc.build_image(
            None, _MONETIZE, tag=None,
            base_image="localhost/missing:latest", pip_mirror="official",
        )


def test_up_skip_build_reconcile_and_up_argv(harness):
    oc.up_stack(None, _QUANT, gpu=False, skip_build=True)
    cmds = harness.runner.commands
    assert not any(" build " in c for c in cmds)
    assert any(c.endswith("up -d") or " up -d" in c for c in cmds)


def test_down_task_volumes_flag(harness):
    tasks = oc.make_stack_tasks(_XMNN)
    tasks["down"].body(None, volumes=True)
    assert harness.runner.commands[-1].endswith("down --volumes")


def test_smoke_running_uses_exec_all_scripts(harness):
    harness.runner.running = True
    oc.smoke_stack(None, _QUANT, gpu=False)
    exec_cmds = [c for c in harness.runner.commands if " exec " in c]
    assert len(exec_cmds) == 3
    for script in ("smoke_dynamic_int8.py", "smoke_fp16.py", "smoke_static_qdq.py"):
        assert any(script in c for c in exec_cmds)


def test_smoke_stopped_quant_runs_three_standalone(harness):
    harness.runner.running = False
    oc.smoke_stack(None, _QUANT)
    run_cmds = [c for c in harness.runner.commands if " run --rm " in c]
    assert len(run_cmds) == 3
    assert not any(" exec " in c for c in harness.runner.commands)


def test_smoke_stopped_xmnn_guard_only(harness):
    harness.runner.running = False
    oc.smoke_stack(None, _XMNN)
    run_cmds = [c for c in harness.runner.commands if " run --rm " in c]
    assert len(run_cmds) == 1
    assert "_toolchain_guards.py" in run_cmds[0]
    assert "smoke_mounts.py" not in run_cmds[0]


def test_smoke_running_monetize_two_scripts(harness):
    harness.runner.running = True
    oc.smoke_stack(None, _MONETIZE)
    exec_cmds = [c for c in harness.runner.commands if " exec " in c]
    assert "_toolchain_guards.py" in exec_cmds[0]
    assert "smoke_native.py" in exec_cmds[1]
